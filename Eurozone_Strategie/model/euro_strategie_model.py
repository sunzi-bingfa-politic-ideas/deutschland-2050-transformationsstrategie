#!/usr/bin/env python3
"""
Euro-Strategie Szenario-Modell v2.0
====================================

Quantifiziert Deutschlands Vermoegensposition unter verschiedenen
Euro-/Dollar-Szenarien mit und ohne RSSP-Kapitalstock.

Neu in v2.0:
- RSSP-Parameter aus dem Rentenreform-Modell (7,5 Bio. Kapitalstock)
- RIG-Fonds (1,95 Bio.) als separater Sachwert-Hedge
- GSP-Kapitalstock (1,15 Bio.) integriert
- Dollar-Dimension (USD-Exposure, Sanctions-Risiko)
- Target2-Abbaupfad
- Monte-Carlo ueber Waehrungsszenarien
- Tornado-Sensitivitaet

Basiert auf:
- Bundesbank Target2-Statistiken (1.100 Mrd. EUR, 2025)
- RSSP-Modell Config F (Rentenreform/)
- GSP-Modell v2.0 (Gesundheitsreform/)
- Historische Waehrungskrisen-Daten (ERM 1992, Argentinien 2001, Griechenland 2012)

Rigor: Medium — Szenarien sind stilisiert; Groessenordnungen empirisch fundiert.
"""

from dataclasses import dataclass, field
from typing import Dict, List
from copy import deepcopy
import json
import os
import random
import math


# ===========================================================================
# DATENSTRUKTUREN
# ===========================================================================

@dataclass
class GermanyPosition:
    """Deutsche Vermoegensposition (in Mrd. EUR)."""
    # Aktiva
    target2_claims: float       # Target2-Forderungen gegen EZB
    rssp_equity: float          # RSSP: Globale Aktien (MSCI World)
    rssp_bonds: float           # RSSP: EUR-Staatsanleihen
    rssp_gold: float            # RSSP: Gold (physisch)
    rig_fund: float             # RIG: Robotik-Infrastruktur (reale Assets)
    gsp_capital: float          # GSP: Gesundheitssparkonto-Kapitalstock
    other_assets: float         # Sonstige Reserven (Bundesbank, Devisenreserven)

    # Passiva
    government_debt: float      # Staatsschulden
    implicit_guarantees: float  # EU/EZB-Garantien, ESM-Verpflichtungen

    @property
    def total_assets(self) -> float:
        return (self.target2_claims + self.rssp_equity + self.rssp_bonds +
                self.rssp_gold + self.rig_fund + self.gsp_capital + self.other_assets)

    @property
    def total_liabilities(self) -> float:
        return self.government_debt + self.implicit_guarantees

    @property
    def net_position(self) -> float:
        return self.total_assets - self.total_liabilities


@dataclass
class CurrencyScenario:
    """Ein Waehrungs-/Geopolitik-Szenario."""
    name: str
    probability: float

    # Waehrungseffekte
    euro_change: float          # 1.0 = stabil; 0.7 = -30% Abwertung
    dollar_change: float        # 1.0 = stabil; 0.8 = -20%

    # Asset-Effekte (Multiplikatoren auf EUR-Wert)
    target2_recovery: float     # Anteil der Target2-Forderungen erhalten
    equity_mult: float          # Globale Aktien (in EUR)
    bond_mult: float            # EUR-Anleihen (Nominalwert)
    gold_mult: float            # Gold (in EUR)
    rig_mult: float             # RIG/Infrastruktur (in EUR)
    gsp_mult: float             # GSP (konservativ angelegt)
    debt_real_value: float      # Realwert der Schulden (1.0 = voll)


# ===========================================================================
# POSITIONEN
# ===========================================================================

# Status Quo Deutschland 2025
STATUS_QUO = GermanyPosition(
    target2_claims=1100,
    rssp_equity=0,
    rssp_bonds=0,
    rssp_gold=0,
    rig_fund=0,
    gsp_capital=0,
    other_assets=500,
    government_debt=2400,
    implicit_guarantees=500,
)

