# Rentenreform/RSSP_v2/src/sensitivity.py
"""
Comprehensive sensitivity analysis for the RSSP_v2 pension model.

Produces:
  - sensitivity_sweep.csv : full multi-dimensional sweep results
  - sensitivity_sweep.json: same data as JSON
  - sensitivity_summary.md : break-even analysis, corrected-parameter run,
                             and political feasibility dashboard
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
from dataclasses import asdict
from itertools import product
from typing import Any, Dict, List, Optional, Tuple

from model import MortalityBucket, Params, simulate

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HORIZON = 100
PASS_LAST_N = 10

# Sweep grid (team-lead specifications)
TAU_HIGH_GRID = [round(0.05 + i * 0.025, 4) for i in range(11)]  # 0.05 to 0.30 step 0.025
REAL_RETURN_GRID = [0.000, 0.005, 0.010, 0.01735, 0.025]
INCOME_PROFILE_GRID = [False, True]
LONGEVITY_POOL_GRID = [False, True]

# For break-even: finer tau_high grid (extended to 0.40 to cover income_profile + longevity combos)
TAU_HIGH_FINE = [round(0.01 + i * 0.0025, 4) for i in range(157)]  # 0.01 to 0.40

# Base params (from base.yaml)
BASE_PARAMS = dict(
    horizon_years=HORIZON,
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
    guarantee_low=1.00,
    guarantee_mid=0.70,
    mortality_enabled=True,
    backstop_enabled=True,
    loan_cap_asset_share=0.10,
    repay_share=0.50,
    reserve_years=3,
    longevity_floor=10_000.0,
    longevity_max_age=95,
    longevity_surplus_share=0.05,
)

# Default mortality buckets
DEFAULT_MORTALITY = [
    MortalityBucket(67, 74, 0.99),
    MortalityBucket(75, 84, 0.975),
    MortalityBucket(85, 95, 0.95),
    MortalityBucket(96, 200, 0.92),
]

# Corrected mortality buckets (from research_validation.md Section 7)
CORRECTED_MORTALITY = [
    MortalityBucket(67, 74, 0.982),
    MortalityBucket(75, 84, 0.955),
    MortalityBucket(85, 95, 0.88),
    MortalityBucket(96, 200, 0.72),
]

# Return scenarios (including paths for robustness)
CONST_SCENARIOS = {
    "base_1p7": [0.01735],
    "low_1p0": [0.010],
    "hard_0p5": [0.005],
    "flat_0p0": [0.000],
}

PATH_SCENARIOS = {
    "drawdown_5y_then_1p5": [-0.03, -0.03, -0.03, -0.03, -0.03, 0.015],
    "crash_then_recover": [-0.10, -0.05, 0.00, 0.01, 0.015, 0.017],
    "stagflation_proxy": [0.00, 0.00, 0.00, 0.005, 0.010, 0.012],
}

# GDP for fiscal exposure calculation
GDP_EUR = 4.1e12  # EUR 4.1 trillion


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_params(tau_high: float,
                income_profile_enabled: bool,
                longevity_pool_enabled: bool,
                mortality_buckets: Optional[List[MortalityBucket]] = None,
                **overrides) -> Params:
    """Build a Params object with the given feature flags."""
    kw = dict(BASE_PARAMS)
    kw["tau_high"] = tau_high
    kw["income_profile_enabled"] = income_profile_enabled
    kw["longevity_pool_enabled"] = longevity_pool_enabled
    kw["mortality_buckets"] = mortality_buckets or list(CORRECTED_MORTALITY)
    kw.update(overrides)
    return Params(**kw)


def run_all_scenarios(p: Params, real_return: float) -> Dict[str, Any]:
    """Run the model at a single constant real return across all scenarios and return summary."""
    # Use only the constant-return scenario at the given rate
    returns = [real_return]
    scenario_name = f"const_{real_return:.4f}"
    res = simulate(p, returns=returns, scenario_name=scenario_name, pass_last_n_years=PASS_LAST_N)
    return {
        "passed": res.passed,
        "fail_years": res.fail_years,
        "pool_depletion_year": res.pool_depletion_year,
        "steady_state_deficit": res.steady_state_deficit,
        "is_structurally_sustainable": res.is_structurally_sustainable,
        "max_state_loan": res.max_state_loan,
        "final_state_loan": res.final_state_loan,
        "peak_longevity_retirees": res.peak_longevity_retirees,
        "min_repl_low": res.min_repl_low,
        "min_repl_mid": res.min_repl_mid,
        "max_loan_to_assets_ratio": res.max_loan_to_assets_ratio,
        "final_longevity_pool": res.final_longevity_pool,
        "total_longevity_payouts": res.total_longevity_payouts,
        "total_longevity_backstop": res.total_longevity_backstop,
    }


def run_multi_scenario_pass(p: Params) -> Tuple[bool, Dict[str, Any]]:
    """Run all const + path scenarios; return (all_pass, worst_case_details)."""
    all_pass = True
    worst = {
        "max_state_loan": 0.0,
        "fail_years": 0,
        "min_repl_low": 10.0,
        "min_repl_mid": 10.0,
    }
    all_results = {}

    for name, ret in {**CONST_SCENARIOS, **PATH_SCENARIOS}.items():
        res = simulate(p, returns=ret, scenario_name=name, pass_last_n_years=PASS_LAST_N)
        all_pass = all_pass and res.passed
        worst["max_state_loan"] = max(worst["max_state_loan"], res.max_state_loan)
        worst["fail_years"] = max(worst["fail_years"], res.fail_years)
        worst["min_repl_low"] = min(worst["min_repl_low"], res.min_repl_low)
        worst["min_repl_mid"] = min(worst["min_repl_mid"], res.min_repl_mid)
        all_results[name] = {
            "passed": res.passed,
            "pool_depletion_year": res.pool_depletion_year,
            "steady_state_deficit": res.steady_state_deficit,
            "is_structurally_sustainable": res.is_structurally_sustainable,
            "max_state_loan": res.max_state_loan,
            "peak_longevity_retirees": res.peak_longevity_retirees,
        }

    return all_pass, {**worst, "scenarios": all_results}


# ---------------------------------------------------------------------------
# 1. Multi-dimensional sweep
# ---------------------------------------------------------------------------

def sweep() -> List[Dict[str, Any]]:
    """Run the full multi-dimensional parameter sweep."""
    rows = []
    combos = list(product(TAU_HIGH_GRID, REAL_RETURN_GRID, INCOME_PROFILE_GRID, LONGEVITY_POOL_GRID))
    total = len(combos)
    print(f"[sweep] {total} combinations to evaluate...")

    for idx, (tau_h, rr, ip, lp) in enumerate(combos, 1):
        p = make_params(tau_high=tau_h, income_profile_enabled=ip, longevity_pool_enabled=lp)
        res = run_all_scenarios(p, rr)
        row = {
            "tau_high": tau_h,
            "real_return": rr,
            "income_profile": ip,
            "longevity_pool": lp,
            **res,
        }
        rows.append(row)
        if idx % 50 == 0 or idx == total:
            print(f"  [{idx}/{total}]")

    return rows


# ---------------------------------------------------------------------------
# 2. Break-even analysis
# ---------------------------------------------------------------------------

def break_even_analysis() -> Dict[str, Any]:
    """Find minimum tau_high and minimum real return for each feature combo."""
    results = {}

    for ip, lp in product(INCOME_PROFILE_GRID, LONGEVITY_POOL_GRID):
        label = f"income_profile={ip},longevity={lp}"
        entry: Dict[str, Any] = {"income_profile": ip, "longevity_pool": lp}

        # 2a. Min tau_high that passes ALL scenarios (const + path)
        min_tau = None
        for tau_h in TAU_HIGH_FINE:
            p = make_params(tau_high=tau_h, income_profile_enabled=ip, longevity_pool_enabled=lp)
            all_pass, _ = run_multi_scenario_pass(p)
            if all_pass:
                min_tau = tau_h
                break
        entry["min_tau_high_all_scenarios"] = min_tau

        # 2b. Min real return for structural sustainability at tau_high=0.20
        min_rr_020 = None
        for rr in [round(x * 0.001, 4) for x in range(0, 51)]:  # 0.0% to 5.0% in 0.1% steps
            p = make_params(tau_high=0.20, income_profile_enabled=ip, longevity_pool_enabled=lp)
            res = run_all_scenarios(p, rr)
            if res["passed"] and res["is_structurally_sustainable"]:
                min_rr_020 = rr
                break
        entry["min_real_return_sustainable_tau020"] = min_rr_020

        # 2c. Min real return for structural sustainability at tau_high=0.15
        min_rr_015 = None
        for rr in [round(x * 0.001, 4) for x in range(0, 51)]:
            p = make_params(tau_high=0.15, income_profile_enabled=ip, longevity_pool_enabled=lp)
            res = run_all_scenarios(p, rr)
            if res["passed"] and res["is_structurally_sustainable"]:
                min_rr_015 = rr
                break
        entry["min_real_return_sustainable_tau015"] = min_rr_015

        results[label] = entry
        print(f"  [break-even] {label}: min_tau={min_tau}, min_rr@0.20={min_rr_020}, min_rr@0.15={min_rr_015}")

    return results


# ---------------------------------------------------------------------------
# 3. Corrected parameters run
# ---------------------------------------------------------------------------

def corrected_params_run() -> Dict[str, Any]:
    """Run optimizer-style search with researcher's recommended corrections."""
    # Corrected parameters per research_validation.md Section 7
    corrected_overrides = dict(
        cohort_size_at_age_start=690_000,
        income_low_retire=30_000.0,
        income_mid_retire=50_000.0,
        mortality_buckets=list(CORRECTED_MORTALITY),
    )

    results = {}
    configs = [
        ("all_features", True, True),
        ("no_income_profile", False, True),
        ("no_longevity", True, False),
        ("baseline", False, False),
    ]

    for label_suffix, ip, lp in configs:
        # Find min tau_high with ORIGINAL params for this feature combo
        min_tau_orig = None
        for tau_h in TAU_HIGH_FINE:
            p = make_params(tau_high=tau_h, income_profile_enabled=ip, longevity_pool_enabled=lp)
            all_pass, _ = run_multi_scenario_pass(p)
            if all_pass:
                min_tau_orig = tau_h
                break
        print(f"  [original] {label_suffix}: min_tau_high={min_tau_orig}")

        # Find min tau_high with CORRECTED params
        min_tau_corr = None
        best_details = None
        for tau_h in TAU_HIGH_FINE:
            p = make_params(
                tau_high=tau_h,
                income_profile_enabled=ip,
                longevity_pool_enabled=lp,
                **corrected_overrides,
            )
            all_pass, details = run_multi_scenario_pass(p)
            if all_pass:
                min_tau_corr = tau_h
                best_details = details
                break
        print(f"  [corrected] {label_suffix}: min_tau_high={min_tau_corr}")

        results[label_suffix] = {
            "income_profile": ip,
            "longevity_pool": lp,
            "min_tau_high_original": min_tau_orig,
            "min_tau_high_corrected": min_tau_corr,
            "worst_case": best_details,
        }

    return results


