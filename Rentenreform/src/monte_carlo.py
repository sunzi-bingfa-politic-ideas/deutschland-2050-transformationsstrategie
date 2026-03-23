# Rentenreform/RSSP_v2/src/monte_carlo.py
"""
Monte Carlo simulation wrapper for RSSP model.

Runs N stochastic return paths through the deterministic cohort model
to quantify sequence-of-returns risk and produce confidence intervals.

Usage:
    python src/monte_carlo.py --config params/config_e.yaml --n_paths 1000
    python src/monte_carlo.py --config params/config_e.yaml --n_paths 10000 --regime
    python src/monte_carlo.py --config params/config_e.yaml --tau_high 0.1225 --json out/mc_base.json
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple

import numpy as np

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import Params, MortalityBucket, RunResult, simulate
from utils import load_yaml


@dataclass
class MCParams:
    """Monte Carlo simulation parameters."""
    n_paths: int = 1_000
    mean_return: float = 0.0175   # expected annual real return
    volatility: float = 0.15      # annual std dev (equity-like: 15-18%)
    seed: int = 42
    n_workers: int = 0            # 0 = auto (cpu_count)

    # Fat-tail returns (Student-t distribution)
    fat_tails_enabled: bool = False
    fat_tails_df: int = 5  # degrees of freedom (lower = fatter tails)

    # Regime-switching (Markov two-state)
    regime_enabled: bool = False
    bull_return: float = 0.06
    bear_return: float = -0.02
    bull_vol: float = 0.12
    bear_vol: float = 0.22
    p_bull_to_bear: float = 0.10
    p_bear_to_bull: float = 0.20


@dataclass
class MCResult:
    """Aggregated Monte Carlo results."""
    n_paths: int
    mean_return: float
    volatility: float
    regime_enabled: bool

    pass_rate: float              # fraction of paths meeting guarantees

    # Replacement rate distributions (minimum over simulation horizon)
    repl_low_p5: float
    repl_low_p25: float
    repl_low_p50: float
    repl_low_p75: float
    repl_low_p95: float

    repl_mid_p5: float
    repl_mid_p25: float
    repl_mid_p50: float
    repl_mid_p75: float
    repl_mid_p95: float

    # Pool sustainability
    pool_depletion_rate: float             # fraction where pool hits 0
    structural_sustainability_rate: float  # fraction structurally sustainable

    # State backstop exposure
    max_loan_p50: float
    max_loan_p95: float
    loan_repaid_rate: float

    # Tontine / longevity per-capita
    longevity_per_capita_p50: float
    longevity_per_capita_p95: float

    # Reserve fund (if enabled)
    peak_reserve_p50: float
    peak_reserve_p95: float

    elapsed_seconds: float


def generate_return_paths(mc: MCParams, horizon: int) -> np.ndarray:
    """Generate N stochastic return paths.

    Returns:
        np.ndarray of shape (n_paths, horizon) with annual real returns.
    """
    rng = np.random.default_rng(mc.seed)

    if mc.regime_enabled:
        # Markov regime-switching: bull/bear states with transition probabilities
        paths = np.zeros((mc.n_paths, horizon))
        for i in range(mc.n_paths):
            in_bull = rng.random() < 0.7  # 70% start in bull regime
            for t in range(horizon):
                if in_bull:
                    paths[i, t] = rng.normal(mc.bull_return, mc.bull_vol)
                    if rng.random() < mc.p_bull_to_bear:
                        in_bull = False
                else:
                    paths[i, t] = rng.normal(mc.bear_return, mc.bear_vol)
                    if rng.random() < mc.p_bear_to_bull:
                        in_bull = True
        return paths
    elif mc.fat_tails_enabled:
        # Fat-tail returns: Student-t distribution scaled to match mean/variance.
        # Lower df = fatter tails (df=5 gives kurtosis ~9 vs normal ~3).
        sigma2 = np.log(1 + (mc.volatility ** 2) / (1 + mc.mean_return) ** 2)
        sigma_log = np.sqrt(sigma2)
        mu_log = np.log(1 + mc.mean_return) - sigma2 / 2

        df = mc.fat_tails_df
        # Student-t has variance df/(df-2), so scale to get unit variance
        t_samples = rng.standard_t(df, size=(mc.n_paths, horizon))
        scale_factor = np.sqrt(df / (df - 2)) if df > 2 else 1.0
        log_returns = mu_log + sigma_log * t_samples / scale_factor
        return np.exp(log_returns) - 1.0
    else:
        # Log-normal returns: ln(1+r) ~ N(mu_log, sigma_log)
        # Calibrated so E[1+r] = 1 + mean_return
        sigma2 = np.log(1 + (mc.volatility ** 2) / (1 + mc.mean_return) ** 2)
        sigma_log = np.sqrt(sigma2)
        mu_log = np.log(1 + mc.mean_return) - sigma2 / 2

        log_returns = rng.normal(mu_log, sigma_log, size=(mc.n_paths, horizon))
        return np.exp(log_returns) - 1.0


def _params_to_dict(p: Params) -> dict:
    """Serialize Params to a picklable dict for multiprocessing."""
    d = {}
    for f in p.__dataclass_fields__:
        val = getattr(p, f)
        if f == "mortality_buckets":
            val = [(b.age_min, b.age_max, b.survival) for b in val]
        d[f] = val
    return d


def _dict_to_params(d: dict) -> Params:
    """Reconstruct Params from dict."""
    d = dict(d)  # copy
    if "mortality_buckets" in d:
        d["mortality_buckets"] = [
            MortalityBucket(a, b, s) for a, b, s in d["mortality_buckets"]
        ]
    return Params(**d)


def _run_single_path(args: Tuple) -> dict:
    """Worker function for multiprocessing. Returns summary dict."""
    params_dict, returns_list, path_idx = args
    p = _dict_to_params(params_dict)
    result = simulate(p, returns_list, f"mc_{path_idx}")

    return {
        "passed": result.passed,
        "min_repl_low": result.min_repl_low,
        "min_repl_mid": result.min_repl_mid,
        "max_state_loan": result.max_state_loan,
        "final_state_loan": result.final_state_loan,
        "pool_depletion_year": result.pool_depletion_year,
        "is_structurally_sustainable": result.is_structurally_sustainable,
        "loan_ever_repaid": result.loan_ever_repaid,
        "peak_longevity_per_capita": result.peak_longevity_per_capita,
        "peak_reserve_fund": result.peak_reserve_fund,
    }


def run_monte_carlo(p: Params, mc: MCParams) -> MCResult:
    """Run Monte Carlo simulation with multiprocessing."""
    t0 = time.time()

    paths = generate_return_paths(mc, p.horizon_years)
    params_dict = _params_to_dict(p)

    work_items = [
        (params_dict, paths[i].tolist(), i)
        for i in range(mc.n_paths)
    ]

    n_workers = mc.n_workers if mc.n_workers > 0 else mp.cpu_count()
    print(f"Running {mc.n_paths} paths on {n_workers} workers (horizon={p.horizon_years})...")

    if n_workers == 1:
        results = [_run_single_path(w) for w in work_items]
    else:
        chunksize = max(1, mc.n_paths // (n_workers * 4))
        with mp.Pool(n_workers) as pool:
            results = pool.map(_run_single_path, work_items, chunksize=chunksize)

    elapsed = time.time() - t0
    n = len(results)

    # Aggregate
    pass_count = sum(1 for r in results if r["passed"])
    min_repl_lows = np.array([r["min_repl_low"] for r in results])
    min_repl_mids = np.array([r["min_repl_mid"] for r in results])
    max_loans = np.array([r["max_state_loan"] for r in results])

    pool_depletion_count = sum(1 for r in results if r["pool_depletion_year"] is not None)
    structural_count = sum(1 for r in results if r["is_structurally_sustainable"])
    loan_repaid_count = sum(1 for r in results if r["loan_ever_repaid"])

    longevity_pcs = np.array([r["peak_longevity_per_capita"] for r in results])
    lpc_nonzero = longevity_pcs[longevity_pcs > 0]
    if len(lpc_nonzero) == 0:
        lpc_nonzero = np.array([0.0])

    reserve_peaks = np.array([r["peak_reserve_fund"] for r in results])

    return MCResult(
        n_paths=n,
        mean_return=mc.mean_return,
        volatility=mc.volatility,
        regime_enabled=mc.regime_enabled,
        pass_rate=pass_count / n,
        repl_low_p5=float(np.percentile(min_repl_lows, 5)),
        repl_low_p25=float(np.percentile(min_repl_lows, 25)),
        repl_low_p50=float(np.percentile(min_repl_lows, 50)),
        repl_low_p75=float(np.percentile(min_repl_lows, 75)),
        repl_low_p95=float(np.percentile(min_repl_lows, 95)),
        repl_mid_p5=float(np.percentile(min_repl_mids, 5)),
        repl_mid_p25=float(np.percentile(min_repl_mids, 25)),
        repl_mid_p50=float(np.percentile(min_repl_mids, 50)),
        repl_mid_p75=float(np.percentile(min_repl_mids, 75)),
        repl_mid_p95=float(np.percentile(min_repl_mids, 95)),
        pool_depletion_rate=pool_depletion_count / n,
        structural_sustainability_rate=structural_count / n,
        max_loan_p50=float(np.percentile(max_loans, 50)),
        max_loan_p95=float(np.percentile(max_loans, 95)),
        loan_repaid_rate=loan_repaid_count / n,
        longevity_per_capita_p50=float(np.percentile(lpc_nonzero, 50)),
        longevity_per_capita_p95=float(np.percentile(lpc_nonzero, 95)),
        peak_reserve_p50=float(np.percentile(reserve_peaks, 50)),
        peak_reserve_p95=float(np.percentile(reserve_peaks, 95)),
        elapsed_seconds=elapsed,
    )


def load_params_from_yaml(path: str) -> Params:
    """Load Params from a YAML config file (same format as config_d/e.yaml)."""
    cfg = load_yaml(path)

    kwargs = {}
    # Direct scalar fields
    for key in ["horizon_years", "age_start", "retire_age", "annuity_years",
                "cohort_size_at_age_start", "low_share", "mid_share", "high_share",
                "income_low_retire", "income_mid_retire", "high_income_factor",
                "tau_low", "tau_mid", "tau_high", "guarantee_low", "guarantee_mid"]:
        if key in cfg:
            kwargs[key] = cfg[key]

    # Mortality
    mort = cfg.get("mortality", {})
    kwargs["mortality_enabled"] = mort.get("enabled", True)
    buckets = []
    for b in mort.get("buckets", []):
        buckets.append(MortalityBucket(b["age_min"], b["age_max"], b["survival"]))
    if buckets:
        kwargs["mortality_buckets"] = buckets

    # Demography
    demo = cfg.get("demography", {})
    kwargs["demography_mode"] = demo.get("mode", "constant")
    kwargs["cohort_path"] = demo.get("cohort_path", [])

    # Backstop
    bs = cfg.get("backstop", {})
    kwargs["backstop_enabled"] = bs.get("enabled", True)
    kwargs["loan_cap_asset_share"] = bs.get("loan_cap_asset_share", 0.10)
    kwargs["repay_share"] = bs.get("repay_share", 0.50)
    kwargs["reserve_years"] = bs.get("reserve_years", 3)

    # Income profile
    ip = cfg.get("income_profile", {})
    kwargs["income_profile_enabled"] = ip.get("enabled", False)

    # Longevity pool + tontine
    lon = cfg.get("longevity", {})
    kwargs["longevity_pool_enabled"] = lon.get("enabled", True)
    kwargs["longevity_floor"] = lon.get("floor", 10_000)
    kwargs["longevity_max_age"] = lon.get("max_age", 95)
    kwargs["longevity_surplus_share"] = lon.get("surplus_share", 0.05)
    kwargs["tontine_enabled"] = lon.get("tontine_enabled", True)
    kwargs["tontine_cap_multiple"] = lon.get("tontine_cap_multiple", 3.0)

    # Reserve rule
    res = cfg.get("reserve_rule", {})
    kwargs["reserve_rule_enabled"] = res.get("enabled", False)
    kwargs["reserve_trigger_high"] = res.get("trigger_high", 0.03)
    kwargs["reserve_trigger_low"] = res.get("trigger_low", 0.01)
    kwargs["reserve_target_return"] = res.get("target_return", 0.02)
    kwargs["reserve_skim_fraction"] = res.get("skim_fraction", 0.30)
    kwargs["reserve_inject_fraction"] = res.get("inject_fraction", 0.30)
    kwargs["reserve_safe_rate"] = res.get("safe_rate", 0.005)

    # RIG (Robotik-Infrastrukturgesellschaft)
    rig = cfg.get("rig", {})
    kwargs["rig_enabled"] = rig.get("enabled", False)
    kwargs["rig_tau_insurance"] = rig.get("tau_insurance", 0.08)
    kwargs["rig_tau_equity"] = rig.get("tau_equity", 0.0425)
    kwargs["rig_base_return"] = rig.get("base_return", 0.03)
    kwargs["rig_beta"] = rig.get("beta", 0.30)
    kwargs["rig_dividend_rate"] = rig.get("dividend_rate", 0.02)
    kwargs["rig_dividend_to_pool"] = rig.get("dividend_to_pool", 0.80)

    # High-earner attrition (brain drain)
    kwargs["high_attrition_rate"] = cfg.get("high_attrition_rate", 0.0)

    # RIG return override (adversarial stress testing)
    kwargs["rig_return_override"] = [float(x) for x in cfg.get("rig_return_override", [])]

    return Params(**kwargs)


def print_results(r: MCResult):
    """Pretty-print Monte Carlo results."""
    print(f"\n{'='*70}")
    print(f"MONTE CARLO ERGEBNISSE — {r.n_paths} Pfade, {r.elapsed_seconds:.1f}s")
    print(f"{'='*70}")
    print(f"Mittlere Rendite: {r.mean_return*100:.2f}%  |  Volatilitaet: {r.volatility*100:.1f}%")
    if r.regime_enabled:
        print(f"Regime-Switching: aktiviert (Bull/Bear Markov-Modell)")

    print(f"\n--- Pass/Fail ---")
    print(f"Pass-Rate:  {r.pass_rate*100:.1f}%  ({int(r.pass_rate * r.n_paths)}/{r.n_paths})")

    print(f"\n--- Ersatzraten Low (Minimum ueber Laufzeit) ---")
    print(f"  P5:  {r.repl_low_p5*100:6.1f}%")
    print(f"  P25: {r.repl_low_p25*100:6.1f}%")
    print(f"  P50: {r.repl_low_p50*100:6.1f}%  (Median)")
    print(f"  P75: {r.repl_low_p75*100:6.1f}%")
    print(f"  P95: {r.repl_low_p95*100:6.1f}%")

    print(f"\n--- Ersatzraten Mid (Minimum ueber Laufzeit) ---")
    print(f"  P5:  {r.repl_mid_p5*100:6.1f}%")
    print(f"  P25: {r.repl_mid_p25*100:6.1f}%")
    print(f"  P50: {r.repl_mid_p50*100:6.1f}%  (Median)")
    print(f"  P75: {r.repl_mid_p75*100:6.1f}%")
    print(f"  P95: {r.repl_mid_p95*100:6.1f}%")

    print(f"\n--- Nachhaltigkeit ---")
    print(f"  Pool-Erschoepfungsrate:  {r.pool_depletion_rate*100:.1f}%")
    print(f"  Strukturell nachhaltig:  {r.structural_sustainability_rate*100:.1f}%")
    print(f"  Kredit zurueckgezahlt:   {r.loan_repaid_rate*100:.1f}%")

    print(f"\n--- Staats-Backstop ---")
    print(f"  Max. Kredit P50: EUR {r.max_loan_p50:>15,.0f}")
    print(f"  Max. Kredit P95: EUR {r.max_loan_p95:>15,.0f}")

    if r.longevity_per_capita_p50 > 0:
        print(f"\n--- Tontine/Longevity Per-Capita ---")
        print(f"  Peak Per-Capita P50: EUR {r.longevity_per_capita_p50:>10,.0f}")
        print(f"  Peak Per-Capita P95: EUR {r.longevity_per_capita_p95:>10,.0f}")

    if r.peak_reserve_p50 > 0:
        print(f"\n--- Reserve-Fonds ---")
        print(f"  Peak P50: EUR {r.peak_reserve_p50:>15,.0f}")
        print(f"  Peak P95: EUR {r.peak_reserve_p95:>15,.0f}")

    print(f"\n{'='*70}")


def main():
    parser = argparse.ArgumentParser(description="RSSP Monte Carlo Simulation")
    parser.add_argument("--config", required=True, help="YAML config file")
    parser.add_argument("--n_paths", type=int, default=1000, help="Number of paths (default 1000)")
    parser.add_argument("--mean_return", type=float, default=0.0175, help="Expected real return")
    parser.add_argument("--volatility", type=float, default=0.15, help="Return std dev")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--workers", type=int, default=0, help="Worker processes (0=auto)")
    parser.add_argument("--regime", action="store_true", help="Enable regime-switching")
    parser.add_argument("--fat_tails", action="store_true", help="Enable fat-tail (Student-t) returns")
    parser.add_argument("--fat_tails_df", type=int, default=5, help="Degrees of freedom for fat tails")
    parser.add_argument("--tau_high", type=float, default=None, help="Override tau_high")
    parser.add_argument("--json", type=str, default=None, help="Output JSON file")

    args = parser.parse_args()

    # Load model params
    p = load_params_from_yaml(args.config)
    if args.tau_high is not None:
        p.tau_high = args.tau_high

    # MC params
    mc = MCParams(
        n_paths=args.n_paths,
        mean_return=args.mean_return,
        volatility=args.volatility,
        seed=args.seed,
        n_workers=args.workers,
        regime_enabled=args.regime,
        fat_tails_enabled=args.fat_tails,
        fat_tails_df=args.fat_tails_df,
    )

    result = run_monte_carlo(p, mc)
    print_results(result)

    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        with open(args.json, "w") as f:
            json.dump(asdict(result), f, indent=2)
        print(f"\nGespeichert: {args.json}")


if __name__ == "__main__":
    main()
