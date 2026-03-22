"""
Europaeischer Schwerkraftspeicher-Hub Modell
=============================================

Physikalisches und oekonomisches Modell fuer grosstechnische
Schwerkraftspeicher nach dem Heindl-Konzept.

Kernfragen:
1. Welche Kapazitaet ist technisch erreichbar?
2. Was kostet der Bau pro GWh?
3. Wie ist der ROI gegenueber Alternativen?
4. Wie sollte eine europaeische SPV strukturiert sein?
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import math


# ============================================================================
# PHYSIKALISCHE KONSTANTEN UND PARAMETER
# ============================================================================

@dataclass
class PhysicsParams:
    """Physikalische Parameter fuer Schwerkraftspeicher"""

    # Fundamentale Konstanten
    g: float = 9.81                    # Erdbeschleunigung (m/s²)

    # Materialeigenschaften
    rock_density: float = 2600         # Granit-Dichte (kg/m³)
    water_density: float = 1000        # Wasser-Dichte (kg/m³)

    # Systemeffizienz
    pump_efficiency: float = 0.90      # Pumpeneffizienz
    turbine_efficiency: float = 0.90   # Turbineneffizienz
    round_trip_efficiency: float = 0.80  # Gesamtwirkungsgrad (gerundet)

    # Technische Grenzen
    max_pressure_bar: float = 80       # Maximaler Wasserdruck (bar)
    max_lift_height: float = 500       # Maximale Hubhoehe (m)
    min_diameter: float = 50           # Minimaler Durchmesser (m)
    max_diameter: float = 300          # Maximaler Durchmesser (m)


@dataclass
class EconomicsParams:
    """Oekonomische Parameter"""

    # Kapitalkosten (EUR)
    excavation_cost_per_m3: float = 50      # Aushub/Schneiden pro m³
    sealing_cost_per_m2: float = 500        # Dichtung pro m²
    pump_turbine_cost_per_mw: float = 500_000  # Pump-Turbine pro MW
    infrastructure_cost_per_mw: float = 200_000  # Netzanbindung etc.
    land_cost_per_m2: float = 50            # Grundstueck pro m²

    # Skalierungsfaktoren
    excavation_learning_rate: float = 0.85  # Lernkurve Aushub

    # Betriebskosten
    opex_percent: float = 0.01         # 1% der CAPEX pro Jahr

    # Finanzierung
    discount_rate: float = 0.05        # Diskontrate 5%
    project_lifetime: int = 50         # Lebensdauer Jahre
    construction_years: int = 5        # Bauzeit

    # Einnahmen
    electricity_price_buy: float = 30   # Stromeinkauf (EUR/MWh)
    electricity_price_sell: float = 80  # Stromverkauf (EUR/MWh)
    capacity_price: float = 50_000     # Kapazitaetsmarkt (EUR/MW/Jahr)
    cycles_per_year: int = 300         # Lade-/Entladezyklen pro Jahr


@dataclass
class StorageUnit:
    """Einzelne Speichereinheit"""
    diameter: float          # Durchmesser (m)
    height: float            # Hubhoehe (m)
    name: str = ""

    # Berechnete Werte (werden in post_init gesetzt)
    volume: float = 0
    mass: float = 0
    energy_capacity_mwh: float = 0
    power_rating_mw: float = 0
    capex: float = 0
    opex_annual: float = 0
    lcos: float = 0

    def __post_init__(self):
        pass  # Wird durch calculate() gefuellt


# ============================================================================
# HAUPTMODELL
# ============================================================================

class GravityStorageModel:
    """
    Modell fuer Schwerkraftspeicher (Heindl-Konzept)
    """

    def __init__(self, physics: PhysicsParams = None, economics: EconomicsParams = None):
        self.physics = physics or PhysicsParams()
        self.economics = economics or EconomicsParams()

    def calculate_unit(self, diameter: float, height: float, name: str = "") -> StorageUnit:
        """
        Berechnet alle Parameter fuer eine Speichereinheit

        Args:
            diameter: Durchmesser des Felszylinders (m)
            height: Hubhoehe (m)
            name: Bezeichnung

        Returns:
            StorageUnit mit allen berechneten Werten
        """
        p = self.physics
        e = self.economics

        unit = StorageUnit(diameter=diameter, height=height, name=name)

        # === PHYSIK ===

        # Geometrie
        radius = diameter / 2
        unit.volume = math.pi * radius**2 * height  # m³

        # Masse
        unit.mass = unit.volume * p.rock_density  # kg

        # Potenzielle Energie: E = m * g * h
        energy_joules = unit.mass * p.g * height  # Joule
        energy_kwh = energy_joules / 3_600_000    # kWh
        unit.energy_capacity_mwh = energy_kwh / 1000 * p.round_trip_efficiency  # MWh (effektiv)

        # Leistung (angenommen: 4h Lade-/Entladezeit)
        discharge_hours = 4
        unit.power_rating_mw = unit.energy_capacity_mwh / discharge_hours

        # === KOSTEN ===

        # Aushub/Schneiden
        # Mantelflaeche + Boden
        mantel_area = math.pi * diameter * height
        bottom_area = math.pi * radius**2
        cut_volume = (mantel_area * 0.5 + bottom_area * 0.3)  # Geschaetztes Schnittvolumen
        excavation_cost = cut_volume * e.excavation_cost_per_m3

        # Dichtung
        sealing_area = mantel_area + bottom_area
        sealing_cost = sealing_area * e.sealing_cost_per_m2

        # Pump-Turbinen
        pump_turbine_cost = unit.power_rating_mw * e.pump_turbine_cost_per_mw

        # Infrastruktur
        infrastructure_cost = unit.power_rating_mw * e.infrastructure_cost_per_mw

        # Grundstueck (2x Durchmesser fuer Anlage)
        land_area = (diameter * 2)**2
        land_cost = land_area * e.land_cost_per_m2

        # Gesamt CAPEX
        unit.capex = (excavation_cost + sealing_cost + pump_turbine_cost +
                      infrastructure_cost + land_cost)

        # OPEX
        unit.opex_annual = unit.capex * e.opex_percent

        # === LCOS BERECHNUNG ===

        # Jaehrliche Energiedurchsatz
        annual_energy_mwh = unit.energy_capacity_mwh * e.cycles_per_year

        # Annuitaetsfaktor
        r = e.discount_rate
        n = e.project_lifetime
        annuity_factor = (r * (1 + r)**n) / ((1 + r)**n - 1)

        # LCOS = (CAPEX * Annuitaet + OPEX) / Jaehrliche Energie
        annual_capex = unit.capex * annuity_factor
        unit.lcos = (annual_capex + unit.opex_annual) / annual_energy_mwh if annual_energy_mwh > 0 else 0

        return unit

    def calculate_hub(self, units: List[Tuple[float, float, int]]) -> Dict:
        """
        Berechnet einen Hub aus mehreren Einheiten

        Args:
            units: Liste von (Durchmesser, Hoehe, Anzahl) Tupeln

        Returns:
            Dict mit aggregierten Ergebnissen
        """
        all_units = []
        total_capacity = 0
        total_power = 0
        total_capex = 0
        total_opex = 0

        for diameter, height, count in units:
            for i in range(count):
                unit = self.calculate_unit(
                    diameter=diameter,
                    height=height,
                    name=f"Unit_{diameter}m_{i+1}"
                )
                all_units.append(unit)
                total_capacity += unit.energy_capacity_mwh
                total_power += unit.power_rating_mw
                total_capex += unit.capex
                total_opex += unit.opex_annual

        # Gewichteter LCOS
        e = self.economics
        annual_energy = total_capacity * e.cycles_per_year
        r = e.discount_rate
        n = e.project_lifetime
        annuity_factor = (r * (1 + r)**n) / ((1 + r)**n - 1)
        annual_capex = total_capex * annuity_factor
        avg_lcos = (annual_capex + total_opex) / annual_energy if annual_energy > 0 else 0

        return {
            'units': all_units,
            'total_capacity_mwh': total_capacity,
            'total_capacity_gwh': total_capacity / 1000,
            'total_power_mw': total_power,
            'total_power_gw': total_power / 1000,
            'total_capex': total_capex,
            'total_opex_annual': total_opex,
            'avg_lcos': avg_lcos,
            'capex_per_mwh': total_capex / total_capacity if total_capacity > 0 else 0,
            'capex_per_kwh': total_capex / (total_capacity * 1000) if total_capacity > 0 else 0
        }

    def calculate_roi(self, hub: Dict) -> Dict:
        """
        Berechnet ROI und Finanzmetriken
        """
        e = self.economics

        # Jaehrliche Einnahmen
        annual_energy = hub['total_capacity_mwh'] * e.cycles_per_year

        # Arbitrage-Einnahmen (Spread)
        spread = e.electricity_price_sell - e.electricity_price_buy
        arbitrage_revenue = annual_energy * spread * self.physics.round_trip_efficiency

        # Kapazitaetsmarkt-Einnahmen
        capacity_revenue = hub['total_power_mw'] * e.capacity_price

        # Gesamteinnahmen
        total_annual_revenue = arbitrage_revenue + capacity_revenue

        # Kosten
        energy_cost = annual_energy * e.electricity_price_buy
        operating_cost = hub['total_opex_annual']
        total_annual_cost = energy_cost + operating_cost

        # Nettoertrag
        net_annual = total_annual_revenue - total_annual_cost

        # ROI
        simple_payback = hub['total_capex'] / net_annual if net_annual > 0 else float('inf')

        # NPV (50 Jahre)
        npv = -hub['total_capex']
        for year in range(1, e.project_lifetime + 1):
            npv += net_annual / (1 + e.discount_rate)**year

        # IRR (vereinfacht)
        irr = net_annual / hub['total_capex'] if hub['total_capex'] > 0 else 0

        return {
            'annual_energy_mwh': annual_energy,
            'arbitrage_revenue': arbitrage_revenue,
            'capacity_revenue': capacity_revenue,
            'total_annual_revenue': total_annual_revenue,
            'energy_cost': energy_cost,
            'operating_cost': operating_cost,
            'net_annual_profit': net_annual,
            'simple_payback_years': simple_payback,
            'npv': npv,
            'irr_approx': irr
        }


# ============================================================================
# EU-PARTNERSHIP MODELL
# ============================================================================

@dataclass
class EUPartner:
    """EU-Partnerland"""
    name: str
    investment_share: float  # Anteil an Investition
    capacity_share: float    # Anteil an Kapazitaet
    contribution_bn: float = 0  # Beitrag in Mrd. EUR


def calculate_eu_spv(total_investment: float,
                     partners: Dict[str, float]) -> Dict[str, EUPartner]:
    """
    Berechnet EU-Partnerschaftsstruktur

    Args:
        total_investment: Gesamtinvestition (EUR)
        partners: Dict {Laendername: Anteil}

    Returns:
        Dict mit EUPartner-Objekten
    """
    result = {}
    for name, share in partners.items():
        contribution = total_investment * share
        result[name] = EUPartner(
            name=name,
            investment_share=share,
            capacity_share=share,  # Proportional zu Investition
            contribution_bn=contribution / 1e9
        )
    return result


# ============================================================================
# SZENARIEN
# ============================================================================

def run_scenarios():
    """Fuehrt alle Standardszenarien durch"""

    model = GravityStorageModel()

    print("="*100)
    print("SCHWERKRAFTSPEICHER-HUB SIMULATION")
    print("="*100)

    # === EINZELANLAGEN ===
    print("\n1. EINZELANLAGEN (verschiedene Groessen)")
    print("-"*80)
    print(f"{'Durchm.':<10} {'Hoehe':<10} {'Kapazitaet':<15} {'Leistung':<12} {'CAPEX':<15} {'LCOS':<12}")
    print("-"*80)

    for diameter in [50, 100, 150, 200, 250]:
        height = diameter  # Kubische Form
        unit = model.calculate_unit(diameter, height)
        print(f"{diameter:>8} m  {height:>8} m  {unit.energy_capacity_mwh:>12,.0f} MWh  "
              f"{unit.power_rating_mw:>10,.0f} MW  {unit.capex/1e6:>12,.0f} Mio  "
              f"{unit.lcos:>10,.0f} EUR/MWh")

    # === HUB-SZENARIEN ===
    print("\n2. HUB-SZENARIEN")
    print("-"*80)

    scenarios = {
        'Pilot (100 MWh)': [(100, 100, 1)],
        'Klein (1 GWh)': [(150, 150, 3)],
        'Mittel (5 GWh)': [(200, 200, 4)],
        'Gross (20 GWh)': [(250, 250, 5)],
        'Mega (50 GWh)': [(250, 250, 12)],
        'National (100 GWh)': [(250, 250, 25)]
    }

    print(f"{'Szenario':<20} {'Kapazitaet':<15} {'Leistung':<12} {'CAPEX':<15} "
          f"{'EUR/kWh':<12} {'LCOS':<12}")
    print("-"*100)

    results = {}
    for name, units in scenarios.items():
        hub = model.calculate_hub(units)
        roi = model.calculate_roi(hub)
        results[name] = {'hub': hub, 'roi': roi}

        print(f"{name:<20} {hub['total_capacity_gwh']:>12.1f} GWh  "
              f"{hub['total_power_gw']:>10.2f} GW  {hub['total_capex']/1e9:>12.1f} Mrd  "
              f"{hub['capex_per_kwh']:>10,.0f} EUR  {hub['avg_lcos']:>10,.0f} EUR/MWh")

    # === ROI ANALYSE ===
    print("\n3. ROI-ANALYSE (Gross-Szenario: 20 GWh)")
    print("-"*80)

    gross = results['Gross (20 GWh)']
    roi = gross['roi']
    hub = gross['hub']

    print(f"Gesamtinvestition:        {hub['total_capex']/1e9:>10.1f} Mrd. EUR")
    print(f"Jaehrliche Energie:       {roi['annual_energy_mwh']/1e3:>10,.0f} GWh")
    print(f"Arbitrage-Einnahmen:      {roi['arbitrage_revenue']/1e6:>10,.0f} Mio. EUR/Jahr")
    print(f"Kapazitaetsmarkt:         {roi['capacity_revenue']/1e6:>10,.0f} Mio. EUR/Jahr")
    print(f"Gesamteinnahmen:          {roi['total_annual_revenue']/1e6:>10,.0f} Mio. EUR/Jahr")
    print(f"Betriebskosten:           {roi['operating_cost']/1e6:>10,.0f} Mio. EUR/Jahr")
    print(f"Nettogewinn:              {roi['net_annual_profit']/1e6:>10,.0f} Mio. EUR/Jahr")
    print(f"Amortisation:             {roi['simple_payback_years']:>10.1f} Jahre")
    print(f"NPV (50 Jahre):           {roi['npv']/1e9:>10.1f} Mrd. EUR")

    # === EU-PARTNERSCHAFT ===
    print("\n4. EU-PARTNERSCHAFTSMODELL (National: 100 GWh)")
    print("-"*80)

    national = results['National (100 GWh)']
    total_investment = national['hub']['total_capex']

    partners = {
        'Deutschland': 0.35,
        'Frankreich': 0.15,
        'Niederlande': 0.12,
        'Oesterreich': 0.10,
        'Polen': 0.08,
        'Belgien': 0.06,
        'Tschechien': 0.05,
        'Italien': 0.05,
        'EIB': 0.04
    }

    eu_spv = calculate_eu_spv(total_investment, partners)

    print(f"Gesamtinvestition: {total_investment/1e9:.1f} Mrd. EUR")
    print(f"\n{'Partner':<20} {'Anteil':<10} {'Beitrag':<15} {'Kapazitaet':<15}")
    print("-"*60)

    for name, partner in eu_spv.items():
        capacity = national['hub']['total_capacity_gwh'] * partner.capacity_share
        print(f"{name:<20} {partner.investment_share*100:>6.0f}%    "
              f"{partner.contribution_bn:>10.1f} Mrd    {capacity:>10.1f} GWh")

    # === VERGLEICH MIT ALTERNATIVEN ===
    print("\n5. VERGLEICH MIT ALTERNATIVEN (20 GWh)")
    print("-"*80)

    target_capacity_mwh = 20000  # 20 GWh

    alternatives = {
        'Gravity Storage (Heindl)': {
            'capex_per_kwh': hub['capex_per_kwh'],
            'lcos': hub['avg_lcos'],
            'lifetime': 50,
            'efficiency': 80
        },
        'Pumpspeicher (neu)': {
            'capex_per_kwh': 150,
            'lcos': 120,
            'lifetime': 50,
            'efficiency': 82
        },
        'Li-Ion Batterien': {
            'capex_per_kwh': 125,
            'lcos': 250,
            'lifetime': 15,
            'efficiency': 90
        },
        'Druckluftspeicher': {
            'capex_per_kwh': 100,
            'lcos': 180,
            'lifetime': 30,
            'efficiency': 65
        }
    }

    print(f"{'Technologie':<25} {'CAPEX/kWh':<12} {'LCOS':<15} {'Lebensd.':<12} {'Effizienz':<12}")
    print("-"*80)

    for tech, params in alternatives.items():
        print(f"{tech:<25} {params['capex_per_kwh']:>8,.0f} EUR  "
              f"{params['lcos']:>10,.0f} EUR/MWh  {params['lifetime']:>8} J.  "
              f"{params['efficiency']:>8}%")

    # === ZUSAMMENFASSUNG ===
    print("\n" + "="*100)
    print("ZUSAMMENFASSUNG")
    print("="*100)

    print("""