# Deutschland 2050 mit RSSP/GSP (basierend auf Modell-Output)
# RSSP Kapitalstock ~7.500 Mrd., Allokation: 45% Aktien, 25% Anleihen, 10% Gold, 20% RIG
# GSP Kapitalstock ~1.150 Mrd. (konservativ angelegt)
# RIG separat: ~1.950 Mrd.
# Target2 reduziert auf ~300 Mrd.
# Schulden gestiegen auf ~5.500 Mrd. (Uebergangsfinanzierung)
WITH_RSSP = GermanyPosition(
    target2_claims=300,
    rssp_equity=3375,       # 45% von 7.500
    rssp_bonds=1875,        # 25% von 7.500
    rssp_gold=750,          # 10% von 7.500
    rig_fund=1950,          # RIG-Fonds (separat, aus High-Earner-Beitraegen)
    gsp_capital=1150,       # GSP-Kapitalstock
    other_assets=500,
    government_debt=5500,
    implicit_guarantees=500,
)


# ===========================================================================
# SZENARIEN (aktualisiert mit Dollar-Dimension)
# ===========================================================================

SCENARIOS = [
    CurrencyScenario(
        name="A: Euro + Dollar stabil",
        probability=0.20,
        euro_change=1.0, dollar_change=1.0,
        target2_recovery=1.0,
        equity_mult=1.0, bond_mult=1.0, gold_mult=1.0,
        rig_mult=1.0, gsp_mult=1.0, debt_real_value=1.0,
    ),
    CurrencyScenario(
        name="B: Fiskalunion (Karolinger-Eurobonds)",
        probability=0.20,
        euro_change=0.95, dollar_change=1.0,
        target2_recovery=0.8,       # Teilvergemeinschaftung
        equity_mult=1.05, bond_mult=0.98, gold_mult=1.05,
        rig_mult=1.10, gsp_mult=1.02, debt_real_value=0.95,
    ),
    CurrencyScenario(
        name="C: Euro schwach (-20%)",
        probability=0.15,
        euro_change=0.80, dollar_change=1.0,
        target2_recovery=0.7,
        equity_mult=1.25, bond_mult=1.0, gold_mult=1.30,
        rig_mult=1.10, gsp_mult=1.05, debt_real_value=0.85,
    ),
    CurrencyScenario(
        name="D: Kontrollierter Italexit",
        probability=0.15,
        euro_change=0.90, dollar_change=1.0,
        target2_recovery=0.5,       # IT-Anteil groesstenteils verloren
        equity_mult=1.15, bond_mult=0.95, gold_mult=1.20,
        rig_mult=1.05, gsp_mult=1.0, debt_real_value=0.90,
    ),
    CurrencyScenario(
        name="E: Euro-Zerfall",
        probability=0.10,
        euro_change=0.50, dollar_change=1.0,
        target2_recovery=0.1,       # Quasi-Totalverlust
        equity_mult=2.00, bond_mult=0.60, gold_mult=2.20,
        rig_mult=1.30, gsp_mult=0.80, debt_real_value=0.55,
    ),
    CurrencyScenario(
        name="F: Dollar-Krise (-30%)",
        probability=0.10,
        euro_change=1.0, dollar_change=0.70,
        target2_recovery=1.0,
        equity_mult=0.85, bond_mult=1.05, gold_mult=1.40,
        rig_mult=1.05, gsp_mult=1.02, debt_real_value=1.0,
    ),
    CurrencyScenario(
        name="G: Stagflation (beide schwach)",
        probability=0.05,
        euro_change=0.85, dollar_change=0.85,
        target2_recovery=0.8,
        equity_mult=0.95, bond_mult=0.90, gold_mult=1.50,
        rig_mult=1.15, gsp_mult=0.95, debt_real_value=0.80,
    ),
    CurrencyScenario(
        name="H: US-Sanktionen gegen EU",
        probability=0.05,
        euro_change=0.90, dollar_change=1.05,
        target2_recovery=0.9,
        equity_mult=0.90, bond_mult=0.95, gold_mult=1.30,
        rig_mult=1.00, gsp_mult=0.98, debt_real_value=0.92,
    ),
]


# ===========================================================================
# KERNMODELL
# ===========================================================================