# ---------------------------------------------------------------------------
# 4. Political feasibility summary
# ---------------------------------------------------------------------------

def political_feasibility(sweep_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """For each passing configuration, compute political feasibility metrics."""
    inc_low = BASE_PARAMS["income_low_retire"]
    inc_mid = BASE_PARAMS["income_mid_retire"]
    inc_high = inc_mid * BASE_PARAMS["high_income_factor"]

    feasibility = []
    for row in sweep_rows:
        if not row["passed"]:
            continue

        tau_h = row["tau_high"]

        # Effective contribution rate (population-weighted)
        eff_rate = (
            BASE_PARAMS["low_share"] * BASE_PARAMS["tau_low"]
            + BASE_PARAMS["mid_share"] * BASE_PARAMS["tau_mid"]
            + BASE_PARAMS["high_share"] * tau_h
        )

        # High-earner annual burden
        high_annual_burden = tau_h * inc_high

        # State fiscal exposure
        max_loan = row["max_state_loan"]
        fiscal_exposure_gdp = max_loan / GDP_EUR

        feasibility.append({
            "tau_high": tau_h,
            "real_return": row["real_return"],
            "income_profile": row["income_profile"],
            "longevity_pool": row["longevity_pool"],
            "eff_contribution_rate": round(eff_rate * 100, 2),
            "high_earner_annual_EUR": round(high_annual_burden, 0),
            "high_earner_monthly_EUR": round(high_annual_burden / 12, 0),
            "max_state_loan_bn": round(max_loan / 1e9, 2),
            "fiscal_exposure_pct_gdp": round(fiscal_exposure_gdp * 100, 4),
            "pool_depletion_year": row["pool_depletion_year"],
            "is_structurally_sustainable": row["is_structurally_sustainable"],
        })

    return feasibility


# ---------------------------------------------------------------------------
# Output generation
# ---------------------------------------------------------------------------

def write_csv(rows: List[Dict[str, Any]], path: str) -> None:
    if not rows:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    keys = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"  Written: {path} ({len(rows)} rows)")


