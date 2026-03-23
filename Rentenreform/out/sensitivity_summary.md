# RSSP_v2 Sensitivity Analysis Summary

**Generated**: 2026-02-15 19:04
**Horizon**: 100 years | **Pass criterion**: last 10 years meet guarantees

## 1. Multi-Dimensional Sweep Overview

- Total configurations tested: **220**
- Passing configurations: **156** (70.9%)
- tau_high range: 5.00% to 30.00%
- Real return range: 0.0% to 2.5%

### Pass Rate by tau_high x Real Return (averaged over feature combos)

| tau_high | 0.0% | 0.5% | 1.0% | 1.7% | 2.5% |
|---|---|---|---|---|---|
| 5.0% | 0/4 | 0/4 | 0/4 | 2/4 | 4/4 |
| 7.5% | 0/4 | 0/4 | 1/4 | 2/4 | 4/4 |
| 10.0% | 0/4 | 1/4 | 2/4 | 3/4 | 4/4 |
| 12.5% | 0/4 | 1/4 | 2/4 | 4/4 | 4/4 |
| 15.0% | 1/4 | 2/4 | 3/4 | 4/4 | 4/4 |
| 17.5% | 1/4 | 3/4 | 3/4 | 4/4 | 4/4 |
| 20.0% | 2/4 | 3/4 | 4/4 | 4/4 | 4/4 |
| 22.5% | 3/4 | 3/4 | 4/4 | 4/4 | 4/4 |
| 25.0% | 3/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| 27.5% | 3/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| 30.0% | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |

### Structurally Sustainable (steady-state deficit >= 0) by tau_high x Real Return
*(count out of 4 feature combinations)*

| tau_high | 0.0% | 0.5% | 1.0% | 1.7% | 2.5% |
|---|---|---|---|---|---|
| 5.0% | 0/4 | 0/4 | 0/4 | 2/4 | 2/4 |
| 7.5% | 0/4 | 0/4 | 0/4 | 2/4 | 4/4 |
| 10.0% | 0/4 | 0/4 | 0/4 | 2/4 | 4/4 |
| 12.5% | 0/4 | 0/4 | 0/4 | 2/4 | 4/4 |
| 15.0% | 0/4 | 0/4 | 2/4 | 2/4 | 4/4 |
| 17.5% | 0/4 | 0/4 | 2/4 | 4/4 | 4/4 |
| 20.0% | 0/4 | 2/4 | 2/4 | 4/4 | 4/4 |
| 22.5% | 0/4 | 2/4 | 2/4 | 4/4 | 4/4 |
| 25.0% | 2/4 | 2/4 | 2/4 | 4/4 | 4/4 |
| 27.5% | 2/4 | 2/4 | 4/4 | 4/4 | 4/4 |
| 30.0% | 2/4 | 2/4 | 4/4 | 4/4 | 4/4 |

## 2. Break-Even Analysis

| Configuration | Min tau_high (all scenarios) | Min real return (sustainable, tau=20%) | Min real return (sustainable, tau=15%) |
|---|---|---|---|
| Income profile: OFF, Longevity: OFF | 13.50% | 0.50% | 1.00% |
| Income profile: OFF, Longevity: ON | 18.00% | 0.50% | 1.00% |
| Income profile: ON, Longevity: OFF | 21.00% | 1.60% | 1.90% |
| Income profile: ON, Longevity: ON | 27.75% | 1.60% | 1.90% |

**Interpretation**: The minimum tau_high column shows the lowest contribution rate for high earners
that passes all 7 return scenarios (4 constant + 3 path-based). The real return columns show
the minimum investment return needed for the system to be structurally sustainable (inflows >= outflows)
in steady state, without relying on backstop loans.

## 3. Corrected Parameters (Researcher Recommendations)

Corrections applied (from research_validation.md Section 7):
- `cohort_size_at_age_start`: 831,435 -> **690,000**
- `mortality_buckets`: {0.99, 0.975, 0.95, 0.92} -> **{0.982, 0.955, 0.88, 0.72}**
- `income_low_retire`: 22,000 -> **30,000**
- `income_mid_retire`: 40,000 -> **50,000**

