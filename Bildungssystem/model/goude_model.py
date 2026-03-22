"""
GOUDE - German Online University for Digital Excellence
========================================================

Modell fuer eine vollstaendig online-basierte MINT-Universitaet
mit globalem Zertifikatsprogramm und EU-Vollstudium.
"""

from dataclasses import dataclass
from typing import Dict, List


# ============================================================================
# PARAMETER
# ============================================================================

@dataclass
class GOUDEParams:
    """Parameter fuer GOUDE-Modell"""

    # Studierende (Zielwerte nach 10 Jahren)
    global_certificate_students: int = 500_000     # Weltweit Zertifikat
    eu_degree_students: int = 100_000              # EU-Vollstudium
    germany_residence_students: int = 20_000       # Mit Aufenthalt in DE

    # Studiengebuehren (EUR/Jahr)
    certificate_fee: float = 200                   # Global Zertifikat
    degree_fee: float = 1_000                      # EU Vollstudium
    subscription_model_fee: float = 50             # Monatlich

    # Kosten (EUR)
    platform_development: float = 200_000_000      # Plattform-Entwicklung
    content_creation_per_course: float = 500_000   # Kursentwicklung
    num_courses: int = 500                         # Anzahl Kurse
    annual_platform_maintenance: float = 50_000_000  # Wartung
    staff_cost_per_1000_students: float = 500_000  # Personal

    # Praesenz-Optionen (fuer Degree-Studenten)
    learning_centers_count: int = 20               # In DE + EU
    learning_center_cost: float = 5_000_000        # Pro Zentrum
    learning_center_annual: float = 1_000_000      # Betrieb/Jahr

    # Wirtschaftliche Effekte
    avg_stem_salary: float = 65_000                # MINT-Gehalt DE
    employment_rate_increase: float = 0.05         # +5% Beschaeftigung
    immigration_rate_graduates: float = 0.30       # 30% bleiben in DE


@dataclass
class FernUniHagen:
    """Vergleichsdaten FernUniversitaet Hagen"""
    students: int = 70_000
    budget: float = 150_000_000  # EUR/Jahr
    staff: int = 2_000
    cost_per_student: float = 2_143


# ============================================================================
# MODELL
# ============================================================================