def calculate_outcome(position: GermanyPosition, scenario: CurrencyScenario) -> Dict:
    """Berechnet das Ergebnis einer Position unter einem Szenario."""

    # Aktiva nach Szenario
    t2 = position.target2_claims * scenario.target2_recovery
    eq = position.rssp_equity * scenario.equity_mult
    bo = position.rssp_bonds * scenario.bond_mult
    go = position.rssp_gold * scenario.gold_mult
    ri = position.rig_fund * scenario.rig_mult
    gs = position.gsp_capital * scenario.gsp_mult
    ot = position.other_assets

    total_assets_after = t2 + eq + bo + go + ri + gs + ot

    # Passiva nach Szenario
    debt_after = position.government_debt * scenario.debt_real_value
    guar_after = position.implicit_guarantees * scenario.euro_change

    total_liab_after = debt_after + guar_after

    net_after = total_assets_after - total_liab_after
    net_change = net_after - position.net_position

    return {
        "scenario": scenario.name,
        "probability": scenario.probability,
        "assets_before": round(position.total_assets, 1),
        "assets_after": round(total_assets_after, 1),
        "liabilities_before": round(position.total_liabilities, 1),
        "liabilities_after": round(total_liab_after, 1),
        "net_before": round(position.net_position, 1),
        "net_after": round(net_after, 1),
        "net_change": round(net_change, 1),
        # Detail
        "target2_loss": round(position.target2_claims - t2, 1),
        "equity_change": round(eq - position.rssp_equity, 1),
        "gold_change": round(go - position.rssp_gold, 1),
        "rig_change": round(ri - position.rig_fund, 1),
        "debt_relief": round(position.government_debt - debt_after, 1),
    }


def run_all_scenarios():
    """Berechnet alle Szenarien fuer beide Positionen."""

    results = {"status_quo": [], "with_rssp": [], "comparison": []}

    for s in SCENARIOS:
        sq = calculate_outcome(STATUS_QUO, s)
        rs = calculate_outcome(WITH_RSSP, s)
        results["status_quo"].append(sq)
        results["with_rssp"].append(rs)
        results["comparison"].append({
            "scenario": s.name,
            "probability": s.probability,
            "sq_net_change": sq["net_change"],
            "rssp_net_change": rs["net_change"],
            "rssp_advantage": rs["net_change"] - sq["net_change"],
        })

    # Erwartungswerte
    ev_sq = sum(r["net_change"] * r["probability"] for r in results["status_quo"])
    ev_rs = sum(r["net_change"] * r["probability"] for r in results["with_rssp"])
    results["expected_values"] = {
        "status_quo": round(ev_sq, 1),
        "with_rssp": round(ev_rs, 1),
        "advantage": round(ev_rs - ev_sq, 1),
    }

    return results


# ===========================================================================
# SENSITIVITAET
# ===========================================================================

def tornado_analysis() -> List[Dict]:
    """Tornado: Einfluss einzelner RSSP-Parameter auf den Erwartungswert."""

    base_ev = run_all_scenarios()["expected_values"]["with_rssp"]
    params = [
        ("RSSP Aktien", "rssp_equity", 2000, 3375, 5000),
        ("RSSP Anleihen", "rssp_bonds", 1000, 1875, 3000),
        ("RSSP Gold", "rssp_gold", 300, 750, 1500),
        ("RIG-Fonds", "rig_fund", 1000, 1950, 3000),
        ("GSP-Kapital", "gsp_capital", 500, 1150, 2000),
        ("Target2 Rest", "target2_claims", 100, 300, 800),
        ("Staatsschulden", "government_debt", 4000, 5500, 7500),
    ]

    results = []
    for name, field_name, low, base, high in params:
        for val, label in [(low, "low"), (high, "high")]:
            p = deepcopy(WITH_RSSP)
            setattr(p, field_name, val)
            # Recalculate with modified position
            ev = sum(
                calculate_outcome(p, s)["net_change"] * s.probability
                for s in SCENARIOS
            )
            if label == "low":
                ev_low = ev
            else:
                ev_high = ev

        results.append({
            "parameter": name,
            "low": low, "base": base, "high": high,
            "ev_low": round(ev_low, 1),
            "ev_base": round(base_ev, 1),
            "ev_high": round(ev_high, 1),
            "range": round(abs(ev_high - ev_low), 1),
        })

    results.sort(key=lambda x: x["range"], reverse=True)
    return results


