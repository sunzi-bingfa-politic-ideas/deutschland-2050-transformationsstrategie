# Config D — Arbeitskonfiguration RSSP v2

## Zusammenfassung

Config D ist das Ergebnis einer systematischen Modellanalyse mit 6 Agenten, Parametervalidierung gegen Destatis-Daten, und einem Vergleich mit 220 Parameterkombinationen. Sie stellt den Punkt dar, an dem **mathematische Ehrlichkeit und politische Machbarkeit** sich treffen.

| Kennzahl | Config D | Aktuelles GRV |
|---|---|---|
| **Effektiver Beitragssatz** | **12.6%** | 18.6% |
| **Ersatzrate Low** (EUR 22k) | 85% = EUR 1.558/mo | ~48% |
| **Ersatzrate Mid** (EUR 40k) | 60% = EUR 2.000/mo | ~48% |
| **Ersatzrate High** (EUR 72k) | 0% (Solidarbeitrag) | ~48% (gedeckelt) |
| **Post-Annuity** (87-95) | EUR 833/mo (Grundsicherung) | Lebenslang |
| **Finanzierung** | Kapitalgedeckt + Garantiepool | Umlageverfahren |
| **Systemhorizont getestet** | 100 Jahre | — |
| **Stresstest 0% Realrendite** | Bestanden (mit Backstop) | Beitragssatz steigt |

## Ergebnis: tau_high = 12.25%

| Szenario | Bestanden | Pool-Depletion | Backstop (Mrd EUR) | Strukturell nachhaltig |
|---|---|---|---|---|
| base_1p7 (1.735%) | Ja | Nie | 0 | **Ja** (+53.9 Mrd/yr) |
| realistic_2p5 (2.5%) | Ja | Nie | 0 | **Ja** (+68.9 Mrd/yr) |
| low_1p0 (1.0%) | Ja | Nie | 0 | **Ja** (+28.9 Mrd/yr) |
| hard_0p5 (0.5%) | Ja | Nie | 0 | Nein (-2.1 Mrd/yr) |
| flat_0p0 (0.0%) | Ja | Jahr 80 | 522.6 | Nein (-27.4 Mrd/yr) |
| drawdown_5y (-3%/yr) | Ja | Nie | 0 | **Ja** (+49.0 Mrd/yr) |
| crash_recover (-10%) | Ja | Nie | 0 | **Ja** (+53.1 Mrd/yr) |

**5 von 7 Szenarien sind strukturell nachhaltig** (steady-state Ueberschuss). Die beiden negativen (0.0% und 0.5%) bestehen trotzdem den Garantietest dank Puffer-Aufbauphase und Staats-Backstop.

## Belastung nach Einkommensgruppe

| Gruppe | Einkommen | Beitrag/Monat | Pension/Monat | Rendite auf Beitrag |
|---|---|---|---|---|
| Low (30%) | EUR 22.000/yr | EUR 220 | EUR 1.558 | Positiv (subventioniert) |
| Mid (50%) | EUR 40.000/yr | EUR 433 | EUR 2.000 | Positiv (teilsubventioniert) |
| High (20%) | EUR 72.000/yr | EUR 735 | EUR 0 | Negativ (Solidarbeitrag) |

High-Earner Lebenszeitbelastung: EUR 735 × 12 × 47 = EUR 414.540 ohne Gegenleistung.
Zum Vergleich: Aktueller GRV-Arbeitnehmeranteil bei EUR 72k: EUR 558/mo (9.3%).

## Warum Config D und nicht die Alternativen

| Konfiguration | tau_high | Problem |
|---|---|---|
| Original (100%, 70%) | 21.75% | Politisch unmoeglich, High zahlt EUR 1.305/mo |
| Gemini "Scenario F" (85%, nur >=1%) | 7.50% | Kein echtes Garantiesystem — bricht bei 0% |
| **Config D (85%, 60%, alle Szenarien)** | **12.25%** | **Robust + machbar** |
| Config D + korr. Einkommen (30k/50k) | 16.50% | Hoehere Garantie-Ziele treiben Kosten |

## Offene Punkte fuer die Breitere Vision

1. **Transitionspfad**: Wie von GRV (Umlage) zu RSSP (Kapitaldeckung) ohne "Doppelzahler"-Generation?
2. **High-Earner Incentive**: Teilrueckerstattung, Katastrophenversicherung, oder breite Steuerfinanzierung statt reinem Solidarbeitrag?
3. **Einkommensprofile**: Bei Aktivierung steigt tau_high auf ~24.5%. Ist flat income eine akzeptable Vereinfachung?
4. **Demografiepfad**: Config D nutzt konstante Kohorten. Schrumpfpfad erhoecht tau_high um ~1.5 pp.
5. **Korrigierte Destatis-Parameter**: Kohorte 690k statt 831k, Einkommen 30k/50k statt 22k/40k — Nettowirkung abhaengig von Garantieniveau.

## Dateien

| Datei | Inhalt |
|---|---|
| `params/config_d.yaml` | Parameter-Datei (direkt nutzbar mit optimize.py) |
| `out/research_validation.md` | Parametervalidierung gegen Destatis/OECD (40+ Quellen) |
| `out/sensitivity_summary.md` | Vollstaendige Sensitivitaetsanalyse (220 Konfigurationen) |
| `out/sensitivity_sweep.csv` | Rohdaten der Sensitivitaetsanalyse |

## Ausfuehren

```bash
# Config D optimieren (Verifikation)
python src/optimize.py \
  --base params/config_d.yaml \
  --scenarios params/scenarios_const.yaml \
  --mode const \
  --out out/best_config_d.json

# Vollstaendiger Report
python src/report.py \
  --base params/config_d.yaml \
  --scenarios params/scenarios_const.yaml \
  --mode const \
  --out_csv out/truth_table_config_d.csv
```
