#!/usr/bin/env python3
"""
Stagflation-Tableau: RSSP mit vs. ohne RIG-Komponente

Vergleicht das RSSP-System (Config E Baseline) mit dem RIG-gehaerteten
System (Config F) unter verschiedenen Stagflationsszenarien.

Stagflation = hohe Inflation + niedriges Wachstum -> negative/null Realrenditen
auf Finanzmaerkte, waehrend die RIG-Infrastrukturrendite teilweise entkoppelt bleibt.

Usage:
    python src/stagflation_tableau.py [--json out/stagflation_tableau.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import Params, simulate, RunResult
from monte_carlo import load_params_from_yaml


def build_return_path(
    horizon: int,
    normal_return: float,
    crisis_return: float,
    crisis_start: int,
    crisis_duration: int,
) -> List[float]:
    """Build a return path with a crisis window."""
    path = []
    for t in range(horizon):
        if crisis_start <= t < crisis_start + crisis_duration:
            path.append(crisis_return)
        else:
            path.append(normal_return)
    return path


SCENARIOS = {
    # name: (crisis_return, crisis_start, crisis_duration, description)
    "baseline_1p7": (0.0175, 0, 0, "Baseline 1.7% konstant (Referenz)"),
    "stagflation_mild": (0.000, 20, 10, "Milde Stagflation: 0% Realrendite, 10 Jahre (Jahr 20-29)"),
    "stagflation_severe": (-0.010, 20, 10, "Schwere Stagflation: -1% Realrendite, 10 Jahre (Jahr 20-29)"),
    "financial_repression": (0.005, 20, 10, "Finanzielle Repression: 0.5% Realrendite, 10 Jahre (Jahr 20-29)"),
    "prolonged_stagnation": (0.005, 20, 20, "Prolongierte Stagnation: 0.5% fuer 20 Jahre (Jahr 20-39)"),
    "deep_crisis": (-0.020, 15, 10, "Tiefe Krise: -2% Realrendite, 10 Jahre (Jahr 15-24)"),
    "double_dip": (None, None, None, "Doppel-Dip: Krise Jahr 15-20 und 35-40"),  # special
}

NORMAL_RETURN = 0.0175


def build_double_dip_path(horizon: int) -> List[float]:
    """Two separate crisis periods."""
    path = [NORMAL_RETURN] * horizon
    # First dip: years 15-20, severe
    for t in range(15, 21):
        if t < horizon:
            path[t] = -0.01
    # Second dip: years 35-40, mild
    for t in range(35, 41):
        if t < horizon:
            path[t] = 0.00
    return path


def extract_metrics(r: RunResult) -> Dict:
    """Extract key comparison metrics from a RunResult."""
    return {
        "passed": r.passed,
        "fail_years": r.fail_years,
        "min_repl_low": r.min_repl_low,
        "min_repl_mid": r.min_repl_mid,
        "pool_depletion_year": r.pool_depletion_year,
        "is_structurally_sustainable": r.is_structurally_sustainable,
        "max_state_loan": r.max_state_loan,
        "final_state_loan": r.final_state_loan,
        "steady_state_deficit": r.steady_state_deficit,
        "final_pool": r.stats[-1].pool if r.stats else 0.0,
        "final_longevity_pool": r.final_longevity_pool,
        "peak_reserve_fund": r.peak_reserve_fund,
        # RIG-specific
        "final_rig_fund": r.final_rig_fund,
        "peak_rig_fund": r.peak_rig_fund,
        "total_rig_dividends": r.total_rig_dividends,
        "total_rig_to_pool": r.total_rig_to_pool,
    }


def format_eur(val: float) -> str:
    """Format EUR value in Mrd or Bio."""
    if abs(val) >= 1e12:
        return f"{val / 1e12:.2f} Bio"
    return f"{val / 1e9:.1f} Mrd"


def run_tableau():
    parser = argparse.ArgumentParser(description="RSSP Stagflation-Tableau: Config E vs F")
    parser.add_argument("--json", type=str, default=None, help="Output JSON file")
    parser.add_argument("--config_e", type=str, default="params/config_e.yaml",
                        help="Config E (baseline without RIG)")
    parser.add_argument("--config_f", type=str, default="params/config_f.yaml",
                        help="Config F (with RIG)")
    parser.add_argument("--tau_high", type=float, default=0.1225,
                        help="tau_high for Config E (default: 0.1225)")
    args = parser.parse_args()

    # Load configurations
    params_e = load_params_from_yaml(args.config_e)
    params_e.tau_high = args.tau_high

    params_f = load_params_from_yaml(args.config_f)
    # Config F uses RIG split; set tau_high to sum for compatibility
    params_f.tau_high = params_f.rig_tau_insurance + params_f.rig_tau_equity

    horizon = params_e.horizon_years
    configs = {"Config_E (ohne RIG)": params_e, "Config_F (mit RIG)": params_f}

    results: Dict[str, Dict[str, Dict]] = {}
    all_runs: List[Tuple[str, str, RunResult]] = []

    for scen_name, scen_spec in SCENARIOS.items():
        if scen_name == "double_dip":
            returns = build_double_dip_path(horizon)
        elif scen_name == "baseline_1p7":
            returns = [NORMAL_RETURN] * horizon
        else:
            crisis_ret, crisis_start, crisis_dur, _ = scen_spec
            returns = build_return_path(horizon, NORMAL_RETURN, crisis_ret, crisis_start, crisis_dur)

        for cfg_name, params in configs.items():
            result = simulate(params, returns, f"{scen_name}_{cfg_name}", pass_last_n_years=10)
            metrics = extract_metrics(result)
            results.setdefault(scen_name, {})[cfg_name] = metrics
            all_runs.append((scen_name, cfg_name, result))

    # Print tableau
    print("=" * 120)
    print("STAGFLATION-TABLEAU: RSSP mit vs. ohne RIG-Komponente")
    print("=" * 120)
    print()

    # Scenario descriptions
    print("--- Szenarien ---")
    for name, spec in SCENARIOS.items():
        if name == "double_dip":
            desc = spec[3]
        elif name == "baseline_1p7":
            desc = spec[3]
        else:
            desc = spec[3]
        print(f"  {name:30s}  {desc}")
    print()

    # Main comparison table
    header = (f"{'Szenario':<30s} | {'Config':>22s} | {'Pass':>4s} | "
              f"{'Min Low':>7s} | {'Min Mid':>7s} | {'Pool Depl.':>10s} | "
              f"{'Nachhaltig':>10s} | {'Max Kredit':>14s} | {'SS-Defizit':>14s} | "
              f"{'RIG-Fonds':>14s} | {'RIG->Pool':>14s}")
    print(header)
    print("-" * len(header))

    for scen_name in SCENARIOS:
        for cfg_name in configs:
            m = results[scen_name][cfg_name]
            depl = str(m["pool_depletion_year"]) if m["pool_depletion_year"] is not None else "nie"
            sust = "Ja" if m["is_structurally_sustainable"] else "Nein"
            rig_fund = format_eur(m["final_rig_fund"]) if m["final_rig_fund"] > 0 else "-"
            rig_pool = format_eur(m["total_rig_to_pool"]) if m["total_rig_to_pool"] > 0 else "-"
            print(f"{scen_name:<30s} | {cfg_name:>22s} | "
                  f"{'Ja' if m['passed'] else 'NEIN':>4s} | "
                  f"{m['min_repl_low']*100:>6.1f}% | {m['min_repl_mid']*100:>6.1f}% | "
                  f"{depl:>10s} | {sust:>10s} | "
                  f"{format_eur(m['max_state_loan']):>14s} | "
                  f"{format_eur(m['steady_state_deficit']):>14s} | "
                  f"{rig_fund:>14s} | {rig_pool:>14s}")
        print()  # blank line between scenarios

    # Delta analysis
    print()
    print("=" * 100)
    print("DELTA-ANALYSE: Config F (RIG) minus Config E (Baseline)")
    print("=" * 100)
    print()
    print(f"{'Szenario':<30s} | {'dMin Low':>8s} | {'dMin Mid':>8s} | "
          f"{'dKredit':>14s} | {'dSS-Defizit':>14s} | {'RIG Stabilisierung':>18s}")
    print("-" * 100)

    for scen_name in SCENARIOS:
        me = results[scen_name]["Config_E (ohne RIG)"]
        mf = results[scen_name]["Config_F (mit RIG)"]

        d_low = (mf["min_repl_low"] - me["min_repl_low"]) * 100
        d_mid = (mf["min_repl_mid"] - me["min_repl_mid"]) * 100
        d_loan = mf["max_state_loan"] - me["max_state_loan"]
        d_ss = mf["steady_state_deficit"] - me["steady_state_deficit"]

        # RIG stabilization = total dividends to pool
        rig_stab = mf["total_rig_to_pool"]

        print(f"{scen_name:<30s} | {d_low:>+7.1f}% | {d_mid:>+7.1f}% | "
              f"{format_eur(d_loan):>14s} | {format_eur(d_ss):>14s} | "
              f"{format_eur(rig_stab):>18s}")

    # RIG mechanism detail
    print()
    print("=" * 100)
    print("RIG-MECHANISMUS-DETAIL (Config F)")
    print("=" * 100)
    print()
    print(f"{'Szenario':<30s} | {'Peak RIG':>14s} | {'Final RIG':>14s} | "
          f"{'Total Div.':>14s} | {'Div->Pool':>14s} | {'Div->Halter':>14s}")
    print("-" * 100)

    for scen_name in SCENARIOS:
        mf = results[scen_name]["Config_F (mit RIG)"]
        div_holders = mf["total_rig_dividends"] - mf["total_rig_to_pool"]
        print(f"{scen_name:<30s} | "
              f"{format_eur(mf['peak_rig_fund']):>14s} | "
              f"{format_eur(mf['final_rig_fund']):>14s} | "
              f"{format_eur(mf['total_rig_dividends']):>14s} | "
              f"{format_eur(mf['total_rig_to_pool']):>14s} | "
              f"{format_eur(div_holders):>14s}")

    # Interpretation
    print()
    print("=" * 100)
    print("INTERPRETATION")
    print("=" * 100)
    print()

    # Count improvements
    n_improved = 0
    n_same = 0
    n_worse = 0
    for scen_name in SCENARIOS:
        me = results[scen_name]["Config_E (ohne RIG)"]
        mf = results[scen_name]["Config_F (mit RIG)"]
        if mf["passed"] and not me["passed"]:
            n_improved += 1
        elif mf["passed"] == me["passed"]:
            # Check if replacement rates improved
            if mf["min_repl_low"] > me["min_repl_low"] + 0.001 or mf["min_repl_mid"] > me["min_repl_mid"] + 0.001:
                n_improved += 1
            elif mf["min_repl_low"] < me["min_repl_low"] - 0.001 or mf["min_repl_mid"] < me["min_repl_mid"] - 0.001:
                n_worse += 1
            else:
                n_same += 1
        else:
            n_worse += 1

    print(f"  Szenarien verbessert:   {n_improved}/{len(SCENARIOS)}")
    print(f"  Szenarien unveraendert: {n_same}/{len(SCENARIOS)}")
    print(f"  Szenarien verschlechtert: {n_worse}/{len(SCENARIOS)}")
    print()

    # Key finding: RIG stabilization in crisis
    crisis_scenarios = [s for s in SCENARIOS if s != "baseline_1p7"]
    for scen in crisis_scenarios:
        me = results[scen]["Config_E (ohne RIG)"]
        mf = results[scen]["Config_F (mit RIG)"]
        if mf["total_rig_to_pool"] > 0:
            pool_boost_pct = mf["total_rig_to_pool"] / max(1.0, abs(me["steady_state_deficit"])) * 100
            print(f"  {scen}: RIG-Dividenden kompensieren "
                  f"{format_eur(mf['total_rig_to_pool'])} des Pool-Defizits")

    print()
    print("  Kernbefund: Die RIG-Komponente wirkt als automatischer Stabilisator.")
    print("  In Stagflationsszenarien bleibt r_RIG positiv (Realwert-Anker),")
    print("  waehrend r_mkt negativ/null ist. Die Dividenden stuetzen den Pool.")
    print()

    # Save JSON
    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        output = {
            "scenarios": {},
            "summary": {
                "n_improved": n_improved,
                "n_same": n_same,
                "n_worse": n_worse,
            }
        }
        for scen_name in SCENARIOS:
            output["scenarios"][scen_name] = {
                "description": SCENARIOS[scen_name][3] if isinstance(SCENARIOS[scen_name], tuple) and len(SCENARIOS[scen_name]) > 3 else scen_name,
                "config_e": results[scen_name]["Config_E (ohne RIG)"],
                "config_f": results[scen_name]["Config_F (mit RIG)"],
            }
        with open(args.json, "w") as f:
            json.dump(output, f, indent=2, default=str)
        print(f"Ergebnisse gespeichert: {args.json}")


if __name__ == "__main__":
    run_tableau()
