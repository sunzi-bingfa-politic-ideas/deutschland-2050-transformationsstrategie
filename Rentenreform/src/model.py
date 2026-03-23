# Rentenreform/RSSP_v2/src/model.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple


@dataclass
class MortalityBucket:
    age_min: int
    age_max: int
    survival: float  # annual survival probability


def survival_rate_for_age(buckets: List[MortalityBucket], age: int) -> float:
    for b in buckets:
        if b.age_min <= age <= b.age_max:
            return b.survival
    return 1.0


@dataclass
class Params:
    horizon_years: int = 80
    age_start: int = 20
    retire_age: int = 67
    annuity_years: int = 20

    # Demography (cohort entrants at age_start)
    cohort_size_at_age_start: int = 831_435

    low_share: float = 0.30
    mid_share: float = 0.50
    high_share: float = 0.20

    income_low_retire: float = 22_000.0
    income_mid_retire: float = 40_000.0
    high_income_factor: float = 1.8

    tau_low: float = 0.12
    tau_mid: float = 0.13
    tau_high: float = 0.05  # will be optimized

    guarantee_low: float = 1.00
    guarantee_mid: float = 0.70

    # --- Haertung 1: Mortalitaet
    mortality_enabled: bool = True
    mortality_buckets: List[MortalityBucket] = field(default_factory=list)

    # --- Haertung 2: Demografiepfade
    demography_mode: str = "constant"  # constant | path
    cohort_path: List[int] = field(default_factory=list)

    # --- Haertung 3: Staats-Backstop (Kreditlinie)
    backstop_enabled: bool = True
    loan_cap_asset_share: float = 0.10
    repay_share: float = 0.50
    reserve_years: int = 3

    # --- Haertung 4: Age-income profiles
    # When enabled, contributions scale by a hump-shaped multiplier over working years.
    # Multipliers are fractions of retire-age income (e.g., 0.40 at age 20, 1.0 at peak).
    # If profile is shorter than work_years, last value repeats.
    income_profile_enabled: bool = False
    income_profile: List[float] = field(default_factory=list)

    # --- Haertung 5: Longevity pool (post-annuity coverage)
    longevity_pool_enabled: bool = True
    longevity_floor: float = 10_000.0  # minimum annual pension after annuity expires (Grundsicherung level)
    longevity_max_age: int = 95  # maximum age the model covers for post-annuity payouts
    longevity_surplus_share: float = 0.05  # fraction of guarantee pool surplus redirected to longevity pool
    tontine_enabled: bool = True  # dynamic per-capita distribution instead of fixed floor
    tontine_cap_multiple: float = 3.0  # max payout as multiple of floor (3.0 = EUR 30k at 10k floor)

    # --- Symmetric Reserve Rule (counter-cyclical buffer for guarantee pool)
    reserve_rule_enabled: bool = False
    reserve_trigger_high: float = 0.03    # skim excess when r > 3%
    reserve_trigger_low: float = 0.01     # inject when r < 1%
    reserve_target_return: float = 0.02   # baseline for excess/shortfall calc
    reserve_skim_fraction: float = 0.30   # fraction of excess skimmed to reserve
    reserve_inject_fraction: float = 0.30 # fraction of shortfall injected from reserve
    reserve_safe_rate: float = 0.005      # 0.5% real return on reserve fund

    # --- Haertung 7: RIG (Robotik-Infrastrukturgesellschaft) & Solidaritaets-Equity-Swap
    # When enabled, high-earner contributions are split:
    #   rig_tau_insurance -> guarantee pool (solidarisch, unwiderruflich)
    #   rig_tau_equity    -> RIG fund (infrastructure certificates for high earners)
    # RIG fund earns a decorrelated return and pays dividends.
    # Part of dividends flow to the guarantee pool (automatic stabilizer).
    rig_enabled: bool = False
    rig_tau_insurance: float = 0.08       # fraction of high income -> guarantee pool
    rig_tau_equity: float = 0.0425        # fraction of high income -> RIG certificates
    rig_base_return: float = 0.03         # RIG intrinsic real return (market-validated 2026)
    rig_beta: float = 0.30               # market sensitivity (0=fully decorrelated, 1=market)
    rig_dividend_rate: float = 0.02       # annual dividend yield on RIG fund
    rig_dividend_to_pool: float = 0.80    # fraction of dividends redirected to guarantee pool

    # --- Haertung 8: High-Earner Attrition (Brain Drain)
    # Annual fraction of high earners lost to emigration/tax optimization.
    # Without RIG incentive: ~0.5%/yr (empirical: Germany loses ~0.2% overall,
    # higher for high-income; Destatis Wanderungsstatistik 2023).
    # With RIG equity swap: reduced (set lower in config_f.yaml).
    high_attrition_rate: float = 0.0  # 0 = no attrition (backward compatible)

    # --- Haertung 9: RIG Return Override (adversarial stress testing)
    # When set, overrides computed r_RIG for each year. Used for governance failure,
    # technology failure, and value destruction scenarios.
    rig_return_override: List[float] = field(default_factory=list)

    def __post_init__(self):
        # Default mortality buckets if mortality enabled and none provided
        if self.mortality_enabled and not self.mortality_buckets:
            self.mortality_buckets = [
                MortalityBucket(67, 74, 0.99),
                MortalityBucket(75, 84, 0.975),
                MortalityBucket(85, 95, 0.95),
                MortalityBucket(96, 200, 0.92),
            ]

        # Default age-income profile if enabled and none provided
        # Hump-shaped: entry-level -> early career -> mid career -> peak -> late decline
        # 47 working years: age 20-66 (retire_age=67 means last working year is age 66)
        if self.income_profile_enabled and not self.income_profile:
            work_yrs = self.retire_age - self.age_start
            profile = []
            for wy in range(work_yrs):
                age = self.age_start + wy
                if age <= 24:      # Entry level: 0.35 -> 0.45
                    f = 0.35 + (age - 20) * 0.025
                elif age <= 34:    # Early career: 0.50 -> 0.75
                    f = 0.50 + (age - 25) * 0.028
                elif age <= 44:    # Mid career: 0.80 -> 0.95
                    f = 0.80 + (age - 35) * 0.015
                elif age <= 55:    # Peak earnings: 0.95 -> 1.00
                    f = 0.95 + (age - 45) * 0.005
                else:              # Late career: 0.95 -> 0.90
                    f = 0.95 - (age - 56) * 0.005
                profile.append(round(f, 4))
            self.income_profile = profile

        # Validate shares sum to 1.0
        share_sum = self.low_share + self.mid_share + self.high_share
        if abs(share_sum - 1.0) > 1e-6:
            raise ValueError(
                f"Income shares must sum to 1.0, got {share_sum:.6f} "
                f"(low={self.low_share}, mid={self.mid_share}, high={self.high_share})"
            )

        # Validate tau values in [0, 1]
        for name, val in [("tau_low", self.tau_low), ("tau_mid", self.tau_mid), ("tau_high", self.tau_high)]:
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"{name} must be in [0, 1], got {val}")

        # Validate retire_age > age_start
        if self.retire_age <= self.age_start:
            raise ValueError(
                f"retire_age ({self.retire_age}) must be greater than age_start ({self.age_start})"
            )

        # Validate annuity_years > 0
        if self.annuity_years <= 0:
            raise ValueError(f"annuity_years must be > 0, got {self.annuity_years}")

        # Validate horizon covers working + retirement period
        min_horizon = (self.retire_age - self.age_start) + self.annuity_years
        if self.horizon_years < min_horizon:
            raise ValueError(
                f"horizon_years ({self.horizon_years}) must be >= "
                f"retire_age - age_start + annuity_years ({min_horizon})"
            )

        # Validate longevity_max_age > retire_age + annuity_years when enabled
        if self.longevity_pool_enabled:
            annuity_end_age = self.retire_age + self.annuity_years
            if self.longevity_max_age <= annuity_end_age:
                raise ValueError(
                    f"longevity_max_age ({self.longevity_max_age}) must be > "
                    f"retire_age + annuity_years ({annuity_end_age})"
                )

        # Validate RIG parameters
        if self.rig_enabled:
            for name, val in [("rig_tau_insurance", self.rig_tau_insurance),
                              ("rig_tau_equity", self.rig_tau_equity)]:
                if not (0.0 <= val <= 1.0):
                    raise ValueError(f"{name} must be in [0, 1], got {val}")
            if not (0.0 <= self.rig_beta <= 1.0):
                raise ValueError(f"rig_beta must be in [0, 1], got {self.rig_beta}")


