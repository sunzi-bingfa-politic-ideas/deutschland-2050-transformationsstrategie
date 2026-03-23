#!/usr/bin/env python3
"""
Monte Carlo Vergleich: RSSP mit vs. ohne RIG + Brain-Drain-Szenarien

Laeuft 4 Konfigurationen mit identischen Renditepfaden:
  1. Config E, keine Attrition (theoretisches Optimum)
  2. Config E, 0.5%/yr Attrition (Brain-Drain-Realitaet)
  3. Config F (RIG), 0.2%/yr Attrition (RIG-Loesung)
  4. Config F (RIG), keine Attrition (RIG-Effekt isoliert)

Usage:
    python src/mc_rig_comparison.py [--n_paths 10000] [--volatility 0.08] [--json out/mc_rig_comparison.json]
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import Params, simulate, RunResult
from monte_carlo import (
    load_params_from_yaml,
    generate_return_paths,
    MCParams,
    _params_to_dict,
    _dict_to_params,
)


ATTRITION_BASE = 0.005    # 0.5%/yr without RIG
ATTRITION_RIG = 0.002     # 0.2%/yr with RIG equity incentive


@dataclass
class ConfigVariant:
    name: str
    label: str
    params: Params


def build_variants() -> List[ConfigVariant]:
    """Build the 4 comparison configurations."""
    # Config E baseline
    pe = load_params_from_yaml("params/config_e.yaml")
    pe.tau_high = 0.1225

    # Config F (RIG)
    pf = load_params_from_yaml("params/config_f.yaml")
    pf.tau_high = pf.rig_tau_insurance + pf.rig_tau_equity

    # Create 4 variants
    variants = []

    # 1. Config E, no attrition
    import copy
    p1 = copy.deepcopy(pe)
    p1.high_attrition_rate = 0.0
    variants.append(ConfigVariant("E_no_attrition", "Config E (ideal, 0% Attrition)", p1))

    # 2. Config E, brain drain
    p2 = copy.deepcopy(pe)
    p2.high_attrition_rate = ATTRITION_BASE
    variants.append(ConfigVariant("E_brain_drain", f"Config E (Brain Drain {ATTRITION_BASE*100:.1f}%/yr)", p2))

    # 3. Config F (RIG), reduced attrition
    p3 = copy.deepcopy(pf)
    p3.high_attrition_rate = ATTRITION_RIG
    variants.append(ConfigVariant("F_rig_low_drain", f"Config F + RIG ({ATTRITION_RIG*100:.1f}%/yr Attrition)", p3))

    # 4. Config F (RIG), no attrition
    p4 = copy.deepcopy(pf)
    p4.high_attrition_rate = 0.0
    variants.append(ConfigVariant("F_rig_no_attrition", "Config F + RIG (ideal, 0% Attrition)", p4))

    return variants


def _run_path(args: Tuple) -> dict:
    """Worker: run one return path through simulate()."""
    params_dict, returns_list, path_idx = args
    p = _dict_to_params(params_dict)
    r = simulate(p, returns_list, f"mc_{path_idx}")
    return {
        "passed": r.passed,
        "min_repl_low": r.min_repl_low,
        "min_repl_mid": r.min_repl_mid,
        "max_state_loan": r.max_state_loan,
        "pool_depletion_year": r.pool_depletion_year,
        "is_structurally_sustainable": r.is_structurally_sustainable,
        "loan_ever_repaid": r.loan_ever_repaid,
        "steady_state_deficit": r.steady_state_deficit,
        "peak_longevity_per_capita": r.peak_longevity_per_capita,
        "peak_reserve_fund": r.peak_reserve_fund,
        "final_rig_fund": r.final_rig_fund,
        "peak_rig_fund": r.peak_rig_fund,
        "total_rig_to_pool": r.total_rig_to_pool,
    }


def aggregate(results: List[dict], n: int) -> dict:
    """Aggregate MC results."""
    arr = lambda key: np.array([r[key] for r in results])

    pass_rate = sum(1 for r in results if r["passed"]) / n
    depletion_rate = sum(1 for r in results if r["pool_depletion_year"] is not None) / n
    sustainable_rate = sum(1 for r in results if r["is_structurally_sustainable"]) / n

    min_lows = arr("min_repl_low")
    min_mids = arr("min_repl_mid")
    max_loans = arr("max_state_loan")
    ss_defs = arr("steady_state_deficit")
    rig_funds = arr("final_rig_fund")
    rig_to_pool = arr("total_rig_to_pool")

    def pct(a, p): return float(np.percentile(a, p))

    return {
        "pass_rate": pass_rate,
        "pool_depletion_rate": depletion_rate,
        "structural_sustainability_rate": sustainable_rate,
        "repl_low_p5": pct(min_lows, 5),
        "repl_low_p25": pct(min_lows, 25),
        "repl_low_p50": pct(min_lows, 50),
        "repl_mid_p5": pct(min_mids, 5),
        "repl_mid_p25": pct(min_mids, 25),
        "repl_mid_p50": pct(min_mids, 50),
        "max_loan_p50": pct(max_loans, 50),
        "max_loan_p95": pct(max_loans, 95),
        "ss_deficit_p50": pct(ss_defs, 50),
        "rig_fund_p50": pct(rig_funds, 50),
        "rig_to_pool_p50": pct(rig_to_pool, 50),
    }


def main():
    parser = argparse.ArgumentParser(description="MC RIG Comparison")
    parser.add_argument("--n_paths", type=int, default=10000)
    parser.add_argument("--volatility", type=float, default=0.08)
    parser.add_argument("--mean_return", type=float, default=0.0175)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--regime", action="store_true")
    parser.add_argument("--json", type=str, default=None)
    args = parser.parse_args()

    variants = build_variants()
    horizon = variants[0].params.horizon_years

    # Generate return paths ONCE (same for all configs)
    mc = MCParams(
        n_paths=args.n_paths,
        mean_return=args.mean_return,
        volatility=args.volatility,
        seed=args.seed,
        regime_enabled=args.regime,
    )
    print(f"Generiere {args.n_paths} Renditepfade (vol={args.volatility*100:.0f}%, "
          f"E[r]={args.mean_return*100:.2f}%, regime={'Ja' if args.regime else 'Nein'})...")
    paths = generate_return_paths(mc, horizon)

    n_workers = args.workers if args.workers > 0 else mp.cpu_count()
    all_results: Dict[str, dict] = {}

    for variant in variants:
        t0 = time.time()
        params_dict = _params_to_dict(variant.params)

        work_items = [
            (params_dict, paths[i].tolist(), i)
            for i in range(args.n_paths)
        ]

        print(f"\n--- {variant.label} ---")
        print(f"  Starte {args.n_paths} Pfade auf {n_workers} Kernen...")

        if n_workers == 1:
            results = [_run_path(w) for w in work_items]
        else:
            chunksize = max(1, args.n_paths // (n_workers * 4))
            with mp.Pool(n_workers) as pool:
                results = pool.map(_run_path, work_items, chunksize=chunksize)

        elapsed = time.time() - t0
        agg = aggregate(results, args.n_paths)
        agg["elapsed_seconds"] = elapsed
        all_results[variant.name] = agg

        print(f"  Pass-Rate:        {agg['pass_rate']*100:.1f}%")
        print(f"  Pool-Depletion:   {agg['pool_depletion_rate']*100:.1f}%")
        print(f"  Low P5/P50:       {agg['repl_low_p5']*100:.1f}% / {agg['repl_low_p50']*100:.1f}%")
        print(f"  Mid P5/P50:       {agg['repl_mid_p5']*100:.1f}% / {agg['repl_mid_p50']*100:.1f}%")
        print(f"  Max Kredit P95:   EUR {agg['max_loan_p95']/1e9:.1f} Mrd")
        if agg["rig_fund_p50"] > 0:
            print(f"  RIG-Fonds P50:    EUR {agg['rig_fund_p50']/1e12:.2f} Bio")
            print(f"  RIG->Pool P50:    EUR {agg['rig_to_pool_p50']/1e9:.1f} Mrd")
        print(f"  ({elapsed:.1f}s)")

    # === COMPARISON TABLE ===
    print()
    print("=" * 130)
    print("VERGLEICHSTABELLE: Monte Carlo RIG-Analyse")
    print(f"  {args.n_paths} Pfade | vol={args.volatility*100:.0f}% | E[r]={args.mean_return*100:.2f}%"
          f" | Regime={'Ja' if args.regime else 'Nein'}")
    print("=" * 130)
    print()

    header = (f"{'Konfiguration':<45s} | {'Pass%':>5s} | {'Depl%':>5s} | "
              f"{'Lo P5':>6s} | {'Lo P50':>6s} | {'Mi P5':>6s} | {'Mi P50':>6s} | "
              f"{'Kredit P95':>12s} | {'RIG P50':>12s} | {'RIG->Pool':>12s}")
    print(header)
    print("-" * len(header))

    for v in variants:
        a = all_results[v.name]
        rig_f = f"{a['rig_fund_p50']/1e12:.2f} Bio" if a['rig_fund_p50'] > 0 else "-"
        rig_p = f"{a['rig_to_pool_p50']/1e9:.0f} Mrd" if a['rig_to_pool_p50'] > 0 else "-"
        print(f"{v.label:<45s} | {a['pass_rate']*100:>4.1f}% | {a['pool_depletion_rate']*100:>4.1f}% | "
              f"{a['repl_low_p5']*100:>5.1f}% | {a['repl_low_p50']*100:>5.1f}% | "
              f"{a['repl_mid_p5']*100:>5.1f}% | {a['repl_mid_p50']*100:>5.1f}% | "
              f"{a['max_loan_p95']/1e9:>10.1f}B | {rig_f:>12s} | {rig_p:>12s}")

    # === DELTA ANALYSIS ===
    print()
    print("=" * 100)
    print("DELTA-ANALYSE (vs. Config E mit Brain Drain = Realitaet)")
    print("=" * 100)
    print()

    baseline = all_results["E_brain_drain"]
    for v in variants:
        if v.name == "E_brain_drain":
            continue
        a = all_results[v.name]
        d_pass = (a["pass_rate"] - baseline["pass_rate"]) * 100
        d_low5 = (a["repl_low_p5"] - baseline["repl_low_p5"]) * 100
        d_mid5 = (a["repl_mid_p5"] - baseline["repl_mid_p5"]) * 100
        d_depl = (a["pool_depletion_rate"] - baseline["pool_depletion_rate"]) * 100
        print(f"  {v.label}:")
        print(f"    dPass-Rate:     {d_pass:+.1f} PP")
        print(f"    dDepletion:     {d_depl:+.1f} PP")
        print(f"    dLow P5:        {d_low5:+.1f} PP")
        print(f"    dMid P5:        {d_mid5:+.1f} PP")
        print()

    # === KEY FINDINGS ===
    print("=" * 100)
    print("KERNBEFUNDE")
    print("=" * 100)
    print()

    e_ideal = all_results["E_no_attrition"]
    e_brain = all_results["E_brain_drain"]
    f_rig = all_results["F_rig_low_drain"]
    f_ideal = all_results["F_rig_no_attrition"]

    brain_drain_cost = (e_ideal["pass_rate"] - e_brain["pass_rate"]) * 100
    rig_recovery = (f_rig["pass_rate"] - e_brain["pass_rate"]) * 100

    print(f"  1. Brain-Drain-Kosten:   {brain_drain_cost:+.1f} PP Pass-Rate"
          f" (Config E ideal vs. Brain Drain)")
    print(f"  2. RIG-Kompensation:     {rig_recovery:+.1f} PP Pass-Rate"
          f" (Config F+RIG vs. Config E Brain Drain)")
    print(f"  3. RIG-Fondsvolumen:     EUR {f_rig['rig_fund_p50']/1e12:.2f} Bio (P50)")
    print(f"  4. RIG-Dividenden->Pool: EUR {f_rig['rig_to_pool_p50']/1e9:.0f} Mrd (P50, kumuliert)")

    depl_e = e_brain["pool_depletion_rate"] * 100
    depl_f = f_rig["pool_depletion_rate"] * 100
    if depl_e > 0 or depl_f > 0:
        print(f"  5. Pool-Depletion:       Config E={depl_e:.1f}% | Config F+RIG={depl_f:.1f}%")

    print()

    # Save JSON
    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        output = {
            "params": {
                "n_paths": args.n_paths,
                "volatility": args.volatility,
                "mean_return": args.mean_return,
                "regime": args.regime,
                "attrition_base": ATTRITION_BASE,
                "attrition_rig": ATTRITION_RIG,
            },
            "results": all_results,
        }
        with open(args.json, "w") as f:
            json.dump(output, f, indent=2)
        print(f"Gespeichert: {args.json}")


if __name__ == "__main__":
    main()
