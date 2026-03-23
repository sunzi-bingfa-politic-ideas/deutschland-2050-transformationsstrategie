#!/usr/bin/env python3
"""
Generational Accounting: NPV of Lifetime Transfers by Birth Cohort

For each birth cohort (entry age 20), computes:
  - NPV of RSSP contributions paid (Low/Mid/High)
  - NPV of RSSP benefits received (Low/Mid only; High = 0)
  - NPV of GRV contributions paid (counterfactual)
  - NPV of GRV benefits received (counterfactual)
  - Net transfer = benefits - contributions (under each system)
  - Break-even cohort: first cohort where RSSP net > GRV net

Shows who wins, who loses, and when the system becomes Pareto-improving.

Usage:
    python src/generational_npv.py [--json out/generational_npv.json]
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GenAcctParams:
    # Demographics
    age_start: int = 20
    retire_age: int = 67
    max_age: int = 87          # annuity end (67 + 20)
    longevity_max: int = 95    # longevity pool end

    # Incomes (real EUR/yr at retire age)
    income_low: float = 22_000
    income_mid: float = 40_000
    income_high: float = 72_000   # 40k * 1.8

    # Population shares
    share_low: float = 0.30
    share_mid: float = 0.50
    share_high: float = 0.20

    # RSSP parameters (Config D/E)
    tau_low: float = 0.12
    tau_mid: float = 0.13
    tau_high: float = 0.1275    # Config E

    guarantee_low: float = 0.85
    guarantee_mid: float = 0.60

    longevity_floor: float = 10_000   # EUR/yr post-annuity

    # GRV counterfactual
    grv_rate: float = 0.186         # current total (AN+AG)
    grv_rate_projected: float = 0.22  # Werding 2060 projection
    bbg: float = 90_600             # Beitragsbemessungsgrenze
    grv_replacement: float = 0.48   # current replacement rate
    grv_replacement_projected: float = 0.42  # projected 2040

    # Discount rate (real)
    discount_rate: float = 0.02

    # Mortality (cumulative survival from retire_age, per year)
    # Simplified: constant annual survival rates by age bracket
    mortality_buckets: list = field(default_factory=lambda: [
        (67, 74, 0.982),
        (75, 84, 0.955),
        (85, 95, 0.88),
        (96, 200, 0.72),
    ])

    # Transition: which year the cohort enters (0 = first RSSP cohort)
    # Cohorts entering before year 0 are pure GRV
    first_rssp_year: int = 0
    n_cohorts: int = 80   # simulate 80 cohorts (year 0 to year 79)


def survival_at_age(buckets, age_from, age_to):
    """Cumulative survival probability from age_from to age_to."""
    s = 1.0
    for a in range(age_from, age_to):
        for (lo, hi, rate) in buckets:
            if lo <= a <= hi:
                s *= rate
                break
    return s


@dataclass
class CohortResult:
    entry_year: int
    group: str          # low / mid / high

    # RSSP
    rssp_contributions_npv: float
    rssp_benefits_npv: float
    rssp_net_npv: float    # benefits - contributions

    # GRV counterfactual (projected rates)
    grv_contributions_npv: float
    grv_benefits_npv: float
    grv_net_npv: float     # benefits - contributions

    # Delta
    rssp_advantage_npv: float   # rssp_net - grv_net (positive = RSSP better)
    rssp_advantage_annual: float  # annualized over working + retirement years


def simulate_cohort(p: GenAcctParams, entry_year: int, group: str) -> CohortResult:
    """Compute NPV of lifetime transfers for one cohort and income group."""
    work_years = p.retire_age - p.age_start
    annuity_years = p.max_age - p.retire_age
    longevity_years = p.longevity_max - p.max_age

    # Select income and rates
    if group == "low":
        income = p.income_low
        tau_rssp = p.tau_low
        guarantee = p.guarantee_low
    elif group == "mid":
        income = p.income_mid
        tau_rssp = p.tau_mid
        guarantee = p.guarantee_mid
    else:  # high
        income = p.income_high
        tau_rssp = p.tau_high
        guarantee = 0.0  # no benefits

    # GRV income (capped at BBG)
    grv_income = min(income, p.bbg)

    r = p.discount_rate

    # --- RSSP contributions NPV ---
    rssp_contrib_npv = 0.0
    for t in range(work_years):
        rssp_contrib_npv += tau_rssp * income / (1 + r) ** t

    # --- RSSP benefits NPV ---
    rssp_benefit_npv = 0.0
    if group != "high":
        # Annuity phase (age 67-87): guaranteed replacement rate
        annual_pension = guarantee * income
        for t in range(annuity_years):
            age = p.retire_age + t
            surv = survival_at_age(p.mortality_buckets, p.retire_age, age)
            year_from_start = work_years + t
            rssp_benefit_npv += annual_pension * surv / (1 + r) ** year_from_start

        # Longevity phase (age 87-95): floor payment
        for t in range(longevity_years):
            age = p.max_age + t
            surv = survival_at_age(p.mortality_buckets, p.retire_age, age)
            year_from_start = work_years + annuity_years + t
            rssp_benefit_npv += p.longevity_floor * surv / (1 + r) ** year_from_start

    rssp_net = rssp_benefit_npv - rssp_contrib_npv

    # --- GRV counterfactual (projected rates) ---
    grv_contrib_npv = 0.0
    for t in range(work_years):
        grv_contrib_npv += p.grv_rate_projected * grv_income / (1 + r) ** t

    grv_benefit_npv = 0.0
    # GRV pays to all groups (including high, but capped at BBG-based pension)
    grv_annual_pension = p.grv_replacement_projected * grv_income
    for t in range(annuity_years + longevity_years):
        age = p.retire_age + t
        if age > p.longevity_max:
            break
        surv = survival_at_age(p.mortality_buckets, p.retire_age, age)
        year_from_start = work_years + t
        grv_benefit_npv += grv_annual_pension * surv / (1 + r) ** year_from_start

    grv_net = grv_benefit_npv - grv_contrib_npv

    # Delta
    rssp_advantage = rssp_net - grv_net
    total_years = work_years + annuity_years
    # Annualize the NPV advantage
    if total_years > 0 and r > 0:
        annuity_factor = (1 - (1 + r) ** (-total_years)) / r
        rssp_advantage_annual = rssp_advantage / annuity_factor if annuity_factor > 0 else 0
    else:
        rssp_advantage_annual = rssp_advantage / max(1, total_years)

    return CohortResult(
        entry_year=entry_year,
        group=group,
        rssp_contributions_npv=round(rssp_contrib_npv, 2),
        rssp_benefits_npv=round(rssp_benefit_npv, 2),
        rssp_net_npv=round(rssp_net, 2),
        grv_contributions_npv=round(grv_contrib_npv, 2),
        grv_benefits_npv=round(grv_benefit_npv, 2),
        grv_net_npv=round(grv_net, 2),
        rssp_advantage_npv=round(rssp_advantage, 2),
        rssp_advantage_annual=round(rssp_advantage_annual, 2),
    )


def simulate_all(p: GenAcctParams) -> List[CohortResult]:
    """Simulate all cohorts for all income groups."""
    results = []
    for year in range(p.n_cohorts):
        for group in ["low", "mid", "high"]:
            results.append(simulate_cohort(p, year, group))
    return results


def find_breakeven(results: List[CohortResult], group: str) -> Optional[int]:
    """Find first cohort year where RSSP advantage is positive."""
    for r in results:
        if r.group == group and r.rssp_advantage_npv > 0:
            return r.entry_year
    return None


def print_report(results: List[CohortResult], p: GenAcctParams) -> None:
    print("=" * 100)
    print("GENERATIONAL ACCOUNTING: NPV of Lifetime Transfers by Birth Cohort")
    print("=" * 100)
    print()
    print(f"Discount rate: {p.discount_rate:.1%} real | RSSP tau_high: {p.tau_high:.2%}")
    print(f"GRV projected: {p.grv_rate_projected:.1%} rate, {p.grv_replacement_projected:.0%} replacement")
    print(f"Mortality: Destatis 2022/2024 corrected | BBG: EUR {p.bbg:,.0f}")
    print()

    for group in ["low", "mid", "high"]:
        group_results = [r for r in results if r.group == group]

        print(f"--- {group.upper()} Earner Group ---")
        print()
        print(f"{'Cohort':>7} {'RSSP Contrib':>14} {'RSSP Benefit':>14} {'RSSP Net':>14} "
              f"{'GRV Contrib':>14} {'GRV Benefit':>14} {'GRV Net':>14} {'Advantage':>14}")
        print("-" * 105)

        # Show every 5th cohort
        for r in group_results:
            if r.entry_year % 5 == 0 or r.entry_year == 0:
                adv_sign = "+" if r.rssp_advantage_npv >= 0 else ""
                print(f"  Y{r.entry_year:>4} {r.rssp_contributions_npv:>14,.0f} "
                      f"{r.rssp_benefits_npv:>14,.0f} {r.rssp_net_npv:>14,.0f} "
                      f"{r.grv_contributions_npv:>14,.0f} {r.grv_benefits_npv:>14,.0f} "
                      f"{r.grv_net_npv:>14,.0f} {adv_sign}{r.rssp_advantage_npv:>13,.0f}")

        breakeven = find_breakeven(group_results, group)
        print()
        if breakeven is not None:
            if breakeven == 0:
                print(f"  RSSP advantage from Year 0 (all cohorts benefit).")
            else:
                print(f"  Break-even: Cohort entering in Year {breakeven}")
        else:
            print(f"  No break-even within {p.n_cohorts} cohorts (GRV always better).")
        print()

    # Summary
    print("--- Summary: Who Wins, Who Loses ---")
    print()
    for group in ["low", "mid", "high"]:
        group_results = [r for r in results if r.group == group]
        year0 = group_results[0]
        year40 = [r for r in group_results if r.entry_year == 40]
        year40 = year40[0] if year40 else year0

        income = {"low": p.income_low, "mid": p.income_mid, "high": p.income_high}[group]
        print(f"  {group.upper()} (EUR {income:,.0f}/yr):")
        print(f"    Year 0 cohort: RSSP net = EUR {year0.rssp_net_npv:,.0f}, "
              f"GRV net = EUR {year0.grv_net_npv:,.0f}, "
              f"advantage = EUR {year0.rssp_advantage_npv:+,.0f}")
        print(f"    Year 40 cohort: RSSP net = EUR {year40.rssp_net_npv:,.0f}, "
              f"GRV net = EUR {year40.grv_net_npv:,.0f}, "
              f"advantage = EUR {year40.rssp_advantage_npv:+,.0f}")
        print()


def make_json(results: List[CohortResult], p: GenAcctParams) -> dict:
    scenarios = []
    for r in results:
        scenarios.append({
            "entry_year": r.entry_year,
            "group": r.group,
            "rssp_contributions_npv": r.rssp_contributions_npv,
            "rssp_benefits_npv": r.rssp_benefits_npv,
            "rssp_net_npv": r.rssp_net_npv,
            "grv_contributions_npv": r.grv_contributions_npv,
            "grv_benefits_npv": r.grv_benefits_npv,
            "grv_net_npv": r.grv_net_npv,
            "rssp_advantage_npv": r.rssp_advantage_npv,
            "rssp_advantage_annual": r.rssp_advantage_annual,
        })

    # Summary
    summary = {}
    for group in ["low", "mid", "high"]:
        gr = [r for r in results if r.group == group]
        breakeven = find_breakeven(gr, group)
        summary[group] = {
            "breakeven_year": breakeven,
            "year0_rssp_net": gr[0].rssp_net_npv if gr else None,
            "year0_grv_net": gr[0].grv_net_npv if gr else None,
            "year0_advantage": gr[0].rssp_advantage_npv if gr else None,
        }

    return {
        "model": "Generational Accounting: NPV of Lifetime Transfers",
        "parameters": {
            "discount_rate": p.discount_rate,
            "grv_rate_projected": p.grv_rate_projected,
            "grv_replacement_projected": p.grv_replacement_projected,
            "rssp_tau_high": p.tau_high,
            "bbg": p.bbg,
        },
        "summary": summary,
        "cohorts": scenarios,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generational Accounting: NPV by Birth Cohort"
    )
    parser.add_argument("--json", type=str, default=None)
    parser.add_argument("--discount", type=float, default=0.02,
                        help="Real discount rate (default: 2%%)")
    parser.add_argument("--grv_rate", type=float, default=0.22,
                        help="Projected GRV contribution rate (default: 22%%)")
    parser.add_argument("--grv_replacement", type=float, default=0.42,
                        help="Projected GRV replacement rate (default: 42%%)")
    args = parser.parse_args()

    p = GenAcctParams(
        discount_rate=args.discount,
        grv_rate_projected=args.grv_rate,
        grv_replacement_projected=args.grv_replacement,
    )

    results = simulate_all(p)
    print_report(results, p)

    if args.json:
        out_dir = os.path.dirname(args.json)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.json, "w") as f:
            json.dump(make_json(results, p), f, indent=2)
        print(f"\nResults written to {args.json}")


if __name__ == "__main__":
    main()
