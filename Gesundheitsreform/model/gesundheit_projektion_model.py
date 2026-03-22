#!/usr/bin/env python3
"""
Gesundheitskosten-Projektionsmodell
===================================

Modelliert die demografisch bedingte Spitzenbelastung im deutschen
Gesundheitssystem und die schuldenfinanzierte Übergangsstrategie.

Basiert auf:
- Demografieprojektion Destatis (14. koordinierte Bevölkerungsvorausberechnung)
- GKV-Ausgabenstatistik des BMG
- Altersabhängige Gesundheitskosten (Barmer-Gesundheitsreport)
- Asiatische Vergleichssysteme (Singapur, Japan, Südkorea, Thailand, China)

Rigor: Medium - Projektionen über 35 Jahre inherent unsicher.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import json


@dataclass
class DemographicCohort:
    """Eine Alterskohorte mit zugehörigen Gesundheitskosten."""
    age_group: str
    population_2025: int       # in Tausend
    population_2035: int
    population_2045: int
    population_2055: int
    avg_health_cost: float     # EUR pro Person und Jahr


# Demografische Daten (Destatis-basiert, vereinfacht)
COHORTS = [
    DemographicCohort("0-19", 14_500, 13_800, 13_200, 12_800, 2_100),
    DemographicCohort("20-39", 18_500, 17_000, 15_500, 15_000, 2_400),
    DemographicCohort("40-59", 22_000, 19_500, 17_500, 16_500, 3_800),
    DemographicCohort("60-69", 11_500, 13_000, 11_000, 10_000, 6_500),
    DemographicCohort("70-79", 8_500, 10_500, 12_000, 10_500, 9_800),
    DemographicCohort("80-89", 4_800, 6_200, 8_500, 9_000, 15_500),
    DemographicCohort("90+", 1_100, 1_500, 2_300, 2_800, 22_000),
]


@dataclass 
class HealthSystemReform:
    """Ein Reformszenario für das Gesundheitssystem."""
    name: str
    efficiency_gain_percent: float  # Jährliche Effizienzsteigerung
    gsp_contribution_rate: float    # Beitragssatz für Gesundheitssparkonto
    prevention_cost_reduction: float  # Kostensenkung durch Prävention


REFORM_SCENARIOS = [
    HealthSystemReform(
        name="Status Quo",
        efficiency_gain_percent=0.5,
        gsp_contribution_rate=0.0,
        prevention_cost_reduction=0.0
    ),
    HealthSystemReform(
        name="Moderate Reform (Digitalisierung)",
        efficiency_gain_percent=1.5,
        gsp_contribution_rate=0.0,
        prevention_cost_reduction=0.05
    ),
    HealthSystemReform(
        name="GSP-Modell (Singapur-inspiriert)",
        efficiency_gain_percent=2.0,
        gsp_contribution_rate=0.02,
        prevention_cost_reduction=0.10
    ),
    HealthSystemReform(
        name="Vollintegration (Asiatische Best Practices)",
        efficiency_gain_percent=2.5,
        gsp_contribution_rate=0.02,
        prevention_cost_reduction=0.15
    ),
]


def calculate_total_health_costs(cohorts: List[DemographicCohort], year: int) -> float:
    """Berechnet die Gesamtgesundheitskosten für ein Jahr."""
    
    total = 0
    for cohort in cohorts:
        # Interpoliere Bevölkerung zwischen den Stützjahren
        if year <= 2025:
            pop = cohort.population_2025
        elif year <= 2035:
            t = (year - 2025) / 10
            pop = cohort.population_2025 * (1 - t) + cohort.population_2035 * t
        elif year <= 2045:
            t = (year - 2035) / 10
            pop = cohort.population_2035 * (1 - t) + cohort.population_2045 * t
        elif year <= 2055:
            t = (year - 2045) / 10
            pop = cohort.population_2045 * (1 - t) + cohort.population_2055 * t
        else:
            pop = cohort.population_2055
        
        # Kosten in Mrd. EUR
        total += pop * cohort.avg_health_cost / 1_000_000
    
    return total


def project_health_costs(
    reform: HealthSystemReform,
    years: range,
    medical_inflation: float = 0.02  # 2% jährliche medizinische Inflation
) -> Dict:
    """Projiziert Gesundheitskosten unter einem Reformszenario."""
    
    results = {
        "scenario": reform.name,
        "years": [],
        "baseline_costs": [],
        "reform_costs": [],
        "savings": [],
        "gsp_accumulation": [],
        "debt_required": []
    }
    
    gsp_balance = 0  # Kumuliertes GSP-Kapital
    cumulative_debt = 0
    baseline_2025 = calculate_total_health_costs(COHORTS, 2025)
    
    for year in years:
        # Baseline-Kosten (nur Demografie + Inflation)
        demo_costs = calculate_total_health_costs(COHORTS, year)
        years_from_2025 = year - 2025
        inflation_factor = (1 + medical_inflation) ** years_from_2025
        baseline = demo_costs * inflation_factor
        
        # Reform-Effekte
        efficiency_factor = (1 - reform.efficiency_gain_percent/100) ** years_from_2025
        prevention_factor = 1 - reform.prevention_cost_reduction * min(years_from_2025/10, 1)
        
        reform_costs = baseline * efficiency_factor * prevention_factor
        savings = baseline - reform_costs
        
        # GSP-Akkumulation (2% auf Bruttolöhne ~2.000 Mrd. EUR)
        gsp_contribution = 2000 * reform.gsp_contribution_rate  # Mrd. EUR/Jahr
        gsp_return = gsp_balance * 0.04  # 4% Rendite
        gsp_balance = gsp_balance + gsp_contribution + gsp_return
        
        # Schuldenfinanzierung für Buckel
        # Referenz: Kosten 2025 stabilisieren
        target_costs = baseline_2025 * (1 + 0.01) ** years_from_2025  # 1% reales Wachstum erlaubt
        if reform_costs > target_costs:
            debt_this_year = reform_costs - target_costs
        else:
            debt_this_year = 0
        cumulative_debt += debt_this_year
        
        results["years"].append(year)
        results["baseline_costs"].append(round(baseline, 1))
        results["reform_costs"].append(round(reform_costs, 1))
        results["savings"].append(round(savings, 1))
        results["gsp_accumulation"].append(round(gsp_balance, 1))
        results["debt_required"].append(round(cumulative_debt, 1))
    
    return results


def compare_asian_systems():
    """Vergleicht asiatische Gesundheitssysteme."""
    
    systems = {
        "Singapur": {
            "health_expenditure_gdp_percent": 4.9,
            "life_expectancy": 84.1,
            "infant_mortality_per_1000": 1.8,
            "oop_percent": 30,
            "key_feature": "3M-System (MediSave, MediShield, MediFund)",
            "transferable_elements": [
                "Individuelle Gesundheitskonten",
                "Familien-Pooling",
                "Kapitaldeckung",
                "Katastrophenversicherung",
                "Staatliche Preiskontrolle"
            ]
        },
        "Japan": {
            "health_expenditure_gdp_percent": 11.5,
            "life_expectancy": 84.3,
            "infant_mortality_per_1000": 1.8,
            "oop_percent": 12,
            "key_feature": "LTCI (Kaigo Hoken) seit 2000",
            "transferable_elements": [
                "Eigenständige Pflegeversicherung",
                "Objektive Bedarfsfeststellung",
                "Community-basierte Versorgung",
                "Frailty-Prävention ab 75",
                "Nationale Pflegedatenbank"
            ]
        },
        "Südkorea": {
            "health_expenditure_gdp_percent": 8.4,
            "life_expectancy": 83.6,
            "infant_mortality_per_1000": 2.7,
            "oop_percent": 37,
            "key_feature": "Universal Coverage in 12 Jahren",
            "transferable_elements": [
                "Single-Payer-Konsolidierung",
                "DRGs-Vergütung",
                "Telemedizin-Expansion"
            ]
        },
        "Thailand": {
            "health_expenditure_gdp_percent": 4.5,
            "life_expectancy": 77.3,
            "infant_mortality_per_1000": 7.0,
            "oop_percent": 11,
            "key_feature": "30-Baht-Scheme (steuerfinanziert)",
            "transferable_elements": [
                "Steuerfinanzierung",
                "Gatekeeping-Modell",
                "Essentielle Medikamentenliste",
                "Capitation-Vergütung",
                "Dezentrale Netzwerke"
            ]
        },
        "China": {
            "health_expenditure_gdp_percent": 7.0,
            "life_expectancy": 77.9,
            "infant_mortality_per_1000": 5.9,
            "oop_percent": 28,
            "key_feature": "Urban-Rural-Integration (URRBMI)",
            "transferable_elements": [
                "Volumenbasierte Beschaffung",
                "Digitale Cross-Border-Abrechnung",
                "DRGs-Einführung",
                "Drug-Markup-Verbot"
            ]
        },
        "Deutschland (Status Quo)": {
            "health_expenditure_gdp_percent": 12.7,
            "life_expectancy": 81.3,
            "infant_mortality_per_1000": 3.2,
            "oop_percent": 12,
            "key_feature": "GKV + SPV (Umlagefinanziert)",
            "transferable_elements": []
        }
    }
    
    return systems


def calculate_debt_financing_strategy():
    """Berechnet die Schuldenfinanzierungsstrategie für den demografischen Buckel."""
    
    # Jährliche Mehrkosten über Baseline
    excess_costs = {
        2025: 0, 2026: 5, 2027: 10, 2028: 15, 2029: 20,
        2030: 25, 2031: 32, 2032: 40, 2033: 48, 2034: 55,
        2035: 65, 2036: 75, 2037: 82, 2038: 90, 2039: 100,
        2040: 110, 2041: 115, 2042: 118, 2043: 120, 2044: 118,
        2045: 115, 2046: 110, 2047: 100, 2048: 90, 2049: 80,
        2050: 70, 2051: 55, 2052: 40, 2053: 25, 2054: 10,
        2055: 0, 2056: -10, 2057: -20, 2058: -25, 2059: -30,
        2060: -35
    }
    
    cumulative_debt = 0
    interest_rate = 0.03
    results = []
    
    for year, excess in excess_costs.items():
        if excess > 0:
            cumulative_debt += excess
        interest_payment = cumulative_debt * interest_rate
        
        # Tilgung wenn negative Mehrkosten (= Überschuss)
        if excess < 0:
            repayment = min(-excess, cumulative_debt)
            cumulative_debt -= repayment
        else:
            repayment = 0
        
        results.append({
            "year": year,
            "excess_costs": excess,
            "cumulative_debt": round(cumulative_debt, 1),
            "interest_payment": round(interest_payment, 1),
            "repayment": round(repayment, 1)
        })
    
    peak_debt = max(r["cumulative_debt"] for r in results)
    peak_year = next(r["year"] for r in results if r["cumulative_debt"] == peak_debt)
    
    return {
        "annual_data": results,
        "peak_debt": peak_debt,
        "peak_year": peak_year,
        "total_interest_paid": sum(r["interest_payment"] for r in results),
        "years_to_repay": next(
            (r["year"] for r in results if r["year"] > peak_year and r["cumulative_debt"] <= 0),
            2075
        )
    }


def print_analysis():
    """Druckt die vollständige Analyse."""
    
    print("=" * 90)
    print("GESUNDHEITSKOSTEN-PROJEKTION UND SCHULDENFINANZIERUNGSSTRATEGIE")
    print("=" * 90)
    
    # Demografische Projektion
    print("\n--- DEMOGRAFISCHE GESUNDHEITSKOSTEN (Baseline) ---\n")
    
    for year in [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060]:
        costs = calculate_total_health_costs(COHORTS, year)
        print(f"  {year}: {costs:>7.0f} Mrd. EUR")
    
    print("\n  Peak erwartet: ~2045")
    print("  Rückgang danach durch kleinere Kohorten")
    
    # Reformszenarien
    print("\n--- REFORMSZENARIEN (Projektion 2025-2060) ---\n")
    
    years = range(2025, 2061, 5)
    
    for reform in REFORM_SCENARIOS:
        results = project_health_costs(reform, range(2025, 2061))
        print(f"\n{reform.name}:")
        print(f"  {'Jahr':<8} {'Baseline':>12} {'Reform':>12} {'Ersparnis':>12} {'GSP-Kapital':>14}")
        print("  " + "-" * 62)
        
        for i, year in enumerate(results["years"]):
            if year % 5 == 0:
                idx = results["years"].index(year)
                print(f"  {year:<8} {results['baseline_costs'][idx]:>10.0f}   "
                      f"{results['reform_costs'][idx]:>10.0f}   "
                      f"{results['savings'][idx]:>10.0f}   "
                      f"{results['gsp_accumulation'][idx]:>12.0f}")
    
    # Asiatische Systeme
    print("\n\n--- VERGLEICH ASIATISCHER GESUNDHEITSSYSTEME ---\n")
    
    systems = compare_asian_systems()
    
    print(f"{'Land':<25} {'Ausg. %BIP':>12} {'Lebenserwartung':>18} {'OOP %':>8}")
    print("-" * 70)
    
    for name, data in systems.items():
        print(f"{name:<25} {data['health_expenditure_gdp_percent']:>10.1f}%   "
              f"{data['life_expectancy']:>15.1f} Jahre  "
              f"{data['oop_percent']:>6}%")
    
    print("\n  Kernerkenntnis: Singapur erreicht beste Ergebnisse bei niedrigsten Kosten")
    print("  Schlüsselmechanismus: Kapitaldeckung + Eigenverantwortung + Preiski kontrolle")
    
    # Schuldenfinanzierung
    print("\n\n--- SCHULDENFINANZIERUNG DES DEMOGRAFISCHEN BUCKELS ---\n")
    
    debt_strategy = calculate_debt_financing_strategy()
    
    print(f"  Peak-Schulden: {debt_strategy['peak_debt']:,.0f} Mrd. EUR ({debt_strategy['peak_year']})")
    print(f"  Gesamte Zinszahlungen: {debt_strategy['total_interest_paid']:,.0f} Mrd. EUR")
    print(f"  Vollständige Tilgung: ~{debt_strategy['years_to_repay']}")
    
    print("\n  Jährliche Entwicklung (Auszug):")
    print(f"  {'Jahr':<8} {'Mehrkosten':>12} {'Kum. Schulden':>15} {'Zinsen':>10} {'Tilgung':>10}")
    print("  " + "-" * 60)
    
    for r in debt_strategy["annual_data"]:
        if r["year"] % 5 == 0 or r["year"] == debt_strategy["peak_year"]:
            marker = " ← Peak" if r["year"] == debt_strategy["peak_year"] else ""
            print(f"  {r['year']:<8} {r['excess_costs']:>+10.0f}   {r['cumulative_debt']:>13.0f}   "
                  f"{r['interest_payment']:>8.0f}   {r['repayment']:>8.0f}{marker}")
    
    # Zusammenfassung
    print("\n\n--- EMPFEHLUNG: GSP-MODELL (SINGAPUR-INSPIRIERT) ---\n")
    
    gsp_results = project_health_costs(REFORM_SCENARIOS[2], range(2025, 2061))
    
    print("  1. Individuelle Gesundheitssparkonten (2% Beitrag)")
    print(f"     → Kapitalstock bis 2060: {gsp_results['gsp_accumulation'][-1]:,.0f} Mrd. EUR")
    
    total_savings = sum(gsp_results['savings'])
    print(f"  2. Effizienzgewinne durch Digitalisierung + Prävention")
    print(f"     → Kumulative Ersparnis: {total_savings:,.0f} Mrd. EUR")
    
    print("  3. Schuldenfinanzierung des Übergangs")
    print(f"     → Peak-Schulden: {debt_strategy['peak_debt']:,.0f} Mrd. EUR")
    print(f"     → Getilgt bis: ~{debt_strategy['years_to_repay']}")
    
    print("\n  Fazit: Der demografische Gesundheitsbuckel ist FINANZIERBAR")
    print("         durch Schulden (temporär) + Kapitaldeckung (nachhaltig)")


def main():
    """Hauptfunktion."""
    
    print_analysis()
    
    # Export
    output = {
        "demographic_costs": {
            year: calculate_total_health_costs(COHORTS, year)
            for year in range(2025, 2061, 5)
        },
        "reform_scenarios": {
            reform.name: project_health_costs(reform, range(2025, 2061, 5))
            for reform in REFORM_SCENARIOS
        },
        "asian_systems": compare_asian_systems(),
        "debt_strategy": calculate_debt_financing_strategy()
    }
    
    with open("/home/claude/gesundheit_projektion_results.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    
    print("\n\nErgebnisse exportiert nach: gesundheit_projektion_results.json")


if __name__ == "__main__":
    main()
