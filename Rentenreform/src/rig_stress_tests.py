#!/usr/bin/env python3
"""
Adversariale RIG-Stresstests

Testet das RIG-gehaertete System gegen 5 spezifische Angriffe, die Kritiker
vorbringen koennten. Fuer jeden Angriff wird verglichen:
  - Config F (RIG, optimale Kalibrierung) unter dem Angriff
  - Config E (ohne RIG) unter aequivalenten Bedingungen
  - Wie weit degradiert das System?

Usage:
    python src/rig_stress_tests.py [--n_paths 2000] [--json out/rig_stress_tests.json]
"""
from __future__ import annotations

import argparse
import copy
import json
import multiprocessing as mp
import os
import sys
import time
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import Params, simulate
from monte_carlo import (
    load_params_from_yaml,
    generate_return_paths,
    MCParams,
    _params_to_dict,
    _dict_to_params,
)


# Final calibrated parameters (Config F, Modus A)
# Validated by 2D sweep + income profile analysis + retirement age sensitivity
OPTIMAL_INSURANCE = 0.085
OPTIMAL_EQUITY = 0.0375
OPTIMAL_DIV_TO_POOL = 0.80
OPTIMAL_BASE_RETURN = 0.03  # 3% real (market-validated 2026)
OPTIMAL_ATTRITION = 0.002   # with RIG incentive
BASELINE_ATTRITION = 0.005  # without RIG
TAU_HIGH = 0.1225


def _run_path(args: Tuple) -> dict:
    params_dict, returns_list, _ = args
    p = _dict_to_params(params_dict)
    r = simulate(p, returns_list, "mc")
    return {
        "passed": r.passed,
        "min_repl_low": r.min_repl_low,
        "min_repl_mid": r.min_repl_mid,
        "pool_depletion_year": r.pool_depletion_year,
        "max_state_loan": r.max_state_loan,
        "is_structurally_sustainable": r.is_structurally_sustainable,
        "final_rig_fund": r.final_rig_fund,
        "total_rig_to_pool": r.total_rig_to_pool,
    }


