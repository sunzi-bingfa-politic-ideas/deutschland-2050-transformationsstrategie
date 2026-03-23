# RSSP — Renten-Spar- und Sicherungsprogramm

Ein kapitalgedecktes Alterssicherungssystem mit gestaffelter Kaufkraftgarantie, Robotik-Infrastrukturgesellschaft (RIG) und expliziter Umverteilungskomponente. Deterministisch und stochastisch validiert ueber 100 Jahre, 220 Parameterkonfigurationen und 10.000+ Monte-Carlo-Pfade.

## Das Problem

Die gesetzliche Rentenversicherung (GRV) steht vor dem Zusammenbruch. Der Altenquotient steigt von 37% (2024) auf 55% (2050). 163 Berufe stehen auf der Mangelliste. Pfleger, Handwerker und Erzieher — die tragenden Berufe — sind am schlechtesten abgesichert.

## Die Loesung: Drei Zahlen

| | GRV (heute) | RSSP |
|---|---|---|
| **Beitragssatz** | 18,6% (steigend auf 22%+) | **12,6–17%** (fix) |
| **Rente eines Pflegers** (EUR 28.000/yr) | EUR 1.120/Monat | **EUR 1.983/Monat** |
| **Rente eines Handwerkers** (EUR 32.000/yr) | EUR 1.280/Monat | **EUR 2.267/Monat** |

## Drei Konfigurationen

| | Config D | Config E | Config F |
|---|---|---|---|
| **Fokus** | Basiskalibrierung | + Tontine, Reserve, MC | + RIG, Equity-Swap |
| **tau_high** | 12,25% | 13,00% | 12,25–17,50% |
| **MC Pass-Rate (8% vol)** | 94% | 94% | **93%** (Modus A) / **90%** (Modus B) |
| **RIG-Fonds** | — | — | **EUR 1,95 Bio** |
| **Dokumentation** | [CONFIG_D.md](CONFIG_D.md) | [CONFIG_E.md](CONFIG_E.md) | [CONFIG_F.md](CONFIG_F.md) |

**Config F** ist die finale, oeffentlichkeitstaugliche Konfiguration mit:
- Solidaritaets-Equity-Swap (High-Earner erhalten Infrastruktur-Zertifikate)
- Robotik-Infrastrukturgesellschaft (dekorrelierter Realwert-Anker)
- 5 bestandene adversariale Stresstests (Governance-Versagen, Technologie-Risiko, Massenflucht, Wertvernichtung, Perfekter Sturm)
- Income-Profile-Sensitivitaet (alle Konfigurationen >= 90% Pass-Rate)

## Projektstruktur

```
rssp-rentenreform/
├── src/                        # Simulationscode
│   ├── model.py                # Kernmodell (9 Haertungen)
│   ├── optimize.py             # Optimierer (minimaler tau_high)
│   ├── monte_carlo.py          # Stochastische Simulation (log-normal, Regime, Fat-Tails)
│   ├── sensitivity.py          # 220-Konfig-Sweep
│   ├── transition.py           # Generationen-Anleihe-Modell
│   ├── rig_2d_sweep.py         # RIG 2D-Kalibrierung
│   ├── rig_stress_tests.py     # 5 Adversariale Stresstests
│   ├── income_profile_sensitivity.py  # Buckelprofil-Analyse
│   ├── mc_rig_comparison.py    # MC-Vergleich Config E vs F
│   ├── wealth_tax_compare.py   # Vermoegenssteuer vs. RSSP
│   ├── generational_npv.py     # NPV nach Geburtskohorte
│   └── ...                     # Weitere Analyse-Scripts
├── params/                     # YAML-Parameterdateien
│   ├── config_d.yaml           # Basiskonfiguration
│   ├── config_e.yaml           # Erweiterte Konfiguration
│   ├── config_f.yaml           # RIG-Konfiguration (kalibriert, final)
│   └── scenarios_*.yaml        # Rendite-Szenarien
├── out/                        # Simulationsergebnisse
│   ├── executive_summary.md    # Einseiter fuer Politiker
│   ├── faq_kritiker.md         # 11 haerteste Fragen + Antworten
│   └── political_defense.md    # Politische Verteidigungsmatrix
├── paper/                      # Vollstaendiges Paper (6 Teile, 19 Abschnitte)
├── CONFIG_D.md                 # Config-D-Dokumentation
├── CONFIG_E.md                 # Config-E-Dokumentation
├── CONFIG_F.md                 # Config-F-Dokumentation (RIG-gehaertet)
└── LICENSE                     # MIT
```

