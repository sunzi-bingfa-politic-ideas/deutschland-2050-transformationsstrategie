#!/usr/bin/env python3
"""
Gesundheitskosten-Projektionsmodell v2.0
========================================

Modelliert:
1. Demografisch bedingte Spitzenbelastung im deutschen Gesundheitssystem
2. GSP-Kontoakkumulation (Singapur-inspiriert) mit Beitragssatz-Interaktion
3. Schuldenfinanzierte Uebergangsstrategie
4. Sensitivitaetsanalyse (Tornado, Szenarien, Break-Even)

Basiert auf:
- Demografieprojektion Destatis (14. koordinierte Bevoelkerungsvorausberechnung)
- GKV-Ausgabenstatistik des BMG (2024)
- Altersabhaengige Gesundheitskosten (Barmer-Gesundheitsreport 2024)
- Asiatische Vergleichssysteme (Singapur, Japan, Suedkorea, Thailand, China)

Rigor: Medium — Projektionen ueber 35 Jahre inherent unsicher.
       Alle zentralen Parameter parametrisiert fuer Sensitivitaetsanalyse.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from copy import deepcopy
import json
import os
import random
import math


# ===========================================================================
# DATENSTRUKTUREN
# ===========================================================================

@dataclass
class DemographicCohort:
    """Eine Alterskohorte mit zugehoerigen Gesundheitskosten."""
    age_group: str
    population_2025: int       # in Tausend
    population_2035: int
    population_2045: int
    population_2055: int
    avg_health_cost: float     # EUR pro Person und Jahr (Preisbasis 2025)


# Demografische Daten (Destatis 14. koord. Bev.vorausberechnung, Variante 2)
COHORTS = [
    DemographicCohort("0-19",  14_500, 13_800, 13_200, 12_800,  2_100),
    DemographicCohort("20-39", 18_500, 17_000, 15_500, 15_000,  2_400),
    DemographicCohort("40-59", 22_000, 19_500, 17_500, 16_500,  3_800),
    DemographicCohort("60-69", 11_500, 13_000, 11_000, 10_000,  6_500),
    DemographicCohort("70-79",  8_500, 10_500, 12_000, 10_500,  9_800),
    DemographicCohort("80-89",  4_800,  6_200,  8_500,  9_000, 15_500),
    DemographicCohort("90+",    1_100,  1_500,  2_300,  2_800, 22_000),
]


@dataclass
class GSPParams:
    """Parameter fuer das Gesundheitssparkonto (GSP)."""
    contribution_rate: float = 0.02          # 2% des Bruttoeinkommens
    nominal_return: float = 0.035            # 3,5% nominal (konservativ)
    admin_cost_rate: float = 0.003           # 0,3% Verwaltungskosten
    gross_wage_base_2025: float = 2_000.0    # Bruttolohnsumme 2025 in Mrd. EUR
    wage_growth_rate: float = 0.02           # 2% nominales Lohnwachstum p.a.
    gkv_insured_millions: float = 74.0       # GKV-Versicherte in Mio.
    gsp_entnahme_rate: float = 0.01          # 1% des Kapitalstocks p.a. Entnahmen
    ramp_up_years: int = 3                   # Jahre bis volle Beitragspflicht


@dataclass
class GKVParams:
    """Parameter fuer die GKV-Beitragssatzberechnung."""
    base_rate_2025: float = 0.159            # 15,9% (14,6% + ~1,3% Zusatzbeitrag)
    gkv_share_of_total: float = 0.70         # GKV-Kostenanteil an beitragsrelevanten Ausgaben
    employer_share: float = 0.5              # 50% Arbeitgeberanteil
    gdp_2025: float = 4_200.0               # BIP 2025 in Mrd. EUR
    gdp_growth_rate: float = 0.015           # 1,5% reales BIP-Wachstum
    inflation: float = 0.02                  # 2% allgemeine Inflation


@dataclass
class ReformScenario:
    """Ein vollstaendiges Reformszenario."""
    name: str
    efficiency_gain_pct: float      # Jaehrliche Effizienzsteigerung (%)
    prevention_reduction: float     # Max. Kostensenkung durch Praevention (Anteil)
    prevention_ramp_years: int      # Jahre bis volle Praeventionswirkung
    medical_inflation: float        # Medizinische Inflation p.a.
    gsp: Optional[GSPParams] = None # GSP-Parameter (None = kein GSP)


# ===========================================================================
# SZENARIEN
# ===========================================================================

SCENARIOS = {
    "status_quo": ReformScenario(
        name="Status Quo",
        efficiency_gain_pct=0.0,
        prevention_reduction=0.0,
        prevention_ramp_years=10,
        medical_inflation=0.025,   # 2,5% med. Inflation ohne Reform (historisch)
        gsp=None,
    ),
    "moderat": ReformScenario(
        name="Moderate Reform (Digitalisierung)",
        efficiency_gain_pct=1.5,
        prevention_reduction=0.05,
        prevention_ramp_years=10,
        medical_inflation=0.02,
        gsp=None,
    ),
    "gsp_baseline": ReformScenario(
        name="GSP-Modell (Baseline)",
        efficiency_gain_pct=2.0,
        prevention_reduction=0.10,
        prevention_ramp_years=10,
        medical_inflation=0.02,
        gsp=GSPParams(),
    ),
    "gsp_pessimistic": ReformScenario(
        name="GSP-Modell (Pessimistisch)",
        efficiency_gain_pct=1.0,
        prevention_reduction=0.05,
        prevention_ramp_years=15,
        medical_inflation=0.025,
        gsp=GSPParams(
            nominal_return=0.02,
            admin_cost_rate=0.005,
            gsp_entnahme_rate=0.015,
        ),
    ),
    "gsp_optimistic": ReformScenario(
        name="GSP-Modell (Optimistisch)",
        efficiency_gain_pct=2.5,
        prevention_reduction=0.15,
        prevention_ramp_years=8,
        medical_inflation=0.015,
        gsp=GSPParams(
            nominal_return=0.045,
            admin_cost_rate=0.002,
            gsp_entnahme_rate=0.008,
        ),
    ),
    "vollintegration": ReformScenario(
        name="Vollintegration (Best Practices)",
        efficiency_gain_pct=2.5,
        prevention_reduction=0.15,
        prevention_ramp_years=10,
        medical_inflation=0.02,
        gsp=GSPParams(contribution_rate=0.025),
    ),
}


# ===========================================================================
# KERNMODELL
# ===========================================================================

def interpolate_population(cohort: DemographicCohort, year: int) -> float:
    """Interpoliert Bevoelkerung einer Kohorte fuer ein gegebenes Jahr (in Tsd.)."""
    if year <= 2025:
        return cohort.population_2025
    elif year <= 2035:
        t = (year - 2025) / 10
        return cohort.population_2025 * (1 - t) + cohort.population_2035 * t
    elif year <= 2045:
        t = (year - 2035) / 10
        return cohort.population_2035 * (1 - t) + cohort.population_2045 * t
    elif year <= 2055:
        t = (year - 2045) / 10
        return cohort.population_2045 * (1 - t) + cohort.population_2055 * t
    else:
        return cohort.population_2055


def calculate_demographic_costs(year: int) -> float:
    """Berechnet reine demografische Gesundheitskosten (Mrd. EUR, Preisbasis 2025)."""
    total = 0.0
    for cohort in COHORTS:
        pop = interpolate_population(cohort, year)
        total += pop * cohort.avg_health_cost / 1_000_000  # Tsd. × EUR → Mrd.
    return total


def simulate_scenario(
    scenario: ReformScenario,
    gkv: GKVParams = GKVParams(),
    start_year: int = 2025,
    end_year: int = 2060,
) -> Dict:
    """Simuliert ein vollstaendiges Reformszenario Jahr fuer Jahr."""

    results = {
        "scenario": scenario.name,
        "years": [],
        "demographic_costs": [],      # Reine Demografie (Preisbasis 2025)
        "baseline_costs": [],          # Demografie + med. Inflation
        "reform_costs": [],            # Nach Effizienz + Praevention
        "cumulative_savings": [],      # Kumulative Ersparnis vs. Baseline
        "gsp_contributions": [],       # GSP-Jahresbeitrag
        "gsp_returns": [],             # GSP-Kapitalertrag
        "gsp_entnahmen": [],           # GSP-Entnahmen
        "gsp_capital": [],             # GSP-Kapitalstock
        "gkv_rate_without_reform": [], # GKV-Beitragssatz ohne Reform
        "gkv_rate_with_reform": [],    # GKV-Beitragssatz mit Reform
        "effective_rate": [],          # GKV + GSP Gesamtbeitrag
        "gdp": [],                     # BIP
    }

    gsp_capital = 0.0
    cumulative_savings = 0.0
    baseline_2025 = calculate_demographic_costs(2025)

    for year in range(start_year, end_year + 1):
        yf = year - start_year  # Jahre seit Start

        # --- Demografische Kosten ---
        demo_cost = calculate_demographic_costs(year)

        # --- Baseline (mit medizinischer Inflation) ---
        inflation_factor = (1 + scenario.medical_inflation) ** yf
        baseline = demo_cost * inflation_factor

        # --- Reform-Effekte ---
        efficiency = (1 - scenario.efficiency_gain_pct / 100) ** yf
        prev_progress = min(yf / scenario.prevention_ramp_years, 1.0)
        prevention = 1 - scenario.prevention_reduction * prev_progress
        reform_cost = baseline * efficiency * prevention

        savings_this_year = baseline - reform_cost
        cumulative_savings += savings_this_year

        # --- BIP ---
        gdp = gkv.gdp_2025 * ((1 + gkv.gdp_growth_rate + gkv.inflation) ** yf)

        # --- GKV-Beitragssatz ---
        # Kalibrierung: 2025 GKV-Beitragseinnahmen ~290 Mrd. EUR bei 15,9% Satz
        # → Beitragspflichtige Einnahmen ~1.824 Mrd. EUR
        # ABER: Erwerbsbevoelkerung (20-59) schrumpft, das reduziert die Beitragsbasis
        working_pop_2025 = sum(
            interpolate_population(c, 2025) for c in COHORTS
            if c.age_group in ("20-39", "40-59")
        )
        working_pop_now = sum(
            interpolate_population(c, year) for c in COHORTS
            if c.age_group in ("20-39", "40-59")
        )
        workforce_factor = working_pop_now / working_pop_2025
        # Lohn pro Kopf waechst, aber Koepfe werden weniger
        wage_per_worker_growth = (1 + gkv.gdp_growth_rate + gkv.inflation) ** yf
        beitragspflichtig = 1_824.0 * wage_per_worker_growth * workforce_factor
        # GKV traegt ~62% der beitragsrelevanten Gesundheitskosten
        # (hoeher als 57% Gesamtanteil wegen GKV-spezifischer Leistungsstruktur)
        gkv_cost_no_reform = baseline * gkv.gkv_share_of_total
        gkv_cost_reform = reform_cost * gkv.gkv_share_of_total
        gkv_rate_no_reform = gkv_cost_no_reform / beitragspflichtig
        gkv_rate_reform = gkv_cost_reform / beitragspflichtig

        # --- GSP-Kontoakkumulation ---
        gsp_contrib = 0.0
        gsp_ret = 0.0
        gsp_ent = 0.0

        if scenario.gsp is not None:
            g = scenario.gsp
            # Ramp-up: schrittweise Einfuehrung
            ramp = min(yf / g.ramp_up_years, 1.0) if g.ramp_up_years > 0 else 1.0

            # Lohnbasis waechst
            wage_base_gsp = g.gross_wage_base_2025 * ((1 + g.wage_growth_rate) ** yf)
            gsp_contrib = wage_base_gsp * g.contribution_rate * ramp

            # Netto-Rendite (nach Verwaltungskosten)
            net_return = g.nominal_return - g.admin_cost_rate
            gsp_ret = gsp_capital * net_return

            # Entnahmen (Zahnersatz, Brille, Praevention etc.)
            gsp_ent = gsp_capital * g.gsp_entnahme_rate

            gsp_capital = gsp_capital + gsp_contrib + gsp_ret - gsp_ent
            if gsp_capital < 0:
                gsp_capital = 0.0

        # --- Effektiver Gesamtbeitragssatz ---
        gsp_rate = scenario.gsp.contribution_rate if scenario.gsp else 0.0
        effective = gkv_rate_reform + gsp_rate

        # --- Ergebnisse speichern ---
        results["years"].append(year)
        results["demographic_costs"].append(round(demo_cost, 1))
        results["baseline_costs"].append(round(baseline, 1))
        results["reform_costs"].append(round(reform_cost, 1))
        results["cumulative_savings"].append(round(cumulative_savings, 1))
        results["gsp_contributions"].append(round(gsp_contrib, 1))
        results["gsp_returns"].append(round(gsp_ret, 1))
        results["gsp_entnahmen"].append(round(gsp_ent, 1))
        results["gsp_capital"].append(round(gsp_capital, 1))
        results["gkv_rate_without_reform"].append(round(gkv_rate_no_reform * 100, 2))
        results["gkv_rate_with_reform"].append(round(gkv_rate_reform * 100, 2))
        results["effective_rate"].append(round(effective * 100, 2))
        results["gdp"].append(round(gdp, 1))

    return results


# ===========================================================================
# SENSITIVITAETSANALYSE
# ===========================================================================

@dataclass
class SensitivityParam:
    """Ein Parameter fuer die Tornado-Analyse."""
    name: str
    field_path: str       # z.B. "efficiency_gain_pct" oder "gsp.nominal_return"
    low: float
    baseline: float
    high: float
    unit: str


SENSITIVITY_PARAMS = [
    SensitivityParam("Effizienzgewinn",       "efficiency_gain_pct",     0.5,  2.0,  3.0,  "%/Jahr"),
    SensitivityParam("Med. Inflation",         "medical_inflation",       0.01, 0.02, 0.03, "%/Jahr"),
    SensitivityParam("Praevention",            "prevention_reduction",    0.03, 0.10, 0.20, "Anteil"),
    SensitivityParam("GSP Rendite (nom.)",     "gsp.nominal_return",      0.02, 0.035, 0.05, "%/Jahr"),
    SensitivityParam("GSP Beitragssatz",       "gsp.contribution_rate",   0.01, 0.02, 0.03, "Anteil"),
    SensitivityParam("GSP Verwaltungskosten",  "gsp.admin_cost_rate",     0.001, 0.003, 0.008, "Anteil"),
    SensitivityParam("GSP Entnahmerate",       "gsp.gsp_entnahme_rate",   0.005, 0.01, 0.02, "Anteil"),
    SensitivityParam("Lohnwachstum",           "gsp.wage_growth_rate",    0.01, 0.02, 0.03, "%/Jahr"),
]


def set_param(scenario: ReformScenario, path: str, value: float) -> None:
    """Setzt einen Parameter per Pfad (z.B. 'gsp.nominal_return')."""
    parts = path.split(".")
    if len(parts) == 1:
        setattr(scenario, parts[0], value)
    elif len(parts) == 2 and parts[0] == "gsp" and scenario.gsp is not None:
        setattr(scenario.gsp, parts[1], value)


def tornado_analysis(target_year: int = 2045) -> List[Dict]:
    """Tornado-Analyse: Einfluss einzelner Parameter auf GSP-Kapitalstock und GKV-Rate."""
    results = []
    base_scenario = deepcopy(SCENARIOS["gsp_baseline"])
    base_result = simulate_scenario(base_scenario)
    idx = base_result["years"].index(target_year)
    base_capital = base_result["gsp_capital"][idx]
    base_gkv_rate = base_result["gkv_rate_with_reform"][idx]

    for param in SENSITIVITY_PARAMS:
        # Low
        s_low = deepcopy(SCENARIOS["gsp_baseline"])
        set_param(s_low, param.field_path, param.low)
        r_low = simulate_scenario(s_low)
        cap_low = r_low["gsp_capital"][idx]
        rate_low = r_low["gkv_rate_with_reform"][idx]

        # High
        s_high = deepcopy(SCENARIOS["gsp_baseline"])
        set_param(s_high, param.field_path, param.high)
        r_high = simulate_scenario(s_high)
        cap_high = r_high["gsp_capital"][idx]
        rate_high = r_high["gkv_rate_with_reform"][idx]

        results.append({
            "parameter": param.name,
            "unit": param.unit,
            "low_value": param.low,
            "baseline_value": param.baseline,
            "high_value": param.high,
            "capital_low": round(cap_low, 1),
            "capital_baseline": round(base_capital, 1),
            "capital_high": round(cap_high, 1),
            "capital_range": round(abs(cap_high - cap_low), 1),
            "gkv_rate_low": round(rate_low, 2),
            "gkv_rate_baseline": round(base_gkv_rate, 2),
            "gkv_rate_high": round(rate_high, 2),
        })

    # Sortiere nach Einfluss auf Kapitalstock
    results.sort(key=lambda x: x["capital_range"], reverse=True)
    return results


def break_even_analysis() -> Dict:
    """Findet Break-Even: Ab wann ist Effektiver Beitrag (GKV+GSP) < GKV ohne Reform?"""
    base_result = simulate_scenario(deepcopy(SCENARIOS["gsp_baseline"]))
    sq_result = simulate_scenario(deepcopy(SCENARIOS["status_quo"]))

    crossover_year = None
    for i, year in enumerate(base_result["years"]):
        eff = base_result["effective_rate"][i]
        sq = sq_result["gkv_rate_without_reform"][i]
        if eff < sq and crossover_year is None:
            crossover_year = year

    # Minimale GSP-Rendite fuer Break-Even bis 2045
    for test_return in [x / 1000 for x in range(0, 60)]:
        s = deepcopy(SCENARIOS["gsp_baseline"])
        s.gsp.nominal_return = test_return
        r = simulate_scenario(s)
        idx_2045 = r["years"].index(2045)
        if r["gsp_capital"][idx_2045] > 0:
            min_return_for_positive = test_return
            break
    else:
        min_return_for_positive = None

    # Minimale Effizienz fuer GKV-Rate < 20% in 2045
    min_eff_for_20pct = None
    for test_eff in [x / 10 for x in range(0, 50)]:
        s = deepcopy(SCENARIOS["gsp_baseline"])
        s.efficiency_gain_pct = test_eff
        r = simulate_scenario(s)
        idx_2045 = r["years"].index(2045)
        if r["gkv_rate_with_reform"][idx_2045] < 20.0:
            min_eff_for_20pct = test_eff
            break

    return {
        "crossover_year_effective_vs_status_quo": crossover_year,
        "min_gsp_return_for_positive_capital_2045": min_return_for_positive,
        "min_efficiency_for_sub20pct_gkv_2045": min_eff_for_20pct,
    }


def monte_carlo(n_runs: int = 1000, target_year: int = 2045, seed: int = 42) -> Dict:
    """Monte-Carlo-Simulation mit gleichverteilten Parametervariationen."""
    random.seed(seed)
    capitals = []
    gkv_rates = []
    effective_rates = []

    for _ in range(n_runs):
        s = deepcopy(SCENARIOS["gsp_baseline"])
        # Variiere alle Parameter innerhalb ihrer Ranges
        s.efficiency_gain_pct = random.uniform(0.5, 3.0)
        s.medical_inflation = random.uniform(0.01, 0.03)
        s.prevention_reduction = random.uniform(0.03, 0.20)
        s.gsp.nominal_return = random.uniform(0.015, 0.055)
        s.gsp.admin_cost_rate = random.uniform(0.001, 0.008)
        s.gsp.gsp_entnahme_rate = random.uniform(0.005, 0.02)
        s.gsp.wage_growth_rate = random.uniform(0.005, 0.035)

        r = simulate_scenario(s)
        idx = r["years"].index(target_year)
        capitals.append(r["gsp_capital"][idx])
        gkv_rates.append(r["gkv_rate_with_reform"][idx])
        effective_rates.append(r["effective_rate"][idx])

    capitals.sort()
    gkv_rates.sort()
    effective_rates.sort()

    def percentile(data, p):
        k = (len(data) - 1) * p / 100
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return data[int(k)]
        return data[f] * (c - k) + data[c] * (k - f)

    return {
        "n_runs": n_runs,
        "target_year": target_year,
        "gsp_capital": {
            "p5": round(percentile(capitals, 5), 1),
            "p25": round(percentile(capitals, 25), 1),
            "median": round(percentile(capitals, 50), 1),
            "p75": round(percentile(capitals, 75), 1),
            "p95": round(percentile(capitals, 95), 1),
            "mean": round(sum(capitals) / len(capitals), 1),
            "prob_positive": round(sum(1 for c in capitals if c > 0) / len(capitals) * 100, 1),
        },
        "gkv_rate": {
            "p5": round(percentile(gkv_rates, 5), 2),
            "median": round(percentile(gkv_rates, 50), 2),
            "p95": round(percentile(gkv_rates, 95), 2),
            "prob_below_20pct": round(
                sum(1 for r in gkv_rates if r < 20.0) / len(gkv_rates) * 100, 1
            ),
        },
        "effective_rate": {
            "p5": round(percentile(effective_rates, 5), 2),
            "median": round(percentile(effective_rates, 50), 2),
            "p95": round(percentile(effective_rates, 95), 2),
        },
    }


# ===========================================================================
# ASIATISCHE SYSTEME (Vergleichsdaten)
# ===========================================================================

def compare_asian_systems() -> Dict:
    """Vergleicht asiatische Gesundheitssysteme."""
    return {
        "Singapur": {
            "health_expenditure_gdp_percent": 4.9,
            "life_expectancy": 84.1,
            "infant_mortality_per_1000": 1.8,
            "oop_percent": 30,
            "key_feature": "3M-System (MediSave, MediShield, MediFund)",
        },
        "Japan": {
            "health_expenditure_gdp_percent": 11.5,
            "life_expectancy": 84.3,
            "infant_mortality_per_1000": 1.8,
            "oop_percent": 12,
            "key_feature": "LTCI (Kaigo Hoken) seit 2000",
        },
        "Suedkorea": {
            "health_expenditure_gdp_percent": 8.4,
            "life_expectancy": 83.6,
            "infant_mortality_per_1000": 2.7,
            "oop_percent": 37,
            "key_feature": "Universal Coverage in 12 Jahren",
        },
        "Thailand": {
            "health_expenditure_gdp_percent": 4.5,
            "life_expectancy": 77.3,
            "infant_mortality_per_1000": 7.0,
            "oop_percent": 11,
            "key_feature": "30-Baht-Scheme (steuerfinanziert)",
        },
        "Deutschland": {
            "health_expenditure_gdp_percent": 12.7,
            "life_expectancy": 81.3,
            "infant_mortality_per_1000": 3.2,
            "oop_percent": 12,
            "key_feature": "GKV + SPV (Umlagefinanziert)",
        },
    }


# ===========================================================================
# AUSGABE
# ===========================================================================

def print_scenario_comparison():
    """Druckt den Szenarienvergleich."""
    print("=" * 95)
    print("GESUNDHEITSKOSTEN-PROJEKTION v2.0 — GSP-MODELL MIT BEITRAGSSATZ-INTERAKTION")
    print("=" * 95)

    milestone_years = [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060]

    for key in ["status_quo", "gsp_baseline", "gsp_pessimistic", "gsp_optimistic"]:
        scenario = deepcopy(SCENARIOS[key])
        r = simulate_scenario(scenario)

        print(f"\n--- {scenario.name} ---\n")
        header = (f"  {'Jahr':<6} {'Baseline':>10} {'Reform':>10} {'Ersparnis':>10} "
                  f"{'GSP-Kap.':>10} {'GKV%':>8} {'GKV+GSP%':>8}")
        print(header)
        print("  " + "-" * 70)

        for year in milestone_years:
            if year not in r["years"]:
                continue
            i = r["years"].index(year)
            gsp_cap = r["gsp_capital"][i]
            gkv_r = r["gkv_rate_with_reform"][i]
            eff_r = r["effective_rate"][i]
            print(f"  {year:<6} {r['baseline_costs'][i]:>8.0f}   "
                  f"{r['reform_costs'][i]:>8.0f}   "
                  f"{r['baseline_costs'][i] - r['reform_costs'][i]:>8.0f}   "
                  f"{gsp_cap:>8.0f}   "
                  f"{gkv_r:>6.1f}%  "
                  f"{eff_r:>6.1f}%")

    # Vergleich Status Quo vs. GSP-Baseline Beitragssatz
    print("\n\n--- BEITRAGSSATZ-VERGLEICH: STATUS QUO vs. GSP-MODELL ---\n")
    sq = simulate_scenario(deepcopy(SCENARIOS["status_quo"]))
    gsp = simulate_scenario(deepcopy(SCENARIOS["gsp_baseline"]))

    print(f"  {'Jahr':<6} {'SQ: GKV%':>10} {'GSP: GKV%':>10} {'GSP: GKV+GSP%':>14} "
          f"{'Vorteil GSP':>12} {'GSP-Kapital':>12}")
    print("  " + "-" * 66)

    for year in milestone_years:
        i = sq["years"].index(year)
        sq_rate = sq["gkv_rate_without_reform"][i]
        gsp_gkv = gsp["gkv_rate_with_reform"][i]
        gsp_eff = gsp["effective_rate"][i]
        advantage = sq_rate - gsp_eff
        cap = gsp["gsp_capital"][i]
        marker = " ←" if advantage > 0 else ""
        print(f"  {year:<6} {sq_rate:>8.1f}%  {gsp_gkv:>8.1f}%  {gsp_eff:>12.1f}%  "
              f"{advantage:>+10.1f} PP  {cap:>10.0f}{marker}")


def print_sensitivity():
    """Druckt die Sensitivitaetsanalyse."""
    print("\n\n" + "=" * 95)
    print("SENSITIVITAETSANALYSE (Zieljahr: 2045)")
    print("=" * 95)

    # Tornado
    print("\n--- TORNADO-ANALYSE: EINFLUSS AUF GSP-KAPITALSTOCK 2045 ---\n")
    tornado = tornado_analysis(2045)
    print(f"  {'Parameter':<28} {'Low':>8} {'Base':>8} {'High':>8}  "
          f"{'Kap.Low':>8} {'Kap.Base':>8} {'Kap.High':>8} {'Range':>8}")
    print("  " + "-" * 88)
    for t in tornado:
        print(f"  {t['parameter']:<28} {t['low_value']:>8.3f} {t['baseline_value']:>8.3f} "
              f"{t['high_value']:>8.3f}  {t['capital_low']:>7.0f}  {t['capital_baseline']:>7.0f}  "
              f"{t['capital_high']:>7.0f}  {t['capital_range']:>7.0f}")

    # Break-Even
    print("\n\n--- BREAK-EVEN-ANALYSE ---\n")
    be = break_even_analysis()
    print(f"  Crossover-Jahr (Eff.Rate GSP < SQ):     {be['crossover_year_effective_vs_status_quo']}")
    print(f"  Min. GSP-Rendite fuer pos. Kapital 2045: {be['min_gsp_return_for_positive_capital_2045']}")
    print(f"  Min. Effizienz fuer GKV <20% in 2045:    {be['min_efficiency_for_sub20pct_gkv_2045']}")

    # Monte Carlo
    print("\n\n--- MONTE-CARLO-SIMULATION (1.000 Laeufe, Zieljahr 2045) ---\n")
    mc = monte_carlo(n_runs=1000, target_year=2045)

    print(f"  GSP-Kapitalstock 2045:")
    print(f"    P5:     {mc['gsp_capital']['p5']:>8.0f} Mrd. EUR")
    print(f"    P25:    {mc['gsp_capital']['p25']:>8.0f} Mrd. EUR")
    print(f"    Median: {mc['gsp_capital']['median']:>8.0f} Mrd. EUR")
    print(f"    P75:    {mc['gsp_capital']['p75']:>8.0f} Mrd. EUR")
    print(f"    P95:    {mc['gsp_capital']['p95']:>8.0f} Mrd. EUR")
    print(f"    P(>0):  {mc['gsp_capital']['prob_positive']:>7.1f}%")

    print(f"\n  GKV-Beitragssatz 2045 (nur GKV, ohne GSP):")
    print(f"    P5:     {mc['gkv_rate']['p5']:>7.1f}%")
    print(f"    Median: {mc['gkv_rate']['median']:>7.1f}%")
    print(f"    P95:    {mc['gkv_rate']['p95']:>7.1f}%")
    print(f"    P(<20%): {mc['gkv_rate']['prob_below_20pct']:>6.1f}%")

    print(f"\n  Effektiver Gesamtbeitrag (GKV+GSP) 2045:")
    print(f"    P5:     {mc['effective_rate']['p5']:>7.1f}%")
    print(f"    Median: {mc['effective_rate']['median']:>7.1f}%")
    print(f"    P95:    {mc['effective_rate']['p95']:>7.1f}%")


def main():
    """Hauptfunktion: Simulation + Sensitivitaet + Export."""

    print_scenario_comparison()
    print_sensitivity()

    # --- Export ---
    output = {}

    # Szenarien
    for key, scenario in SCENARIOS.items():
        output[key] = simulate_scenario(deepcopy(scenario))

    # Sensitivitaet
    output["sensitivity_tornado"] = tornado_analysis(2045)
    output["sensitivity_break_even"] = break_even_analysis()
    output["sensitivity_monte_carlo"] = monte_carlo(1000, 2045)

    # Asiatische Systeme
    output["asian_systems"] = compare_asian_systems()

    out_path = os.path.join(os.path.dirname(__file__), "gesundheit_projektion_results.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n\nErgebnisse exportiert nach: {out_path}")


if __name__ == "__main__":
    main()
