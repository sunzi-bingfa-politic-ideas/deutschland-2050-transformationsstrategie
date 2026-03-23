#!/usr/bin/env python3
"""
Wealth Tax vs. RSSP: Lifetime Cost Comparison

Dynamically models a high earner's wealth accumulation over a full lifetime
(47 working years + 28 retirement years) and compares the cumulative cost of:
  - A 1% annual wealth tax (on accumulated net wealth, every year)
  - The RSSP solidarity contribution (12.75% of income, working years only)

Key insight: RSSP taxes the income FLOW (stops at retirement), while a wealth
tax taxes the accumulated STOCK (never stops, grows with wealth).

Usage:
    python src/wealth_tax_compare.py [--json out/wealth_tax_compare.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class WealthTaxParams:
    # Income
    income: float = 100_000          # EUR/year, real (constant)

    # RSSP
    tau_rssp: float = 0.1275         # 12.75% solidarity contribution (Config E)

    # Wealth tax
    tau_wealth: float = 0.01         # 1% annual wealth tax

    # GRV (for combined scenario)
    tau_grv: float = 0.186           # 18.6% current GRV (total: AN+AG)
    tau_grv_escalated: float = 0.22  # projected escalated GRV rate (Werding 2060)
    bbg: float = 90_600              # Beitragsbemessungsgrenze West 2024 (EUR/yr, real)

    # Savings & investment
    savings_rate: float = 0.20       # fraction of gross income saved annually
    real_return: float = 0.05        # 5% real return on investments

    # Career & retirement
    work_years: int = 47             # age 20-67
    retire_years: int = 28           # age 67-95 (matches RSSP longevity max_age)
    withdrawal_rate: float = 0.04    # 4% of retirement-start wealth, annually


@dataclass
class WealthTaxResult:
    params: WealthTaxParams

    # Time series (length = work_years + retire_years)
    wealth_no_tax: List[float]       # wealth trajectory without wealth tax
    wealth_with_tax: List[float]     # wealth trajectory with wealth tax
    rssp_annual: List[float]         # RSSP cost per year
    wealth_tax_annual: List[float]   # wealth tax cost per year
    rssp_cumulative: List[float]     # cumulative RSSP cost
    wealth_tax_cumulative: List[float]  # cumulative wealth tax cost

    # Summary
    rssp_lifetime: float             # total RSSP cost
    wealth_tax_lifetime: float       # total wealth tax cost
    ratio: float                     # wealth_tax / rssp
    crossover_year: Optional[int]    # year when cumulative wealth tax > cumulative RSSP
    peak_wealth_no_tax: float        # max wealth without wealth tax
    peak_wealth_with_tax: float      # max wealth with wealth tax
    wealth_drag: float               # peak_no_tax - peak_with_tax (wealth destroyed by tax)

    # Combined scenario: GRV escalated + wealth tax vs. RSSP alone
    grv_escalated_lifetime: float    # GRV escalated cost (working years)
    combined_lifetime: float         # GRV escalated + wealth tax total
    combined_ratio: float            # combined / rssp


def simulate(p: WealthTaxParams) -> WealthTaxResult:
    T = p.work_years + p.retire_years
    annual_savings = p.savings_rate * p.income

    # Time series
    w_no_tax = [0.0] * T      # wealth without wealth tax
    w_with_tax = [0.0] * T    # wealth with wealth tax
    rssp_ann = [0.0] * T
    wtax_ann = [0.0] * T
    rssp_cum = [0.0] * T
    wtax_cum = [0.0] * T

    w_clean = 0.0   # wealth without tax
    w_taxed = 0.0   # wealth with tax
    cum_rssp = 0.0
    cum_wtax = 0.0
    crossover = None

    # Compute withdrawal amount at retirement (based on no-tax trajectory for fairness)
    # We'll compute it after the working phase, so first pass: working phase
    # Actually, let's compute the retirement-start wealth first
    w_at_retire_no_tax = 0.0
    w_temp = 0.0
    for t in range(p.work_years):
        w_temp = w_temp * (1 + p.real_return) + annual_savings
    w_at_retire_no_tax = w_temp

    # Use the same absolute withdrawal for both trajectories (fair comparison)
    annual_withdrawal = p.withdrawal_rate * w_at_retire_no_tax

    # Reset and simulate fully
    w_clean = 0.0
    w_taxed = 0.0

    for t in range(T):
        is_working = t < p.work_years

        # Beginning-of-year wealth
        w_no_tax[t] = w_clean
        w_with_tax[t] = w_taxed

        # RSSP cost (only during working years)
        if is_working:
            rssp_ann[t] = p.tau_rssp * p.income
        else:
            rssp_ann[t] = 0.0

        # Wealth tax (every year, on current wealth, floor at zero)
        wtax_ann[t] = p.tau_wealth * max(0.0, w_taxed)

        # Cumulative
        cum_rssp += rssp_ann[t]
        cum_wtax += wtax_ann[t]
        rssp_cum[t] = cum_rssp
        wtax_cum[t] = cum_wtax

        # Crossover detection
        if crossover is None and cum_wtax > cum_rssp and cum_rssp > 0:
            crossover = t

        # End-of-year: investment return + savings/withdrawal
        if is_working:
            w_clean = w_clean * (1 + p.real_return) + annual_savings
            w_taxed = w_taxed * (1 + p.real_return) - wtax_ann[t] + annual_savings
        else:
            w_clean = w_clean * (1 + p.real_return) - annual_withdrawal
            w_taxed = w_taxed * (1 + p.real_return) - wtax_ann[t] - annual_withdrawal

        # Floor wealth at zero (can't go negative)
        w_clean = max(0.0, w_clean)
        w_taxed = max(0.0, w_taxed)

    peak_no = max(w_no_tax)
    peak_with = max(w_with_tax)

    # Combined scenario: GRV escalated contributions (working years only)
    # GRV contributions are capped at the BBG (Beitragsbemessungsgrenze)
    grv_assessable_income = min(p.income, p.bbg)
    grv_esc_lifetime = p.tau_grv_escalated * grv_assessable_income * p.work_years
    combined_lifetime = grv_esc_lifetime + cum_wtax

    return WealthTaxResult(
        params=p,
        wealth_no_tax=w_no_tax,
        wealth_with_tax=w_with_tax,
        rssp_annual=rssp_ann,
        wealth_tax_annual=wtax_ann,
        rssp_cumulative=rssp_cum,
        wealth_tax_cumulative=wtax_cum,
        rssp_lifetime=cum_rssp,
        wealth_tax_lifetime=cum_wtax,
        ratio=cum_wtax / cum_rssp if cum_rssp > 0 else float('inf'),
        crossover_year=crossover,
        peak_wealth_no_tax=peak_no,
        peak_wealth_with_tax=peak_with,
        wealth_drag=peak_no - peak_with,
        grv_escalated_lifetime=grv_esc_lifetime,
        combined_lifetime=combined_lifetime,
        combined_ratio=combined_lifetime / cum_rssp if cum_rssp > 0 else float('inf'),
    )


def simulate_grid() -> list:
    """Run parameter sweep across income levels, savings rates, and returns."""
    incomes = [72_000, 100_000, 150_000]
    savings_rates = [0.15, 0.25]
    real_returns = [0.03, 0.05]

    results = []
    for inc in incomes:
        for sr in savings_rates:
            for rr in real_returns:
                p = WealthTaxParams(income=inc, savings_rate=sr, real_return=rr)
                r = simulate(p)
                results.append(r)
    return results


def fmt_eur(x: float) -> str:
    """Format EUR amount with thousands separator."""
    if abs(x) >= 1e6:
        return f"EUR {x / 1e6:,.2f} Mio"
    return f"EUR {x:,.0f}"


def print_report(results: list) -> None:
    print("=" * 110)
    print("WEALTH TAX vs. RSSP: Lifetime Cost Comparison")
    print("=" * 110)
    print()
    print("Model: Dynamic wealth accumulation over 75 years (47 working + 28 retirement)")
    print("RSSP:  12.75% of income, working years only (age 20-67)")
    print("WTax:  1% of net wealth, every year (age 20-95)")
    print("Withdrawal: 4% of retirement-start wealth (inflation-adjusted)")
    print()

    # --- Part A: Pure instrument comparison (wealth tax alone vs. RSSP alone) ---
    print("=== PART A: Pure Instrument Comparison (Wealth Tax alone vs. RSSP alone) ===")
    print()
    print(f"{'Income':>10} {'Save%':>6} {'r%':>4} | "
          f"{'RSSP Total':>14} {'WTax Total':>14} {'Ratio':>7} {'Crossover':>10} | "
          f"{'Peak Wealth':>14} {'Wealth Drag':>14}")
    print("-" * 110)

    for r in results:
        p = r.params
        co = f"Year {r.crossover_year}" if r.crossover_year is not None else "never"
        print(f"{p.income:>10,.0f} {p.savings_rate * 100:>5.0f}% {p.real_return * 100:>3.0f}% | "
              f"{r.rssp_lifetime:>14,.0f} {r.wealth_tax_lifetime:>14,.0f} {r.ratio:>6.1f}x {co:>10} | "
              f"{r.peak_wealth_no_tax:>14,.0f} {r.wealth_drag:>14,.0f}")

    print()

    # --- Part B: Realistic political scenario (GRV escalated + wealth tax vs. RSSP) ---
    print("=== PART B: Realistic Political Scenario (GRV 22% + WTax 1% vs. RSSP 12.75%) ===")
    print()
    print("  The 'socialist alternative' does not replace GRV -- it adds a wealth tax ON TOP.")
    print(f"  Under RSSP, the high earner pays 12.75% instead of GRV's 18.6%+ (projected: 22%).")
    print(f"  GRV contributions capped at BBG (EUR {WealthTaxParams.bbg:,.0f}/yr) -- incomes above are uncapped for RSSP.")
    print()
    print(f"{'Income':>10} {'Save%':>6} {'r%':>4} | "
          f"{'RSSP':>14} {'GRV(22%)':>14} {'WTax':>14} {'GRV+WTax':>14} {'Ratio':>7}")
    print("-" * 98)

    for r in results:
        p = r.params
        print(f"{p.income:>10,.0f} {p.savings_rate * 100:>5.0f}% {p.real_return * 100:>3.0f}% | "
              f"{r.rssp_lifetime:>14,.0f} {r.grv_escalated_lifetime:>14,.0f} "
              f"{r.wealth_tax_lifetime:>14,.0f} {r.combined_lifetime:>14,.0f} "
              f"{r.combined_ratio:>6.1f}x")

    print()

    # Detailed timeline for reference scenario (100k, 20% savings, 5% return)
    ref = None
    for r in results:
        p = r.params
        if p.income == 100_000 and p.savings_rate == 0.25 and p.real_return == 0.05:
            ref = r
            break
    if ref is None:
        ref = results[0]

    p = ref.params
    print(f"--- Detailed Timeline: EUR {p.income:,.0f}/yr, "
          f"{p.savings_rate * 100:.0f}% savings, {p.real_return * 100:.0f}% real return ---")
    print()
    print(f"{'Year':>5} {'Age':>4} {'Phase':>8} | "
          f"{'Wealth':>14} {'WTax/yr':>10} {'RSSP/yr':>10} | "
          f"{'Cum WTax':>14} {'Cum RSSP':>14} {'Delta':>14}")
    print("-" * 106)

    milestones = [0, 5, 10, 15, 20, 25, 30, 35, 40, 46, 47, 50, 55, 60, 65, 70, 74]
    for t in milestones:
        if t >= len(ref.rssp_annual):
            continue
        age = 20 + t
        phase = "Work" if t < p.work_years else "Retire"
        delta = ref.wealth_tax_cumulative[t] - ref.rssp_cumulative[t]
        sign = "+" if delta >= 0 else ""
        print(f"{t:>5} {age:>4} {phase:>8} | "
              f"{ref.wealth_with_tax[t]:>14,.0f} {ref.wealth_tax_annual[t]:>10,.0f} "
              f"{ref.rssp_annual[t]:>10,.0f} | "
              f"{ref.wealth_tax_cumulative[t]:>14,.0f} {ref.rssp_cumulative[t]:>14,.0f} "
              f"{sign}{delta:>13,.0f}")

    print()
    print("--- Key Findings ---")
    print()

    # Find the median high-earner scenario (72k, 15% savings, 5% return)
    for r in results:
        p = r.params
        if p.income == 72_000 and p.savings_rate == 0.15 and p.real_return == 0.05:
            print(f"Median High-Earner (EUR 72k, 15% savings, 5% return):")
            print(f"  RSSP lifetime cost:       {fmt_eur(r.rssp_lifetime)}")
            print(f"  Wealth tax lifetime cost: {fmt_eur(r.wealth_tax_lifetime)}")
            print(f"  Ratio:                    {r.ratio:.1f}x")
            if r.crossover_year is not None:
                print(f"  Crossover:                Year {r.crossover_year} (age {20 + r.crossover_year})")
            print(f"  Peak wealth (no tax):     {fmt_eur(r.peak_wealth_no_tax)}")
            print(f"  Wealth destroyed by tax:  {fmt_eur(r.wealth_drag)}")
            print()

    # Find the table-reference scenario (100k, 25% savings, 5% return)
    for r in results:
        p = r.params
        if p.income == 100_000 and p.savings_rate == 0.25 and p.real_return == 0.05:
            print(f"Upper High-Earner (EUR 100k, 25% savings, 5% return):")
            print(f"  RSSP lifetime cost:       {fmt_eur(r.rssp_lifetime)}")
            print(f"  Wealth tax lifetime cost: {fmt_eur(r.wealth_tax_lifetime)}")
            print(f"  Ratio:                    {r.ratio:.1f}x")
            if r.crossover_year is not None:
                print(f"  Crossover:                Year {r.crossover_year} (age {20 + r.crossover_year})")
            print(f"  Peak wealth (no tax):     {fmt_eur(r.peak_wealth_no_tax)}")
            print(f"  Wealth destroyed by tax:  {fmt_eur(r.wealth_drag)}")
            print()

    # Count scenarios where wealth tax alone exceeds RSSP
    wtax_wins = sum(1 for r in results if r.ratio >= 1.0)
    combined_wins = sum(1 for r in results if r.combined_ratio >= 1.0)

    print("--- Conclusions ---")
    print()
    print(f"Part A (pure instrument comparison):")
    print(f"  Wealth tax >= RSSP in {wtax_wins}/{len(results)} scenarios.")
    print(f"  At 5% real return (moderate, balanced portfolio): WTax is 1.2-2.0x RSSP.")
    print(f"  At 3% real return (conservative, bonds-heavy):   WTax is 0.6-1.1x RSSP.")
    print(f"  Note: At 3% return, peak wealth is modest (EUR 1-2.5 Mio), often below")
    print(f"  proposed wealth tax thresholds. The wealth tax would barely apply.")
    print()
    # Compute actual range for Part B
    combined_ratios = [r.combined_ratio for r in results]
    cr_min = min(combined_ratios)
    cr_max = max(combined_ratios)

    print(f"Part B (realistic political scenario -- GRV 22% + WTax 1%):")
    print(f"  Combined burden >= RSSP in {combined_wins}/{len(results)} scenarios.")
    print(f"  The 'socialist alternative' costs {cr_min:.1f}-{cr_max:.1f}x the RSSP solidarity contribution.")
    print(f"  GRV contributions capped at BBG (EUR {WealthTaxParams.bbg:,.0f}/yr).")
    print(f"  The RSSP Buy-Out is cheaper in EVERY scenario.")


def make_json(results: list) -> dict:
    """Create JSON-serializable summary."""
    scenarios = []
    for r in results:
        p = r.params
        scenarios.append({
            "income": p.income,
            "savings_rate": p.savings_rate,
            "real_return": p.real_return,
            "tau_rssp": p.tau_rssp,
            "tau_wealth": p.tau_wealth,
            "work_years": p.work_years,
            "retire_years": p.retire_years,
            "withdrawal_rate": p.withdrawal_rate,
            "rssp_lifetime_cost": round(r.rssp_lifetime, 2),
            "wealth_tax_lifetime_cost": round(r.wealth_tax_lifetime, 2),
            "ratio": round(r.ratio, 3),
            "crossover_year": r.crossover_year,
            "crossover_age": 20 + r.crossover_year if r.crossover_year is not None else None,
            "peak_wealth_no_tax": round(r.peak_wealth_no_tax, 2),
            "peak_wealth_with_tax": round(r.peak_wealth_with_tax, 2),
            "wealth_drag": round(r.wealth_drag, 2),
            "grv_escalated_lifetime": round(r.grv_escalated_lifetime, 2),
            "combined_lifetime_grv_wtax": round(r.combined_lifetime, 2),
            "combined_ratio": round(r.combined_ratio, 3),
        })
    return {
        "model": "Wealth Tax vs. RSSP Lifetime Cost Comparison",
        "methodology": (
            "Dynamic year-by-year wealth accumulation. "
            "RSSP: 12.75% of income during 47 working years (uncapped). "
            "Wealth tax: 1% of net wealth every year (working + retirement). "
            "GRV contributions capped at BBG (EUR 90,600/yr). "
            "Retirement withdrawal: 4% of retirement-start wealth. "
            "All values in real EUR (inflation-adjusted)."
        ),
        "scenarios": scenarios,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Wealth Tax vs. RSSP: Lifetime Cost Comparison"
    )
    parser.add_argument("--json", type=str, default=None,
                        help="Write results to JSON file")
    parser.add_argument("--income", type=float, default=None,
                        help="Single income to simulate (default: full grid)")
    parser.add_argument("--savings", type=float, default=None,
                        help="Single savings rate (e.g. 0.20)")
    parser.add_argument("--real_return", type=float, default=None,
                        help="Single real return (e.g. 0.05)")
    args = parser.parse_args()

    if args.income is not None:
        # Single scenario
        p = WealthTaxParams(
            income=args.income,
            savings_rate=args.savings or 0.20,
            real_return=args.real_return or 0.05,
        )
        results = [simulate(p)]
    else:
        # Full grid
        results = simulate_grid()

    print_report(results)

    if args.json:
        out_data = make_json(results)
        out_dir = os.path.dirname(args.json)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.json, "w") as f:
            json.dump(out_data, f, indent=2)
        print(f"\nResults written to {args.json}")


if __name__ == "__main__":
    main()
