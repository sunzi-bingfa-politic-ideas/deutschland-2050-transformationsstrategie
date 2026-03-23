#!/usr/bin/env python3
"""
RIG Split-Ratio Sweep: Optimaler Versicherung/Equity-Split

Variiert den Split von tau_high (12.25%) zwischen Garantie-Pool und RIG-Zertifikaten.
Fuer jeden Split wird eine MC-Simulation durchgefuehrt.

Zielkonflikt:
  - Mehr Insurance -> stabilerer Pool, aber weniger Anreiz fuer High-Earner
  - Mehr Equity -> staerkerer Anreiz, aber weniger direkte Pool-Finanzierung

Usage:
    python src/rig_split_sweep.py [--n_paths 2000] [--json out/rig_split_sweep.json]
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


TAU_HIGH_TOTAL = 0.1225
ATTRITION_BASE = 0.005    # baseline attrition without RIG


def attrition_for_equity_share(equity_share: float) -> float:
    """
    Model: higher equity share -> more incentive -> lower attrition.
    Linear interpolation:
      equity_share = 0    -> attrition = ATTRITION_BASE (no incentive)
      equity_share = 0.5  -> attrition = ATTRITION_BASE * 0.2 (strong incentive)
    Capped at equity_share = 0.5 (max effect).
    """
    reduction = min(equity_share / 0.5, 1.0) * 0.8  # max 80% reduction
    return ATTRITION_BASE * (1.0 - reduction)


def _run_path(args: Tuple) -> dict:
    params_dict, returns_list, path_idx = args
    p = _dict_to_params(params_dict)
    r = simulate(p, returns_list, f"mc_{path_idx}")
    return {
        "passed": r.passed,
        "min_repl_low": r.min_repl_low,
        "min_repl_mid": r.min_repl_mid,
        "pool_depletion_year": r.pool_depletion_year,
        "is_structurally_sustainable": r.is_structurally_sustainable,
        "max_state_loan": r.max_state_loan,
        "steady_state_deficit": r.steady_state_deficit,
        "final_rig_fund": r.final_rig_fund,
        "total_rig_to_pool": r.total_rig_to_pool,
    }


def main():
    parser = argparse.ArgumentParser(description="RIG Split-Ratio Sweep")
    parser.add_argument("--n_paths", type=int, default=2000, help="MC paths per split")
    parser.add_argument("--volatility", type=float, default=0.08)
    parser.add_argument("--mean_return", type=float, default=0.0175)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--json", type=str, default=None)
    # Split range
    parser.add_argument("--ins_min", type=float, default=0.05, help="Min insurance rate")
    parser.add_argument("--ins_max", type=float, default=0.12, help="Max insurance rate")
    parser.add_argument("--ins_step", type=float, default=0.005, help="Insurance rate step")
    args = parser.parse_args()

    # Load base Config F
    base = load_params_from_yaml("params/config_f.yaml")
    horizon = base.horizon_years

    # Generate return paths once
    mc = MCParams(
        n_paths=args.n_paths,
        mean_return=args.mean_return,
        volatility=args.volatility,
        seed=args.seed,
    )
    paths = generate_return_paths(mc, horizon)
    n_workers = args.workers if args.workers > 0 else mp.cpu_count()

    # Also run Config E with brain drain as reference
    pe = load_params_from_yaml("params/config_e.yaml")
    pe.tau_high = TAU_HIGH_TOTAL
    pe.high_attrition_rate = ATTRITION_BASE

    print(f"RIG Split-Ratio Sweep: tau_high_total = {TAU_HIGH_TOTAL*100:.2f}%")
    print(f"  MC: {args.n_paths} Pfade, vol={args.volatility*100:.0f}%")
    print(f"  Insurance-Range: {args.ins_min*100:.1f}% bis {args.ins_max*100:.1f}%, Step {args.ins_step*100:.1f}%")
    print()

    # Reference: Config E with brain drain
    print("--- Referenz: Config E (Brain Drain 0.5%/yr, keine RIG) ---")
    params_dict_e = _params_to_dict(pe)
    work_e = [(params_dict_e, paths[i].tolist(), i) for i in range(args.n_paths)]
    chunksize = max(1, args.n_paths // (n_workers * 4))
    with mp.Pool(n_workers) as pool:
        results_e = pool.map(_run_path, work_e, chunksize=chunksize)
    ref_pass = sum(1 for r in results_e if r["passed"]) / args.n_paths
    ref_depl = sum(1 for r in results_e if r["pool_depletion_year"] is not None) / args.n_paths
    ref_low5 = float(np.percentile([r["min_repl_low"] for r in results_e], 5))
    ref_mid5 = float(np.percentile([r["min_repl_mid"] for r in results_e], 5))
    print(f"  Pass: {ref_pass*100:.1f}% | Depletion: {ref_depl*100:.1f}% | "
          f"Low P5: {ref_low5*100:.1f}% | Mid P5: {ref_mid5*100:.1f}%")
    print()

    # Sweep
    splits = []
    ins_rate = args.ins_min
    while ins_rate <= args.ins_max + 1e-9:
        splits.append(round(ins_rate, 4))
        ins_rate += args.ins_step

    results_table = []

    print(f"{'Ins%':>5s} | {'Eq%':>5s} | {'Attr%':>5s} | {'Pass%':>5s} | {'dPass':>5s} | "
          f"{'Depl%':>5s} | {'Lo P5':>6s} | {'Mi P5':>6s} | {'RIG Bio':>8s} | "
          f"{'RIG->Pool':>10s} | {'SS-Def':>10s}")
    print("-" * 95)

    for ins in splits:
        eq = round(TAU_HIGH_TOTAL - ins, 4)
        if eq < 0:
            continue

        equity_share = eq / TAU_HIGH_TOTAL
        attr = attrition_for_equity_share(equity_share)

        p = copy.deepcopy(base)
        p.rig_enabled = True
        p.rig_tau_insurance = ins
        p.rig_tau_equity = eq
        p.tau_high = TAU_HIGH_TOTAL
        p.high_attrition_rate = attr

        params_dict = _params_to_dict(p)
        work_items = [(params_dict, paths[i].tolist(), i) for i in range(args.n_paths)]

        with mp.Pool(n_workers) as pool:
            results = pool.map(_run_path, work_items, chunksize=chunksize)

        n = len(results)
        pass_rate = sum(1 for r in results if r["passed"]) / n
        depl_rate = sum(1 for r in results if r["pool_depletion_year"] is not None) / n
        low5 = float(np.percentile([r["min_repl_low"] for r in results], 5))
        mid5 = float(np.percentile([r["min_repl_mid"] for r in results], 5))
        rig_p50 = float(np.percentile([r["final_rig_fund"] for r in results], 50))
        rtp_p50 = float(np.percentile([r["total_rig_to_pool"] for r in results], 50))
        ss_p50 = float(np.percentile([r["steady_state_deficit"] for r in results], 50))

        d_pass = (pass_rate - ref_pass) * 100

        row = {
            "insurance": ins,
            "equity": eq,
            "attrition": attr,
            "pass_rate": pass_rate,
            "delta_pass": d_pass,
            "depletion_rate": depl_rate,
            "repl_low_p5": low5,
            "repl_mid_p5": mid5,
            "rig_fund_p50": rig_p50,
            "rig_to_pool_p50": rtp_p50,
            "ss_deficit_p50": ss_p50,
        }
        results_table.append(row)

        print(f"{ins*100:>4.1f}% | {eq*100:>4.1f}% | {attr*100:>4.2f}% | "
              f"{pass_rate*100:>4.1f}% | {d_pass:>+4.1f}% | {depl_rate*100:>4.1f}% | "
              f"{low5*100:>5.1f}% | {mid5*100:>5.1f}% | "
              f"{rig_p50/1e12:>7.2f}T | "
              f"{rtp_p50/1e9:>8.0f}B | {ss_p50/1e9:>8.1f}B")

    # Find optimal split
    print()
    print("=" * 95)
    print("OPTIMALER SPLIT")
    print("=" * 95)
    print()

    # Optimal = highest pass rate. Among ties, highest equity (more incentive)
    best = max(results_table, key=lambda r: (r["pass_rate"], r["equity"]))
    print(f"  Bester Split:  Insurance {best['insurance']*100:.1f}% / Equity {best['equity']*100:.1f}%")
    print(f"  Pass-Rate:     {best['pass_rate']*100:.1f}%")
    print(f"  vs. Referenz:  {best['delta_pass']:+.1f} PP")
    print(f"  Attrition:     {best['attrition']*100:.2f}%/yr")
    print(f"  RIG-Fonds:     EUR {best['rig_fund_p50']/1e12:.2f} Bio")
    print()

    # Find Pareto frontier (splits where no other split dominates on both pass_rate AND equity)
    print("  Pareto-Optimale Splits (Pass-Rate vs. Anreiz-Staerke):")
    pareto = []
    for r in sorted(results_table, key=lambda x: x["insurance"]):
        dominated = False
        for other in results_table:
            if other["pass_rate"] > r["pass_rate"] + 0.001 and other["equity"] > r["equity"] + 0.001:
                dominated = True
                break
        if not dominated:
            pareto.append(r)
            marker = " <-- Vorschlag (8/4.25)" if abs(r["insurance"] - 0.08) < 0.001 else ""
            print(f"    Ins={r['insurance']*100:.1f}% Eq={r['equity']*100:.1f}% "
                  f"Pass={r['pass_rate']*100:.1f}% "
                  f"RIG={r['rig_fund_p50']/1e12:.2f}Bio{marker}")

    # Save
    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        output = {
            "params": {
                "tau_high_total": TAU_HIGH_TOTAL,
                "n_paths": args.n_paths,
                "volatility": args.volatility,
                "mean_return": args.mean_return,
                "attrition_base": ATTRITION_BASE,
            },
            "reference": {
                "pass_rate": ref_pass,
                "depletion_rate": ref_depl,
                "repl_low_p5": ref_low5,
                "repl_mid_p5": ref_mid5,
            },
            "sweep": results_table,
            "best_split": best,
            "pareto_splits": pareto,
        }
        with open(args.json, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nGespeichert: {args.json}")


if __name__ == "__main__":
    main()