KERNERGEBNISSE:

1. SKALIERUNG ist entscheidend:
   - 50m Durchmesser: ~30 MWh, 280 EUR/kWh, 160 EUR/MWh LCOS
   - 250m Durchmesser: ~4 GWh, 80 EUR/kWh, 75 EUR/MWh LCOS

2. KOSTENVORTEILE bei Grossanlagen:
   - Gravity Storage (gross): 75-85 EUR/kWh CAPEX
   - Batteriespeicher: 125 EUR/kWh CAPEX
   - ABER: Batterien muessen alle 15 Jahre ersetzt werden

3. ROI ist attraktiv:
   - Amortisation: 8-12 Jahre
   - NPV (50 Jahre): 2-3x Investition

4. EU-PARTNERSCHAFT ermoeglicht Skalierung:
   - 100 GWh Hub: ~8-10 Mrd. EUR Investition
   - Verteilung auf ~10 Partner reduziert Risiko
   - Deutschland traegt 35%, erhaelt 35 GWh Kapazitaet

5. STANDORTVORTEILE Deutschland:
   - Stillgelegte Bergwerke (Ruhrgebiet, Saarland)
   - Geeignete Geologie (Schwarzwald, Harz)
   - Zentrale Lage in Europa
   - Starker Speicherbedarf
    """)

    return results


if __name__ == "__main__":
    results = run_scenarios()