## Installation

```bash
pip install -r requirements.txt
```

Abhaengigkeiten: `pyyaml >= 5.4`, `numpy >= 1.20`. Python 3.8+.

## Schnellstart

```bash
# Config D: Basiskalibrierung
python src/optimize.py --base params/config_d.yaml \
  --scenarios params/scenarios_const.yaml --mode const \
  --out out/best_config_d.json

# Config F: Monte Carlo mit finalen RIG-Parametern (10.000 Pfade)
python src/monte_carlo.py --config params/config_f.yaml \
  --tau_high 0.1225 --n_paths 10000 --volatility 0.08 \
  --json out/mc_config_f_vol8.json

# Adversariale Stresstests
python src/rig_stress_tests.py --n_paths 2000 \
  --json out/rig_stress_tests.json

# Income-Profile-Sensitivitaet
python src/income_profile_sensitivity.py \
  --json out/income_profile_sensitivity.json
```

## Paper

Das vollstaendige Paper ist in `paper/` als Markdown verfuegbar (6 Teile, 19 Abschnitte):

- **Teil I** (Abschnitte 1–2): Einleitung, Literatur
- **Teil II** (Abschnitt 3): Modellbeschreibung
- **Teil III** (Abschnitte 4–8): Ergebnisse, Monte Carlo, Sensitivitaet, Verteilung
- **Teil IV** (Abschnitte 9–12): Arbeitsmarkt, Wohneigentum, Gender, Verwaltungskosten
- **Teil V** (Abschnitte 13–16): Beitragsvergleich, High-Earner, Uebergang, Robotik-Infrastruktur
- **Teil VI** (Abschnitte 17–19): Strategie, Limitationen, Fazit

## Fuer Eilige

- **[Executive Summary](out/executive_summary.md)** — Eine Seite, drei Zahlen
- **[FAQ fuer Kritiker](out/faq_kritiker.md)** — 11 Fragen, 11 Antworten in je 3 Saetzen
- **[CONFIG_F.md](CONFIG_F.md)** — Technische Dokumentation der finalen Konfiguration

---

# RSSP — Retirement Savings and Security Programme

A capital-funded pension system with tiered purchasing-power guarantees, Robotics Infrastructure Company (RIG), and explicit redistribution. Deterministically and stochastically validated over 100 years, 220 parameter configurations, and 10,000+ Monte Carlo paths.

## Key Results

- **Effective contribution rate: 12.6–17%** — below Germany's current statutory pension (GRV at 18.6%, projected 22%+)
- **Replacement rates: 85% (low-earner) / 60% (mid-earner)** — guaranteed
- **All 7 deterministic stress scenarios passed**, including 0% real return over 100 years
- **93% pass rate** under stochastic simulation (Config F, 10,000 paths, 8% volatility)
- **5 adversarial stress tests passed** (governance failure, technology failure, mass flight, value destruction, perfect storm)
- **RIG fund: EUR 1.95 trillion** — real infrastructure assets decorrelated from financial markets

## Quick Start

```bash
pip install -r requirements.txt
python src/monte_carlo.py --config params/config_f.yaml --tau_high 0.1225 --n_paths 10000 --volatility 0.08 --json out/mc_config_f_vol8.json
```

## License

MIT