def write_json(data: Any, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  Written: {path}")


def fmt_pct(v: Optional[float], decimals: int = 2) -> str:
    if v is None:
        return "N/A"
    return f"{v * 100:.{decimals}f}%"


def fmt_eur(v: Optional[float]) -> str:
    if v is None:
        return "N/A"
    if abs(v) >= 1e9:
        return f"{v / 1e9:.1f} bn"
    if abs(v) >= 1e6:
        return f"{v / 1e6:.0f} M"
    return f"{v:,.0f}"


def generate_summary_md(
    sweep_rows: List[Dict[str, Any]],
    breakeven: Dict[str, Any],
    corrected: Dict[str, Any],
    feasibility: List[Dict[str, Any]],
) -> str:
    """Generate the full markdown summary."""
    lines = []
    lines.append("# RSSP_v2 Sensitivity Analysis Summary")
    lines.append("")
    lines.append(f"**Generated**: {time.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Horizon**: {HORIZON} years | **Pass criterion**: last {PASS_LAST_N} years meet guarantees")
    lines.append("")

    # --- Section 1: Sweep overview ---
    lines.append("## 1. Multi-Dimensional Sweep Overview")
    lines.append("")
    total = len(sweep_rows)
    passing = [r for r in sweep_rows if r["passed"]]
    lines.append(f"- Total configurations tested: **{total}**")
    lines.append(f"- Passing configurations: **{len(passing)}** ({len(passing)/total*100:.1f}%)")
    lines.append(f"- tau_high range: {min(TAU_HIGH_GRID):.2%} to {max(TAU_HIGH_GRID):.2%}")
    lines.append(f"- Real return range: {min(REAL_RETURN_GRID):.1%} to {max(REAL_RETURN_GRID):.1%}")
    lines.append("")

    # Pivot table: pass rate by tau_high x real_return (aggregated over features)
    lines.append("### Pass Rate by tau_high x Real Return (averaged over feature combos)")
    lines.append("")
    header = "| tau_high |"
    for rr in REAL_RETURN_GRID:
        header += f" {rr:.1%} |"
    lines.append(header)
    lines.append("|" + "---|" * (len(REAL_RETURN_GRID) + 1))

    for tau_h in TAU_HIGH_GRID:
        row_str = f"| {tau_h:.1%} |"
        for rr in REAL_RETURN_GRID:
            matching = [r for r in sweep_rows if r["tau_high"] == tau_h and r["real_return"] == rr]
            n_pass = sum(1 for r in matching if r["passed"])
            n_total = len(matching)
            if n_total > 0:
                row_str += f" {n_pass}/{n_total} |"
            else:
                row_str += " - |"
        lines.append(row_str)
    lines.append("")

    # Pivot: structural sustainability
    lines.append("### Structurally Sustainable (steady-state deficit >= 0) by tau_high x Real Return")
    lines.append("*(count out of 4 feature combinations)*")
    lines.append("")
    lines.append(header)
    lines.append("|" + "---|" * (len(REAL_RETURN_GRID) + 1))

    for tau_h in TAU_HIGH_GRID:
        row_str = f"| {tau_h:.1%} |"
        for rr in REAL_RETURN_GRID:
            matching = [r for r in sweep_rows if r["tau_high"] == tau_h and r["real_return"] == rr]
            n_sust = sum(1 for r in matching if r["is_structurally_sustainable"])
            n_total = len(matching)
            if n_total > 0:
                row_str += f" {n_sust}/{n_total} |"
            else:
                row_str += " - |"
        lines.append(row_str)
    lines.append("")

    # --- Section 2: Break-even ---
    lines.append("## 2. Break-Even Analysis")
    lines.append("")
    lines.append("| Configuration | Min tau_high (all scenarios) | Min real return (sustainable, tau=20%) | Min real return (sustainable, tau=15%) |")
    lines.append("|---|---|---|---|")
    for label, entry in breakeven.items():
        ip_str = "ON" if entry["income_profile"] else "OFF"
        lp_str = "ON" if entry["longevity_pool"] else "OFF"
        tau_str = fmt_pct(entry["min_tau_high_all_scenarios"]) if entry["min_tau_high_all_scenarios"] is not None else ">40%"
        rr020 = fmt_pct(entry["min_real_return_sustainable_tau020"]) if entry["min_real_return_sustainable_tau020"] is not None else ">5.0%"
        rr015 = fmt_pct(entry["min_real_return_sustainable_tau015"]) if entry["min_real_return_sustainable_tau015"] is not None else ">5.0%"
        lines.append(f"| Income profile: {ip_str}, Longevity: {lp_str} | {tau_str} | {rr020} | {rr015} |")
    lines.append("")

    lines.append("**Interpretation**: The minimum tau_high column shows the lowest contribution rate for high earners")
    lines.append("that passes all 7 return scenarios (4 constant + 3 path-based). The real return columns show")
    lines.append("the minimum investment return needed for the system to be structurally sustainable (inflows >= outflows)")
    lines.append("in steady state, without relying on backstop loans.")
    lines.append("")

    # --- Section 3: Corrected parameters ---
    lines.append("## 3. Corrected Parameters (Researcher Recommendations)")
    lines.append("")
    lines.append("Corrections applied (from research_validation.md Section 7):")
    lines.append("- `cohort_size_at_age_start`: 831,435 -> **690,000**")
    lines.append("- `mortality_buckets`: {0.99, 0.975, 0.95, 0.92} -> **{0.982, 0.955, 0.88, 0.72}**")
    lines.append("- `income_low_retire`: 22,000 -> **30,000**")
    lines.append("- `income_mid_retire`: 40,000 -> **50,000**")
    lines.append("")
    lines.append("| Configuration | Min tau_high (original) | Min tau_high (corrected) | Delta |")
    lines.append("|---|---|---|---|")

    label_map = {
        "all_features": "All features ON",
        "no_income_profile": "Longevity ON, income profile OFF",
        "no_longevity": "Income profile ON, longevity OFF",
        "baseline": "Baseline (both OFF)",
    }

    for key, entry in corrected.items():
        label = label_map.get(key, key)
        orig_tau = entry.get("min_tau_high_original")
        corr_tau = entry.get("min_tau_high_corrected")

        orig_str = fmt_pct(orig_tau) if orig_tau is not None else ">40%"
        corr_str = fmt_pct(corr_tau) if corr_tau is not None else ">40%"
        if orig_tau is not None and corr_tau is not None:
            delta = corr_tau - orig_tau
            delta_str = f"{delta:+.2%}"
        else:
            delta_str = "N/A"
        lines.append(f"| {label} | {orig_str} | {corr_str} | {delta_str} |")

    lines.append("")
    lines.append("**Key insight**: More realistic mortality (higher death rates) reduces the number of retirees")
    lines.append("the system must support, while higher incomes increase both contributions and guarantee targets.")
    lines.append("The net effect on tau_high depends on which factor dominates.")
    lines.append("")

    # --- Section 4: Political feasibility ---
    lines.append("## 4. Political Feasibility Dashboard")
    lines.append("")
    lines.append("**Reference**: Current GRV contribution rate = 18.6% (employer + employee), replacement rate ~48%")
    lines.append("")

    if feasibility:
        # Show a representative subset: group by (income_profile, longevity_pool),
        # pick a few tau_high levels per return
        lines.append("| tau_high | Real Return | Income Prof. | Longevity | Eff. Rate | High-Earner Annual | Max State Loan | Fiscal/GDP | Sustainable |")
        lines.append("|---|---|---|---|---|---|---|---|---|")

        # Sort for readability
        sorted_f = sorted(feasibility, key=lambda x: (x["income_profile"], x["longevity_pool"], x["tau_high"], x["real_return"]))

        # Show all passing configs (but limit to avoid excessive length)
        shown = 0
        for f in sorted_f:
            ip_str = "ON" if f["income_profile"] else "OFF"
            lp_str = "ON" if f["longevity_pool"] else "OFF"
            sust_str = "Yes" if f["is_structurally_sustainable"] else "No"
            lines.append(
                f"| {f['tau_high']:.1%} | {f['real_return']:.2%} | {ip_str} | {lp_str} | "
                f"{f['eff_contribution_rate']:.1f}% | EUR {f['high_earner_annual_EUR']:,.0f} | "
                f"{f['max_state_loan_bn']:.1f} bn | {f['fiscal_exposure_pct_gdp']:.3f}% | {sust_str} |"
            )
            shown += 1
            if shown >= 80:
                lines.append(f"| ... | ... | ... | ... | ... | ... | ... | ... | ... |")
                lines.append(f"*({len(sorted_f) - shown} more rows in CSV)*")
                break
    else:
        lines.append("*No passing configurations found in sweep.*")

    lines.append("")
    lines.append("### Comparison to Current GRV")
    lines.append("")
    lines.append("| Metric | Current GRV | RSSP (typical passing config) |")
    lines.append("|---|---|---|")
    lines.append("| Contribution rate (total) | 18.6% (employer + employee) | See Eff. Rate above |")
    lines.append("| Replacement rate (low earners) | ~48% of average wage | 100% of retire-age income |")
    lines.append("| Replacement rate (mid earners) | ~48% of average wage | 70% of retire-age income |")
    lines.append("| High earners | Pay 18.6%, receive ~48% | Pay tau_high, receive 0% |")
    lines.append("| Funding model | 100% PAYG | 100% funded (individual accounts) |")
    lines.append("| State fiscal exposure | Implicit (tax-funded deficit) | Explicit backstop loan |")
    lines.append("| Post-87 coverage | GRV pays until death | Longevity pool (floor EUR 10k/yr) |")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
    os.makedirs(out_dir, exist_ok=True)

    t0 = time.time()

    # 1. Multi-dimensional sweep
    print("=" * 60)
    print("PHASE 1: Multi-dimensional sensitivity sweep")
    print("=" * 60)
    sweep_rows = sweep()
    csv_path = os.path.join(out_dir, "sensitivity_sweep.csv")
    json_path = os.path.join(out_dir, "sensitivity_sweep.json")
    write_csv(sweep_rows, csv_path)
    write_json(sweep_rows, json_path)

    # 2. Break-even analysis
    print("\n" + "=" * 60)
    print("PHASE 2: Break-even analysis")
    print("=" * 60)
    breakeven = break_even_analysis()

    # 3. Corrected parameters
    print("\n" + "=" * 60)
    print("PHASE 3: Corrected parameters run")
    print("=" * 60)
    corrected = corrected_params_run()

    # 4. Political feasibility
    print("\n" + "=" * 60)
    print("PHASE 4: Political feasibility dashboard")
    print("=" * 60)
    feasibility = political_feasibility(sweep_rows)

    # Generate summary markdown
    md_path = os.path.join(out_dir, "sensitivity_summary.md")
    md_content = generate_summary_md(sweep_rows, breakeven, corrected, feasibility)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"  Written: {md_path}")

    # Also write breakeven + corrected to JSON for traceability
    meta_path = os.path.join(out_dir, "sensitivity_meta.json")
    write_json({
        "breakeven": breakeven,
        "corrected_params": corrected,
        "feasibility_count": len(feasibility),
        "sweep_count": len(sweep_rows),
        "passing_count": sum(1 for r in sweep_rows if r["passed"]),
    }, meta_path)

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")

    # Print key results to stdout
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    passing = [r for r in sweep_rows if r["passed"]]
    print(f"Sweep: {len(passing)}/{len(sweep_rows)} configs pass")

    print("\nBreak-even min tau_high (all scenarios):")
    for label, entry in breakeven.items():
        val = entry.get("min_tau_high_all_scenarios")
        print(f"  {label}: {fmt_pct(val) if val else 'Not found'}")

    print("\nCorrected vs original min tau_high:")
    for key, entry in corrected.items():
        orig = entry.get("min_tau_high_original")
        corr = entry.get("min_tau_high_corrected")
        orig_s = fmt_pct(orig) if orig else ">40%"
        corr_s = fmt_pct(corr) if corr else ">40%"
        print(f"  {key}: original={orig_s}, corrected={corr_s}")


if __name__ == "__main__":
    main()
