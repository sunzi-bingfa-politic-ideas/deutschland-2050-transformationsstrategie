#!/usr/bin/env python3
"""
Soft Power Education Model: Exchange-Develop und Franchise
============================================================

Simuliert die wirtschaftlichen und diplomatischen Effekte einer
Bildungs-Soft-Power-Strategie durch:
1. Exchange-Develop: Stipendien für Studierende aus Entwicklungsländern an deutschen Schulen
2. Franchise: Deutsche Partnerschulen in Entwicklungsländern

Basiert auf:
- DAAD Statistiken (753 Mio EUR Budget, 141.000 Geförderte/Jahr)
- Deutsche Auslandsschulen (140 Schulen, 85.000 Schüler)
- Goethe-Institut (350 Mio EUR Budget, 158 Institute)
- World Bank Returns to Education (9% globaler Durchschnitt)
- Soft Power Forschung (Education Diplomacy Effectiveness)

Rigor: Medium - Basiert auf DAAD/ZfA-Daten und Soft Power Forschung.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import json


@dataclass
class ExchangeDevelopParams:
    """Parameter für das Exchange-Develop Stipendienprogramm."""
    # Zielgruppe
    stipendien_pro_jahr: int = 5000              # Neue Stipendiaten/Jahr
    programm_dauer_jahre: int = 3                # Durchschnittliche Aufenthaltsdauer
    ziellaender: int = 50                        # Anzahl Partnerländer

    # Kosten pro Stipendiat
    stipendium_monatlich: int = 1200             # EUR/Monat (Lebenshaltung)
    schulgebuehr_jahr: int = 0                   # Öffentliche Schulen kostenlos
    betreuung_jahr: int = 2000                   # Mentoring, Integration
    reisekosten: int = 2000                      # Hin- und Rückflug

    # Infrastruktur
    koordinationsbuero: int = 5_000_000          # EUR/Jahr zentrale Verwaltung
    regionale_bueros: int = 2_000_000            # EUR/Jahr (10 Büros × 200k)

    # Erfolgsquoten
    abschlussquote: float = 0.90                 # 90% schließen erfolgreich ab
    bleiber_quote: float = 0.15                  # 15% bleiben in Deutschland
    rueckkehrer_wirkung: float = 0.85            # 85% der Rückkehrer sind "Botschafter"


@dataclass
class FranchiseParams:
    """Parameter für das Franchise-Schulmodell."""
    # Expansion
    neue_schulen_pro_jahr: int = 10              # Neue Partnerschulen/Jahr
    schueler_pro_schule: int = 500               # Durchschnitt
    max_schulen: int = 100                       # Langfristiges Ziel

    # Investitionskosten pro Schule
    gebaeude_ausstattung: int = 2_000_000        # EUR (lokale Partner tragen 50%)
    curriculum_entwicklung: int = 500_000        # EUR (einmalig, teilbar)
    lehrerausbildung: int = 300_000              # EUR (pro Schule initial)
    technologie_paket: int = 200_000             # EUR (EdTech, Computer)
    deutschland_beitrag: float = 0.50            # 50% der Kosten trägt Deutschland

    # Laufende Kosten pro Schule (Deutschland-Anteil)
    personal_entsendung: int = 150_000           # 2-3 deutsche Lehrer
    qualitaetssicherung: int = 50_000            # Audits, Standards
    austauschprogramme: int = 30_000             # Schüleraustausch

    # Wirkung
    deutsch_niveau_b2: float = 0.60              # 60% erreichen B2 Deutsch
    weiterbildung_de: float = 0.05               # 5% studieren später in DE


@dataclass
class SoftPowerParams:
    """Parameter für Soft Power Bewertung."""
    # Wert eines "Botschafters"
    handelswert_jaehrlich: int = 50_000          # EUR potenzielle Handelsförderung
    diplomatischer_wert: int = 10_000            # EUR/Jahr (Netzwerk, Einfluss)
    wissenstransfer_wert: int = 5_000            # EUR/Jahr

    # Karriereeffekte Bleiber
    durchschnittsgehalt_bleiber: int = 55_000    # EUR/Jahr (qualifizierte Zuwanderer)
    steuerquote: float = 0.35                    # 35% Abgaben
    beschaeftigungsdauer_jahre: int = 30         # Erwartete Karrieredauer in DE

    # Multiplikatoren
    alumni_netzwerk_effekt: float = 1.5          # Netzwerkeffekte
    zeitliche_persistenz: float = 0.95           # Jährlicher Effekterhalt


@dataclass
class EconomicParams:
    """Ökonomische Annahmen."""
    discount_rate: float = 0.03                  # 3% Diskontrate
    simulation_jahre: int = 30                   # Langfristige Projektion
    inflation: float = 0.02                      # 2% Inflation

    # Returns to Education (Entwicklungsländer)
    return_per_year_education: float = 0.09     # 9% pro Schuljahr (World Bank)
    income_developing_country: int = 5_000       # EUR/Jahr Durchschnitt

    # Handelseffekte
    export_elastizitaet_bildung: float = 0.03   # +3% Exporte pro 1000 Alumni


@dataclass
class ExchangeDevelopResult:
    """Ergebnis des Exchange-Develop Programms."""
    jahr: int
    stipendiaten_aktiv: int
    stipendiaten_kumuliert: int
    absolventen_kumuliert: int
    bleiber_kumuliert: int
    botschafter_kumuliert: int
    kosten_jahr: float
    kosten_kumuliert: float


@dataclass
class FranchiseResult:
    """Ergebnis des Franchise-Programms."""
    jahr: int
    schulen_aktiv: int
    schueler_total: int
    absolventen_kumuliert: int
    deutschsprecher_kumuliert: int
    studenten_de_kumuliert: int
    kosten_jahr: float
    kosten_kumuliert: float


@dataclass
class SoftPowerResult:
    """Ergebnis der Soft Power Bewertung."""
    jahr: int
    botschafter_aktiv: int
    handelswert: float
    diplomatischer_wert: float
    steuereinnahmen_bleiber: float
    total_wert: float
    npv_kumuliert: float


@dataclass
class SimulationResult:
    """Gesamtergebnis der Simulation."""
    exchange_results: List[ExchangeDevelopResult]
    franchise_results: List[FranchiseResult]
    soft_power_results: List[SoftPowerResult]

    # Zusammenfassung
    total_investment: float = 0.0
    total_running_costs: float = 0.0
    npv_benefits: float = 0.0
    benefit_cost_ratio: float = 0.0
    roi_percent: float = 0.0

    # Reichweite
    total_stipendiaten: int = 0
    total_franchise_schueler: int = 0
    total_botschafter: int = 0
    laender_erreicht: int = 0


def simulate_exchange_develop(
    params: ExchangeDevelopParams,
    econ: EconomicParams
) -> List[ExchangeDevelopResult]:
    """Simuliert das Exchange-Develop Stipendienprogramm."""
    results = []

    # Laufende Variablen
    stipendiaten_aktiv = 0
    stipendiaten_kumuliert = 0
    absolventen_kumuliert = 0
    bleiber_kumuliert = 0
    botschafter_kumuliert = 0
    kosten_kumuliert = 0.0

    # Kosten pro Stipendiat pro Jahr
    kosten_pro_stipendiat_jahr = (
        params.stipendium_monatlich * 12 +
        params.schulgebuehr_jahr +
        params.betreuung_jahr
    )

    for jahr in range(1, econ.simulation_jahre + 1):
        # Neue Stipendiaten
        neue_stipendiaten = params.stipendien_pro_jahr
        stipendiaten_kumuliert += neue_stipendiaten

        # Absolventen (nach Programmdauer)
        if jahr > params.programm_dauer_jahre:
            neue_absolventen = int(params.stipendien_pro_jahr * params.abschlussquote)
            absolventen_kumuliert += neue_absolventen

            # Bleiber und Botschafter
            bleiber_neu = int(neue_absolventen * params.bleiber_quote)
            botschafter_neu = int((neue_absolventen - bleiber_neu) * params.rueckkehrer_wirkung)

            bleiber_kumuliert += bleiber_neu
            botschafter_kumuliert += botschafter_neu

        # Aktive Stipendiaten (rollierend)
        stipendiaten_aktiv = min(
            params.stipendien_pro_jahr * params.programm_dauer_jahre,
            stipendiaten_kumuliert
        )

        # Kosten
        kosten_stipendien = stipendiaten_aktiv * kosten_pro_stipendiat_jahr
        kosten_reise = neue_stipendiaten * params.reisekosten
        kosten_infrastruktur = params.koordinationsbuero + params.regionale_bueros

        kosten_jahr = kosten_stipendien + kosten_reise + kosten_infrastruktur
        kosten_kumuliert += kosten_jahr

        results.append(ExchangeDevelopResult(
            jahr=jahr,
            stipendiaten_aktiv=stipendiaten_aktiv,
            stipendiaten_kumuliert=stipendiaten_kumuliert,
            absolventen_kumuliert=absolventen_kumuliert,
            bleiber_kumuliert=bleiber_kumuliert,
            botschafter_kumuliert=botschafter_kumuliert,
            kosten_jahr=kosten_jahr,
            kosten_kumuliert=kosten_kumuliert
        ))

    return results


def simulate_franchise(
    params: FranchiseParams,
    econ: EconomicParams
) -> List[FranchiseResult]:
    """Simuliert das Franchise-Schulprogramm."""
    results = []

    schulen_aktiv = 0
    schueler_kumuliert = 0
    absolventen_kumuliert = 0
    deutschsprecher_kumuliert = 0
    studenten_de_kumuliert = 0
    kosten_kumuliert = 0.0

    # Investitionskosten pro Schule (Deutschland-Anteil)
    invest_pro_schule = (
        params.gebaeude_ausstattung +
        params.curriculum_entwicklung +
        params.lehrerausbildung +
        params.technologie_paket
    ) * params.deutschland_beitrag

    # Laufende Kosten pro Schule
    laufend_pro_schule = (
        params.personal_entsendung +
        params.qualitaetssicherung +
        params.austauschprogramme
    )

    for jahr in range(1, econ.simulation_jahre + 1):
        # Neue Schulen (bis Maximum)
        if schulen_aktiv < params.max_schulen:
            neue_schulen = min(
                params.neue_schulen_pro_jahr,
                params.max_schulen - schulen_aktiv
            )
            schulen_aktiv += neue_schulen
        else:
            neue_schulen = 0

        # Schüler
        schueler_total = schulen_aktiv * params.schueler_pro_schule
        schueler_kumuliert += schueler_total  # Vereinfacht

        # Absolventen (nach 12 Jahren Schulzeit, ab Jahr 12)
        if jahr >= 12:
            # Etwa 1/12 der Schüler pro Jahr
            neue_absolventen = schueler_total // 12
            absolventen_kumuliert += neue_absolventen

            deutschsprecher_neu = int(neue_absolventen * params.deutsch_niveau_b2)
            studenten_de_neu = int(neue_absolventen * params.weiterbildung_de)

            deutschsprecher_kumuliert += deutschsprecher_neu
            studenten_de_kumuliert += studenten_de_neu

        # Kosten
        kosten_invest = neue_schulen * invest_pro_schule
        kosten_laufend = schulen_aktiv * laufend_pro_schule

        kosten_jahr = kosten_invest + kosten_laufend
        kosten_kumuliert += kosten_jahr

        results.append(FranchiseResult(
            jahr=jahr,
            schulen_aktiv=schulen_aktiv,
            schueler_total=schueler_total,
            absolventen_kumuliert=absolventen_kumuliert,
            deutschsprecher_kumuliert=deutschsprecher_kumuliert,
            studenten_de_kumuliert=studenten_de_kumuliert,
            kosten_jahr=kosten_jahr,
            kosten_kumuliert=kosten_kumuliert
        ))

    return results


def calculate_soft_power_value(
    exchange_results: List[ExchangeDevelopResult],
    franchise_results: List[FranchiseResult],
    sp_params: SoftPowerParams,
    econ: EconomicParams
) -> List[SoftPowerResult]:
    """Berechnet den Soft Power Wert."""
    results = []
    npv_kumuliert = 0.0

    for jahr in range(len(exchange_results)):
        ex = exchange_results[jahr]
        fr = franchise_results[jahr]

        # Botschafter: Exchange + Franchise Deutschsprecher
        botschafter_aktiv = ex.botschafter_kumuliert + fr.deutschsprecher_kumuliert

        # Handelswert (mit Persistenz)
        # Annahme: Nur ein Teil der Botschafter sind wirtschaftlich aktiv
        aktive_botschafter = int(botschafter_aktiv * 0.5)  # 50% wirtschaftlich aktiv
        handelswert = aktive_botschafter * sp_params.handelswert_jaehrlich * sp_params.zeitliche_persistenz ** jahr

        # Diplomatischer Wert
        diplomatischer_wert = botschafter_aktiv * sp_params.diplomatischer_wert

        # Steuereinnahmen von Bleibern
        steuereinnahmen = (
            ex.bleiber_kumuliert *
            sp_params.durchschnittsgehalt_bleiber *
            sp_params.steuerquote
        )

        # Total Wert
        total_wert = handelswert + diplomatischer_wert + steuereinnahmen

        # NPV
        discount_factor = (1 + econ.discount_rate) ** (jahr + 1)
        npv_jahr = total_wert / discount_factor
        npv_kumuliert += npv_jahr

        results.append(SoftPowerResult(
            jahr=jahr + 1,
            botschafter_aktiv=botschafter_aktiv,
            handelswert=handelswert,
            diplomatischer_wert=diplomatischer_wert,
            steuereinnahmen_bleiber=steuereinnahmen,
            total_wert=total_wert,
            npv_kumuliert=npv_kumuliert
        ))

    return results


def run_simulation(
    exchange_params: ExchangeDevelopParams = None,
    franchise_params: FranchiseParams = None,
    soft_power_params: SoftPowerParams = None,
    econ_params: EconomicParams = None
) -> SimulationResult:
    """Führt die vollständige Simulation durch."""

    # Defaults
    if exchange_params is None:
        exchange_params = ExchangeDevelopParams()
    if franchise_params is None:
        franchise_params = FranchiseParams()
    if soft_power_params is None:
        soft_power_params = SoftPowerParams()
    if econ_params is None:
        econ_params = EconomicParams()

    # Simulationen
    exchange_results = simulate_exchange_develop(exchange_params, econ_params)
    franchise_results = simulate_franchise(franchise_params, econ_params)
    soft_power_results = calculate_soft_power_value(
        exchange_results, franchise_results, soft_power_params, econ_params
    )

    # Zusammenfassung
    final_exchange = exchange_results[-1]
    final_franchise = franchise_results[-1]
    final_soft_power = soft_power_results[-1]

    # Investitionen (erste 10 Jahre)
    total_investment = sum(
        ex.kosten_jahr + fr.kosten_jahr
        for ex, fr in zip(exchange_results[:10], franchise_results[:10])
    )

    # Laufende Kosten (Jahre 11-30)
    total_running = sum(
        ex.kosten_jahr + fr.kosten_jahr
        for ex, fr in zip(exchange_results[10:], franchise_results[10:])
    )

    # NPV Kosten
    npv_costs = 0.0
    for i, (ex, fr) in enumerate(zip(exchange_results, franchise_results)):
        discount = (1 + econ_params.discount_rate) ** (i + 1)
        npv_costs += (ex.kosten_jahr + fr.kosten_jahr) / discount

    # NPV Benefits
    npv_benefits = final_soft_power.npv_kumuliert

    # ROI
    if npv_costs > 0:
        benefit_cost_ratio = npv_benefits / npv_costs
        roi_percent = (npv_benefits - npv_costs) / npv_costs * 100
    else:
        benefit_cost_ratio = 0
        roi_percent = 0

    return SimulationResult(
        exchange_results=exchange_results,
        franchise_results=franchise_results,
        soft_power_results=soft_power_results,
        total_investment=total_investment,
        total_running_costs=total_running,
        npv_benefits=npv_benefits,
        benefit_cost_ratio=benefit_cost_ratio,
        roi_percent=roi_percent,
        total_stipendiaten=final_exchange.stipendiaten_kumuliert,
        total_franchise_schueler=final_franchise.absolventen_kumuliert,
        total_botschafter=final_soft_power.botschafter_aktiv,
        laender_erreicht=exchange_params.ziellaender
    )


def sensitivity_analysis(base_result: SimulationResult) -> Dict:
    """Führt Sensitivitätsanalyse durch."""
    scenarios = {}

    # Pessimistisch
    pess_exchange = ExchangeDevelopParams(
        stipendien_pro_jahr=3000,
        abschlussquote=0.80,
        bleiber_quote=0.10,
        rueckkehrer_wirkung=0.70
    )
    pess_franchise = FranchiseParams(
        neue_schulen_pro_jahr=5,
        max_schulen=50,
        deutsch_niveau_b2=0.40,
        weiterbildung_de=0.03
    )
    pess_soft = SoftPowerParams(
        handelswert_jaehrlich=25_000,
        diplomatischer_wert=5_000
    )
    pess_result = run_simulation(pess_exchange, pess_franchise, pess_soft)
    scenarios['pessimistisch'] = {
        'npv_benefits': pess_result.npv_benefits,
        'benefit_cost_ratio': pess_result.benefit_cost_ratio,
        'total_botschafter': pess_result.total_botschafter
    }

    # Optimistisch
    opt_exchange = ExchangeDevelopParams(
        stipendien_pro_jahr=8000,
        abschlussquote=0.95,
        bleiber_quote=0.20,
        rueckkehrer_wirkung=0.90
    )
    opt_franchise = FranchiseParams(
        neue_schulen_pro_jahr=15,
        max_schulen=150,
        deutsch_niveau_b2=0.75,
        weiterbildung_de=0.08
    )
    opt_soft = SoftPowerParams(
        handelswert_jaehrlich=75_000,
        diplomatischer_wert=15_000
    )
    opt_result = run_simulation(opt_exchange, opt_franchise, opt_soft)
    scenarios['optimistisch'] = {
        'npv_benefits': opt_result.npv_benefits,
        'benefit_cost_ratio': opt_result.benefit_cost_ratio,
        'total_botschafter': opt_result.total_botschafter
    }

    # Baseline
    scenarios['baseline'] = {
        'npv_benefits': base_result.npv_benefits,
        'benefit_cost_ratio': base_result.benefit_cost_ratio,
        'total_botschafter': base_result.total_botschafter
    }

    return scenarios


def format_currency(value: float) -> str:
    """Formatiert Währungswerte."""
    if abs(value) >= 1e9:
        return f"{value/1e9:.1f} Mrd. EUR"
    elif abs(value) >= 1e6:
        return f"{value/1e6:.1f} Mio. EUR"
    else:
        return f"{value:,.0f} EUR"


def print_summary(result: SimulationResult):
    """Gibt eine Zusammenfassung aus."""
    print("=" * 70)
    print("SOFT POWER EDUCATION MODEL - ERGEBNISSE")
    print("Exchange-Develop + Franchise")
    print("=" * 70)

    print("\n### REICHWEITE (30 Jahre)")
    print(f"  Stipendiaten gesamt:        {result.total_stipendiaten:,}")
    print(f"  Franchise-Absolventen:      {result.total_franchise_schueler:,}")
    print(f"  'Botschafter' aktiv:        {result.total_botschafter:,}")
    print(f"  Länder erreicht:            {result.laender_erreicht}")

    ex_final = result.exchange_results[-1]
    fr_final = result.franchise_results[-1]
    print("\n### EXCHANGE-DEVELOP")
    print(f"  Absolventen kumuliert:      {ex_final.absolventen_kumuliert:,}")
    print(f"  Bleiber in Deutschland:     {ex_final.bleiber_kumuliert:,}")
    print(f"  Rückkehrer-Botschafter:     {ex_final.botschafter_kumuliert:,}")
    print(f"  Kosten gesamt:              {format_currency(ex_final.kosten_kumuliert)}")

    print("\n### FRANCHISE-SCHULEN")
    print(f"  Schulen aktiv:              {fr_final.schulen_aktiv}")
    print(f"  Absolventen kumuliert:      {fr_final.absolventen_kumuliert:,}")
    print(f"  Deutschsprecher (B2+):      {fr_final.deutschsprecher_kumuliert:,}")
    print(f"  Studenten in DE:            {fr_final.studenten_de_kumuliert:,}")
    print(f"  Kosten gesamt:              {format_currency(fr_final.kosten_kumuliert)}")

    sp_final = result.soft_power_results[-1]
    print("\n### SOFT POWER WERT (Jahr 30)")
    print(f"  Handelswert/Jahr:           {format_currency(sp_final.handelswert)}")
    print(f"  Diplomatischer Wert/Jahr:   {format_currency(sp_final.diplomatischer_wert)}")
    print(f"  Steuereinnahmen Bleiber:    {format_currency(sp_final.steuereinnahmen_bleiber)}")
    print(f"  Total Wert/Jahr:            {format_currency(sp_final.total_wert)}")

    print("\n### KOSTEN-NUTZEN (NPV, 30 Jahre)")
    print(f"  Kosten (NPV):               {format_currency(result.total_investment + result.total_running_costs)}")
    print(f"  Nutzen (NPV):               {format_currency(result.npv_benefits)}")
    print(f"  Benefit/Cost Ratio:         {result.benefit_cost_ratio:.1f}x")
    print(f"  ROI:                        {result.roi_percent:.0f}%")

    print("\n### SENSITIVITÄTSANALYSE")
    scenarios = sensitivity_analysis(result)
    for name, data in scenarios.items():
        print(f"  {name.upper():15} B/C: {data['benefit_cost_ratio']:.1f}x  "
              f"Botschafter: {data['total_botschafter']:,}")

    print("\n" + "=" * 70)


def main():
    """Hauptfunktion."""
    print("Starte Soft Power Education Simulation...")
    print()

    result = run_simulation()
    print_summary(result)

    # 10-Jahres Snapshots
    print("\n### 10-JAHRES ENTWICKLUNG")
    print("-" * 70)
    print(f"{'Jahr':>5} {'Stipend.':>10} {'Schulen':>8} {'Botsch.':>10} "
          f"{'Kosten/J':>15} {'NPV Nutzen':>15}")
    print("-" * 70)

    for i in [0, 4, 9, 14, 19, 29]:  # Jahre 1, 5, 10, 15, 20, 30
        ex = result.exchange_results[i]
        fr = result.franchise_results[i]
        sp = result.soft_power_results[i]
        kosten_jahr = ex.kosten_jahr + fr.kosten_jahr
        print(f"{i+1:>5} {ex.stipendiaten_aktiv:>10,} {fr.schulen_aktiv:>8} "
              f"{sp.botschafter_aktiv:>10,} {format_currency(kosten_jahr):>15} "
              f"{format_currency(sp.npv_kumuliert):>15}")

    print("-" * 70)

    # Vergleich mit bestehenden Programmen
    print("\n### VERGLEICH MIT BESTEHENDEN PROGRAMMEN")
    print("-" * 70)
    print(f"{'Programm':25} {'Budget':>15} {'Reichweite':>15}")
    print("-" * 70)
    print(f"{'DAAD (2024)':25} {'753 Mio. EUR':>15} {'141.000/Jahr':>15}")
    print(f"{'Goethe-Institut':25} {'350 Mio. EUR':>15} {'158 Institute':>15}")
    print(f"{'Auslandsschulen (ZfA)':25} {'~200 Mio. EUR':>15} {'85.000 Schüler':>15}")
    print(f"{'Soft Power Education':25} {format_currency(result.exchange_results[9].kosten_jahr + result.franchise_results[9].kosten_jahr):>15} "
          f"{result.exchange_results[9].stipendiaten_aktiv + result.franchise_results[9].schueler_total:>12,}/Jahr")
    print("-" * 70)

    return result


if __name__ == "__main__":
    main()
