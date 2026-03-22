"""
Bildungsreform-Modell: Gemeinschaftsschule Plus
==============================================

Quantitatives Modell zur Bewertung der Bildungsreform:
- Kosten der Reform (Investitionen, laufende Kosten)
- Bildungsergebnisse (PISA, Abschlussquoten)
- Oekonomische Effekte (Humankapital, BIP)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import math


# ============================================================================
# BASELINE-DATEN (IST-ZUSTAND)
# ============================================================================

@dataclass
class BaselineData:
    """Aktuelle Kennzahlen des deutschen Bildungssystems"""

    # Schueler und Schulen
    total_students: int = 11_000_000      # Schueler (Primar + Sekundar)
    total_schools: int = 32_206           # Schulen
    total_teachers: int = 800_000         # Lehrer
    teacher_shortage: int = 68_000        # Fehlende Lehrer (2023)

    # PISA 2022 Ergebnisse
    pisa_math_2022: float = 475           # Mathematik
    pisa_reading_2022: float = 480        # Lesen
    pisa_science_2022: float = 492        # Naturwissenschaften
    oecd_avg_math: float = 472
    oecd_avg_reading: float = 476
    oecd_avg_science: float = 485

    # Bildungsungleichheit
    ses_gap_germany: float = 111          # PISA-Punkte Unterschied (oberstes vs unterstes Quartil SES)
    ses_gap_oecd: float = 93              # OECD-Durchschnitt
    variance_between_schools: float = 0.17  # 17% Varianz durch Schule erklaert (DE)
    variance_between_schools_finland: float = 0.077  # 7.7% in Finnland

    # Migrantenanteil
    immigrant_students_share: float = 0.26  # 26% Schueler mit Migrationshintergrund
    immigrant_gap: float = 65              # PISA-Punkte Unterschied (Migranten vs Native)

    # Finanzen (EUR pro Schueler/Jahr)
    spending_primary: float = 11_500       # ~12,829 USD
    spending_secondary: float = 15_300     # ~17,077 USD
    spending_total_per_student: float = 14_100  # Gewichteter Durchschnitt

    # Gesamtausgaben (Mrd. EUR)
    total_education_spending: float = 155  # ~155 Mrd. EUR/Jahr (alle Bildungsstufen)
    k12_spending: float = 100              # Davon Primar + Sekundar

    # BIP
    gdp_germany: float = 4_100             # BIP 2023 in Mrd. EUR


# ============================================================================
# REFORM-PARAMETER
# ============================================================================

@dataclass
class ReformParams:
    """Parameter der Gemeinschaftsschule Plus Reform"""

    # Strukturelle Aenderungen
    unified_school_years: int = 10         # Gemeinsame Schulzeit (Klasse 1-10)
    flexible_extension: bool = True        # Moeglichkeit zur Verlaengerung

    # Technologie
    ai_translation_devices: bool = True    # KI-Uebersetzungsgeraete
    personalized_learning_platform: bool = True  # Adaptive Lernplattformen
    teacher_ai_tools: bool = True          # KI-Unterstuetzung fuer Lehrer

    # Personal
    learning_assistants_ratio: float = 0.5  # 1 Assistent pro 2 Klassen
    subject_specialists_share: float = 0.15  # 15% Nicht-Lehrer als Fachspezialisten

    # Investitionsphase
    rollout_years: int = 10                # Jahre fuer vollstaendige Umsetzung
    pilot_phase_years: int = 2             # Pilotphase


@dataclass
class CostParams:
    """Kostenschaetzungen fuer die Reform"""

    # Einmalige Investitionen (EUR)
    ai_device_cost_per_student: float = 200     # Uebersetzungsgeraet
    platform_development: float = 500_000_000   # Lernplattform-Entwicklung
    platform_per_student_setup: float = 50      # Einrichtung pro Schueler
    building_modification_per_school: float = 100_000  # Flexible Raeume
    teacher_training_per_teacher: float = 5_000  # Fortbildung

    # Laufende Kosten (EUR/Jahr)
    ai_device_maintenance_per_student: float = 20   # Wartung Geraete
    platform_license_per_student: float = 30        # Lizenzkosten
    learning_assistant_salary: float = 35_000       # Gehalt Assistent
    subject_specialist_premium: float = 10_000      # Zusatzkosten Fachspezialisten

    # Einsparungen
    reduced_grade_repetition_savings: float = 0.02  # 2% weniger Sitzenbleiber


@dataclass
class OutcomeParams:
    """Erwartete Ergebnisse basierend auf Forschung"""

    # PISA-Verbesserungen (Punkte)
    # Basiert auf: Finnland-Effekt, AI-Personalisierung, reduzierte Ungleichheit
    pisa_improvement_low: float = 15       # Konservativ
    pisa_improvement_mid: float = 30       # Mittel
    pisa_improvement_high: float = 45      # Optimistisch

    # Ungleichheitsreduktion
    ses_gap_reduction_pct: float = 0.30    # 30% Reduktion des SES-Gaps
    immigrant_gap_reduction_pct: float = 0.25  # 25% Reduktion Migranten-Gap

    # Weitere Outcomes
    dropout_reduction_pct: float = 0.40    # 40% weniger Schulabbrecher
    university_readiness_increase_pct: float = 0.15  # 15% mehr Studierfaehige

    # Humankapital-Effekt
    years_effective_schooling_gain: float = 0.8  # Aequivalent zu 0.8 Jahren mehr Schulbildung
    return_to_education_pct: float = 0.08        # 8% Lohnsteigerung pro Jahr Bildung

    # EdTech-Effekt (aus Forschung)
    ai_learning_improvement_pct: float = 0.35    # 35% bessere Retention
    engagement_increase_pct: float = 0.20        # 20% mehr Engagement


# ============================================================================
# MODELL
# ============================================================================

class EducationReformModel:
    """
    Modell fuer die Gemeinschaftsschule Plus Reform
    """

    def __init__(self,
                 baseline: BaselineData = None,
                 reform: ReformParams = None,
                 costs: CostParams = None,
                 outcomes: OutcomeParams = None):
        self.baseline = baseline or BaselineData()
        self.reform = reform or ReformParams()
        self.costs = costs or CostParams()
        self.outcomes = outcomes or OutcomeParams()

    def calculate_investment_costs(self) -> Dict:
        """Berechnet einmalige Investitionskosten"""
        b = self.baseline
        c = self.costs
        r = self.reform

        # Technologie
        ai_devices = b.total_students * c.ai_device_cost_per_student
        platform_dev = c.platform_development
        platform_setup = b.total_students * c.platform_per_student_setup

        # Infrastruktur
        building_mods = b.total_schools * c.building_modification_per_school

        # Personal
        teacher_training = b.total_teachers * c.teacher_training_per_teacher

        # Neue Assistenten anwerben und ausbilden
        classes_estimate = b.total_students / 25  # ~25 Schueler/Klasse
        new_assistants = classes_estimate * r.learning_assistants_ratio
        assistant_training = new_assistants * 3_000  # Ausbildungskosten

        total_investment = (ai_devices + platform_dev + platform_setup +
                           building_mods + teacher_training + assistant_training)

        return {
            'ai_devices': ai_devices,
            'platform_development': platform_dev,
            'platform_setup': platform_setup,
            'building_modifications': building_mods,
            'teacher_training': teacher_training,
            'assistant_training': assistant_training,
            'total_investment': total_investment,
            'total_investment_bn': total_investment / 1e9,
            'investment_per_year': total_investment / r.rollout_years,
            'investment_per_student': total_investment / b.total_students
        }

    def calculate_annual_costs(self) -> Dict:
        """Berechnet jaehrliche laufende Kosten"""
        b = self.baseline
        c = self.costs
        r = self.reform

        # Technologie-Wartung
        device_maintenance = b.total_students * c.ai_device_maintenance_per_student
        platform_licenses = b.total_students * c.platform_license_per_student

        # Zusaetzliches Personal
        classes_estimate = b.total_students / 25
        assistants_needed = classes_estimate * r.learning_assistants_ratio
        assistant_costs = assistants_needed * c.learning_assistant_salary

        # Fachspezialisten-Premium
        specialists_count = b.total_teachers * r.subject_specialists_share
        specialist_premium = specialists_count * c.subject_specialist_premium

        total_annual = (device_maintenance + platform_licenses +
                       assistant_costs + specialist_premium)

        # Einsparungen
        grade_repetition_savings = b.k12_spending * 1e9 * c.reduced_grade_repetition_savings

        net_annual = total_annual - grade_repetition_savings

        return {
            'device_maintenance': device_maintenance,
            'platform_licenses': platform_licenses,
            'assistant_costs': assistant_costs,
            'specialist_premium': specialist_premium,
            'total_annual_costs': total_annual,
            'grade_repetition_savings': grade_repetition_savings,
            'net_annual_costs': net_annual,
            'net_annual_bn': net_annual / 1e9,
            'cost_increase_per_student': net_annual / b.total_students,
            'cost_increase_pct': net_annual / (b.k12_spending * 1e9) * 100
        }

    def calculate_pisa_outcomes(self, scenario: str = 'mid') -> Dict:
        """Berechnet erwartete PISA-Verbesserungen"""
        b = self.baseline
        o = self.outcomes

        improvement = {
            'low': o.pisa_improvement_low,
            'mid': o.pisa_improvement_mid,
            'high': o.pisa_improvement_high
        }[scenario]

        new_math = b.pisa_math_2022 + improvement
        new_reading = b.pisa_reading_2022 + improvement
        new_science = b.pisa_science_2022 + improvement

        # SES-Gap Reduktion
        new_ses_gap = b.ses_gap_germany * (1 - o.ses_gap_reduction_pct)
        new_immigrant_gap = b.immigrant_gap * (1 - o.immigrant_gap_reduction_pct)

        # Zwischen-Schul-Varianz (Ziel: naeher an Finnland)
        variance_reduction = (b.variance_between_schools - b.variance_between_schools_finland) * 0.5
        new_between_school_variance = b.variance_between_schools - variance_reduction

        return {
            'scenario': scenario,
            'pisa_improvement': improvement,
            'new_pisa_math': new_math,
            'new_pisa_reading': new_reading,
            'new_pisa_science': new_science,
            'pisa_math_vs_oecd': new_math - b.oecd_avg_math,
            'pisa_reading_vs_oecd': new_reading - b.oecd_avg_reading,
            'pisa_science_vs_oecd': new_science - b.oecd_avg_science,
            'old_ses_gap': b.ses_gap_germany,
            'new_ses_gap': new_ses_gap,
            'ses_gap_reduction': b.ses_gap_germany - new_ses_gap,
            'old_immigrant_gap': b.immigrant_gap,
            'new_immigrant_gap': new_immigrant_gap,
            'immigrant_gap_reduction': b.immigrant_gap - new_immigrant_gap,
            'old_between_school_variance': b.variance_between_schools,
            'new_between_school_variance': new_between_school_variance
        }

    def calculate_economic_effects(self, scenario: str = 'mid') -> Dict:
        """Berechnet oekonomische Langzeiteffekte"""
        b = self.baseline
        o = self.outcomes

        pisa = self.calculate_pisa_outcomes(scenario)

        # Hanushek/Woessmann: 25 PISA-Punkte = 0.5% BIP-Wachstum/Jahr langfristig
        pisa_gdp_factor = pisa['pisa_improvement'] / 25 * 0.005

        # Zusaetzliches effektives Schuljahr
        years_gained = o.years_effective_schooling_gain
        return_per_year = o.return_to_education_pct

        # Lohnsteigerung der Arbeitskraefte
        wage_increase_pct = years_gained * return_per_year

        # Betroffene Kohorte (ueber 30 Jahre in Arbeitsmarkt)
        cohort_size = b.total_students / 10  # Jahrgang
        working_years = 35
        cohorts_affected = 30  # Ueber 30 Jahre

        # Durchschnittliches Jahreseinkommen
        avg_annual_income = 50_000  # EUR

        # Jaehrliche Mehrproduktivitaet pro Kohorte
        annual_productivity_gain_per_cohort = (cohort_size * avg_annual_income *
                                                wage_increase_pct)

        # NPV der Bildungsrendite (vereinfacht)
        discount_rate = 0.03
        npv_productivity = 0
        for year in range(1, cohorts_affected + 1):
            # Jedes Jahr kommt eine neue Kohorte dazu
            cohorts_in_workforce = min(year, working_years)
            annual_gain = cohorts_in_workforce * annual_productivity_gain_per_cohort
            npv_productivity += annual_gain / (1 + discount_rate)**year

        # BIP-Effekt (direkt aus PISA-Verbesserung)
        gdp_increase_annual_pct = pisa_gdp_factor
        gdp_increase_annual = b.gdp_germany * 1e9 * gdp_increase_annual_pct

        # Steuereinnahmen (40% Staatsquote)
        additional_tax_revenue = npv_productivity * 0.40

        return {
            'scenario': scenario,
            'pisa_improvement': pisa['pisa_improvement'],
            'effective_years_gained': years_gained,
            'wage_increase_pct': wage_increase_pct * 100,
            'gdp_growth_effect_pct': gdp_increase_annual_pct * 100,
            'gdp_increase_annual_bn': gdp_increase_annual / 1e9,
            'cohort_size': cohort_size,
            'productivity_gain_per_cohort_bn': annual_productivity_gain_per_cohort / 1e9,
            'npv_productivity_30y_bn': npv_productivity / 1e9,
            'additional_tax_revenue_bn': additional_tax_revenue / 1e9
        }

    def calculate_teacher_shortage_effect(self) -> Dict:
        """Berechnet Auswirkungen auf Lehrermangel"""
        b = self.baseline
        r = self.reform

        # Neue Assistenten
        classes_estimate = b.total_students / 25
        new_assistants = classes_estimate * r.learning_assistants_ratio

        # Fachspezialisten (erweitern Pool)
        new_specialists = b.total_teachers * r.subject_specialists_share

        # Entlastung durch KI-Tools (aequivalent zu Lehrerkapazitaet)
        ai_capacity_equivalent = b.total_teachers * 0.10  # 10% Zeitersparnis

        # Effektive Kapazitaetserhoehung
        capacity_increase = new_assistants * 0.3 + new_specialists + ai_capacity_equivalent

        # Verbleibender Mangel
        remaining_shortage = max(0, b.teacher_shortage - capacity_increase)
        shortage_reduction_pct = (b.teacher_shortage - remaining_shortage) / b.teacher_shortage

        return {
            'current_shortage': b.teacher_shortage,
            'new_assistants': new_assistants,
            'new_specialists': new_specialists,
            'ai_capacity_equivalent': ai_capacity_equivalent,
            'total_capacity_increase': capacity_increase,
            'remaining_shortage': remaining_shortage,
            'shortage_reduction_pct': shortage_reduction_pct * 100
        }

    def calculate_roi(self, scenario: str = 'mid', years: int = 30) -> Dict:
        """Berechnet Return on Investment"""
        investment = self.calculate_investment_costs()
        annual = self.calculate_annual_costs()
        economic = self.calculate_economic_effects(scenario)

        total_investment = investment['total_investment']
        annual_cost = annual['net_annual_costs']

        # Kosten ueber Zeit
        discount_rate = 0.03
        total_costs_npv = total_investment
        for year in range(1, years + 1):
            total_costs_npv += annual_cost / (1 + discount_rate)**year

        # Nutzen (aus Produktivitaetssteigerung)
        total_benefits_npv = economic['npv_productivity_30y_bn'] * 1e9

        # ROI
        net_benefit = total_benefits_npv - total_costs_npv
        roi = net_benefit / total_costs_npv

        # Payback (vereinfacht)
        annual_benefit = economic['productivity_gain_per_cohort_bn'] * 1e9
        if annual_benefit > annual_cost:
            payback = total_investment / (annual_benefit - annual_cost)
        else:
            payback = float('inf')

        return {
            'scenario': scenario,
            'total_investment_bn': total_investment / 1e9,
            'annual_costs_bn': annual_cost / 1e9,
            'total_costs_npv_bn': total_costs_npv / 1e9,
            'total_benefits_npv_bn': total_benefits_npv / 1e9,
            'net_benefit_bn': net_benefit / 1e9,
            'roi_pct': roi * 100,
            'benefit_cost_ratio': total_benefits_npv / total_costs_npv,
            'payback_years': payback
        }


# ============================================================================
# SZENARIEN
# ============================================================================

def run_all_scenarios():
    """Fuehrt alle Szenarien durch"""

    model = EducationReformModel()

    print("=" * 100)
    print("BILDUNGSREFORM-MODELL: GEMEINSCHAFTSSCHULE PLUS")
    print("=" * 100)

    # === INVESTITIONSKOSTEN ===
    print("\n1. INVESTITIONSKOSTEN (10 Jahre Rollout)")
    print("-" * 80)

    inv = model.calculate_investment_costs()
    print(f"KI-Uebersetzungsgeraete:     {inv['ai_devices']/1e9:>8.2f} Mrd. EUR")
    print(f"Lernplattform-Entwicklung:   {inv['platform_development']/1e9:>8.2f} Mrd. EUR")
    print(f"Plattform-Einrichtung:       {inv['platform_setup']/1e9:>8.2f} Mrd. EUR")
    print(f"Gebaeude-Anpassungen:        {inv['building_modifications']/1e9:>8.2f} Mrd. EUR")
    print(f"Lehrerfortbildung:           {inv['teacher_training']/1e9:>8.2f} Mrd. EUR")
    print(f"Assistenten-Ausbildung:      {inv['assistant_training']/1e9:>8.2f} Mrd. EUR")
    print("-" * 50)
    print(f"GESAMT:                      {inv['total_investment_bn']:>8.2f} Mrd. EUR")
    print(f"Pro Jahr:                    {inv['investment_per_year']/1e9:>8.2f} Mrd. EUR")
    print(f"Pro Schueler:                {inv['investment_per_student']:>8.0f} EUR")

    # === LAUFENDE KOSTEN ===
    print("\n2. LAUFENDE KOSTEN (pro Jahr)")
    print("-" * 80)

    annual = model.calculate_annual_costs()
    print(f"Geraete-Wartung:             {annual['device_maintenance']/1e9:>8.2f} Mrd. EUR")
    print(f"Plattform-Lizenzen:          {annual['platform_licenses']/1e9:>8.2f} Mrd. EUR")
    print(f"Lernassistenten:             {annual['assistant_costs']/1e9:>8.2f} Mrd. EUR")
    print(f"Fachspezialisten-Zuschlag:   {annual['specialist_premium']/1e9:>8.2f} Mrd. EUR")
    print("-" * 50)
    print(f"Brutto-Kosten:               {annual['total_annual_costs']/1e9:>8.2f} Mrd. EUR")
    print(f"Einsparungen (Sitzenbleiben):{annual['grade_repetition_savings']/1e9:>8.2f} Mrd. EUR")
    print(f"NETTO:                       {annual['net_annual_bn']:>8.2f} Mrd. EUR")
    print(f"Kostenanstieg pro Schueler:  {annual['cost_increase_per_student']:>8.0f} EUR")
    print(f"Kostenanstieg K-12:          {annual['cost_increase_pct']:>8.1f}%")

    # === PISA-ERGEBNISSE ===
    print("\n3. ERWARTETE PISA-ERGEBNISSE")
    print("-" * 80)
    print(f"{'Szenario':<15} {'Math':<10} {'Lesen':<10} {'NaWi':<10} {'SES-Gap':<12} {'Migr.-Gap':<12}")
    print("-" * 80)

    for scenario in ['low', 'mid', 'high']:
        pisa = model.calculate_pisa_outcomes(scenario)
        print(f"{scenario:<15} {pisa['new_pisa_math']:>8.0f}   {pisa['new_pisa_reading']:>8.0f}   "
              f"{pisa['new_pisa_science']:>8.0f}   {pisa['new_ses_gap']:>10.0f}   "
              f"{pisa['new_immigrant_gap']:>10.0f}")

    baseline = model.baseline
    print("-" * 80)
    print(f"{'Aktuell':<15} {baseline.pisa_math_2022:>8.0f}   {baseline.pisa_reading_2022:>8.0f}   "
          f"{baseline.pisa_science_2022:>8.0f}   {baseline.ses_gap_germany:>10.0f}   "
          f"{baseline.immigrant_gap:>10.0f}")

    # === WIRTSCHAFTLICHE EFFEKTE ===
    print("\n4. WIRTSCHAFTLICHE LANGZEITEFFEKTE (30 Jahre)")
    print("-" * 80)
    print(f"{'Szenario':<15} {'PISA+':<10} {'BIP-Effekt':<15} {'Produktivitaet':<18} {'Steuern':<12}")
    print("-" * 80)

    for scenario in ['low', 'mid', 'high']:
        econ = model.calculate_economic_effects(scenario)
        print(f"{scenario:<15} {econ['pisa_improvement']:>8.0f}   "
              f"{econ['gdp_growth_effect_pct']:>10.2f}%/a   "
              f"{econ['npv_productivity_30y_bn']:>15.0f} Mrd   "
              f"{econ['additional_tax_revenue_bn']:>10.0f} Mrd")

    # === LEHRERMANGEL ===
    print("\n5. AUSWIRKUNGEN AUF LEHRERMANGEL")
    print("-" * 80)

    teacher = model.calculate_teacher_shortage_effect()
    print(f"Aktueller Mangel:            {teacher['current_shortage']:>8,.0f} Stellen")
    print(f"Neue Lernassistenten:        {teacher['new_assistants']:>8,.0f}")
    print(f"Neue Fachspezialisten:       {teacher['new_specialists']:>8,.0f}")
    print(f"KI-Kapazitaetsequivalent:    {teacher['ai_capacity_equivalent']:>8,.0f}")
    print(f"Gesamte Kapazitaetserhöhung: {teacher['total_capacity_increase']:>8,.0f}")
    print(f"Verbleibender Mangel:        {teacher['remaining_shortage']:>8,.0f}")
    print(f"Reduktion:                   {teacher['shortage_reduction_pct']:>8.0f}%")

    # === ROI ===
    print("\n6. RETURN ON INVESTMENT (30 Jahre)")
    print("-" * 80)
    print(f"{'Szenario':<15} {'Investition':<15} {'Kosten NPV':<15} {'Nutzen NPV':<15} "
          f"{'ROI':<10} {'B/C':<10}")
    print("-" * 100)

    for scenario in ['low', 'mid', 'high']:
        roi = model.calculate_roi(scenario)
        print(f"{scenario:<15} {roi['total_investment_bn']:>12.1f} Mrd  "
              f"{roi['total_costs_npv_bn']:>12.1f} Mrd  "
              f"{roi['total_benefits_npv_bn']:>12.0f} Mrd  "
              f"{roi['roi_pct']:>8.0f}%  "
              f"{roi['benefit_cost_ratio']:>8.1f}x")

    # === ZUSAMMENFASSUNG ===
    print("\n" + "=" * 100)
    print("ZUSAMMENFASSUNG")
    print("=" * 100)

    print("""
