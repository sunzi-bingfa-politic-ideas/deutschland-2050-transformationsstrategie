#!/usr/bin/env python3
"""
Generationen-Anleihe: Transition Gap Calculator

Models the financing gap during GRV → RSSP phase-in.
Cohort-based transition: each year, one new age-cohort enters RSSP instead of GRV.
After 47 years (one full working life), no working-age contributors remain in GRV.
GRV expenditures wind down as remaining retirees die off.

The gap is financed by 100-year Generationen-Anleihen (government bonds).

Usage:
    python src/transition.py [--bond_yield 0.02] [--bundeszuschuss_fixed]
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class TransitionParams:
    # GRV baseline (2024, real EUR)
    grv_expenditure: float = 350e9      # EUR 350 Mrd/yr total GRV pensions
    grv_contributions: float = 250e9    # EUR 250 Mrd/yr from contributions
    grv_bundeszuschuss: float = 100e9   # EUR 100 Mrd/yr federal subsidy

    # Demographics
    work_years: int = 47                # age 20-67
    retire_years: int = 20              # average retirement duration
    cohort_size: int = 831_435          # annual cohort entering workforce

    # Transition design
    transition_type: str = "cohort"     # cohort | stichtag
    phase_in_years: int = 47            # years until all workers are in RSSP

    # Bond financing
    bond_yield_real: float = 0.02       # 100-year bond real yield
    bond_maturity: int = 100            # years

    # RSSP surplus available for debt service (grows over time as fund matures)
    rssp_surplus_start_year: int = 50   # when RSSP generates enough surplus
    rssp_surplus_initial: float = 54e9  # EUR 54 Mrd/yr initially (Config D steady-state)
    rssp_surplus_mature: float = 120e9  # EUR 120 Mrd/yr at maturity (larger fund, higher returns)
    rssp_surplus_ramp_years: int = 30   # years from initial to mature surplus

    # Freed Bundeszuschuss redirect: after GRV winds down, the EUR 100 Mrd/yr
    # federal subsidy is no longer needed. It can be redirected to bond service.
    redirect_freed_bundeszuschuss: bool = True

    # Options
    bundeszuschuss_continues: bool = True   # does federal subsidy continue during transition?
    target2_mobilization: float = 0.0       # EUR from Target2-Equity-Swap (seed capital)

    # Simulation
    sim_years: int = 120                # total simulation years


@dataclass
class TransitionResult:
    params: TransitionParams
    years: List[int]
    grv_expenditure: List[float]        # GRV pension expenditure per year
    grv_contributions: List[float]      # GRV contribution income per year
    bundeszuschuss: List[float]         # federal subsidy per year
    annual_gap: List[float]             # financing gap per year
    cumulative_gap: List[float]         # cumulative gap (total borrowing needed)
    bond_outstanding: List[float]       # outstanding bond debt
    interest_payments: List[float]      # annual interest on bonds
    total_fiscal_burden: List[float]    # gap + interest
    rssp_debt_service: List[float]      # RSSP surplus used for debt service

    # Summary
    peak_annual_gap: float = 0.0
    peak_annual_gap_year: int = 0
    peak_bond_outstanding: float = 0.0
    peak_fiscal_burden: float = 0.0
    total_interest_paid: float = 0.0
    total_gap_undiscounted: float = 0.0
    total_gap_npv: float = 0.0
    bond_fully_repaid_year: Optional[int] = None
    gap_as_pct_gdp_peak: float = 0.0   # peak gap as % of GDP (~4.2T)


def simulate_transition(p: TransitionParams) -> TransitionResult:
    """
    Simulate the GRV→RSSP transition gap year by year.

    The key dynamics:
    - Year t: (t/phase_in_years) fraction of the workforce is in RSSP
    - GRV contributions shrink proportionally
    - GRV expenditure stays high initially (existing retirees), then declines
      as GRV retirees die off (starting ~20 years after last GRV worker retires)
    - The gap = expenditure - contributions - Bundeszuschuss
    - Gap is financed by issuing Generationen-Anleihen
    """
    T = p.sim_years

    years = list(range(T))
    grv_exp = [0.0] * T
    grv_contr = [0.0] * T
    bz = [0.0] * T
    gap = [0.0] * T
    cum_gap = [0.0] * T
    bond_out = [0.0] * T
    interest = [0.0] * T
    fiscal = [0.0] * T
    rssp_service = [0.0] * T

    # Phase 1: Contribution ramp-down (years 0 to phase_in_years-1)
    # Each year, one more cohort pays RSSP instead of GRV.
    # GRV contributions decline linearly.
    #
    # Phase 2: Zero GRV contributions (years phase_in to phase_in + retire_years - 1)
    # GRV still pays retirees who entered before transition.
    # Expenditure declines as these retirees die.
    #
    # Phase 3: GRV wind-down complete (year phase_in + retire_years onward)
    # No more GRV expenditure.

    # Contribution decline: linear over phase_in_years
    # GRV expenditure decline: starts after phase_in_years, takes ~retire_years to reach 0
    # (last GRV worker retires at year phase_in - 1, last retiree dies ~retire_years later)

    gdp = 4.2e12  # approximate German GDP for % calculations

    cumulative = 0.0
    outstanding = 0.0

    # Seed from Target2 mobilization (if any)
    if p.target2_mobilization > 0:
        outstanding = -p.target2_mobilization  # negative = credit balance

    for t in range(T):
        # --- GRV Contributions ---
        if t < p.phase_in_years:
            # Linear decline: fraction remaining = 1 - (t+1)/phase_in
            # Year 0: lose 1/47 of contributors
            # Year 46: lose 47/47 (all gone)
            fraction_remaining = max(0.0, 1.0 - (t + 1) / p.phase_in_years)
            grv_contr[t] = p.grv_contributions * fraction_remaining
        else:
            grv_contr[t] = 0.0

        # --- GRV Expenditure ---
        # Expenditure stays at baseline until the last GRV contributor retires,
        # then declines linearly over retire_years as retirees die off.
        # Last GRV worker retires at year = phase_in_years - 1
        # Last GRV retiree: entered retirement at year phase_in - 1,
        #   dies ~retire_years later = year phase_in - 1 + retire_years
        wind_down_start = p.phase_in_years
        wind_down_end = p.phase_in_years + p.retire_years

        if t < wind_down_start:
            # Full expenditure (all existing retirees still alive, new retirees still entering)
            # Actually, expenditure grows slightly as more retirees accumulate,
            # then stabilizes. Simplification: constant during phase-in.
            grv_exp[t] = p.grv_expenditure
        elif t < wind_down_end:
            # Linear wind-down of GRV retirees
            years_into_winddown = t - wind_down_start
            fraction = 1.0 - years_into_winddown / p.retire_years
            grv_exp[t] = p.grv_expenditure * max(0.0, fraction)
        else:
            grv_exp[t] = 0.0

        # --- Bundeszuschuss ---
        if p.bundeszuschuss_continues and grv_exp[t] > 0:
            # Scale Bundeszuschuss proportionally to expenditure
            bz[t] = p.grv_bundeszuschuss * (grv_exp[t] / p.grv_expenditure)
        else:
            bz[t] = 0.0

        # --- Gap ---
        gap[t] = max(0.0, grv_exp[t] - grv_contr[t] - bz[t])
        cumulative += gap[t]
        cum_gap[t] = cumulative

        # --- Bond accounting ---
        # Interest on outstanding bonds
        int_payment = max(0.0, outstanding * p.bond_yield_real)
        interest[t] = int_payment

        # New borrowing = gap (issued as bonds)
        outstanding += gap[t]

        # Interest is added to outstanding (or paid from budget)
        outstanding += int_payment

        # Debt service from multiple sources:
        # 1) RSSP surplus (available after system matures, growing over time)
        # 2) Freed Bundeszuschuss (available as GRV expenditure declines)
        total_service = 0.0

        # RSSP surplus (grows linearly from initial to mature over ramp_years)
        if t >= p.rssp_surplus_start_year and outstanding > 0:
            years_since_start = t - p.rssp_surplus_start_year
            if years_since_start >= p.rssp_surplus_ramp_years:
                rssp_surplus = p.rssp_surplus_mature
            else:
                frac = years_since_start / p.rssp_surplus_ramp_years
                rssp_surplus = p.rssp_surplus_initial + frac * (p.rssp_surplus_mature - p.rssp_surplus_initial)
            total_service += rssp_surplus

        # Freed Bundeszuschuss: the difference between baseline BZ and actual BZ
        # represents fiscal space freed up by GRV wind-down
        if p.redirect_freed_bundeszuschuss and outstanding > 0:
            freed_bz = p.grv_bundeszuschuss - bz[t]
            total_service += max(0.0, freed_bz)

        if total_service > 0 and outstanding > 0:
            service = min(outstanding, total_service)
            outstanding -= service
            rssp_service[t] = service

        bond_out[t] = max(0.0, outstanding)

        # Total fiscal burden = gap + interest
        fiscal[t] = gap[t] + int_payment

    # --- Summary statistics ---
    peak_gap = max(gap)
    peak_gap_yr = gap.index(peak_gap)
    peak_bond = max(bond_out)
    peak_fiscal = max(fiscal)
    total_interest = sum(interest)
    total_gap = sum(gap)

    # NPV of gap at bond yield
    npv = sum(g / (1 + p.bond_yield_real) ** t for t, g in enumerate(gap))

    # When is bond fully repaid?
    repaid_year = None
    was_positive = False
    for t in range(T):
        if bond_out[t] > 1e6:
            was_positive = True
        elif was_positive and bond_out[t] < 1e6:
            repaid_year = t
            break

    return TransitionResult(
        params=p,
        years=years,
        grv_expenditure=grv_exp,
        grv_contributions=grv_contr,
        bundeszuschuss=bz,
        annual_gap=gap,
        cumulative_gap=cum_gap,
        bond_outstanding=bond_out,
        interest_payments=interest,
        total_fiscal_burden=fiscal,
        rssp_debt_service=rssp_service,
        peak_annual_gap=peak_gap,
        peak_annual_gap_year=peak_gap_yr,
        peak_bond_outstanding=peak_bond,
        peak_fiscal_burden=peak_fiscal,
        total_interest_paid=total_interest,
        total_gap_undiscounted=total_gap,
        total_gap_npv=npv,
        bond_fully_repaid_year=repaid_year,
        gap_as_pct_gdp_peak=peak_gap / gdp * 100,
    )


def print_report(r: TransitionResult) -> None:
    p = r.params
    B = 1e9  # billion
    T = 1e12  # trillion

    print("=" * 80)
    print("GENERATIONEN-ANLEIHE: Transition Gap Analysis")
    print("=" * 80)
    print()
    print(f"Transition type:     {p.transition_type} (cohort-based)")
    print(f"Phase-in period:     {p.phase_in_years} years")
    print(f"Bond yield (real):   {p.bond_yield_real * 100:.1f}%")
    print(f"Bond maturity:       {p.bond_maturity} years")
    print(f"Target2 seed:        EUR {p.target2_mobilization / B:.0f} Mrd")
    print(f"RSSP surplus:        EUR {p.rssp_surplus_initial / B:.0f}-{p.rssp_surplus_mature / B:.0f} Mrd/yr (from year {p.rssp_surplus_start_year}, ramp {p.rssp_surplus_ramp_years}yr)")
    print()

    print("--- GRV Baseline ---")
    print(f"Expenditure:         EUR {p.grv_expenditure / B:.0f} Mrd/yr")
    print(f"Contributions:       EUR {p.grv_contributions / B:.0f} Mrd/yr")
    print(f"Bundeszuschuss:      EUR {p.grv_bundeszuschuss / B:.0f} Mrd/yr")
    print()

    print("--- Key Results ---")
    print(f"Peak annual gap:     EUR {r.peak_annual_gap / B:.1f} Mrd (year {r.peak_annual_gap_year})")
    print(f"Peak gap as % GDP:   {r.gap_as_pct_gdp_peak:.2f}%")
    print(f"Total gap (undisc.): EUR {r.total_gap_undiscounted / T:.2f} Bio")
    print(f"Total gap (NPV):     EUR {r.total_gap_npv / T:.2f} Bio")
    print(f"Peak bond outstand.: EUR {r.peak_bond_outstanding / T:.2f} Bio")
    print(f"Total interest paid: EUR {r.total_interest_paid / T:.2f} Bio")
    print(f"Peak fiscal burden:  EUR {r.peak_fiscal_burden / B:.1f} Mrd/yr")
    if r.bond_fully_repaid_year:
        print(f"Bond fully repaid:   Year {r.bond_fully_repaid_year}")
    else:
        print(f"Bond fully repaid:   NOT within {p.sim_years} years")
    print()

    # Timeline table
    print("--- Timeline (selected years) ---")
    print(f"{'Year':>5} {'GRV Exp':>12} {'GRV Contr':>12} {'BZ':>10} {'Gap':>12} "
          f"{'Cum Gap':>12} {'Bond Out':>12} {'Interest':>10} {'RSSP Svc':>10}")
    print("-" * 106)

    milestones = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 47, 50, 55, 60, 67, 70, 80, 90, 100, 110, 119]
    for t in milestones:
        if t >= p.sim_years:
            continue
        print(f"{t:>5} "
              f"{r.grv_expenditure[t] / B:>11.1f}B "
              f"{r.grv_contributions[t] / B:>11.1f}B "
              f"{r.bundeszuschuss[t] / B:>9.1f}B "
              f"{r.annual_gap[t] / B:>11.1f}B "
              f"{r.cumulative_gap[t] / B:>11.1f}B "
              f"{r.bond_outstanding[t] / B:>11.1f}B "
              f"{r.interest_payments[t] / B:>9.1f}B "
              f"{r.rssp_debt_service[t] / B:>9.1f}B")

    print()

    # Scenario comparison
    print("--- Scenario Comparison ---")
    scenarios = [
        ("Base (2% yield, no Target2)", 0.02, 0.0, 54e9, 120e9),
        ("Low yield (1.5%)", 0.015, 0.0, 54e9, 120e9),
        ("Ultra-low yield (1.0%)", 0.01, 0.0, 54e9, 120e9),
        ("High yield (3%)", 0.03, 0.0, 54e9, 120e9),
        ("Base + Target2 (200 Mrd)", 0.02, 200e9, 54e9, 120e9),
        ("Base + Target2 (500 Mrd)", 0.02, 500e9, 54e9, 120e9),
        ("1.5% + Target2 (500 Mrd)", 0.015, 500e9, 54e9, 120e9),
        ("1.0% + Target2 (500 Mrd)", 0.01, 500e9, 54e9, 120e9),
        ("1.5% + T2(500) + high surplus", 0.015, 500e9, 54e9, 200e9),
    ]
    print(f"{'Scenario':<45} {'Peak Bond':>12} {'Repaid Yr':>10} {'Tot Interest':>14}")
    print("-" * 83)
    for name, yld, t2, s_init, s_mat in scenarios:
        sp = TransitionParams(
            bond_yield_real=yld,
            target2_mobilization=t2,
            rssp_surplus_initial=s_init,
            rssp_surplus_mature=s_mat,
        )
        sr = simulate_transition(sp)
        repaid = str(sr.bond_fully_repaid_year) if sr.bond_fully_repaid_year else f">{p.sim_years}"
        print(f"{name:<45} {sr.peak_bond_outstanding / T:>11.2f}T {repaid:>10} "
              f"{sr.total_interest_paid / T:>13.2f}T")

    print()
    print("--- Interpretation ---")
    print(f"The transition from GRV to RSSP requires financing a gap of")
    print(f"EUR {r.total_gap_npv / T:.2f} Bio (NPV) over ~{p.phase_in_years + p.retire_years} years.")
    print(f"Peak annual burden: EUR {r.peak_annual_gap / B:.1f} Mrd/yr ({r.gap_as_pct_gdp_peak:.2f}% of GDP).")
    print(f"For comparison: the implicit GRV debt is EUR 8-10 Bio.")
    print(f"The Generationen-Anleihe converts implicit debt into explicit, manageable debt.")


def main():
    parser = argparse.ArgumentParser(description="Generationen-Anleihe Transition Calculator")
    parser.add_argument("--bond_yield", type=float, default=0.02, help="Real bond yield (default: 0.02)")
    parser.add_argument("--target2", type=float, default=0.0, help="Target2 seed capital in EUR (default: 0)")
    parser.add_argument("--rssp_surplus_init", type=float, default=54e9, help="RSSP initial surplus for debt service")
    parser.add_argument("--rssp_surplus_mature", type=float, default=120e9, help="RSSP mature surplus for debt service")
    parser.add_argument("--rssp_surplus_start", type=int, default=50, help="Year RSSP surplus starts")
    parser.add_argument("--no_bundeszuschuss", action="store_true", help="Bundeszuschuss stops during transition")
    parser.add_argument("--json", type=str, default=None, help="Write results to JSON file")
    parser.add_argument("--sim_years", type=int, default=120, help="Simulation years (default: 120)")
    args = parser.parse_args()

    p = TransitionParams(
        bond_yield_real=args.bond_yield,
        target2_mobilization=args.target2,
        rssp_surplus_initial=args.rssp_surplus_init,
        rssp_surplus_mature=args.rssp_surplus_mature,
        rssp_surplus_start_year=args.rssp_surplus_start,
        bundeszuschuss_continues=not args.no_bundeszuschuss,
        sim_years=args.sim_years,
    )

    result = simulate_transition(p)
    print_report(result)

    if args.json:
        summary = {
            "peak_annual_gap": result.peak_annual_gap,
            "peak_annual_gap_year": result.peak_annual_gap_year,
            "peak_bond_outstanding": result.peak_bond_outstanding,
            "peak_fiscal_burden": result.peak_fiscal_burden,
            "total_interest_paid": result.total_interest_paid,
            "total_gap_undiscounted": result.total_gap_undiscounted,
            "total_gap_npv": result.total_gap_npv,
            "bond_fully_repaid_year": result.bond_fully_repaid_year,
            "gap_as_pct_gdp_peak": result.gap_as_pct_gdp_peak,
            "params": {
                "bond_yield_real": p.bond_yield_real,
                "target2_mobilization": p.target2_mobilization,
                "rssp_surplus_initial": p.rssp_surplus_initial,
            "rssp_surplus_mature": p.rssp_surplus_mature,
                "phase_in_years": p.phase_in_years,
            }
        }
        with open(args.json, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\nResults written to {args.json}")


if __name__ == "__main__":
    main()