@dataclass
class YearStats:
    year: int
    r: float

    retirees_low: int
    retirees_mid: int

    payout_low_per_capita: float
    payout_mid_per_capita: float

    repl_low: float
    repl_mid: float

    topup_need_low: float
    topup_need_mid: float
    topup_paid: float

    state_loan: float
    loan_added: float
    loan_repaid: float

    pool: float
    assets_low: float
    assets_mid: float

    # Longevity pool fields (Haertung 5)
    longevity_pool: float = 0.0
    longevity_payout_total: float = 0.0
    longevity_retirees: int = 0
    longevity_backstop: float = 0.0
    longevity_per_capita: float = 0.0
    reserve_fund: float = 0.0
    rig_fund: float = 0.0
    rig_r: float = 0.0
    rig_div_total: float = 0.0
    rig_div_to_pool: float = 0.0
    rig_div_to_holders: float = 0.0


@dataclass
class RunResult:
    params: Params
    scenario_name: str
    stats: List[YearStats]
    passed: bool
    fail_years: int
    min_repl_low: float
    min_repl_mid: float
    min_pool: float
    max_state_loan: float
    final_state_loan: float

    # Sustainability metrics
    pool_depletion_year: Optional[int] = None  # first year where pool hits 0
    steady_state_deficit: float = 0.0  # avg annual (inflow - outflow) after build-up
    is_structurally_sustainable: bool = False  # True if steady_state_deficit >= 0 w/o backstop
    loan_ever_repaid: bool = False  # True if state_loan returns to 0 after being > 0
    max_loan_to_assets_ratio: float = 0.0  # peak loan / total_assets ratio

    # Longevity metrics (Haertung 5)
    final_longevity_pool: float = 0.0
    total_longevity_payouts: float = 0.0
    total_longevity_backstop: float = 0.0
    peak_longevity_retirees: int = 0

    # Tontine metrics
    peak_longevity_per_capita: float = 0.0
    avg_longevity_per_capita: float = 0.0

    # Reserve fund metrics
    final_reserve_fund: float = 0.0
    peak_reserve_fund: float = 0.0

    # RIG metrics (Haertung 7)
    final_rig_fund: float = 0.0
    peak_rig_fund: float = 0.0
    total_rig_dividends: float = 0.0
    total_rig_to_pool: float = 0.0