| Configuration | Min tau_high (original) | Min tau_high (corrected) | Delta |
|---|---|---|---|
| All features ON | 27.75% | 28.50% | +0.75% |
| Longevity ON, income profile OFF | 18.00% | 18.50% | +0.50% |
| Income profile ON, longevity OFF | 21.00% | 21.50% | +0.50% |
| Baseline (both OFF) | 13.50% | 14.00% | +0.50% |

**Key insight**: More realistic mortality (higher death rates) reduces the number of retirees
the system must support, while higher incomes increase both contributions and guarantee targets.
The net effect on tau_high depends on which factor dominates.

## 4. Political Feasibility Dashboard

**Reference**: Current GRV contribution rate = 18.6% (employer + employee), replacement rate ~48%

| tau_high | Real Return | Income Prof. | Longevity | Eff. Rate | High-Earner Annual | Max State Loan | Fiscal/GDP | Sustainable |
|---|---|---|---|---|---|---|---|---|
| 5.0% | 1.74% | OFF | OFF | 11.1% | EUR 3,600 | 0.0 bn | 0.000% | Yes |
| 5.0% | 2.50% | OFF | OFF | 11.1% | EUR 3,600 | 0.0 bn | 0.000% | Yes |
| 7.5% | 1.00% | OFF | OFF | 11.6% | EUR 5,400 | 0.0 bn | 0.000% | No |
| 7.5% | 1.74% | OFF | OFF | 11.6% | EUR 5,400 | 0.0 bn | 0.000% | Yes |
| 7.5% | 2.50% | OFF | OFF | 11.6% | EUR 5,400 | 0.0 bn | 0.000% | Yes |
| 10.0% | 0.50% | OFF | OFF | 12.1% | EUR 7,200 | 407.9 bn | 9.948% | No |
| 10.0% | 1.00% | OFF | OFF | 12.1% | EUR 7,200 | 0.0 bn | 0.000% | No |
| 10.0% | 1.74% | OFF | OFF | 12.1% | EUR 7,200 | 0.0 bn | 0.000% | Yes |
| 10.0% | 2.50% | OFF | OFF | 12.1% | EUR 7,200 | 0.0 bn | 0.000% | Yes |
| 12.5% | 0.50% | OFF | OFF | 12.6% | EUR 9,000 | 0.0 bn | 0.000% | No |
| 12.5% | 1.00% | OFF | OFF | 12.6% | EUR 9,000 | 0.0 bn | 0.000% | No |
| 12.5% | 1.74% | OFF | OFF | 12.6% | EUR 9,000 | 0.0 bn | 0.000% | Yes |
| 12.5% | 2.50% | OFF | OFF | 12.6% | EUR 9,000 | 0.0 bn | 0.000% | Yes |
| 15.0% | 0.00% | OFF | OFF | 13.1% | EUR 10,800 | 0.0 bn | 0.000% | No |
| 15.0% | 0.50% | OFF | OFF | 13.1% | EUR 10,800 | 0.0 bn | 0.000% | No |
| 15.0% | 1.00% | OFF | OFF | 13.1% | EUR 10,800 | 0.0 bn | 0.000% | Yes |
| 15.0% | 1.74% | OFF | OFF | 13.1% | EUR 10,800 | 0.0 bn | 0.000% | Yes |
| 15.0% | 2.50% | OFF | OFF | 13.1% | EUR 10,800 | 0.0 bn | 0.000% | Yes |
| 17.5% | 0.00% | OFF | OFF | 13.6% | EUR 12,600 | 0.0 bn | 0.000% | No |
| 17.5% | 0.50% | OFF | OFF | 13.6% | EUR 12,600 | 0.0 bn | 0.000% | No |
| 17.5% | 1.00% | OFF | OFF | 13.6% | EUR 12,600 | 0.0 bn | 0.000% | Yes |
| 17.5% | 1.74% | OFF | OFF | 13.6% | EUR 12,600 | 0.0 bn | 0.000% | Yes |
| 17.5% | 2.50% | OFF | OFF | 13.6% | EUR 12,600 | 0.0 bn | 0.000% | Yes |
| 20.0% | 0.00% | OFF | OFF | 14.1% | EUR 14,400 | 0.0 bn | 0.000% | No |
| 20.0% | 0.50% | OFF | OFF | 14.1% | EUR 14,400 | 0.0 bn | 0.000% | Yes |
| 20.0% | 1.00% | OFF | OFF | 14.1% | EUR 14,400 | 0.0 bn | 0.000% | Yes |
| 20.0% | 1.74% | OFF | OFF | 14.1% | EUR 14,400 | 0.0 bn | 0.000% | Yes |
| 20.0% | 2.50% | OFF | OFF | 14.1% | EUR 14,400 | 0.0 bn | 0.000% | Yes |
| 22.5% | 0.00% | OFF | OFF | 14.6% | EUR 16,200 | 0.0 bn | 0.000% | No |
| 22.5% | 0.50% | OFF | OFF | 14.6% | EUR 16,200 | 0.0 bn | 0.000% | Yes |
| 22.5% | 1.00% | OFF | OFF | 14.6% | EUR 16,200 | 0.0 bn | 0.000% | Yes |
| 22.5% | 1.74% | OFF | OFF | 14.6% | EUR 16,200 | 0.0 bn | 0.000% | Yes |
| 22.5% | 2.50% | OFF | OFF | 14.6% | EUR 16,200 | 0.0 bn | 0.000% | Yes |
| 25.0% | 0.00% | OFF | OFF | 15.1% | EUR 18,000 | 0.0 bn | 0.000% | Yes |
| 25.0% | 0.50% | OFF | OFF | 15.1% | EUR 18,000 | 0.0 bn | 0.000% | Yes |
| 25.0% | 1.00% | OFF | OFF | 15.1% | EUR 18,000 | 0.0 bn | 0.000% | Yes |
| 25.0% | 1.74% | OFF | OFF | 15.1% | EUR 18,000 | 0.0 bn | 0.000% | Yes |
| 25.0% | 2.50% | OFF | OFF | 15.1% | EUR 18,000 | 0.0 bn | 0.000% | Yes |
| 27.5% | 0.00% | OFF | OFF | 15.6% | EUR 19,800 | 0.0 bn | 0.000% | Yes |
| 27.5% | 0.50% | OFF | OFF | 15.6% | EUR 19,800 | 0.0 bn | 0.000% | Yes |
| 27.5% | 1.00% | OFF | OFF | 15.6% | EUR 19,800 | 0.0 bn | 0.000% | Yes |
| 27.5% | 1.74% | OFF | OFF | 15.6% | EUR 19,800 | 0.0 bn | 0.000% | Yes |
| 27.5% | 2.50% | OFF | OFF | 15.6% | EUR 19,800 | 0.0 bn | 0.000% | Yes |
| 30.0% | 0.00% | OFF | OFF | 16.1% | EUR 21,600 | 0.0 bn | 0.000% | Yes |
| 30.0% | 0.50% | OFF | OFF | 16.1% | EUR 21,600 | 0.0 bn | 0.000% | Yes |
| 30.0% | 1.00% | OFF | OFF | 16.1% | EUR 21,600 | 0.0 bn | 0.000% | Yes |
| 30.0% | 1.74% | OFF | OFF | 16.1% | EUR 21,600 | 0.0 bn | 0.000% | Yes |
| 30.0% | 2.50% | OFF | OFF | 16.1% | EUR 21,600 | 0.0 bn | 0.000% | Yes |
| 5.0% | 1.74% | OFF | ON | 11.1% | EUR 3,600 | 0.0 bn | 0.000% | Yes |
| 5.0% | 2.50% | OFF | ON | 11.1% | EUR 3,600 | 0.0 bn | 0.000% | Yes |
| 7.5% | 1.74% | OFF | ON | 11.6% | EUR 5,400 | 0.0 bn | 0.000% | Yes |
| 7.5% | 2.50% | OFF | ON | 11.6% | EUR 5,400 | 0.0 bn | 0.000% | Yes |
| 10.0% | 1.00% | OFF | ON | 12.1% | EUR 7,200 | 361.7 bn | 8.823% | No |
| 10.0% | 1.74% | OFF | ON | 12.1% | EUR 7,200 | 0.0 bn | 0.000% | Yes |
| 10.0% | 2.50% | OFF | ON | 12.1% | EUR 7,200 | 0.0 bn | 0.000% | Yes |
| 12.5% | 1.00% | OFF | ON | 12.6% | EUR 9,000 | 0.0 bn | 0.000% | No |
| 12.5% | 1.74% | OFF | ON | 12.6% | EUR 9,000 | 0.0 bn | 0.000% | Yes |
| 12.5% | 2.50% | OFF | ON | 12.6% | EUR 9,000 | 0.0 bn | 0.000% | Yes |
| 15.0% | 0.50% | OFF | ON | 13.1% | EUR 10,800 | 245.9 bn | 5.998% | No |
| 15.0% | 1.00% | OFF | ON | 13.1% | EUR 10,800 | 0.0 bn | 0.000% | Yes |
| 15.0% | 1.74% | OFF | ON | 13.1% | EUR 10,800 | 0.0 bn | 0.000% | Yes |
| 15.0% | 2.50% | OFF | ON | 13.1% | EUR 10,800 | 0.0 bn | 0.000% | Yes |
| 17.5% | 0.50% | OFF | ON | 13.6% | EUR 12,600 | 0.0 bn | 0.000% | No |
| 17.5% | 1.00% | OFF | ON | 13.6% | EUR 12,600 | 0.0 bn | 0.000% | Yes |
| 17.5% | 1.74% | OFF | ON | 13.6% | EUR 12,600 | 0.0 bn | 0.000% | Yes |
| 17.5% | 2.50% | OFF | ON | 13.6% | EUR 12,600 | 0.0 bn | 0.000% | Yes |
| 20.0% | 0.00% | OFF | ON | 14.1% | EUR 14,400 | 36.4 bn | 0.887% | No |
| 20.0% | 0.50% | OFF | ON | 14.1% | EUR 14,400 | 0.0 bn | 0.000% | Yes |
| 20.0% | 1.00% | OFF | ON | 14.1% | EUR 14,400 | 0.0 bn | 0.000% | Yes |
| 20.0% | 1.74% | OFF | ON | 14.1% | EUR 14,400 | 0.0 bn | 0.000% | Yes |
| 20.0% | 2.50% | OFF | ON | 14.1% | EUR 14,400 | 0.0 bn | 0.000% | Yes |
| 22.5% | 0.00% | OFF | ON | 14.6% | EUR 16,200 | 0.0 bn | 0.000% | No |
| 22.5% | 0.50% | OFF | ON | 14.6% | EUR 16,200 | 0.0 bn | 0.000% | Yes |
| 22.5% | 1.00% | OFF | ON | 14.6% | EUR 16,200 | 0.0 bn | 0.000% | Yes |
| 22.5% | 1.74% | OFF | ON | 14.6% | EUR 16,200 | 0.0 bn | 0.000% | Yes |
| 22.5% | 2.50% | OFF | ON | 14.6% | EUR 16,200 | 0.0 bn | 0.000% | Yes |
| 25.0% | 0.00% | OFF | ON | 15.1% | EUR 18,000 | 0.0 bn | 0.000% | Yes |
| 25.0% | 0.50% | OFF | ON | 15.1% | EUR 18,000 | 0.0 bn | 0.000% | Yes |
| 25.0% | 1.00% | OFF | ON | 15.1% | EUR 18,000 | 0.0 bn | 0.000% | Yes |
| 25.0% | 1.74% | OFF | ON | 15.1% | EUR 18,000 | 0.0 bn | 0.000% | Yes |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
*(76 more rows in CSV)*

### Comparison to Current GRV

| Metric | Current GRV | RSSP (typical passing config) |
|---|---|---|
| Contribution rate (total) | 18.6% (employer + employee) | See Eff. Rate above |
| Replacement rate (low earners) | ~48% of average wage | 100% of retire-age income |
| Replacement rate (mid earners) | ~48% of average wage | 70% of retire-age income |
| High earners | Pay 18.6%, receive ~48% | Pay tau_high, receive 0% |
| Funding model | 100% PAYG | 100% funded (individual accounts) |
| State fiscal exposure | Implicit (tax-funded deficit) | Explicit backstop loan |
| Post-87 coverage | GRV pays until death | Longevity pool (floor EUR 10k/yr) |
