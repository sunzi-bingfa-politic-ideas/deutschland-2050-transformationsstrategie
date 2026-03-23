# Rentenreform/RSSP_v2/src/optimize.py
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Dict, List, Tuple

from model import Params, simulate, MortalityBucket
from scenarios import load_scenarios_const, load_scenarios_paths
from utils import frange, load_yaml


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="params/base.yaml")
    ap.add_argument("--scenarios", required=True, help="params/scenarios_const.yaml OR scenarios_paths.yaml")
    ap.add_argument("--mode", choices=["const", "paths"], required=True)
    ap.add_argument("--out", default="Rentenreform/RSSP_v2/out/best.json")
    ap.add_argument("--min_horizon", type=int, default=100,
                     help="Minimum horizon_years (overrides base.yaml if larger)")
    args = ap.parse_args()

    base = load_yaml(args.base)
    scen = load_yaml(args.scenarios)

    if args.mode == "const":
        scenarios = load_scenarios_const(scen)
    else:
        scenarios = load_scenarios_paths(scen)

    # Parse Haertung 1: Mortalitaet
    mort = base.get("mortality", {})
    mort_enabled = bool(mort.get("enabled", True))
    mort_buckets = []
    for b in mort.get("buckets", []):
        mort_buckets.append(
            MortalityBucket(
                age_min=int(b["age_min"]),
                age_max=int(b["age_max"]),
                survival=float(b["survival"]),
            )
        )

    # Parse Haertung 2: Demografie
    demo = base.get("demography", {})
    demo_mode = str(demo.get("mode", "constant"))
    cohort_path = [int(x) for x in demo.get("cohort_path", [])]

    # Parse Haertung 3: Backstop
    back = base.get("backstop", {})
    back_enabled = bool(back.get("enabled", True))
    loan_cap = float(back.get("loan_cap_asset_share", 0.10))
    repay_share = float(back.get("repay_share", 0.50))
    reserve_years = int(back.get("reserve_years", 3))

    # Parse Haertung 4: Age-income profiles
    inc_prof = base.get("income_profile", {})
    income_profile_enabled = bool(inc_prof.get("enabled", False))
    income_profile = [float(x) for x in inc_prof.get("profile", [])]

    # Parse Haertung 5: Longevity pool
    long = base.get("longevity", {})
    longevity_pool_enabled = bool(long.get("enabled", True))
    longevity_floor = float(long.get("floor", 10000.0))
    longevity_max_age = int(long.get("max_age", 95))
    longevity_surplus_share = float(long.get("surplus_share", 0.20))
    tontine_enabled = bool(long.get("tontine_enabled", True))
    tontine_cap_multiple = float(long.get("tontine_cap_multiple", 3.0))

    # Parse Haertung 6: Reserve rule
    res = base.get("reserve_rule", {})
    reserve_rule_enabled = bool(res.get("enabled", False))
    reserve_trigger_high = float(res.get("trigger_high", 0.03))
    reserve_trigger_low = float(res.get("trigger_low", 0.01))
    reserve_target_return = float(res.get("target_return", 0.02))
    reserve_skim_fraction = float(res.get("skim_fraction", 0.30))
    reserve_inject_fraction = float(res.get("inject_fraction", 0.30))
    reserve_safe_rate = float(res.get("safe_rate", 0.005))

    horizon = max(int(base["horizon_years"]), args.min_horizon)

    p = Params(
        horizon_years=horizon,
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
        guarantee_low=float(base["guarantee_low"]),
        guarantee_mid=float(base["guarantee_mid"]),
        tau_high=0.0,
        mortality_enabled=mort_enabled,
        mortality_buckets=mort_buckets,
        demography_mode=demo_mode,
        cohort_path=cohort_path,
        backstop_enabled=back_enabled,
        loan_cap_asset_share=loan_cap,
        repay_share=repay_share,
        reserve_years=reserve_years,
        income_profile_enabled=income_profile_enabled,
        income_profile=income_profile,
        longevity_pool_enabled=longevity_pool_enabled,
        longevity_floor=longevity_floor,
        longevity_max_age=longevity_max_age,
        longevity_surplus_share=longevity_surplus_share,
        tontine_enabled=tontine_enabled,
        tontine_cap_multiple=tontine_cap_multiple,
        reserve_rule_enabled=reserve_rule_enabled,
        reserve_trigger_high=reserve_trigger_high,
        reserve_trigger_low=reserve_trigger_low,
        reserve_target_return=reserve_target_return,
        reserve_skim_fraction=reserve_skim_fraction,
        reserve_inject_fraction=reserve_inject_fraction,
        reserve_safe_rate=reserve_safe_rate,
    )

    search = base["tau_high_search"]
    grid = frange(float(search["start"]), float(search["end"]), float(search["step"]))

    best = None
    best_details = None

    for tau_h in grid:
        p.tau_high = tau_h

        all_pass = True
        worst = {"min_repl_low": 10.0, "min_repl_mid": 10.0, "min_pool": 1e99, "max_state_loan": 0.0, "fail_years": 0}
        per_scenario = {}

        for name, ret in scenarios.items():
            res = simulate(p, returns=ret, scenario_name=name, pass_last_n_years=10)
            per_scenario[name] = {
                "passed": res.passed,
                "fail_years": res.fail_years,
                "min_repl_low": res.min_repl_low,
                "min_repl_mid": res.min_repl_mid,
                "min_pool": res.min_pool,
                "max_state_loan": res.max_state_loan,
                "final_state_loan": res.final_state_loan,
                "pool_depletion_year": res.pool_depletion_year,
                "steady_state_deficit": res.steady_state_deficit,
                "is_structurally_sustainable": res.is_structurally_sustainable,
                "loan_ever_repaid": res.loan_ever_repaid,
                "max_loan_to_assets_ratio": res.max_loan_to_assets_ratio,
                "final_longevity_pool": res.final_longevity_pool,
                "total_longevity_payouts": res.total_longevity_payouts,
                "total_longevity_backstop": res.total_longevity_backstop,
                "peak_longevity_retirees": res.peak_longevity_retirees,
            }
            all_pass = all_pass and res.passed
            worst["min_repl_low"] = min(worst["min_repl_low"], res.min_repl_low)
            worst["min_repl_mid"] = min(worst["min_repl_mid"], res.min_repl_mid)
            worst["min_pool"] = min(worst["min_pool"], res.min_pool)
            worst["max_state_loan"] = max(worst["max_state_loan"], res.max_state_loan)
            worst["fail_years"] = max(worst["fail_years"], res.fail_years)

        if all_pass:
            best = tau_h
            best_details = {"tau_high": tau_h, "worst": worst, "per_scenario": per_scenario}
            break

    out_obj = {
        "found": best is not None,
        "best_tau_high": best,
        "base_params": asdict(p),
        "details": best_details,
    }

    import os
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, indent=2)

    print(json.dumps(out_obj, indent=2))


if __name__ == "__main__":
    main()