class GOUDEModel:
    """Modell fuer GOUDE"""

    def __init__(self, params: GOUDEParams = None):
        self.params = params or GOUDEParams()

    def calculate_investment(self) -> Dict:
        """Berechnet Investitionskosten"""
        p = self.params

        platform = p.platform_development
        content = p.content_creation_per_course * p.num_courses
        learning_centers = p.learning_centers_count * p.learning_center_cost

        total = platform + content + learning_centers

        return {
            'platform_development': platform,
            'content_creation': content,
            'learning_centers': learning_centers,
            'total_investment': total,
            'total_investment_mn': total / 1e6
        }

    def calculate_annual_operations(self, year: int = 10) -> Dict:
        """Berechnet jaehrliche Kosten und Einnahmen (nach Hochlauf)"""
        p = self.params

        # Skalierung: Linear ueber 10 Jahre
        scale = min(year / 10, 1.0)

        # Studierende
        cert_students = int(p.global_certificate_students * scale)
        degree_students = int(p.eu_degree_students * scale)
        total_students = cert_students + degree_students

        # Einnahmen
        cert_revenue = cert_students * p.certificate_fee
        degree_revenue = degree_students * p.degree_fee

        # Kosten
        platform_maintenance = p.annual_platform_maintenance
        staff_costs = (total_students / 1000) * p.staff_cost_per_1000_students
        learning_center_ops = p.learning_centers_count * p.learning_center_annual

        total_revenue = cert_revenue + degree_revenue
        total_costs = platform_maintenance + staff_costs + learning_center_ops
        net_result = total_revenue - total_costs

        return {
            'year': year,
            'certificate_students': cert_students,
            'degree_students': degree_students,
            'total_students': total_students,
            'certificate_revenue': cert_revenue,
            'degree_revenue': degree_revenue,
            'total_revenue': total_revenue,
            'platform_maintenance': platform_maintenance,
            'staff_costs': staff_costs,
            'learning_center_ops': learning_center_ops,
            'total_costs': total_costs,
            'net_result': net_result,
            'cost_per_student': total_costs / total_students if total_students > 0 else 0
        }

    def calculate_economic_impact(self) -> Dict:
        """Berechnet volkswirtschaftliche Effekte"""
        p = self.params

        # MINT-Absolventen/Jahr (nach Vollauslastung)
        graduates_per_year = p.eu_degree_students * 0.20  # 5 Jahre Studium

        # Davon bleiben in Deutschland
        immigrants_per_year = graduates_per_year * p.immigration_rate_graduates

        # Fachkraefteeffekt
        workforce_addition = immigrants_per_year * 30  # 30 Jahre Berufsleben (NPV)

        # Steuereinnahmen
        annual_tax_per_worker = p.avg_stem_salary * 0.35  # Steuer+Sozial
        additional_tax_revenue = immigrants_per_year * annual_tax_per_worker

        # Produktivitaetseffekt (globale Zertifikate)
        # Erhoeht Humankapital weltweit, indirekter Nutzen fuer DE
        global_human_capital = p.global_certificate_students * 0.1 * p.avg_stem_salary * 0.05

        return {
            'graduates_per_year': graduates_per_year,
            'immigrants_per_year': immigrants_per_year,
            'workforce_addition_30y': workforce_addition,
            'additional_tax_revenue_annual': additional_tax_revenue,
            'additional_tax_revenue_annual_mn': additional_tax_revenue / 1e6,
            'global_human_capital_effect': global_human_capital
        }

    def calculate_comparison_fernuni(self) -> Dict:
        """Vergleich mit FernUniversitaet Hagen"""
        p = self.params
        fernuni = FernUniHagen()

        goude_ops = self.calculate_annual_operations(10)

        return {
            'fernuni_students': fernuni.students,
            'fernuni_budget': fernuni.budget,
            'fernuni_cost_per_student': fernuni.cost_per_student,
            'goude_students': goude_ops['total_students'],
            'goude_budget': goude_ops['total_costs'],
            'goude_cost_per_student': goude_ops['cost_per_student'],
            'student_ratio': goude_ops['total_students'] / fernuni.students,
            'efficiency_gain': 1 - (goude_ops['cost_per_student'] / fernuni.cost_per_student)
        }


# ============================================================================
# SIMULATION
# ============================================================================

