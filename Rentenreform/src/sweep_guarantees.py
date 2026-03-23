# Rentenreform/RSSP_v2/src/sweep_guarantees.py
"""
Sweep guarantee levels at fixed tau_high to find achievable replacement rates.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import List

from model import Params, simulate, MortalityBucket
from scenarios import load_scenarios_const, load_scenarios_paths
from utils import frange, load_yaml


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--scenarios", required=True)
    ap.add_argument("--mode", choices=["const", "paths"], required=True)
    ap.add_argument("--tau_high", type=float, default=0.05, help="Fixed tau_high rate")
    ap.add_argument("--out", default="../out/sweep_guarantees.json")
    args = ap.parse_args()

    base = load_yaml(args.base)
    scen = load_yaml(args.scenarios)

    scenarios = load_scenarios_const(scen) if args.mode == "const" else load_scenarios_paths(scen)

    # Parse hardenings
    mort = base.get("mortality", {})
    mort_enabled = bool(mort.get("enabled", True))
    mort_buckets = [
        MortalityBucket(int(b["age_min"]), int(b["age_max"]), float(b["survival"]))
        for b in mort.get("buckets", [])
    ]

    demo = base.get("demography", {})
    demo_mode = str(demo.get("mode", "constant"))
    cohort_path = [int(x) for x in demo.get("cohort_path", [])]

    back = base.get("backstop", {})
    back_enabled = bool(back.get("enabled", True))
    loan_cap = float(back.get("loan_cap_asset_share", 0.10))
    repay_share = float(back.get("repay_share", 0.50))
    reserve_years = int(back.get("reserve_years", 3))

    # Grid of guarantee levels to test
    guarantee_low_grid = frange(0.50, 1.00, 0.05, ndigits=4)  # 50% to 100%
    guarantee_mid_grid = frange(0.40, 0.70, 0.05, ndigits=4)  # 40% to 70%

    results = []

    for g_low in guarantee_low_grid:
        for g_mid in guarantee_mid_grid:
            if g_mid > g_low:  # Mid guarantee shouldn't exceed Low
                continue

            p = Params(
                horizon_years=int(base["horizon_years"]),
                age_start=int(base["age_start"]),
                retire_age=int(base["retire_age"]),
                annuity_years=int(base["annuity_years"]),
                cohort_size_at_age_start=int(base["cohort_size_at_age_start"]),
                low_share=float(base["low_share"]),
                mid_share=float(base["mid_share"]),
                high_share=float(base["high_share"]),
                income_low_retire=float(base["income_low_retire"]),
                income_mid_retire=float(base["income_mid_retire"]),
                high_income_factor=float(base["high_income_factor"]),
                tau_low=float(base["tau_low"]),
                tau_mid=float(base["tau_mid"]),
                tau_high=args.tau_high,
                guarantee_low=g_low,
                guarantee_mid=g_mid,
                mortality_enabled=mort_enabled,
                mortality_buckets=mort_buckets,
                demography_mode=demo_mode,
                cohort_path=cohort_path,
                backstop_enabled=back_enabled,
                loan_cap_asset_share=loan_cap,
                repay_share=repay_share,
                reserve_years=reserve_years,
            )

            all_pass = True
            worst_fail = 0
            worst_loan = 0.0
            per_scenario = {}

            for name, ret in scenarios.items():
                res = simulate(p, returns=ret, scenario_name=name, pass_last_n_years=10)
                per_scenario[name] = {
                    "passed": res.passed,
                    "fail_years": res.fail_years,
                    "min_repl_low": round(res.min_repl_low, 4),
                    "min_repl_mid": round(res.min_repl_mid, 4),
                    "max_state_loan": res.max_state_loan,
                }
                all_pass = all_pass and res.passed
                worst_fail = max(worst_fail, res.fail_years)
                worst_loan = max(worst_loan, res.max_state_loan)

            results.append({
                "guarantee_low": g_low,
                "guarantee_mid": g_mid,
                "tau_high": args.tau_high,
                "all_pass": all_pass,
                "worst_fail_years": worst_fail,
                "worst_state_loan": worst_loan,
                "per_scenario": per_scenario,
            })

    # Find best passing combination
    passing = [r for r in results if r["all_pass"]]
    if passing:
        # Sort by highest guarantee_low, then highest guarantee_mid
        passing.sort(key=lambda x: (x["guarantee_low"], x["guarantee_mid"]), reverse=True)
        best = passing[0]
    else:
        # No passing - find least failing
        results.sort(key=lambda x: x["worst_fail_years"])
        best = results[0]

    output = {
        "tau_high_fixed": args.tau_high,
        "best_achievable": {
            "guarantee_low": best["guarantee_low"],
            "guarantee_mid": best["guarantee_mid"],
            "all_pass": best["all_pass"],
            "worst_fail_years": best["worst_fail_years"],
            "worst_state_loan": best["worst_state_loan"],
        },
        "all_passing_combinations": [
            {"g_low": r["guarantee_low"], "g_mid": r["guarantee_mid"], "worst_loan": r["worst_state_loan"]}
            for r in passing
        ],
        "full_results": results,
    }

    import os
    os.makedirs(os.path.dirname(args.out) if os.path.dirname(args.out) else ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"=== tau_high = {args.tau_high*100:.1f}% ===")
    print(f"Best achievable: Low={best['guarantee_low']*100:.0f}%, Mid={best['guarantee_mid']*100:.0f}%")
    print(f"All scenarios pass: {best['all_pass']}")
    print(f"Worst state loan: {best['worst_state_loan']/1e9:.1f} Mrd EUR")
    print(f"\nAll passing combinations ({len(passing)}):")
    for r in passing[:10]:
        print(f"  Low={r['guarantee_low']*100:.0f}%, Mid={r['guarantee_mid']*100:.0f}% -> Loan max {r['worst_state_loan']/1e9:.1f} Mrd")


if __name__ == "__main__":
    main()
