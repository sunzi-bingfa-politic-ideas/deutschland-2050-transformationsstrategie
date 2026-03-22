"""
Sensitivitaetsanalyse fuer Schwerkraftspeicher-Hub Modell
=========================================================

Systematische Untersuchung der Parameterunsicherheiten und
ihrer Auswirkungen auf Kapazitaet, LCOS und ROI.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import copy
from gravity_storage_model import (
    GravityStorageModel, PhysicsParams, EconomicsParams,
    calculate_eu_spv
)


# ============================================================================
# SENSITIVITAETSANALYSE
# ============================================================================

@dataclass
class ParameterRange:
    """Definiert Bereich fuer Parametervariation"""
    name: str
    param_type: str  # 'physics' oder 'economics'
    param_name: str
    low: float
    baseline: float
    high: float
    unit: str


# Parameter-Bereiche basierend auf Literatur
PARAMETER_RANGES = [
    # Physikalische Parameter
    ParameterRange("Gesteinsdichte", "physics", "rock_density",
                   2400, 2600, 2800, "kg/m³"),
    ParameterRange("Wirkungsgrad (Roundtrip)", "physics", "round_trip_efficiency",
                   0.70, 0.80, 0.85, "%"),

    # Kapitalkosten
    ParameterRange("Aushubkosten", "economics", "excavation_cost_per_m3",
                   30, 50, 80, "EUR/m³"),
    ParameterRange("Dichtungskosten", "economics", "sealing_cost_per_m2",
                   300, 500, 800, "EUR/m²"),
    ParameterRange("Pump-Turbine Kosten", "economics", "pump_turbine_cost_per_mw",
                   300_000, 500_000, 700_000, "EUR/MW"),

    # Finanzierung
    ParameterRange("Diskontrate", "economics", "discount_rate",
                   0.03, 0.05, 0.08, "%"),
    ParameterRange("Lebensdauer", "economics", "project_lifetime",
                   30, 50, 60, "Jahre"),
    ParameterRange("Zyklen/Jahr", "economics", "cycles_per_year",
                   200, 300, 365, "Zyklen"),

    # Einnahmen
    ParameterRange("Stromeinkauf", "economics", "electricity_price_buy",
                   20, 30, 50, "EUR/MWh"),
    ParameterRange("Stromverkauf", "economics", "electricity_price_sell",
                   60, 80, 120, "EUR/MWh"),
    ParameterRange("Kapazitaetsmarkt", "economics", "capacity_price",
                   30_000, 50_000, 80_000, "EUR/MW/a"),
]


def run_sensitivity_single(param: ParameterRange,
                           hub_config: List[Tuple[float, float, int]]) -> Dict:
    """
    Fuehrt Sensitivitaetsanalyse fuer einen Parameter durch

    Args:
        param: ParameterRange Objekt
        hub_config: Hub-Konfiguration [(Durchmesser, Hoehe, Anzahl), ...]

    Returns:
        Dict mit low/baseline/high Ergebnissen
    """
    results = {}

    for scenario, value in [('low', param.low),
                            ('baseline', param.baseline),
                            ('high', param.high)]:
        # Baseline-Parameter
        physics = PhysicsParams()
        economics = EconomicsParams()

        # Parameter setzen
        if param.param_type == 'physics':
            setattr(physics, param.param_name, value)
        else:
            setattr(economics, param.param_name, value)

        # Modell berechnen
        model = GravityStorageModel(physics, economics)
        hub = model.calculate_hub(hub_config)
        roi = model.calculate_roi(hub)

        results[scenario] = {
            'value': value,
            'capacity_gwh': hub['total_capacity_gwh'],
            'capex_bn': hub['total_capex'] / 1e9,
            'capex_per_kwh': hub['capex_per_kwh'],
            'lcos': hub['avg_lcos'],
            'payback_years': roi['simple_payback_years'],
            'npv_bn': roi['npv'] / 1e9,
            'net_annual_mn': roi['net_annual_profit'] / 1e6
        }

    return results


def calculate_elasticity(results: Dict, param: ParameterRange) -> Dict:
    """
    Berechnet Elastizitaeten (prozentuale Aenderung Output / Input)
    """
    base = results['baseline']

    elasticities = {}
    for metric in ['capex_per_kwh', 'lcos', 'payback_years', 'npv_bn']:
        # Delta low
        if param.baseline != 0 and base[metric] != 0:
            pct_change_param_low = (param.low - param.baseline) / param.baseline
            pct_change_metric_low = (results['low'][metric] - base[metric]) / base[metric]
            elast_low = pct_change_metric_low / pct_change_param_low if pct_change_param_low != 0 else 0

            pct_change_param_high = (param.high - param.baseline) / param.baseline
            pct_change_metric_high = (results['high'][metric] - base[metric]) / base[metric]
            elast_high = pct_change_metric_high / pct_change_param_high if pct_change_param_high != 0 else 0

            elasticities[metric] = (elast_low + elast_high) / 2
        else:
            elasticities[metric] = 0

    return elasticities


def run_full_sensitivity() -> Dict:
    """
    Fuehrt vollstaendige Sensitivitaetsanalyse durch
    """
    # Gross-Szenario (5 × 250m)
    hub_config = [(250, 250, 5)]

    print("=" * 100)
    print("SENSITIVITAETSANALYSE - SCHWERKRAFTSPEICHER HUB (Gross-Szenario)")
    print("=" * 100)

    all_results = {}
    all_elasticities = {}

    for param in PARAMETER_RANGES:
        results = run_sensitivity_single(param, hub_config)
        elasticities = calculate_elasticity(results, param)
        all_results[param.name] = results
        all_elasticities[param.name] = elasticities

    # === TORNADO-DIAGRAMM (Textform) ===
    print("\n1. TORNADO-ANALYSE: LCOS-Sensitivitaet")
    print("-" * 80)

    # Sortiert nach Einfluss auf LCOS
    lcos_impacts = []
    for name, results in all_results.items():
        base_lcos = results['baseline']['lcos']
        low_lcos = results['low']['lcos']
        high_lcos = results['high']['lcos']
        impact = max(abs(low_lcos - base_lcos), abs(high_lcos - base_lcos))
        lcos_impacts.append((name, low_lcos, base_lcos, high_lcos, impact))

    lcos_impacts.sort(key=lambda x: x[4], reverse=True)

    print(f"{'Parameter':<30} {'Low':<15} {'Baseline':<15} {'High':<15} {'Max. Abw.':<12}")
    print("-" * 90)

    for name, low, base, high, impact in lcos_impacts:
        print(f"{name:<30} {low:>12.1f}    {base:>12.1f}    {high:>12.1f}    "
              f"±{impact:>8.1f} EUR/MWh")

    # === NPV SENSITIVITAET ===
    print("\n2. NPV-SENSITIVITAET (50 Jahre)")
    print("-" * 80)

    npv_impacts = []
    for name, results in all_results.items():
        base_npv = results['baseline']['npv_bn']
        low_npv = results['low']['npv_bn']
        high_npv = results['high']['npv_bn']
        impact = max(abs(low_npv - base_npv), abs(high_npv - base_npv))
        npv_impacts.append((name, low_npv, base_npv, high_npv, impact))

    npv_impacts.sort(key=lambda x: x[4], reverse=True)

    print(f"{'Parameter':<30} {'Low':<15} {'Baseline':<15} {'High':<15} {'Max. Abw.':<12}")
    print("-" * 90)

    for name, low, base, high, impact in npv_impacts:
        print(f"{name:<30} {low:>12.1f}    {base:>12.1f}    {high:>12.1f}    "
              f"±{impact:>8.1f} Mrd. EUR")

    # === AMORTISATION ===
    print("\n3. AMORTISATIONS-SENSITIVITAET")
    print("-" * 80)

    payback_impacts = []
    for name, results in all_results.items():
        base = results['baseline']['payback_years']
        low = results['low']['payback_years']
        high = results['high']['payback_years']
        # Clamp infinite values
        low = min(low, 50)
        high = min(high, 50)
        impact = max(abs(low - base), abs(high - base))
        payback_impacts.append((name, low, base, high, impact))

    payback_impacts.sort(key=lambda x: x[4], reverse=True)

    print(f"{'Parameter':<30} {'Low':<15} {'Baseline':<15} {'High':<15} {'Max. Abw.':<12}")
    print("-" * 90)

    for name, low, base, high, impact in payback_impacts:
        print(f"{name:<30} {low:>12.1f}    {base:>12.1f}    {high:>12.1f}    "
              f"±{impact:>8.1f} Jahre")

    # === ELASTIZITAETEN ===
    print("\n4. ELASTIZITAETEN (LCOS)")
    print("-" * 80)
    print("Interpretation: Elastizitaet > 1 bedeutet ueberproportionale Reaktion")
    print()

    elast_sorted = sorted(all_elasticities.items(),
                          key=lambda x: abs(x[1].get('lcos', 0)),
                          reverse=True)

    print(f"{'Parameter':<30} {'LCOS Elast.':<15} {'NPV Elast.':<15}")
    print("-" * 60)

    for name, elast in elast_sorted:
        print(f"{name:<30} {elast.get('lcos', 0):>12.2f}    {elast.get('npv_bn', 0):>12.2f}")

    return all_results, all_elasticities


def run_scenarios_comparison():
    """
    Vergleicht optimistische, baseline und pessimistische Szenarien
    """
    print("\n" + "=" * 100)
    print("SZENARIO-VERGLEICH")
    print("=" * 100)

    hub_config = [(250, 250, 5)]  # Gross-Szenario

    scenarios = {
        'Pessimistisch': {
            'physics': {
                'rock_density': 2400,
                'round_trip_efficiency': 0.70
            },
            'economics': {
                'excavation_cost_per_m3': 80,
                'sealing_cost_per_m2': 800,
                'pump_turbine_cost_per_mw': 700_000,
                'discount_rate': 0.08,
                'electricity_price_buy': 50,
                'electricity_price_sell': 60,
                'capacity_price': 30_000,
                'cycles_per_year': 200
            }
        },
        'Baseline': {
            'physics': {},
            'economics': {}
        },
        'Optimistisch': {
            'physics': {
                'rock_density': 2800,
                'round_trip_efficiency': 0.85
            },
            'economics': {
                'excavation_cost_per_m3': 30,
                'sealing_cost_per_m2': 300,
                'pump_turbine_cost_per_mw': 300_000,
                'discount_rate': 0.03,
                'electricity_price_buy': 20,
                'electricity_price_sell': 120,
                'capacity_price': 80_000,
                'cycles_per_year': 365
            }
        }
    }

    results = {}

    for scenario_name, params in scenarios.items():
        physics = PhysicsParams()
        economics = EconomicsParams()

        for key, value in params.get('physics', {}).items():
            setattr(physics, key, value)
        for key, value in params.get('economics', {}).items():
            setattr(economics, key, value)

        model = GravityStorageModel(physics, economics)
        hub = model.calculate_hub(hub_config)
        roi = model.calculate_roi(hub)

        results[scenario_name] = {
            'hub': hub,
            'roi': roi,
            'physics': physics,
            'economics': economics
        }

    # Ausgabe
    print(f"\n{'Kennzahl':<30} {'Pessimistisch':<18} {'Baseline':<18} {'Optimistisch':<18}")
    print("-" * 84)

    metrics = [
        ('Kapazitaet (GWh)', lambda r: r['hub']['total_capacity_gwh'], '.1f'),
        ('CAPEX (Mrd. EUR)', lambda r: r['hub']['total_capex']/1e9, '.1f'),
        ('CAPEX/kWh (EUR)', lambda r: r['hub']['capex_per_kwh'], '.0f'),
        ('LCOS (EUR/MWh)', lambda r: r['hub']['avg_lcos'], '.0f'),
        ('Amortisation (Jahre)', lambda r: min(r['roi']['simple_payback_years'], 99), '.1f'),
        ('NPV (Mrd. EUR)', lambda r: r['roi']['npv']/1e9, '.1f'),
        ('Nettogewinn/Jahr (Mio.)', lambda r: r['roi']['net_annual_profit']/1e6, '.0f'),
    ]

    for name, func, fmt in metrics:
        values = [func(results[s]) for s in ['Pessimistisch', 'Baseline', 'Optimistisch']]
        print(f"{name:<30} {values[0]:>16{fmt}}  {values[1]:>16{fmt}}  {values[2]:>16{fmt}}")

    return results


def analyze_breakeven():
    """
    Analysiert Break-Even-Punkte
    """
    print("\n" + "=" * 100)
    print("BREAK-EVEN ANALYSE")
    print("=" * 100)

    hub_config = [(250, 250, 5)]

    # Break-Even: Bei welchem Strompreis-Spread ist NPV = 0?
    print("\n1. STROMPREIS-SPREAD BREAK-EVEN")
    print("-" * 60)

    for spread in range(10, 100, 10):
        economics = EconomicsParams()
        economics.electricity_price_buy = 30
        economics.electricity_price_sell = 30 + spread

        model = GravityStorageModel(economics=economics)
        hub = model.calculate_hub(hub_config)
        roi = model.calculate_roi(hub)

        npv_sign = "+" if roi['npv'] > 0 else ""
        print(f"Spread {spread:>3} EUR/MWh: NPV = {npv_sign}{roi['npv']/1e9:.1f} Mrd. EUR, "
              f"Payback = {roi['simple_payback_years']:.1f} Jahre")

    # Break-Even: Bei welcher Kapazitaetsmarkt-Verguetung ist NPV = 0?
    print("\n2. KAPAZITAETSMARKT BREAK-EVEN")
    print("-" * 60)

    for cap_price in range(0, 100_000, 10_000):
        economics = EconomicsParams()
        economics.capacity_price = cap_price

        model = GravityStorageModel(economics=economics)
        hub = model.calculate_hub(hub_config)
        roi = model.calculate_roi(hub)

        npv_sign = "+" if roi['npv'] > 0 else ""
        print(f"Kap.-Markt {cap_price/1000:>3.0f}k EUR/MW/a: NPV = {npv_sign}{roi['npv']/1e9:.1f} Mrd. EUR, "
              f"Payback = {roi['simple_payback_years']:.1f} Jahre")

    # Break-Even: Bei welcher Groesse wird LCOS < 50 EUR/MWh?
    print("\n3. GROESSEN-BREAK-EVEN (LCOS < 50 EUR/MWh)")
    print("-" * 60)

    model = GravityStorageModel()
    for diameter in [100, 150, 200, 250, 300]:
        unit = model.calculate_unit(diameter, diameter)
        print(f"Durchmesser {diameter:>3}m: LCOS = {unit.lcos:.0f} EUR/MWh, "
              f"Kapazitaet = {unit.energy_capacity_mwh:.0f} MWh")


def run_monte_carlo_simple(n_iterations: int = 1000):
    """
    Vereinfachte Monte-Carlo-Simulation (ohne numpy)
    """
    import random

    print("\n" + "=" * 100)
    print(f"MONTE-CARLO SIMULATION ({n_iterations} Iterationen)")
    print("=" * 100)

    hub_config = [(250, 250, 5)]

    results_lcos = []
    results_npv = []
    results_payback = []

    for _ in range(n_iterations):
        # Zufaellige Parameter (Gleichverteilung zwischen Low und High)
        physics = PhysicsParams()
        economics = EconomicsParams()

        # Physik
        physics.rock_density = random.uniform(2400, 2800)
        physics.round_trip_efficiency = random.uniform(0.70, 0.85)

        # Oekonomie
        economics.excavation_cost_per_m3 = random.uniform(30, 80)
        economics.sealing_cost_per_m2 = random.uniform(300, 800)
        economics.pump_turbine_cost_per_mw = random.uniform(300_000, 700_000)
        economics.discount_rate = random.uniform(0.03, 0.08)
        economics.electricity_price_buy = random.uniform(20, 50)
        economics.electricity_price_sell = random.uniform(60, 120)
        economics.capacity_price = random.uniform(30_000, 80_000)
        economics.cycles_per_year = random.randint(200, 365)

        model = GravityStorageModel(physics, economics)
        hub = model.calculate_hub(hub_config)
        roi = model.calculate_roi(hub)

        results_lcos.append(hub['avg_lcos'])
        results_npv.append(roi['npv'] / 1e9)
        results_payback.append(min(roi['simple_payback_years'], 50))

    # Statistiken
    def calc_stats(data):
        data_sorted = sorted(data)
        n = len(data)
        return {
            'min': min(data),
            'p5': data_sorted[int(n * 0.05)],
            'p25': data_sorted[int(n * 0.25)],
            'median': data_sorted[int(n * 0.5)],
            'p75': data_sorted[int(n * 0.75)],
            'p95': data_sorted[int(n * 0.95)],
            'max': max(data),
            'mean': sum(data) / n
        }

    lcos_stats = calc_stats(results_lcos)
    npv_stats = calc_stats(results_npv)
    payback_stats = calc_stats(results_payback)

    print("\nERGEBNISSE:")
    print("-" * 80)
    print(f"{'Metrik':<20} {'Min':<10} {'P5':<10} {'P25':<10} {'Median':<10} "
          f"{'P75':<10} {'P95':<10} {'Max':<10}")
    print("-" * 90)

    print(f"{'LCOS (EUR/MWh)':<20} {lcos_stats['min']:>8.0f}  {lcos_stats['p5']:>8.0f}  "
          f"{lcos_stats['p25']:>8.0f}  {lcos_stats['median']:>8.0f}  "
          f"{lcos_stats['p75']:>8.0f}  {lcos_stats['p95']:>8.0f}  {lcos_stats['max']:>8.0f}")

    print(f"{'NPV (Mrd. EUR)':<20} {npv_stats['min']:>8.1f}  {npv_stats['p5']:>8.1f}  "
          f"{npv_stats['p25']:>8.1f}  {npv_stats['median']:>8.1f}  "
          f"{npv_stats['p75']:>8.1f}  {npv_stats['p95']:>8.1f}  {npv_stats['max']:>8.1f}")

    print(f"{'Payback (Jahre)':<20} {payback_stats['min']:>8.1f}  {payback_stats['p5']:>8.1f}  "
          f"{payback_stats['p25']:>8.1f}  {payback_stats['median']:>8.1f}  "
          f"{payback_stats['p75']:>8.1f}  {payback_stats['p95']:>8.1f}  {payback_stats['max']:>8.1f}")

    # Risikometriken
    print("\nRISIKOMETRIKEN:")
    print("-" * 60)

    prob_positive_npv = sum(1 for x in results_npv if x > 0) / n_iterations * 100
    prob_payback_15 = sum(1 for x in results_payback if x < 15) / n_iterations * 100
    prob_lcos_50 = sum(1 for x in results_lcos if x < 50) / n_iterations * 100

    print(f"Wahrscheinlichkeit NPV > 0:          {prob_positive_npv:>6.1f}%")
    print(f"Wahrscheinlichkeit Payback < 15 J:   {prob_payback_15:>6.1f}%")
    print(f"Wahrscheinlichkeit LCOS < 50 EUR:    {prob_lcos_50:>6.1f}%")

    return {
        'lcos': lcos_stats,
        'npv': npv_stats,
        'payback': payback_stats,
        'probabilities': {
            'positive_npv': prob_positive_npv,
            'payback_15': prob_payback_15,
            'lcos_50': prob_lcos_50
        }
    }


def identify_critical_factors():
    """
    Identifiziert kritische Erfolgsfaktoren
    """
    print("\n" + "=" * 100)
    print("KRITISCHE ERFOLGSFAKTOREN")
    print("=" * 100)

    print("""