def monte_carlo(n_runs: int = 2000, seed: int = 42) -> Dict:
    """Monte-Carlo: Variiere Szenario-Wahrscheinlichkeiten und Asset-Allokation."""

    random.seed(seed)
    sq_changes = []
    rssp_changes = []

    for _ in range(n_runs):
        # Variiere Position
        p = deepcopy(WITH_RSSP)
        p.rssp_equity = WITH_RSSP.rssp_equity * random.uniform(0.6, 1.4)
        p.rssp_gold = WITH_RSSP.rssp_gold * random.uniform(0.5, 2.0)
        p.rig_fund = WITH_RSSP.rig_fund * random.uniform(0.7, 1.3)
        p.government_debt = WITH_RSSP.government_debt * random.uniform(0.8, 1.3)

        # Variiere ein zufaelliges Szenario (gewichtet nach Wahrscheinlichkeit)
        r = random.random()
        cumulative = 0
        chosen = SCENARIOS[0]
        for s in SCENARIOS:
            cumulative += s.probability
            if r <= cumulative:
                chosen = s
                break

        # Variiere Szenario-Multiplikatoren leicht
        sc = deepcopy(chosen)
        sc.equity_mult *= random.uniform(0.85, 1.15)
        sc.gold_mult *= random.uniform(0.80, 1.20)
        sc.rig_mult *= random.uniform(0.90, 1.10)
        sc.debt_real_value *= random.uniform(0.90, 1.10)
        sc.target2_recovery *= random.uniform(0.80, 1.20)
        sc.target2_recovery = min(sc.target2_recovery, 1.0)

        sq_out = calculate_outcome(STATUS_QUO, sc)
        rs_out = calculate_outcome(p, sc)

        sq_changes.append(sq_out["net_change"])
        rssp_changes.append(rs_out["net_change"])

    sq_changes.sort()
    rssp_changes.sort()

    def pct(data, p):
        k = (len(data) - 1) * p / 100
        f, c = math.floor(k), math.ceil(k)
        if f == c:
            return data[int(k)]
        return data[f] * (c - k) + data[c] * (k - f)

    return {
        "n_runs": n_runs,
        "status_quo": {
            "p5": round(pct(sq_changes, 5), 1),
            "median": round(pct(sq_changes, 50), 1),
            "p95": round(pct(sq_changes, 95), 1),
            "prob_positive": round(sum(1 for x in sq_changes if x > 0) / n_runs * 100, 1),
        },
        "with_rssp": {
            "p5": round(pct(rssp_changes, 5), 1),
            "median": round(pct(rssp_changes, 50), 1),
            "p95": round(pct(rssp_changes, 95), 1),
            "prob_positive": round(sum(1 for x in rssp_changes if x > 0) / n_runs * 100, 1),
        },
        "rssp_dominates": round(
            sum(1 for sq, rs in zip(sq_changes, rssp_changes) if rs > sq) / n_runs * 100, 1
        ),
    }


# ===========================================================================
# AUSGABE
# ===========================================================================