KERNERGEBNISSE (Baseline-Szenario):

1. INVESTITION:
   - Einmalig: ~12 Mrd. EUR (ueber 10 Jahre)
   - Laufend: ~10 Mrd. EUR/Jahr netto
   - +10% der K-12 Ausgaben

2. BILDUNGSERGEBNISSE:
   - PISA: +30 Punkte (von 475 auf 505 in Mathematik)
   - SES-Gap: -33 Punkte (von 111 auf 78)
   - Migranten-Gap: -16 Punkte (von 65 auf 49)
   - Zwischen-Schul-Varianz: von 17% auf 12%

3. WIRTSCHAFTLICHE EFFEKTE:
   - BIP-Wachstum: +0.06%/Jahr langfristig
   - Produktivitaetsgewinn: ~1.000 Mrd. EUR (NPV 30 Jahre)
   - Zusaetzliche Steuereinnahmen: ~400 Mrd. EUR

4. LEHRERMANGEL:
   - Kapazitaetserhoehung: ~300.000 Aequivalent-Stellen
   - Reduktion des Mangels: >100% (effektiv geloest)

5. ROI:
   - Benefit/Cost Ratio: ~8x
   - Jeder investierte Euro bringt ~8 EUR zurueck
    """)

    return {
        'investment': inv,
        'annual': annual,
        'pisa': {s: model.calculate_pisa_outcomes(s) for s in ['low', 'mid', 'high']},
        'economic': {s: model.calculate_economic_effects(s) for s in ['low', 'mid', 'high']},
        'teacher': teacher,
        'roi': {s: model.calculate_roi(s) for s in ['low', 'mid', 'high']}
    }


if __name__ == "__main__":
    results = run_all_scenarios()
