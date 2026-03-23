# Rentenreform/RSSP_v2/src/report.py
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, replace
from typing import Dict, List

from model import Params, simulate, MortalityBucket
from scenarios import load_scenarios_const, load_scenarios_paths
from utils import frange, load_yaml


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--scenarios", required=True)
    ap.add_argument("--mode", choices=["const", "paths"], required=True)
    ap.add_argument("--out_csv", default="Rentenreform/RSSP_v2/out/truth_table.csv")
    args = ap.parse_args()

    base = load_yaml(args.base)
    scen = load_yaml(args.scenarios)
    scenarios = load_scenarios_const(scen) if args.mode == "const" else load_scenarios_paths(scen)

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

    p0 = Params(
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
    )

    search = base["tau_high_search"]
    grid = frange(float(search["start"]), float(search["end"]), float(search["step"]))

    import os
    os.makedirs(os.path.dirname(args.out_csv), exist_ok=True)

    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tau_high", "scenario", "passed", "fail_years_last10", "min_repl_low", "min_repl_mid", "min_pool", "max_state_loan", "final_state_loan"])

        for tau_h in grid:
            p = replace(p0, tau_high=tau_h,
                         mortality_buckets=list(p0.mortality_buckets),
                         cohort_path=list(p0.cohort_path))
            for name, ret in scenarios.items():
                res = simulate(p, returns=ret, scenario_name=name, pass_last_n_years=10)
                w.writerow([tau_h, name, int(res.passed), res.fail_years, res.min_repl_low, res.min_repl_mid, res.min_pool, res.max_state_loan, res.final_state_loan])

    print(f"Wrote {args.out_csv}")


if __name__ == "__main__":
    main()
