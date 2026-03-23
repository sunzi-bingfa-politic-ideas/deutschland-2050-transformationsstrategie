#!/usr/bin/env python3
"""
Tontine Longevity Pool Solvency Verification

Runs Config E (tontine enabled, reserve rule enabled) at the optimal tau_high
across all return scenarios and outputs the longevity pool balance trajectory,
per-capita payouts, and solvency metrics.

Usage:
    python src/tontine_verify.py [--json out/tontine_solvency.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List

from model import MortalityBucket, Params, simulate

# Config E parameters
CONFIG_E_MORTALITY = [
    MortalityBucket(67, 74, 0.982),
    MortalityBucket(75, 84, 0.955),
    MortalityBucket(85, 95, 0.88),
    MortalityBucket(96, 200, 0.72),
]

# Return scenarios (same as optimizer)
SCENARIOS = {
    "base_1p7": [0.01735],
    "low_1p0": [0.010],
    "hard_0p5": [0.005],
    "flat_0p0": [0.000],
    "drawdown_5y": [-0.03, -0.03, -0.03, -0.03, -0.03, 0.015],
    "crash_recover": [-0.10, -0.05, 0.00, 0.01, 0.015, 0.017],
    "stagflation": [0.00, 0.00, 0.00, 0.005, 0.010, 0.012],
}


def make_config_e_params(tau_high: float) -> Params:
    """Build Config E params."""
    return Params(
        horizon_years=100,
        age_start=20,
        retire_age=67,
        annuity_years=20,
        cohort_size_at_age_start=831_435,
        low_share=0.30,
        mid_share=0.50,
        high_share=0.20,
        income_low_retire=22_000.0,
        income_mid_retire=40_000.0,
        high_income_factor=1.8,
        tau_low=0.12,
        tau_mid=0.13,
        tau_high=tau_high,
        guarantee_low=0.85,
        guarantee_mid=0.60,
        mortality_enabled=True,
        mortality_buckets=list(CONFIG_E_MORTALITY),
        backstop_enabled=True,
        loan_cap_asset_share=0.10,
        repay_share=0.50,
        reserve_years=3,
        longevity_pool_enabled=True,
        longevity_floor=10_000.0,
        longevity_max_age=95,
        longevity_surplus_share=0.05,
        tontine_enabled=True,
        tontine_cap_multiple=3.0,
        reserve_rule_enabled=True,
        reserve_trigger_high=0.03,
        reserve_trigger_low=0.01,
        reserve_target_return=0.02,
        reserve_skim_fraction=0.30,
        reserve_inject_fraction=0.30,
        reserve_safe_rate=0.005,
    )


def find_optimal_tau_high() -> float:
    """Find minimum tau_high that passes all scenarios for Config E."""
    for tau_h_x100 in range(100, 4000, 25):  # 1% to 40% in 0.25% steps
        tau_h = tau_h_x100 / 10000.0
        p = make_config_e_params(tau_h)
        all_pass = True
        for name, ret in SCENARIOS.items():
            res = simulate(p, returns=ret, scenario_name=name, pass_last_n_years=10)
            if not res.passed:
                all_pass = False
                break
        if all_pass:
            return tau_h
    return 0.40  # fallback


def verify_solvency(tau_high: float) -> Dict:
    """Run all scenarios and extract longevity pool trajectory."""
    p = make_config_e_params(tau_high)
    results = {}

    for name, ret in SCENARIOS.items():
        res = simulate(p, returns=ret, scenario_name=name, pass_last_n_years=10)

        # Extract longevity pool trajectory
        pool_trajectory = []
        for s in res.stats:
            pool_trajectory.append({
                "year": s.year,
                "longevity_pool": round(s.longevity_pool, 2),
                "longevity_retirees": s.longevity_retirees,
                "longevity_per_capita": round(s.longevity_per_capita, 2),
                "longevity_payout_total": round(s.longevity_payout_total, 2),
                "longevity_backstop": round(s.longevity_backstop, 2),
                "reserve_fund": round(s.reserve_fund, 2),
            })

        # Solvency metrics
        pool_min = min(s.longevity_pool for s in res.stats)
        pool_final = res.stats[-1].longevity_pool
        years_with_retirees = [s for s in res.stats if s.longevity_retirees > 0]
        per_capita_values = [s.longevity_per_capita for s in years_with_retirees]
        pool_ever_zero = any(s.longevity_pool < 1.0 and s.longevity_retirees > 0
                            for s in res.stats)

        results[name] = {
            "passed": res.passed,
            "pool_min": round(pool_min, 2),
            "pool_final": round(pool_final, 2),
            "pool_ever_zero_with_retirees": pool_ever_zero,
            "total_longevity_payouts": round(res.total_longevity_payouts, 2),
            "total_longevity_backstop": round(res.total_longevity_backstop, 2),
            "peak_longevity_retirees": res.peak_longevity_retirees,
            "peak_per_capita": round(res.peak_longevity_per_capita, 2),
            "avg_per_capita": round(res.avg_longevity_per_capita, 2),
            "longevity_self_financing_ratio": round(
                res.total_longevity_payouts /
                max(1.0, res.total_longevity_payouts + res.total_longevity_backstop),
                4
            ),
            "trajectory": pool_trajectory,
        }

    return results


def print_report(tau_high: float, results: Dict) -> None:
    print("=" * 90)
    print("TONTINE LONGEVITY POOL SOLVENCY VERIFICATION")
    print("=" * 90)
    print()
    print(f"Config E: tau_high = {tau_high:.2%}, tontine enabled, reserve rule enabled")
    print(f"Horizon: 100 years | Annuity: 20 years (age 67-87) | Longevity: age 87-95")
    print(f"Floor: EUR 10,000/yr | Tontine cap: 3.0x floor (EUR 30,000/yr)")
    print()

    print(f"{'Scenario':<20} {'Pass':>5} {'Pool Min':>14} {'Pool Final':>14} "
          f"{'Pool Depl?':>10} {'Backstop':>14} {'Self-Fin%':>10} "
          f"{'Avg p.c.':>10} {'Peak p.c.':>10}")
    print("-" * 120)

    all_solvent = True
    for name, data in results.items():
        depl = "YES" if data["pool_ever_zero_with_retirees"] else "no"
        if data["pool_ever_zero_with_retirees"]:
            all_solvent = False
        sf = data["longevity_self_financing_ratio"]
        print(f"{name:<20} {'PASS' if data['passed'] else 'FAIL':>5} "
              f"{data['pool_min']:>14,.0f} {data['pool_final']:>14,.0f} "
              f"{depl:>10} {data['total_longevity_backstop']:>14,.0f} "
              f"{sf * 100:>9.1f}% "
              f"{data['avg_per_capita']:>10,.0f} {data['peak_per_capita']:>10,.0f}")

    print()
    if all_solvent:
        print("RESULT: Tontine longevity pool is SOLVENT in all scenarios.")
        print("        Pool never depletes while retirees are present.")
    else:
        depleted = [n for n, d in results.items() if d["pool_ever_zero_with_retirees"]]
        print(f"WARNING: Tontine pool depletes in {len(depleted)} scenario(s): {depleted}")
        print("         Backstop covers the gap, but tontine bonus is not sustainable.")

    # Tontine bonus analysis
    print()
    print("--- Tontine Bonus Analysis ---")
    for name, data in results.items():
        if data["avg_per_capita"] > 0:
            bonus = data["avg_per_capita"] - 10_000
            bonus_pct = bonus / 10_000 * 100
            print(f"  {name}: avg EUR {data['avg_per_capita']:,.0f}/yr "
                  f"(floor + {bonus_pct:+.1f}% tontine bonus)")


def main():
    parser = argparse.ArgumentParser(description="Tontine Solvency Verification")
    parser.add_argument("--json", type=str, default=None)
    parser.add_argument("--tau_high", type=float, default=None,
                        help="Override tau_high (default: auto-optimize)")
    args = parser.parse_args()

    print("Finding optimal tau_high for Config E...")
    tau_high = args.tau_high if args.tau_high else find_optimal_tau_high()
    print(f"  tau_high = {tau_high:.4f} ({tau_high * 100:.2f}%)")
    print()

    results = verify_solvency(tau_high)
    print_report(tau_high, results)

    if args.json:
        out_dir = os.path.dirname(args.json)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        # Strip trajectory for compact JSON (too large)
        compact = {}
        for name, data in results.items():
            compact[name] = {k: v for k, v in data.items() if k != "trajectory"}
        # Add summary trajectory (every 5 years) for the base scenario
        base_key = "base_1p7" if "base_1p7" in results else list(results.keys())[0]
        compact["_trajectory_sample"] = {
            "scenario": base_key,
            "note": "Every 5th year for base scenario",
            "data": [t for t in results[base_key]["trajectory"] if t["year"] % 5 == 0],
        }

        out_data = {
            "model": "Tontine Longevity Pool Solvency Verification",
            "config": "Config E",
            "tau_high": tau_high,
            "scenarios": compact,
        }
        with open(args.json, "w") as f:
            json.dump(out_data, f, indent=2)
        print(f"\nResults written to {args.json}")


if __name__ == "__main__":
    main()