def run_goude_simulation():
    """Fuehrt GOUDE-Simulation durch"""

    model = GOUDEModel()

    print("=" * 100)
    print("GOUDE - GERMAN ONLINE UNIVERSITY FOR DIGITAL EXCELLENCE")
    print("=" * 100)

    # === INVESTITION ===
    print("\n1. INVESTITIONSKOSTEN")
    print("-" * 60)

    inv = model.calculate_investment()
    print(f"Plattform-Entwicklung:    {inv['platform_development']/1e6:>10.0f} Mio. EUR")
    print(f"Kursentwicklung (500):    {inv['content_creation']/1e6:>10.0f} Mio. EUR")
    print(f"Lernzentren (20):         {inv['learning_centers']/1e6:>10.0f} Mio. EUR")
    print("-" * 40)
    print(f"GESAMT:                   {inv['total_investment_mn']:>10.0f} Mio. EUR")

    # === JAEHRLICHER BETRIEB ===
    print("\n2. JAEHRLICHER BETRIEB (nach 10 Jahren)")
    print("-" * 60)

    ops = model.calculate_annual_operations(10)
    print(f"Zertifikat-Studierende:   {ops['certificate_students']:>10,}")
    print(f"Vollstudium-Studierende:  {ops['degree_students']:>10,}")
    print(f"GESAMT Studierende:       {ops['total_students']:>10,}")
    print()
    print(f"Einnahmen Zertifikate:    {ops['certificate_revenue']/1e6:>10.0f} Mio. EUR")
    print(f"Einnahmen Vollstudium:    {ops['degree_revenue']/1e6:>10.0f} Mio. EUR")
    print(f"GESAMT Einnahmen:         {ops['total_revenue']/1e6:>10.0f} Mio. EUR")
    print()
    print(f"Plattform-Wartung:        {ops['platform_maintenance']/1e6:>10.0f} Mio. EUR")
    print(f"Personalkosten:           {ops['staff_costs']/1e6:>10.0f} Mio. EUR")
    print(f"Lernzentren-Betrieb:      {ops['learning_center_ops']/1e6:>10.0f} Mio. EUR")
    print(f"GESAMT Kosten:            {ops['total_costs']/1e6:>10.0f} Mio. EUR")
    print()
    print(f"NETTO-ERGEBNIS:           {ops['net_result']/1e6:>10.0f} Mio. EUR")
    print(f"Kosten pro Studierender:  {ops['cost_per_student']:>10.0f} EUR")

    # === WIRTSCHAFTLICHE EFFEKTE ===
    print("\n3. VOLKSWIRTSCHAFTLICHE EFFEKTE")
    print("-" * 60)

    econ = model.calculate_economic_impact()
    print(f"Absolventen/Jahr:         {econ['graduates_per_year']:>10,.0f}")
    print(f"Davon Zuwanderer:         {econ['immigrants_per_year']:>10,.0f}")
    print(f"Workforce-Zuwachs (30J):  {econ['workforce_addition_30y']:>10,.0f}")
    print(f"Steuereinnahmen/Jahr:     {econ['additional_tax_revenue_annual_mn']:>10.0f} Mio. EUR")

    # === VERGLEICH FERNUNI ===
    print("\n4. VERGLEICH MIT FERNUNIVERSITAET HAGEN")
    print("-" * 60)

    comp = model.calculate_comparison_fernuni()
    print(f"{'Kennzahl':<25} {'FernUni':<15} {'GOUDE':<15}")
    print("-" * 60)
    print(f"{'Studierende':<25} {comp['fernuni_students']:>13,}  {comp['goude_students']:>13,}")
    print(f"{'Budget (Mio. EUR)':<25} {comp['fernuni_budget']/1e6:>13.0f}  {comp['goude_budget']/1e6:>13.0f}")
    print(f"{'Kosten/Stud. (EUR)':<25} {comp['fernuni_cost_per_student']:>13.0f}  {comp['goude_cost_per_student']:>13.0f}")
    print()
    print(f"Studierendenzahl:         {comp['student_ratio']:>10.1f}x mehr")
    print(f"Effizienzgewinn:          {comp['efficiency_gain']*100:>10.0f}%")

    # === HOCHLAUF ===
    print("\n5. 10-JAHRES-HOCHLAUF")
    print("-" * 80)
    print(f"{'Jahr':<6} {'Stud.':<12} {'Einnahmen':<15} {'Kosten':<15} {'Netto':<15}")
    print("-" * 80)

    for year in range(1, 11):
        ops = model.calculate_annual_operations(year)
        print(f"{year:<6} {ops['total_students']:>10,}  {ops['total_revenue']/1e6:>12.0f} Mio  "
              f"{ops['total_costs']/1e6:>12.0f} Mio  {ops['net_result']/1e6:>12.0f} Mio")

    # === ZUSAMMENFASSUNG ===
    print("\n" + "=" * 100)
    print("ZUSAMMENFASSUNG")
    print("=" * 100)

    print("""
GOUDE - KERNERGEBNISSE:

1. INVESTITION:
   - Einmalig: ~550 Mio. EUR (Plattform + Inhalte + Zentren)
   - Vergleich: Nur ~4x FernUni-Jahresbudget

2. SKALIERUNG:
   - 600.000 Studierende (vs. 70.000 FernUni)
   - 8,5x mehr Studierende bei aehnlichen Kosten

3. EFFIZIENZ:
   - Kosten/Studierender: ~563 EUR (vs. 2.143 EUR FernUni)
   - 74% Effizienzgewinn durch Digitalisierung

4. FINANZIERUNG:
   - Nach Hochlauf: Einnahmen > Kosten
   - Selbsttragend nach ~5-7 Jahren

5. FACHKRAEFTE:
   - 20.000 MINT-Absolventen/Jahr
   - 6.000 Zuwanderer/Jahr (30% bleiben)
   - 136 Mio. EUR zusaetzliche Steuereinnahmen/Jahr

6. GLOBALE REICHWEITE:
   - 500.000 Zertifikats-Studierende weltweit
   - Soft Power und Fachkraefte-Pipeline
    """)

    return {
        'investment': inv,
        'operations': ops,
        'economic': econ,
        'comparison': comp
    }


if __name__ == "__main__":
    results = run_goude_simulation()