def _repeat_last(values: List[float], n: int) -> List[float]:
    if not values:
        return [0.0] * n
    if len(values) >= n:
        return values[:n]
    last = values[-1]
    return values + [last] * (n - len(values))


def simulate(
    p: Params,
    returns: List[float],
    scenario_name: str,
    pass_last_n_years: int = 10,
    eps: float = 1e-9,
) -> RunResult:
    """
    Clean-room cohort model with 5 hardenings:
    - Low/Mid build individual accounts via contributions.
    - High contributes to pooled guarantee fund (pay-only, no benefits).
    - Pool ONLY finances guarantee top-ups (no bonus payouts).
    - Deterministic annuity drawdown over annuity_years.

    Haertung 1: Mortality - retiree count shrinks over retirement years
    Haertung 2: Demography path - each cohort can have its own size
    Haertung 3: Backstop - state credit line fills guarantee gaps, capped, repaid from surplus
    Haertung 4: Age-income profiles - contributions scale with career earnings trajectory
    Haertung 5: Longevity pool - post-annuity coverage for survivors past annuity end age
    """
    T = p.horizon_years
    rs = _repeat_last(returns, T)

    work_years = p.retire_age - p.age_start
    retire_window = p.annuity_years

    # Post-annuity window: years between annuity end and longevity_max_age
    # E.g., annuity ends at age 87, longevity_max_age=95 -> 8 post-annuity years
    longevity_years = p.longevity_max_age - (p.retire_age + p.annuity_years) if p.longevity_pool_enabled else 0

    # Precompute survival factors for full retirement span (annuity + post-annuity):
    # surv[k] = probability of being alive at retire_age + k given alive at retire_age
    max_ret_years = retire_window + longevity_years
    surv_factors = [1.0] * max_ret_years
    if p.mortality_enabled:
        s = 1.0
        for k in range(max_ret_years):
            surv_factors[k] = s
            age = p.retire_age + k
            s *= survival_rate_for_age(p.mortality_buckets, age)

    # cohort assets arrays
    low_assets_by_cohort = [0.0] * T
    mid_assets_by_cohort = [0.0] * T

    # cohort counts per entry year (Demography path)
    cohort_low_size = [0] * T
    cohort_mid_size = [0] * T
    cohort_high_size = [0] * T

    def cohort_total_at(entry_year: int) -> int:
        if p.demography_mode == "path" and p.cohort_path:
            if entry_year < len(p.cohort_path):
                return int(p.cohort_path[entry_year])
            return int(p.cohort_path[-1])
        return int(p.cohort_size_at_age_start)

    for i in range(T):
        tot = cohort_total_at(i)
        cohort_low_size[i] = int(round(tot * p.low_share))
        cohort_mid_size[i] = int(round(tot * p.mid_share))
        cohort_high_size[i] = int(round(tot * p.high_share))

    # incomes (simple, constant real at retire-age levels)
    inc_low = p.income_low_retire
    inc_mid = p.income_mid_retire
    inc_high = p.income_mid_retire * p.high_income_factor

    # Precompute age-income profile factors (one per working year)
    if p.income_profile_enabled and p.income_profile:
        income_factors = _repeat_last(p.income_profile, work_years)
    else:
        income_factors = [1.0] * work_years

    pool = 0.0
    longevity_pool = 0.0
    state_loan = 0.0
    max_state_loan = 0.0
    reserve_fund = 0.0
    max_reserve_fund = 0.0
    rig_fund = 0.0
    max_rig_fund = 0.0
    topup_need_hist: List[float] = []
    stats: List[YearStats] = []

    # Track which cohorts have already transferred residual assets to longevity pool
    cohort_transferred_to_longevity = [False] * T

    # helper: annuity payout for a cohort at a given "years into retirement"
    def cohort_payout(account: float, years_into_retirement: int) -> float:
        remaining = retire_window - years_into_retirement
        if remaining <= 0:
            return 0.0
        return account / remaining

    for t in range(T):
        r = rs[t]
        loan_added = 0.0
        loan_repaid = 0.0
        longevity_payout_total = 0.0
        longevity_retirees_count = 0
        longevity_backstop_this_year = 0.0

        # 1) New cohort enters at t (starts with 0 assets)

        # 2) Contributions from working cohorts + high to pool
        # Working cohorts are those with t - i in [0, work_years-1]
        for i in range(max(0, t - (work_years - 1)), t + 1):
            years_worked = t - i
            if years_worked < 0 or years_worked >= work_years:
                continue
            inc_factor = income_factors[years_worked]
            low_assets_by_cohort[i] += cohort_low_size[i] * inc_low * inc_factor * p.tau_low
            mid_assets_by_cohort[i] += cohort_mid_size[i] * inc_mid * inc_factor * p.tau_mid
            # High-earner attrition: effective contributors shrink over career years
            attrition = (1.0 - p.high_attrition_rate) ** years_worked if p.high_attrition_rate > 0 else 1.0
            effective_high = cohort_high_size[i] * attrition
            if p.rig_enabled:
                pool += effective_high * inc_high * inc_factor * p.rig_tau_insurance
                rig_fund += effective_high * inc_high * inc_factor * p.rig_tau_equity
            else:
                pool += effective_high * inc_high * inc_factor * p.tau_high  # pay-only

        # 3) Apply investment return to all assets (accounts + pool + longevity pool)
        pool_before_return = pool  # saved for reserve rule
        grow = (1.0 + r)
        for i in range(0, t + 1):
            low_assets_by_cohort[i] *= grow
            mid_assets_by_cohort[i] *= grow
        pool *= grow
        if p.longevity_pool_enabled:
            longevity_pool *= grow

        # 3a) RIG fund: decorrelated return + dividend distribution
        rig_r_this_year = 0.0
        rig_div_total_this_year = 0.0
        rig_div_pool_this_year = 0.0
        rig_div_holders_this_year = 0.0
        if p.rig_enabled:
            if p.rig_return_override and t < len(p.rig_return_override):
                rig_r_this_year = p.rig_return_override[t]
            else:
                rig_r_this_year = p.rig_base_return + p.rig_beta * (r - p.rig_base_return)
            rig_fund *= (1.0 + rig_r_this_year)
            # Distribute dividends
            rig_div_total_this_year = rig_fund * p.rig_dividend_rate
            rig_div_pool_this_year = rig_div_total_this_year * p.rig_dividend_to_pool
            rig_div_holders_this_year = rig_div_total_this_year - rig_div_pool_this_year
            rig_fund -= rig_div_total_this_year
            pool += rig_div_pool_this_year
            max_rig_fund = max(max_rig_fund, rig_fund)

        # 3b) Symmetric Reserve Rule (counter-cyclical buffer on guarantee pool)
        if p.reserve_rule_enabled:
            if r > p.reserve_trigger_high:
                # Good year: skim excess pool growth into reserve
                excess = pool_before_return * (r - p.reserve_target_return)
                skim = max(0.0, excess * p.reserve_skim_fraction)
                skim = min(skim, pool * 0.10)  # cap at 10% of pool per year
                pool -= skim
                reserve_fund += skim
            elif r < p.reserve_trigger_low:
                # Bad year: inject from reserve to compensate shortfall
                shortfall = pool_before_return * (p.reserve_target_return - r)
                inject = max(0.0, shortfall * p.reserve_inject_fraction)
                inject = min(inject, reserve_fund)
                reserve_fund -= inject
                pool += inject
            reserve_fund *= (1 + p.reserve_safe_rate)
            max_reserve_fund = max(max_reserve_fund, reserve_fund)

        # 4) Pay pensions for retired cohorts and compute per-capita payouts
        retirees_low = 0
        retirees_mid = 0
        payout_low_total = 0.0
        payout_mid_total = 0.0

        # retired cohorts are those with t - i in [work_years, work_years + retire_window - 1]
        for i in range(0, t + 1):
            age_years = t - i
            years_into_ret = age_years - work_years
            if years_into_ret < 0 or years_into_ret >= retire_window:
                continue

            pay_low_per = cohort_payout(low_assets_by_cohort[i], years_into_ret)
            pay_mid_per = cohort_payout(mid_assets_by_cohort[i], years_into_ret)

            # reduce assets accordingly (drawdown)
            low_assets_by_cohort[i] = max(0.0, low_assets_by_cohort[i] - pay_low_per)
            mid_assets_by_cohort[i] = max(0.0, mid_assets_by_cohort[i] - pay_mid_per)

            # survivors this year (Mortalitaet)
            surv = surv_factors[years_into_ret] if years_into_ret < len(surv_factors) else 0.0
            low_ret = int(round(cohort_low_size[i] * surv))
            mid_ret = int(round(cohort_mid_size[i] * surv))

            # pay_low_per is total cohort payout (cohort_payout divides total assets)
            # survivors affect headcount for per-capita calc, not the total payout
            payout_low_total += pay_low_per
            payout_mid_total += pay_mid_per
            retirees_low += low_ret
            retirees_mid += mid_ret

        # 4b) Longevity pool: transfer residual assets from cohorts whose annuity just ended
        #     and count post-annuity survivors for longevity payouts
        longevity_per_capita_this_year = 0.0
        if p.longevity_pool_enabled:
            remaining_years_weighted_sum = 0.0
            for i in range(0, t + 1):
                age_years = t - i
                years_into_ret = age_years - work_years

                # Transfer residual assets at annuity expiry (years_into_ret == retire_window)
                if years_into_ret == retire_window and not cohort_transferred_to_longevity[i]:
                    residual = low_assets_by_cohort[i] + mid_assets_by_cohort[i]
                    longevity_pool += residual
                    low_assets_by_cohort[i] = 0.0
                    mid_assets_by_cohort[i] = 0.0
                    cohort_transferred_to_longevity[i] = True

                # Post-annuity survivors: years_into_ret in [retire_window, retire_window + longevity_years - 1]
                if years_into_ret >= retire_window and years_into_ret < retire_window + longevity_years:
                    surv = surv_factors[years_into_ret] if years_into_ret < len(surv_factors) else 0.0
                    low_surv = int(round(cohort_low_size[i] * surv))
                    mid_surv = int(round(cohort_mid_size[i] * surv))
                    n_surv = low_surv + mid_surv
                    longevity_retirees_count += n_surv
                    # Track remaining years in longevity window for tontine draw rate
                    remaining = (retire_window + longevity_years) - years_into_ret
                    remaining_years_weighted_sum += n_surv * remaining

            # Pay longevity: tontine (dynamic per-capita) or fixed floor
            if longevity_retirees_count > 0:
                if p.tontine_enabled:
                    # Tontine: distribute pool surplus per-capita above floor obligations.
                    # Only pay bonus when pool covers all remaining floor obligations,
                    # ensuring the tontine never depletes the pool below sustainability.
                    avg_remaining = remaining_years_weighted_sum / longevity_retirees_count
                    total_remaining_floor_need = remaining_years_weighted_sum * p.longevity_floor
                    tontine_cap = p.longevity_floor * p.tontine_cap_multiple

                    if longevity_pool > total_remaining_floor_need:
                        # Pool surplus above floor obligations → distribute as tontine bonus
                        tontine_surplus = longevity_pool - total_remaining_floor_need
                        bonus_per_capita = tontine_surplus / longevity_retirees_count / max(1.0, avg_remaining)
                        per_capita_payout = min(p.longevity_floor + bonus_per_capita, tontine_cap)
                    else:
                        # Pool insufficient for full floor coverage → pay floor only
                        per_capita_payout = p.longevity_floor

                    longevity_need = per_capita_payout * longevity_retirees_count
                    longevity_per_capita_this_year = per_capita_payout
                else:
                    # Fixed floor (legacy Config D behavior)
                    longevity_need = p.longevity_floor * longevity_retirees_count
                    longevity_per_capita_this_year = p.longevity_floor

                longevity_paid_from_pool = min(longevity_pool, longevity_need)
                longevity_pool -= longevity_paid_from_pool
                longevity_payout_total = longevity_paid_from_pool

                # Backstop only guarantees the floor, not the tontine uplift.
                # Tontine bonus above floor is "best effort" from pool only.
                longevity_floor_need = p.longevity_floor * longevity_retirees_count
                longevity_gap = max(0.0, longevity_floor_need - longevity_paid_from_pool)
                # State backstop fills the floor guarantee gap (same mechanism as guarantee backstop)
                if longevity_gap > 0 and p.backstop_enabled:
                    assets_low_tmp = sum(low_assets_by_cohort[: t + 1])
                    assets_mid_tmp = sum(mid_assets_by_cohort[: t + 1])
                    assets_total_tmp = max(1.0, pool + longevity_pool + rig_fund + assets_low_tmp + assets_mid_tmp)
                    cap = p.loan_cap_asset_share * assets_total_tmp
                    room = max(0.0, cap - state_loan)
                    longevity_backstop_this_year = min(room, longevity_gap)
                    state_loan += longevity_backstop_this_year
                    max_state_loan = max(max_state_loan, state_loan)
                    longevity_payout_total += longevity_backstop_this_year

        payout_low_per_cap = payout_low_total / retirees_low if retirees_low > 0 else 0.0
        payout_mid_per_cap = payout_mid_total / retirees_mid if retirees_mid > 0 else 0.0

        # 5) Guarantee top-ups from pool (ONLY)
        target_low = p.guarantee_low * inc_low
        target_mid = p.guarantee_mid * inc_mid

        topup_need_low = max(0.0, target_low - payout_low_per_cap) * retirees_low
        topup_need_mid = max(0.0, target_mid - payout_mid_per_cap) * retirees_mid
        topup_need = topup_need_low + topup_need_mid

        topup_paid = min(pool, topup_need)
        pool -= topup_paid

        gap = topup_need - topup_paid
        topup_need_hist.append(topup_need)

        # total assets (for loan cap)
        assets_low = sum(low_assets_by_cohort[: t + 1])
        assets_mid = sum(mid_assets_by_cohort[: t + 1])
        assets_total = max(1.0, pool + longevity_pool + rig_fund + assets_low + assets_mid)

        # 6) Backstop: state credit line fills remaining gap
        if gap > 0 and p.backstop_enabled:
            cap = p.loan_cap_asset_share * assets_total
            room = max(0.0, cap - state_loan)
            loan_added = min(room, gap)
            state_loan += loan_added
            max_state_loan = max(max_state_loan, state_loan)
            topup_paid += loan_added
            gap -= loan_added  # if still >0 -> guarantees may fail

        # distribute topup to raise per-capita payouts as much as possible
        # proportional to need
        if topup_need > 0 and topup_paid > 0:
            paid_low = topup_paid * (topup_need_low / topup_need) if topup_need_low > 0 else 0.0
            paid_mid = topup_paid * (topup_need_mid / topup_need) if topup_need_mid > 0 else 0.0
            payout_low_per_cap += (paid_low / retirees_low) if retirees_low > 0 else 0.0
            payout_mid_per_cap += (paid_mid / retirees_mid) if retirees_mid > 0 else 0.0

        # 7) Repay loan from real pool surplus above a reserve
        if p.backstop_enabled and state_loan > 0:
            # rolling avg of needs (last 5 years)
            k = min(5, len(topup_need_hist))
            avg_need = sum(topup_need_hist[-k:]) / max(1, k)
            needed_reserve = p.reserve_years * avg_need
            if pool > needed_reserve and avg_need > 0:
                surplus = pool - needed_reserve
                loan_repaid = min(state_loan, p.repay_share * surplus)
                pool -= loan_repaid
                state_loan -= loan_repaid

        # 7b) Redirect a fraction of guarantee pool surplus to longevity pool
        if p.longevity_pool_enabled and p.longevity_surplus_share > 0:
            k = min(5, len(topup_need_hist))
            avg_need = sum(topup_need_hist[-k:]) / max(1, k)
            needed_reserve = p.reserve_years * avg_need
            if pool > needed_reserve:
                transferable = (pool - needed_reserve) * p.longevity_surplus_share
                pool -= transferable
                longevity_pool += transferable

        repl_low = payout_low_per_cap / inc_low if inc_low > 0 else 0.0
        repl_mid = payout_mid_per_cap / inc_mid if inc_mid > 0 else 0.0

        # track remaining assets totals
        assets_low = sum(low_assets_by_cohort[: t + 1])
        assets_mid = sum(mid_assets_by_cohort[: t + 1])

        stats.append(
            YearStats(
                year=t,
                r=r,
                retirees_low=retirees_low,
                retirees_mid=retirees_mid,
                payout_low_per_capita=payout_low_per_cap,
                payout_mid_per_capita=payout_mid_per_cap,
                repl_low=repl_low,
                repl_mid=repl_mid,
                topup_need_low=topup_need_low,
                topup_need_mid=topup_need_mid,
                topup_paid=topup_paid,
                state_loan=state_loan,
                loan_added=loan_added,
                loan_repaid=loan_repaid,
                pool=pool,
                assets_low=assets_low,
                assets_mid=assets_mid,
                longevity_pool=longevity_pool,
                longevity_payout_total=longevity_payout_total,
                longevity_retirees=longevity_retirees_count,
                longevity_backstop=longevity_backstop_this_year,
                longevity_per_capita=longevity_per_capita_this_year,
                reserve_fund=reserve_fund,
                rig_fund=rig_fund,
                rig_r=rig_r_this_year,
                rig_div_total=rig_div_total_this_year,
                rig_div_to_pool=rig_div_pool_this_year,
                rig_div_to_holders=rig_div_holders_this_year,
            )
        )

    # Pass/Fail on last N years where retirees exist
    last = stats[-pass_last_n_years:] if len(stats) >= pass_last_n_years else stats
    fail_years = 0
    min_low = 10.0
    min_mid = 10.0
    min_pool = float("inf")
    for s in last:
        min_low = min(min_low, s.repl_low)
        min_mid = min(min_mid, s.repl_mid)
        min_pool = min(min_pool, s.pool)
        if (s.retirees_low + s.retirees_mid) > 0:
            if s.repl_low + eps < p.guarantee_low or s.repl_mid + eps < p.guarantee_mid:
                fail_years += 1

    passed = (fail_years == 0)

    # --- Sustainability metrics ---

    # Pool depletion year: first year where pool hits 0 (or near-zero)
    pool_depletion_year: Optional[int] = None
    for s in stats:
        if s.pool < 1.0:  # effectively zero (< 1 EUR)
            pool_depletion_year = s.year
            break

    # Steady-state deficit: average (pool_inflow - topup_need) for years after build-up.
    # Full steady state = all retirement cohorts present = work_years + retire_window.
    full_steady_year = work_years + retire_window
    ss_deficits = []
    tau_h_pool = p.rig_tau_insurance if p.rig_enabled else p.tau_high
    for t_idx in range(full_steady_year, T):
        # Count working high-earners contributing in year t_idx
        high_inflow = 0.0
        for i in range(max(0, t_idx - (work_years - 1)), t_idx + 1):
            years_worked = t_idx - i
            if 0 <= years_worked < work_years:
                attrition = (1.0 - p.high_attrition_rate) ** years_worked if p.high_attrition_rate > 0 else 1.0
                high_inflow += cohort_high_size[i] * attrition * inc_high * income_factors[years_worked] * tau_h_pool
        # Include RIG dividends flowing to pool
        high_inflow += stats[t_idx].rig_div_to_pool
        topup_demand = stats[t_idx].topup_need_low + stats[t_idx].topup_need_mid
        ss_deficits.append(high_inflow - topup_demand)

    steady_state_deficit = (
        sum(ss_deficits) / len(ss_deficits) if ss_deficits else 0.0
    )
    is_structurally_sustainable = steady_state_deficit >= 0.0

    # Loan repayment: did the loan ever go to 0 after being positive?
    loan_was_positive = False
    loan_ever_repaid = False
    for s in stats:
        if s.state_loan > 1.0:  # > 1 EUR threshold
            loan_was_positive = True
        elif loan_was_positive and s.state_loan < 1.0:
            loan_ever_repaid = True
            break
    # If loan was never taken, consider it trivially "repaid"
    if not loan_was_positive:
        loan_ever_repaid = True

    # Max loan-to-assets ratio
    max_loan_to_assets = 0.0
    for s in stats:
        total_assets = s.pool + s.assets_low + s.assets_mid + s.longevity_pool + s.rig_fund
        if total_assets > 1.0:
            ratio = s.state_loan / total_assets
            max_loan_to_assets = max(max_loan_to_assets, ratio)

    # --- Longevity metrics ---
    total_longevity_payouts = sum(s.longevity_payout_total for s in stats)
    total_longevity_backstop = sum(s.longevity_backstop for s in stats)
    peak_longevity_retirees = max((s.longevity_retirees for s in stats), default=0)

    # --- Tontine metrics ---
    longevity_per_capita_list = [s.longevity_per_capita for s in stats if s.longevity_retirees > 0]
    peak_longevity_per_capita = max(longevity_per_capita_list) if longevity_per_capita_list else 0.0
    avg_longevity_per_capita = (
        sum(longevity_per_capita_list) / len(longevity_per_capita_list)
    ) if longevity_per_capita_list else 0.0

    # --- Reserve fund metrics ---
    peak_reserve_fund = max((s.reserve_fund for s in stats), default=0.0)

    # --- RIG metrics (Haertung 7) ---
    total_rig_dividends = sum(s.rig_div_total for s in stats)
    total_rig_to_pool = sum(s.rig_div_to_pool for s in stats)
    peak_rig_fund = max((s.rig_fund for s in stats), default=0.0)

    return RunResult(
        params=p,
        scenario_name=scenario_name,
        stats=stats,
        passed=passed,
        fail_years=fail_years,
        min_repl_low=min_low,
        min_repl_mid=min_mid,
        min_pool=min_pool if min_pool != float("inf") else 0.0,
        max_state_loan=max_state_loan,
        final_state_loan=state_loan,
        pool_depletion_year=pool_depletion_year,
        steady_state_deficit=steady_state_deficit,
        is_structurally_sustainable=is_structurally_sustainable,
        loan_ever_repaid=loan_ever_repaid,
        max_loan_to_assets_ratio=max_loan_to_assets,
        final_longevity_pool=longevity_pool,
        total_longevity_payouts=total_longevity_payouts,
        total_longevity_backstop=total_longevity_backstop,
        peak_longevity_retirees=peak_longevity_retirees,
        peak_longevity_per_capita=peak_longevity_per_capita,
        avg_longevity_per_capita=avg_longevity_per_capita,
        final_reserve_fund=reserve_fund,
        peak_reserve_fund=peak_reserve_fund,
        final_rig_fund=rig_fund,
        peak_rig_fund=peak_rig_fund,
        total_rig_dividends=total_rig_dividends,
        total_rig_to_pool=total_rig_to_pool,
    )
