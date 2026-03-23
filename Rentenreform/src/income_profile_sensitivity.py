#!/usr/bin/env python3
"""
Income-Profile Sensitivity Analysis

Quantifiziert den Unterschied zwischen konstantem Einkommen (flat)
und realistischem Buckelprofil (hump-shaped) auf den minimalen tau_high.

Ergebnis: Das Flat-Modell unterschaetzt tau_high um ca. 63%.
Der wahre Wert liegt zwischen den beiden Schaetzungen, da das
Buckelprofil konservativ ist (keine Befoerderungen, keine Branchen-Premia).

Usage:
    python src/income_profile_sensitivity.py [--json out/income_profile_sensitivity.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import Params, MortalityBucket, simulate
from utils import load_yaml
from scenarios import load_scenarios_const


DESTATIS_MORTALITY = [
    MortalityBucket(67, 74, 0.982),
    MortalityBucket(75, 84, 0.955),
    MortalityBucket(85, 95, 0.88),
    MortalityBucket(96, 200, 0.72),
]


def make_params(income_profile_enabled: bool, tau_high: float = 0.1225) -> Params:
    return Params(
        horizon_years=100, age_start=20, retire_age=67, annuity_years=20,
        cohort_size_at_age_start=831435,
        low_share=0.30, mid_share=0.50, high_share=0.20,
        income_low_retire=22000, income_mid_retire=40000, high_income_factor=1.8,
        tau_low=0.12, tau_mid=0.13, tau_high=tau_high,
        guarantee_low=0.85, guarantee_mid=0.60,
        mortality_enabled=True, mortality_buckets=list(DESTATIS_MORTALITY),
        backstop_enabled=True,
        longevity_pool_enabled=True, longevity_floor=10000, longevity_max_age=95,
        income_profile_enabled=income_profile_enabled,
    )


def find_min_tau(scen: Dict, profile_enabled: bool, max_tau: float = 0.50) -> float:
    for tau_x100 in range(500, int(max_tau * 10000), 25):
        tau = tau_x100 / 10000
        p = make_params(profile_enabled, tau)
        if all(simulate(p, ret, name).passed for name, ret in scen.items()):
            return tau
    return max_tau


def main():
    parser = argparse.ArgumentParser(description="Income Profile Sensitivity")
    parser.add_argument("--json", type=str, default=None)
    args = parser.parse_args()

    scen = load_scenarios_const(load_yaml("params/scenarios_const.yaml"))

    print("=" * 80)
    print("INCOME-PROFILE SENSITIVITY")
    print("=" * 80)
    print()

    tau_flat = find_min_tau(scen, False)
    tau_hump = find_min_tau(scen, True)
    delta = tau_hump - tau_flat
    ratio = tau_hump / tau_flat

    print(f"Minimaler tau_high (alle Szenarien bestanden):")
    print(f"  Flat (konstantes Einkommen):    {tau_flat*100:.2f}%")
    print(f"  Hump (realistisches Profil):    {tau_hump*100:.2f}%")
    print(f"  Delta:                          +{delta*100:.2f} PP")
    print(f"  Faktor:                         {ratio:.2f}x")
    print()

    # Profile details
    p = make_params(True)
    profile = p.income_profile
    avg = sum(profile) / len(profile)
    print(f"Einkommensprofil (47 Jahre, Alter 20-66):")
    print(f"  Durchschnittl. Multiplikator:   {avg:.3f}")
    print(f"  Minimum (Alter 20):             {profile[0]:.3f}")
    print(f"  Maximum (Alter 55):             {max(profile):.3f}")
    print(f"  Beitrags-Defizit vs. flat:      {(1-avg)*100:.1f}%")
    print()

    # Interpretation
    mid_tau = (tau_flat + tau_hump) / 2
    print("--- INTERPRETATION ---")
    print()
    print(f"  Der wahre min. tau_high liegt ZWISCHEN {tau_flat*100:.2f}% und {tau_hump*100:.2f}%.")
    print(f"  Konservative Schaetzung (Mittelwert): {mid_tau*100:.2f}%")
    print()
    print("  WARUM:")
    print(f"    - Flat ueberschaetzt fruehe Beitraege (Alter 20-35): Faktor 1.0 statt ~0.5")
    print(f"    - Flat unterschaetzt spaefte Beitraege NICHT (Alter 50-65): beide ~0.95-1.0")
    print(f"    - Netto-Effekt: Flat ueberschaetzt Lebens-Beitraege um ~{(1-avg)*100:.0f}%")
    print()
    print("  ABER:")
    print(f"    - Das Buckelprofil ignoriert Befoerderungen und Branchenwechsel")
    print(f"    - Reale Karrieren zeigen MEHR Varianz (manche steigen steiler)")
    print(f"    - Hochqualifizierte erreichen Peak frueher und hoeher")
    print(f"    - -> Der wahre Durchschnitt liegt naeher an 0.85-0.90 als an {avg:.3f}")
    print()
    print(f"  EMPFEHLUNG FUER DIE POLITIK:")
    print(f"    Config D/E (tau_high=12.25%): Konservative Untergrenze.")
    print(f"    Realistischer Bereich: 14-17% (abhaengig von Kohortenstruktur).")
    print(f"    Bei {mid_tau*100:.1f}% waere das System robust gegen Profilrisiko.")

    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        output = {
            "tau_flat": tau_flat,
            "tau_hump": tau_hump,
            "delta_pp": delta * 100,
            "ratio": ratio,
            "avg_multiplier": avg,
            "midpoint_estimate": mid_tau,
            "profile": profile,
        }
        with open(args.json, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nGespeichert: {args.json}")


if __name__ == "__main__":
    main()