def run_mc(params: Params, paths: np.ndarray, n_workers: int) -> dict:
    params_dict = _params_to_dict(params)
    n = paths.shape[0]
    work = [(params_dict, paths[i].tolist(), i) for i in range(n)]
    chunksize = max(1, n // (n_workers * 4))
    with mp.Pool(n_workers) as pool:
        results = pool.map(_run_path, work, chunksize=chunksize)
    pass_rate = sum(1 for r in results if r["passed"]) / n
    depl_rate = sum(1 for r in results if r["pool_depletion_year"] is not None) / n

    def pct(key, p):
        return float(np.percentile([r[key] for r in results], p))

    return {
        "pass_rate": pass_rate,
        "depletion_rate": depl_rate,
        "repl_low_p5": pct("min_repl_low", 5),
        "repl_mid_p5": pct("min_repl_mid", 5),
        "max_loan_p95": pct("max_state_loan", 95),
        "rig_fund_p50": pct("final_rig_fund", 50),
        "rig_to_pool_p50": pct("total_rig_to_pool", 50),
    }


def make_config_f(horizon: int) -> Params:
    """Config F with optimal RIG parameters."""
    p = load_params_from_yaml("params/config_f.yaml")
    p.tau_high = TAU_HIGH
    p.rig_enabled = True
    p.rig_tau_insurance = OPTIMAL_INSURANCE
    p.rig_tau_equity = OPTIMAL_EQUITY
    p.rig_dividend_to_pool = OPTIMAL_DIV_TO_POOL
    p.high_attrition_rate = OPTIMAL_ATTRITION
    return p


def make_config_e() -> Params:
    """Config E baseline with brain drain."""
    p = load_params_from_yaml("params/config_e.yaml")
    p.tau_high = TAU_HIGH
    p.high_attrition_rate = BASELINE_ATTRITION
    return p


def build_rig_override(horizon: int, base_return: float, beta: float,
                       crisis_return: float, crisis_start: int,
                       crisis_end: int) -> List[float]:
    """Build a rig_return_override list with a crisis window."""
    override = []
    normal_r = base_return + beta * (0.0175 - base_return)  # approximate normal RIG return
    for t in range(horizon):
        if crisis_start <= t < crisis_end:
            override.append(crisis_return)
        else:
            override.append(normal_r)
    return override


def main():
    parser = argparse.ArgumentParser(description="RIG Adversarial Stress Tests")
    parser.add_argument("--n_paths", type=int, default=2000)
    parser.add_argument("--volatility", type=float, default=0.08)
    parser.add_argument("--mean_return", type=float, default=0.0175)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--json", type=str, default=None)
    args = parser.parse_args()

    n_workers = args.workers if args.workers > 0 else mp.cpu_count()
    mc = MCParams(
        n_paths=args.n_paths,
        mean_return=args.mean_return,
        volatility=args.volatility,
        seed=args.seed,
    )

    pf_base = make_config_f(100)
    pe_base = make_config_e()
    horizon = pf_base.horizon_years

    paths = generate_return_paths(mc, horizon)

    # Also generate regime-switching paths for attack #4
    mc_regime = MCParams(
        n_paths=args.n_paths,
        mean_return=args.mean_return,
        volatility=args.volatility,
        seed=args.seed,
        regime_enabled=True,
    )
    paths_regime = generate_return_paths(mc_regime, horizon)

    print("=" * 100)
    print("ADVERSARIALE RIG-STRESSTESTS")
    print(f"  {args.n_paths} Pfade | vol={args.volatility*100:.0f}%")
    print(f"  Config F: Ins={OPTIMAL_INSURANCE*100:.1f}% Eq={OPTIMAL_EQUITY*100:.2f}% "
          f"Div->Pool={OPTIMAL_DIV_TO_POOL*100:.0f}%")
    print("=" * 100)
    print()

    # === Baselines ===
    print("--- Baselines (keine Angriffe) ---")
    ref_e = run_mc(pe_base, paths, n_workers)
    print(f"  Config E (Brain Drain): Pass={ref_e['pass_rate']*100:.1f}% "
          f"Depl={ref_e['depletion_rate']*100:.1f}%")

    ref_f = run_mc(pf_base, paths, n_workers)
    print(f"  Config F (RIG):         Pass={ref_f['pass_rate']*100:.1f}% "
          f"Depl={ref_f['depletion_rate']*100:.1f}% "
          f"RIG={ref_f['rig_fund_p50']/1e12:.2f}T")
    print()

    scenarios = {}
    scenarios["baseline_E"] = ref_e
    scenarios["baseline_F"] = ref_f

    # === Attack 1: Governance Failure ===
    # RIG wird politisch vereinnahmt. r_RIG = 0% fuer 15 Jahre (Jahr 20-34).
    # Danach Reform und Normalisierung.
    print("--- Angriff 1: GOVERNANCE-VERSAGEN ---")
    print("  RIG politisiert, r_RIG = 0% fuer Jahre 20-34 (15 Jahre)")
    pf_gov = copy.deepcopy(pf_base)
    pf_gov.rig_return_override = build_rig_override(
        horizon, pf_base.rig_base_return, pf_base.rig_beta,
        crisis_return=0.0, crisis_start=20, crisis_end=35)
    r_gov = run_mc(pf_gov, paths, n_workers)
    d_pass = (r_gov["pass_rate"] - ref_f["pass_rate"]) * 100
    print(f"  Config F unter Angriff: Pass={r_gov['pass_rate']*100:.1f}% "
          f"(d={d_pass:+.1f}PP) RIG={r_gov['rig_fund_p50']/1e12:.2f}T")
    scenarios["attack_1_governance"] = r_gov

    # === Attack 2: Technology Failure ===
    # Physical AI liefert nicht. RIG hat keine Dekorrelation: beta = 1.0.
    print("\n--- Angriff 2: TECHNOLOGIE-SACKGASSE ---")
    print("  Physical AI scheitert, RIG korreliert vollstaendig mit Markt (beta=1.0)")
    pf_tech = copy.deepcopy(pf_base)
    pf_tech.rig_beta = 1.0
    r_tech = run_mc(pf_tech, paths, n_workers)
    d_pass = (r_tech["pass_rate"] - ref_f["pass_rate"]) * 100
    print(f"  Config F unter Angriff: Pass={r_tech['pass_rate']*100:.1f}% "
          f"(d={d_pass:+.1f}PP) RIG={r_tech['rig_fund_p50']/1e12:.2f}T")
    scenarios["attack_2_technology"] = r_tech

    # === Attack 3: Mass Flight ===
    # Extreme Abwanderung: 2%/yr (4x Basis). Politischer Backlash.
    print("\n--- Angriff 3: MASSENFLUCHT ---")
    print("  Extreme Abwanderung: 2%/yr High-Earner Attrition (4x Basis)")
    pf_flight = copy.deepcopy(pf_base)
    pf_flight.high_attrition_rate = 0.02
    r_flight_f = run_mc(pf_flight, paths, n_workers)
    # Config E under same extreme attrition
    pe_flight = copy.deepcopy(pe_base)
    pe_flight.high_attrition_rate = 0.02
    r_flight_e = run_mc(pe_flight, paths, n_workers)
    d_pass_f = (r_flight_f["pass_rate"] - ref_f["pass_rate"]) * 100
    d_pass_e = (r_flight_e["pass_rate"] - ref_e["pass_rate"]) * 100
    print(f"  Config F unter Angriff: Pass={r_flight_f['pass_rate']*100:.1f}% (d={d_pass_f:+.1f}PP)")
    print(f"  Config E unter Angriff: Pass={r_flight_e['pass_rate']*100:.1f}% (d={d_pass_e:+.1f}PP)")
    print(f"  RIG-Vorteil bei Massenflucht: {(r_flight_f['pass_rate'] - r_flight_e['pass_rate'])*100:+.1f}PP")
    scenarios["attack_3_flight_F"] = r_flight_f
    scenarios["attack_3_flight_E"] = r_flight_e

    # === Attack 4: Perfect Storm ===
    # Governance failure + mass flight + regime-switching returns
    print("\n--- Angriff 4: PERFEKTER STURM ---")
    print("  Governance-Versagen + Massenflucht + Regime-Switching Renditen")
    pf_storm = copy.deepcopy(pf_base)
    pf_storm.rig_return_override = build_rig_override(
        horizon, pf_base.rig_base_return, pf_base.rig_beta,
        crisis_return=0.0, crisis_start=20, crisis_end=35)
    pf_storm.high_attrition_rate = 0.02
    r_storm_f = run_mc(pf_storm, paths_regime, n_workers)
    # Config E under same regime-switching + extreme attrition
    pe_storm = copy.deepcopy(pe_base)
    pe_storm.high_attrition_rate = 0.02
    r_storm_e = run_mc(pe_storm, paths_regime, n_workers)
    print(f"  Config F unter Angriff: Pass={r_storm_f['pass_rate']*100:.1f}%")
    print(f"  Config E unter Angriff: Pass={r_storm_e['pass_rate']*100:.1f}%")
    print(f"  RIG-Vorteil im Sturm:   {(r_storm_f['pass_rate'] - r_storm_e['pass_rate'])*100:+.1f}PP")
    scenarios["attack_4_storm_F"] = r_storm_f
    scenarios["attack_4_storm_E"] = r_storm_e

    # === Attack 5: Value Destruction ===
    # RIG wird zum Verlustgeschaeft. r_RIG = -2% fuer 15 Jahre.
    print("\n--- Angriff 5: WERTVERNICHTUNG ---")
    print("  RIG vernichtet Kapital: r_RIG = -2% fuer Jahre 15-29 (15 Jahre)")
    pf_destroy = copy.deepcopy(pf_base)
    pf_destroy.rig_return_override = build_rig_override(
        horizon, pf_base.rig_base_return, pf_base.rig_beta,
        crisis_return=-0.02, crisis_start=15, crisis_end=30)
    r_destroy = run_mc(pf_destroy, paths, n_workers)
    d_pass = (r_destroy["pass_rate"] - ref_f["pass_rate"]) * 100
    print(f"  Config F unter Angriff: Pass={r_destroy['pass_rate']*100:.1f}% "
          f"(d={d_pass:+.1f}PP) RIG={r_destroy['rig_fund_p50']/1e12:.2f}T")
    scenarios["attack_5_destruction"] = r_destroy

    # === Summary Table ===
    print()
    print("=" * 100)
    print("ZUSAMMENFASSUNG: Degradation unter Angriffen")
    print("=" * 100)
    print()

    attacks = [
        ("Baseline (kein Angriff)", "baseline_F", "baseline_E"),
        ("1. Governance-Versagen", "attack_1_governance", None),
        ("2. Technologie-Sackgasse", "attack_2_technology", None),
        ("3. Massenflucht", "attack_3_flight_F", "attack_3_flight_E"),
        ("4. Perfekter Sturm", "attack_4_storm_F", "attack_4_storm_E"),
        ("5. Wertvernichtung", "attack_5_destruction", None),
    ]

    print(f"{'Szenario':<30s} | {'F Pass%':>7s} {'F Depl%':>7s} {'F Lo P5':>7s} | "
          f"{'E Pass%':>7s} | {'F-E':>5s} | {'Degradation':>12s}")
    print("-" * 95)

    for name, key_f, key_e in attacks:
        rf = scenarios[key_f]
        re = scenarios.get(key_e, ref_e) if key_e else ref_e
        d_fe = (rf["pass_rate"] - re["pass_rate"]) * 100
        d_base = (rf["pass_rate"] - ref_f["pass_rate"]) * 100

        degrad = "Keine" if abs(d_base) < 0.5 else (
            f"{d_base:+.1f} PP" if d_base > -3 else
            f"{d_base:+.1f} PP (!)"
        )

        print(f"{name:<30s} | {rf['pass_rate']*100:>6.1f}% {rf['depletion_rate']*100:>6.1f}% "
              f"{rf['repl_low_p5']*100:>6.1f}% | "
              f"{re['pass_rate']*100:>6.1f}% | {d_fe:>+4.1f}% | {degrad:>12s}")

    # === Resilience Assessment ===
    print()
    print("=" * 100)
    print("RESILIENZ-BEWERTUNG")
    print("=" * 100)
    print()

    worst_f = min(scenarios[k]["pass_rate"] for k in scenarios
                  if k.startswith("attack") and k.endswith("_F") or k == "attack_1_governance"
                  or k == "attack_2_technology" or k == "attack_5_destruction")
    worst_scenario = min(
        [(k, scenarios[k]["pass_rate"]) for k in scenarios
         if k.startswith("attack") and ("_F" in k or k in ("attack_1_governance", "attack_2_technology", "attack_5_destruction"))],
        key=lambda x: x[1]
    )

    print(f"  Schlechtester Angriff:    {worst_scenario[0]} ({worst_scenario[1]*100:.1f}%)")
    print(f"  Baseline Config F:        {ref_f['pass_rate']*100:.1f}%")
    print(f"  Maximale Degradation:     {(worst_scenario[1] - ref_f['pass_rate'])*100:+.1f} PP")
    print()

    # Check: does the system survive all attacks (pass > 80%)?
    all_survive = all(
        scenarios[k]["pass_rate"] > 0.80
        for k in scenarios if k.startswith("attack")
    )
    print(f"  Alle Angriffe ueberlebt (>80%): {'JA' if all_survive else 'NEIN'}")
    print()

    if all_survive:
        print("  FAZIT: Das RIG-gehaertete System degradiert unter adversarialen")
        print("  Szenarien, aber bricht nicht zusammen. Selbst im 'Perfekten Sturm'")
        print("  bleibt die Pass-Rate ueber 80%. Die Degradation ist graceful.")
    else:
        failed = [k for k in scenarios if k.startswith("attack") and scenarios[k]["pass_rate"] <= 0.80]
        print(f"  WARNUNG: Folgende Angriffe senken Pass-Rate unter 80%: {failed}")
        print("  Empfehlung: Backstop-Mechanismus verstaerken oder RIG-Anteil reduzieren.")

    # Save
    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        output = {
            "params": {
                "n_paths": args.n_paths,
                "volatility": args.volatility,
                "optimal_insurance": OPTIMAL_INSURANCE,
                "optimal_equity": OPTIMAL_EQUITY,
                "optimal_div_to_pool": OPTIMAL_DIV_TO_POOL,
            },
            "scenarios": scenarios,
        }
        with open(args.json, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nGespeichert: {args.json}")


if __name__ == "__main__":
    main()
