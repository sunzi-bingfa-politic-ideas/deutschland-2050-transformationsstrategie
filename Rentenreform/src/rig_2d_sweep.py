#!/usr/bin/env python3
"""
RIG 2D-Recalibration Sweep: Insurance-Rate x Dividend-to-Pool

Findet den optimalen Betriebspunkt auf der Pareto-Front:
  - Achse 1: rig_tau_insurance (wie viel direkt an Pool)
  - Achse 2: rig_dividend_to_pool (wie viel RIG-Dividenden an Pool fliessen)

Fuer jede Kombination wird die Pass-Rate via MC bestimmt.
Zwei Attritions-Modelle (optimistisch + konservativ) liefern Robustheits-Banden.

Usage:
    python src/rig_2d_sweep.py [--n_paths 2000] [--json out/rig_2d_sweep.json]
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
ATTRITION_BASE = 0.005  # 0.5%/yr without RIG


def attrition_optimistic(equity_share: float) -> float:
    """Optimistic: full linear reduction. 0% equity -> 0.5%, 50% equity -> 0.1%."""
    reduction = min(equity_share / 0.5, 1.0) * 0.8
    return ATTRITION_BASE * (1.0 - reduction)


def attrition_conservative(equity_share: float) -> float:
    """Conservative: half the effect. Attrition reduction only 50% as strong."""
    reduction = min(equity_share / 0.5, 1.0) * 0.4  # half of 0.8
    return ATTRITION_BASE * (1.0 - reduction)


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
        "steady_state_deficit": r.steady_state_deficit,
        "final_rig_fund": r.final_rig_fund,
        "total_rig_to_pool": r.total_rig_to_pool,
        "total_rig_dividends": r.total_rig_dividends,
    }


def run_mc_for_params(params: Params, paths: np.ndarray, n_workers: int) -> dict:
    """Run MC for given params and return aggregated metrics."""
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
        "repl_low_p50": pct("min_repl_low", 50),
        "repl_mid_p5": pct("min_repl_mid", 5),
        "repl_mid_p50": pct("min_repl_mid", 50),
        "max_loan_p95": pct("max_state_loan", 95),
        "ss_deficit_p50": pct("steady_state_deficit", 50),
        "rig_fund_p50": pct("final_rig_fund", 50),
        "rig_to_pool_p50": pct("total_rig_to_pool", 50),
        "rig_div_total_p50": pct("total_rig_dividends", 50),
    }


def main():
    parser = argparse.ArgumentParser(description="RIG 2D Recalibration Sweep")
    parser.add_argument("--n_paths", type=int, default=2000)
    parser.add_argument("--volatility", type=float, default=0.08)
    parser.add_argument("--mean_return", type=float, default=0.0175)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--json", type=str, default=None)
    args = parser.parse_args()

    base = load_params_from_yaml("params/config_f.yaml")
    horizon = base.horizon_years
    n_workers = args.workers if args.workers > 0 else mp.cpu_count()

    mc = MCParams(
        n_paths=args.n_paths,
        mean_return=args.mean_return,
        volatility=args.volatility,
        seed=args.seed,
    )
    print(f"RIG 2D-Sweep: {args.n_paths} Pfade, vol={args.volatility*100:.0f}%")
    paths = generate_return_paths(mc, horizon)

    # === Reference: Config E with brain drain ===
    pe = load_params_from_yaml("params/config_e.yaml")
    pe.tau_high = TAU_HIGH_TOTAL
    pe.high_attrition_rate = ATTRITION_BASE
    print("\n--- Referenz: Config E (Brain Drain 0.5%/yr) ---")
    ref = run_mc_for_params(pe, paths, n_workers)
    print(f"  Pass: {ref['pass_rate']*100:.1f}% | Depl: {ref['depletion_rate']*100:.1f}%")

    # === Sweep grid ===
    ins_grid = [round(0.08 + i * 0.005, 4) for i in range(8)]  # 0.08 to 0.115
    div_grid = [round(0.30 + i * 0.10, 2) for i in range(7)]   # 0.30 to 0.90

    print(f"\nSweep: {len(ins_grid)} x {len(div_grid)} = {len(ins_grid)*len(div_grid)} Kombinationen")
    print(f"  Insurance: {[f'{x*100:.1f}%' for x in ins_grid]}")
    print(f"  Div->Pool: {[f'{x*100:.0f}%' for x in div_grid]}")

    results_opt = []  # optimistic attrition
    results_con = []  # conservative attrition
    t0 = time.time()

    for ins in ins_grid:
        for div in div_grid:
            eq = round(TAU_HIGH_TOTAL - ins, 4)
            if eq < 0:
                continue
            equity_share = eq / TAU_HIGH_TOTAL

            for attrition_model, attrition_fn, result_list in [
                ("optimistic", attrition_optimistic, results_opt),
                ("conservative", attrition_conservative, results_con),
            ]:
                attr = attrition_fn(equity_share)
                p = copy.deepcopy(base)
                p.rig_enabled = True
                p.rig_tau_insurance = ins
                p.rig_tau_equity = eq
                p.rig_dividend_to_pool = div
                p.tau_high = TAU_HIGH_TOTAL
                p.high_attrition_rate = attr

                agg = run_mc_for_params(p, paths, n_workers)

                row = {
                    "insurance": ins,
                    "equity": eq,
                    "dividend_to_pool": div,
                    "attrition_model": attrition_model,
                    "attrition_rate": attr,
                    "equity_share_pct": equity_share * 100,
                    **agg,
                }
                result_list.append(row)

            # Print progress (optimistic model)
            r = results_opt[-1]
            d_pass = (r["pass_rate"] - ref["pass_rate"]) * 100
            print(f"  Ins={ins*100:5.1f}% Eq={eq*100:5.2f}% Div={div*100:3.0f}% | "
                  f"Pass={r['pass_rate']*100:5.1f}% (d={d_pass:+5.1f}) | "
                  f"RIG={r['rig_fund_p50']/1e12:.2f}T | "
                  f"Div->H={r['rig_div_total_p50']/1e9 - r['rig_to_pool_p50']/1e9:.0f}B")

    elapsed = time.time() - t0
    print(f"\n{len(results_opt)} Kombinationen in {elapsed:.1f}s")

    # === Find optimal region ===
    tolerance = 0.005  # 0.5 PP
    ref_pass = ref["pass_rate"]

    def find_candidates(results):
        candidates = [r for r in results if r["pass_rate"] >= ref_pass - tolerance]
        # Sort by equity (descending) — maximize incentive
        candidates.sort(key=lambda r: r["equity"], reverse=True)
        return candidates

    cand_opt = find_candidates(results_opt)
    cand_con = find_candidates(results_con)

    # Candidates that survive BOTH attrition models
    cand_robust = []
    for r_opt in cand_opt:
        key = (r_opt["insurance"], r_opt["dividend_to_pool"])
        for r_con in cand_con:
            if (r_con["insurance"], r_con["dividend_to_pool"]) == key:
                cand_robust.append({
                    "insurance": r_opt["insurance"],
                    "equity": r_opt["equity"],
                    "dividend_to_pool": r_opt["dividend_to_pool"],
                    "pass_rate_optimistic": r_opt["pass_rate"],
                    "pass_rate_conservative": r_con["pass_rate"],
                    "pass_rate_avg": (r_opt["pass_rate"] + r_con["pass_rate"]) / 2,
                    "rig_fund_p50": r_opt["rig_fund_p50"],
                    "rig_to_pool_p50": r_opt["rig_to_pool_p50"],
                    "rig_div_holders_p50": r_opt["rig_div_total_p50"] - r_opt["rig_to_pool_p50"],
                    "attrition_optimistic": r_opt["attrition_rate"],
                    "attrition_conservative": r_con["attrition_rate"],
                })
                break
    cand_robust.sort(key=lambda r: (r["pass_rate_avg"], r["equity"]), reverse=True)

    # === Print results ===
    print()
    print("=" * 110)
    print(f"OPTIMALE REGION (Pass-Rate >= {(ref_pass - tolerance)*100:.1f}% in BEIDEN Attritions-Modellen)")
    print(f"Referenz Config E: {ref_pass*100:.1f}%")
    print("=" * 110)
    print()

    if cand_robust:
        print(f"{'Ins%':>5s} {'Eq%':>5s} {'Div%':>5s} | {'Pass(opt)':>9s} {'Pass(con)':>9s} {'Pass(avg)':>9s} | "
              f"{'RIG-Fonds':>12s} {'RIG->Pool':>12s} {'RIG->Halter':>12s}")
        print("-" * 100)
        for c in cand_robust[:15]:
            print(f"{c['insurance']*100:>4.1f}% {c['equity']*100:>4.2f}% {c['dividend_to_pool']*100:>4.0f}% | "
                  f"{c['pass_rate_optimistic']*100:>8.1f}% {c['pass_rate_conservative']*100:>8.1f}% "
                  f"{c['pass_rate_avg']*100:>8.1f}% | "
                  f"{c['rig_fund_p50']/1e12:>10.2f}T {c['rig_to_pool_p50']/1e9:>10.0f}B "
                  f"{c['rig_div_holders_p50']/1e9:>10.0f}B")

        # Best robust candidate
        best = cand_robust[0]
        print()
        print(">>> EMPFEHLUNG:")
        print(f"    Insurance:       {best['insurance']*100:.1f}%")
        print(f"    Equity:          {best['equity']*100:.2f}%")
        print(f"    Div->Pool:       {best['dividend_to_pool']*100:.0f}%")
        print(f"    Pass-Rate:       {best['pass_rate_avg']*100:.1f}% (Band: "
              f"{best['pass_rate_conservative']*100:.1f}%-{best['pass_rate_optimistic']*100:.1f}%)")
        print(f"    RIG-Fonds:       EUR {best['rig_fund_p50']/1e12:.2f} Bio")
        print(f"    Div. an Halter:  EUR {best['rig_div_holders_p50']/1e9:.0f} Mrd (kumuliert)")
        print(f"    vs. Referenz:    {(best['pass_rate_avg'] - ref_pass)*100:+.1f} PP")
    else:
        print("  KEINE Kombination erfuellt beide Attritions-Modelle!")
        print("  Empfehlung: Toleranz erhoehen oder Equity-Anteil weiter senken.")

    # === Heatmap data ===
    print()
    print("=" * 110)
    print("HEATMAP: Pass-Rate (optimistisches Modell)")
    print("=" * 110)
    print()
    header = f"{'Ins\\Div':>8s}" + "".join(f" {d*100:>5.0f}%" for d in div_grid)
    print(header)
    print("-" * len(header))
    for ins in ins_grid:
        row = f"{ins*100:>7.1f}%"
        for div in div_grid:
            match = [r for r in results_opt
                     if abs(r["insurance"] - ins) < 1e-6 and abs(r["dividend_to_pool"] - div) < 1e-6]
            if match:
                val = match[0]["pass_rate"] * 100
                row += f" {val:>5.1f}%"
            else:
                row += "    - "
        print(row)

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
            "reference": ref,
            "sweep_optimistic": results_opt,
            "sweep_conservative": results_con,
            "robust_candidates": cand_robust,
            "recommendation": cand_robust[0] if cand_robust else None,
        }
        with open(args.json, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nGespeichert: {args.json}")


if __name__ == "__main__":
    main()