def print_results():
    """Formatierte Ausgabe."""

    print("=" * 100)
    print("EURO-STRATEGIE v2.0 — RSSP-INTEGRIERTE SZENARIO-ANALYSE")
    print("=" * 100)

    # Positionen
    print("\n--- AUSGANGSPOSITIONEN ---\n")
    for label, pos in [("STATUS QUO (2025)", STATUS_QUO), ("MIT RSSP (2050)", WITH_RSSP)]:
        print(f"{label}:")
        print(f"  Target2:        {pos.target2_claims:>8,.0f} Mrd. EUR")
        print(f"  RSSP Aktien:    {pos.rssp_equity:>8,.0f} Mrd. EUR")
        print(f"  RSSP Anleihen:  {pos.rssp_bonds:>8,.0f} Mrd. EUR")
        print(f"  RSSP Gold:      {pos.rssp_gold:>8,.0f} Mrd. EUR")
        print(f"  RIG-Fonds:      {pos.rig_fund:>8,.0f} Mrd. EUR")
        print(f"  GSP-Kapital:    {pos.gsp_capital:>8,.0f} Mrd. EUR")
        print(f"  Sonstige:       {pos.other_assets:>8,.0f} Mrd. EUR")
        print(f"  ─────────────────────────────")
        print(f"  AKTIVA:         {pos.total_assets:>8,.0f} Mrd. EUR")
        print(f"  Schulden:       {pos.government_debt:>8,.0f} Mrd. EUR")
        print(f"  Garantien:      {pos.implicit_guarantees:>8,.0f} Mrd. EUR")
        print(f"  ─────────────────────────────")
        print(f"  NETTO:          {pos.net_position:>+8,.0f} Mrd. EUR\n")

    # Szenarien
    results = run_all_scenarios()

    print("--- SZENARIO-ERGEBNISSE (Netto-Veraenderung in Mrd. EUR) ---\n")
    print(f"  {'Szenario':<40} {'P':>5} {'Status Quo':>12} {'Mit RSSP':>12} {'Vorteil':>12}")
    print("  " + "-" * 85)

    for c in results["comparison"]:
        print(f"  {c['scenario']:<40} {c['probability']*100:>4.0f}% "
              f"{c['sq_net_change']:>+10,.0f}  {c['rssp_net_change']:>+10,.0f}  "
              f"{c['rssp_advantage']:>+10,.0f}")

    print("  " + "-" * 85)
    ev = results["expected_values"]
    print(f"  {'ERWARTUNGSWERT':<40} {'100':>4}% "
          f"{ev['status_quo']:>+10,.0f}  {ev['with_rssp']:>+10,.0f}  "
          f"{ev['advantage']:>+10,.0f}")

    # Dominanz
    all_better = all(c["rssp_advantage"] >= 0 for c in results["comparison"])
    print(f"\n  RSSP dominiert in JEDEM Szenario: {'JA' if all_better else 'NEIN'}")

    # Tornado
    print("\n\n--- TORNADO-ANALYSE: WELCHE RSSP-PARAMETER TREIBEN DEN ERWARTUNGSWERT? ---\n")
    tornado = tornado_analysis()
    print(f"  {'Parameter':<20} {'Low':>8} {'Base':>8} {'High':>8}  "
          f"{'EV Low':>10} {'EV Base':>10} {'EV High':>10} {'Range':>8}")
    print("  " + "-" * 88)
    for t in tornado:
        print(f"  {t['parameter']:<20} {t['low']:>7,.0f} {t['base']:>7,.0f} {t['high']:>7,.0f}  "
              f"{t['ev_low']:>+9,.0f} {t['ev_base']:>+9,.0f} {t['ev_high']:>+9,.0f} "
              f"{t['range']:>7,.0f}")

    # Monte Carlo
    print("\n\n--- MONTE-CARLO (2.000 LAEUFE) ---\n")
    mc = monte_carlo(2000)

    print(f"  Status Quo:")
    print(f"    P5:     {mc['status_quo']['p5']:>+8,.0f} Mrd. EUR")
    print(f"    Median: {mc['status_quo']['median']:>+8,.0f} Mrd. EUR")
    print(f"    P95:    {mc['status_quo']['p95']:>+8,.0f} Mrd. EUR")
    print(f"    P(>0):  {mc['status_quo']['prob_positive']:>7.1f}%")

    print(f"\n  Mit RSSP:")
    print(f"    P5:     {mc['with_rssp']['p5']:>+8,.0f} Mrd. EUR")
    print(f"    Median: {mc['with_rssp']['median']:>+8,.0f} Mrd. EUR")
    print(f"    P95:    {mc['with_rssp']['p95']:>+8,.0f} Mrd. EUR")
    print(f"    P(>0):  {mc['with_rssp']['prob_positive']:>7.1f}%")

    print(f"\n  RSSP besser als SQ: {mc['rssp_dominates']:.1f}% der Laeufe")


def main():
    print_results()

    # Export
    results = run_all_scenarios()
    output = {
        "positions": {
            "status_quo": {
                "total_assets": STATUS_QUO.total_assets,
                "total_liabilities": STATUS_QUO.total_liabilities,
                "net": STATUS_QUO.net_position,
            },
            "with_rssp": {
                "total_assets": WITH_RSSP.total_assets,
                "total_liabilities": WITH_RSSP.total_liabilities,
                "net": WITH_RSSP.net_position,
            },
        },
        "scenarios": results["comparison"],
        "expected_values": results["expected_values"],
        "tornado": tornado_analysis(),
        "monte_carlo": monte_carlo(2000),
    }

    out_path = os.path.join(os.path.dirname(__file__), "euro_strategie_results.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n\nExportiert nach: {out_path}")


if __name__ == "__main__":
    main()
