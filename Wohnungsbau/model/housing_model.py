"""
GCADI Housing Construction Model
================================

Modell zur Simulation der deutschen Wohnungsbauproduktion unter verschiedenen
Technologieszenarien (Modulbau, Robotik, 3D-Druck).

Kernfragen:
1. Wie schnell kann das Wohnungsdefizit geschlossen werden?
2. Welche Kostenreduktion ist erreichbar?
3. Wie viel Investition ist erforderlich?
4. Wie viele Arbeitskraefte werden eingespart/umgeschult?
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import math


@dataclass
class HousingParams:
    """Parameter fuer das Wohnungsbaumodell"""

    # === Ausgangslage Deutschland 2024 ===
    current_deficit: int = 1_200_000          # Wohnungsdefizit (Einheiten)
    annual_demand: int = 320_000              # Jaehrlicher Bedarf (Neubau + Ersatz)
    current_production: int = 252_000         # Aktuelle Fertigstellungen 2024
    production_gap: int = 68_000              # Jaehrliche Luecke

    # Sozialwohnungen
    social_housing_deficit: int = 1_050_000   # Sozialwohnungsdefizit
    social_housing_stock: int = 1_000_000     # Aktueller Bestand
    social_housing_target: int = 2_050_000    # Ziel 2030

    # === Baukosten (EUR/m²) ===
    cost_conventional: float = 2_500          # Konventionelle Baukosten
    cost_modular: float = 1_875               # Modulbau (-25%)
    cost_modular_robotics: float = 1_625      # Modulbau + Robotik (-35%)
    cost_3d_print_structure: float = 1_000    # 3D-Druck Rohbau
    cost_3d_print_total: float = 1_750        # 3D-Druck komplett (-30%)
    cost_optimized_future: float = 1_250      # Optimiertes System (-50%)

    # === Durchschnittliche Wohnungsgroesse ===
    avg_unit_size: float = 85                 # m² pro Wohneinheit
    social_unit_size: float = 65              # m² Sozialwohnung

    # === Bauzeit (Monate) ===
    time_conventional: float = 18             # Konventionell
    time_modular: float = 9                   # Modulbau (-50%)
    time_modular_robotics: float = 6          # Modulbau + Robotik
    time_3d_print: float = 3                  # 3D-Druck + Ausbau

    # === Arbeitskraefte ===
    workers_shortage: int = 530_000           # Aktuelle offene Stellen
    workers_per_unit_conventional: float = 0.8  # Arbeitsjahre pro Einheit (konv.)
    workers_per_unit_modular: float = 0.4     # Modulbau (-50%)
    workers_per_unit_automated: float = 0.2   # Vollautomatisiert (-75%)

    # === Investitionen ===
    factory_cost: float = 200_000_000         # Kosten pro Modulbau-Fabrik (200 Mio EUR)
    factory_capacity: int = 5_000             # Einheiten/Jahr pro Fabrik
    robot_cost: float = 500_000               # Durchschnittlicher Industrieroboter
    printer_cost: float = 2_000_000           # 3D-Bau-Drucker

    # === Skalierungseffekte ===
    learning_rate: float = 0.85               # Lernkurve (15% Kostensenkung bei Verdopplung)
    max_cost_reduction: float = 0.50          # Maximale Kostenreduktion durch Skalierung

    # === Zeithorizont ===
    simulation_years: int = 20                # Simulationszeitraum
    ramp_up_years: int = 5                    # Jahre bis Vollauslastung


@dataclass
class YearlyResult:
    """Ergebnisse fuer ein Simulationsjahr"""
    year: int
    units_produced: int
    units_conventional: int
    units_modular: int
    units_automated: int
    cumulative_units: int
    remaining_deficit: int
    cost_per_sqm: float
    total_investment: float
    cumulative_investment: float
    workers_needed: int
    workers_saved: int
    cost_savings: float
    cumulative_savings: float


@dataclass
class ScenarioResult:
    """Gesamtergebnis eines Szenarios"""
    name: str
    description: str
    yearly_results: List[YearlyResult]
    total_units: int
    deficit_closed_year: int  # Jahr, in dem Defizit geschlossen
    total_investment: float
    total_cost_savings: float
    avg_cost_reduction: float
    workers_retrained: int
    roi_years: float


class HousingModel:
    """
    Simulationsmodell fuer die deutsche Wohnungsbauproduktion
    """

    def __init__(self, params: HousingParams = None):
        self.params = params or HousingParams()

    def simulate_scenario(self,
                         name: str,
                         description: str,
                         modular_share_final: float = 0.5,
                         automated_share_final: float = 0.3,
                         production_increase: float = 1.5,
                         ramp_up_years: int = 5) -> ScenarioResult:
        """
        Simuliert ein Produktionsszenario

        Args:
            name: Name des Szenarios
            description: Beschreibung
            modular_share_final: Zielanteil Modulbau
            automated_share_final: Zielanteil Automatisierung (3D-Druck, Robotik)
            production_increase: Faktor Produktionssteigerung
            ramp_up_years: Jahre bis Zielkapazitaet
        """
        p = self.params
        yearly_results = []

        cumulative_units = 0
        cumulative_investment = 0
        cumulative_savings = 0
        deficit_closed_year = None
        remaining_deficit = p.current_deficit

        for year in range(1, p.simulation_years + 1):
            # Ramp-up Faktor (S-Kurve)
            if year <= ramp_up_years:
                ramp = (year / ramp_up_years) ** 1.5  # S-Kurven-Approximation
            else:
                ramp = 1.0

            # Produktionsmix
            modular_share = modular_share_final * ramp
            automated_share = automated_share_final * ramp
            conventional_share = 1.0 - modular_share - automated_share

            # Gesamtproduktion
            production_factor = 1 + (production_increase - 1) * ramp
            total_units = int(p.current_production * production_factor)

            units_conventional = int(total_units * conventional_share)
            units_modular = int(total_units * modular_share)
            units_automated = int(total_units * automated_share)

            # Lernkurven-Effekt auf Kosten
            cumulative_modular = sum(r.units_modular for r in yearly_results) + units_modular
            cumulative_automated = sum(r.units_automated for r in yearly_results) + units_automated

            # Kostenberechnung (gewichteter Durchschnitt)
            cost_conventional_adj = p.cost_conventional
            cost_modular_adj = self._apply_learning_curve(
                p.cost_modular, cumulative_modular, p.factory_capacity
            )
            cost_automated_adj = self._apply_learning_curve(
                p.cost_3d_print_total, cumulative_automated, p.factory_capacity
            )

            avg_cost = (
                conventional_share * cost_conventional_adj +
                modular_share * cost_modular_adj +
                automated_share * cost_automated_adj
            )

            # Investitionen (Fabriken, Equipment)
            new_modular_capacity_needed = max(0, units_modular -
                                              sum(r.units_modular for r in yearly_results[-1:]))
            new_factories = math.ceil(new_modular_capacity_needed / p.factory_capacity) if year <= ramp_up_years else 0

            investment = new_factories * p.factory_cost
            if year <= ramp_up_years and automated_share > 0:
                investment += (units_automated / 100) * p.printer_cost  # 1 Drucker pro 100 Einheiten

            cumulative_investment += investment

            # Arbeitskraefte
            workers_conventional = units_conventional * p.workers_per_unit_conventional
            workers_modular = units_modular * p.workers_per_unit_modular
            workers_automated = units_automated * p.workers_per_unit_automated
            workers_needed = int(workers_conventional + workers_modular + workers_automated)

            # Ersparnisse vs. rein konventionell
            workers_if_conventional = int(total_units * p.workers_per_unit_conventional)
            workers_saved = workers_if_conventional - workers_needed

            # Kostenersparnis
            cost_if_conventional = total_units * p.avg_unit_size * p.cost_conventional
            actual_cost = total_units * p.avg_unit_size * avg_cost
            cost_savings = cost_if_conventional - actual_cost
            cumulative_savings += cost_savings

            # Defizit-Tracking
            cumulative_units += total_units
            remaining_deficit = max(0, p.current_deficit - (cumulative_units -
                                    year * (p.annual_demand - p.current_production)))

            # Defizit geschlossen?
            if remaining_deficit == 0 and deficit_closed_year is None:
                deficit_closed_year = year

            yearly_results.append(YearlyResult(
                year=year,
                units_produced=total_units,
                units_conventional=units_conventional,
                units_modular=units_modular,
                units_automated=units_automated,
                cumulative_units=cumulative_units,
                remaining_deficit=remaining_deficit,
                cost_per_sqm=avg_cost,
                total_investment=investment,
                cumulative_investment=cumulative_investment,
                workers_needed=workers_needed,
                workers_saved=workers_saved,
                cost_savings=cost_savings,
                cumulative_savings=cumulative_savings
            ))

        # ROI berechnen
        if cumulative_savings > 0 and cumulative_investment > 0:
            roi_years = cumulative_investment / (cumulative_savings / p.simulation_years)
        else:
            roi_years = float('inf')

        return ScenarioResult(
            name=name,
            description=description,
            yearly_results=yearly_results,
            total_units=cumulative_units,
            deficit_closed_year=deficit_closed_year or p.simulation_years,
            total_investment=cumulative_investment,
            total_cost_savings=cumulative_savings,
            avg_cost_reduction=(p.cost_conventional - yearly_results[-1].cost_per_sqm) / p.cost_conventional,
            workers_retrained=max(yearly_results, key=lambda x: x.workers_saved).workers_saved,
            roi_years=roi_years
        )

    def _apply_learning_curve(self, base_cost: float, cumulative_units: int,
                              reference_volume: int) -> float:
        """Wendet Lernkurven-Effekt auf Kosten an"""
        if cumulative_units <= reference_volume:
            return base_cost

        doublings = math.log2(cumulative_units / reference_volume)
        reduction = 1 - (1 - self.params.learning_rate) * min(doublings,
                        -math.log2(1 - self.params.max_cost_reduction) /
                        (1 - self.params.learning_rate))

        return base_cost * max(1 - self.params.max_cost_reduction, reduction)

    def run_all_scenarios(self) -> Dict[str, ScenarioResult]:
        """Fuehrt alle Standardszenarien durch"""

        scenarios = {
            'baseline': self.simulate_scenario(
                name="Baseline (Status Quo)",
                description="Keine technologische Veraenderung",
                modular_share_final=0.10,
                automated_share_final=0.02,
                production_increase=1.0,
                ramp_up_years=1
            ),
            'moderate': self.simulate_scenario(
                name="Moderates Szenario",
                description="Schrittweise Einfuehrung Modulbau",
                modular_share_final=0.40,
                automated_share_final=0.10,
                production_increase=1.3,
                ramp_up_years=7
            ),
            'ambitious': self.simulate_scenario(
                name="Ambitioniertes Szenario (GCADI)",
                description="Aggressive Technologieeinfuehrung",
                modular_share_final=0.60,
                automated_share_final=0.25,
                production_increase=1.6,
                ramp_up_years=5
            ),
            'aggressive': self.simulate_scenario(
                name="Aggressives Szenario",
                description="Maximale Automatisierung",
                modular_share_final=0.50,
                automated_share_final=0.40,
                production_increase=2.0,
                ramp_up_years=5
            )
        }

        return scenarios

    def print_scenario_comparison(self, scenarios: Dict[str, ScenarioResult]):
        """Druckt Vergleichstabelle"""

        print("\n" + "="*100)
        print("SZENARIO-VERGLEICH: GCADI Wohnungsbau-Reform")
        print("="*100)

        print(f"\n{'Szenario':<30} {'Einheiten':<12} {'Defizit':<10} {'Investition':<15} "
              f"{'Ersparnis':<15} {'Kosten/m²':<12} {'ROI':<8}")
        print("-"*100)

        for key, result in scenarios.items():
            final = result.yearly_results[-1]
            print(f"{result.name:<30} {result.total_units:>10,} "
                  f"{result.deficit_closed_year:>8} J. "
                  f"{result.total_investment/1e9:>12.1f} Mrd "
                  f"{result.total_cost_savings/1e9:>12.1f} Mrd "
                  f"{final.cost_per_sqm:>10,.0f} EUR "
                  f"{result.roi_years:>6.1f} J.")

        print("\n" + "="*100)
        print("DETAILANALYSE: Ambitioniertes Szenario (GCADI)")
        print("="*100)

        gcadi = scenarios['ambitious']
        print(f"\n{'Jahr':<6} {'Produktion':<12} {'Konvent.':<10} {'Modular':<10} "
              f"{'Autom.':<10} {'Defizit':<12} {'Kosten/m²':<12} {'Arbeiter':<10}")
        print("-"*100)

        for r in gcadi.yearly_results[:10]:  # Erste 10 Jahre
            print(f"{r.year:<6} {r.units_produced:>10,} {r.units_conventional:>10,} "
                  f"{r.units_modular:>10,} {r.units_automated:>10,} "
                  f"{r.remaining_deficit:>10,} {r.cost_per_sqm:>10,.0f} EUR "
                  f"{r.workers_needed:>10,}")

    def calculate_social_housing_scenario(self) -> Dict:
        """Berechnet Sozialwohnungs-Szenario"""
        p = self.params

        # Mit optimiertem System: Kosten = 1.250 EUR/m² * 65 m² = 81.250 EUR/Einheit
        cost_per_social_unit = p.cost_optimized_future * p.social_unit_size

        # Bedarf: 1,05 Mio. neue Sozialwohnungen bis 2030
        total_cost = p.social_housing_deficit * cost_per_social_unit

        # Mit konventionellem Bau: 2.500 * 65 = 162.500 EUR/Einheit
        conventional_cost = p.cost_conventional * p.social_unit_size
        total_cost_conventional = p.social_housing_deficit * conventional_cost

        savings = total_cost_conventional - total_cost

        # Jaehrlicher Bedarf
        years_to_2030 = 5
        annual_units_needed = p.social_housing_deficit / years_to_2030
        annual_cost = annual_units_needed * cost_per_social_unit

        return {
            'units_needed': p.social_housing_deficit,
            'cost_per_unit_optimized': cost_per_social_unit,
            'cost_per_unit_conventional': conventional_cost,
            'total_cost_optimized': total_cost,
            'total_cost_conventional': total_cost_conventional,
            'total_savings': savings,
            'annual_units_needed': annual_units_needed,
            'annual_cost': annual_cost,
            'savings_per_unit': conventional_cost - cost_per_social_unit
        }


def main():
    """Hauptfunktion"""
    model = HousingModel()

    # Alle Szenarien durchfuehren
    scenarios = model.run_all_scenarios()
    model.print_scenario_comparison(scenarios)

    # Sozialwohnungs-Analyse
    print("\n" + "="*100)
    print("SOZIALWOHNUNGS-ANALYSE")
    print("="*100)

    social = model.calculate_social_housing_scenario()
    print(f"\nBedarf bis 2030: {social['units_needed']:,} Einheiten")
    print(f"Kosten pro Einheit (optimiert): {social['cost_per_unit_optimized']:,.0f} EUR")
    print(f"Kosten pro Einheit (konventionell): {social['cost_per_unit_conventional']:,.0f} EUR")
    print(f"Ersparnis pro Einheit: {social['savings_per_unit']:,.0f} EUR")
    print(f"\nGesamtkosten (optimiert): {social['total_cost_optimized']/1e9:.1f} Mrd. EUR")
    print(f"Gesamtkosten (konventionell): {social['total_cost_conventional']/1e9:.1f} Mrd. EUR")
    print(f"Gesamtersparnis: {social['total_savings']/1e9:.1f} Mrd. EUR")
    print(f"\nJaehrlicher Bedarf: {social['annual_units_needed']:,.0f} Einheiten")
    print(f"Jaehrliche Kosten: {social['annual_cost']/1e9:.1f} Mrd. EUR")

    return scenarios, social


if __name__ == "__main__":
    scenarios, social = main()