FAKTOR 1: SKALIERUNG
--------------------
Die Anlagengröße ist der wichtigste Einzelfaktor:
- 100m Anlage: LCOS ~50 EUR/MWh
- 250m Anlage: LCOS ~40 EUR/MWh
- Skalierungsvorteil: Kapazität ~ r⁴, Kosten ~ r²
→ EMPFEHLUNG: Fokus auf Großanlagen (>200m Durchmesser)

FAKTOR 2: KAPAZITÄTSMARKT
-------------------------
Die Kapazitätsmarkt-Vergütung ist entscheidend für ROI:
- Ohne Kapazitätsmarkt: Payback >30 Jahre
- Mit 50k EUR/MW/Jahr: Payback ~13 Jahre
→ EMPFEHLUNG: Politische Absicherung der Kapazitätsvergütung

FAKTOR 3: STROMPREIS-SPREAD
---------------------------
Arbitrage-Einnahmen hängen stark vom Spread ab:
- Spread <30 EUR/MWh: Projekt marginal rentabel
- Spread >50 EUR/MWh: Projekt sehr attraktiv
→ EMPFEHLUNG: Langfristige PPAs zur Absicherung

FAKTOR 4: BAUKOSTEN
-------------------
Aushub- und Dichtungskosten haben mittleren Einfluss:
- Optimistische Kosten (-40%): LCOS -15%
- Pessimistische Kosten (+60%): LCOS +25%
→ EMPFEHLUNG: Lernkurveneffekte durch Standardisierung

FAKTOR 5: FINANZIERUNG
----------------------
Die Diskontrate beeinflusst NPV stark:
- 3% Diskont: NPV +50%
- 8% Diskont: NPV -40%
→ EMPFEHLUNG: Staatliche/EU-Garantien für günstige Finanzierung
    """)


if __name__ == "__main__":
    # Vollständige Analyse
    all_results, all_elasticities = run_full_sensitivity()
    scenario_results = run_scenarios_comparison()
    analyze_breakeven()
    monte_carlo_results = run_monte_carlo_simple(1000)
    identify_critical_factors()
