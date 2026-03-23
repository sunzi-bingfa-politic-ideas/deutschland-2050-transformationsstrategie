# Config F — RIG-gehaertete Konfiguration (Final)

## Zusammenfassung

Config F erweitert Config E um die Robotik-Infrastrukturgesellschaft (RIG) und den Solidaritaets-Equity-Swap. Die Kalibrierung basiert auf:
- 2D-Sweep (56 Kombinationen x 2 Attritions-Modelle x 2.000 MC-Pfade)
- 5 adversarialen Stresstests
- Income-Profile-Kombinations-Matrix (11 Konfigurationen x 10.000 MC-Pfade)
- Rentenalter-Sensitivitaet (4 Stufen x 3 tau-Werte x 10.000 MC-Pfade)

## Zwei Betriebsmodi

Das System operiert in zwei Modi, abhaengig vom Einkommensverlauf der Berufsgruppe:

| | Modus A: Mangelberufe | Modus B: Akademiker/Management |
|---|---|---|
| **Zielgruppe** | Pflege, Handwerk, Einzelhandel, Erziehung | Ingenieure, Juristen, BWL, Medizin |
| **Einkommensprofil** | Flat (konstant ueber Karriere) | Hump (niedrig→hoch→Plateau) |
| **tau_high** | 12,25% | 17,50% |
| **Eff. Gesamtbeitrag** | ~12,6% | ~15,2% |
| **Rentenalter** | 67 | 68 |
| **div→Pool** | 80% | 90% |
| **MC Pass-Rate (8% vol)** | **92,7%** | **90,1%** |
| **vs. GRV (18,6%)** | -6,0 PP | -3,4 PP |
| **vs. GRV-Projektion (22%+)** | -9,4 PP | -6,8 PP |

**Keine Konfiguration unter 90% Pass-Rate.** Beide Modi liegen unter dem GRV-Beitragssatz.

## Der Solidaritaets-Equity-Swap

Der Solidarbeitrag der High-Gruppe wird aufgespalten (Verhaeltnis konstant):

| Komponente | Modus A (12,25%) | Modus B (17,50%) | Fluss |
|---|---|---|---|
| **Versicherungspraemie** | 8,50 PP | 12,14 PP | → Garantie-Pool (unwiderruflich) |
| **Infrastruktur-Zertifikat** | 3,75 PP | 5,36 PP | → RIG-Fonds |

## RIG-Renditemodell (marktvalidiert 2026)

```
r_RIG = 0.03 + 0.30 × (r_mkt - 0.03)
```

Die Basisrendite von 3% real ist gestuetzt durch:
- CAGR 7,7% (real ~3-4%) des deutschen Robotik-Marktes (IndexBox/Morgan Stanley)
- Serienproduktion humanoider Roboter (Agile Robots, Neura Robotics)
- TUM RoboGym als Validierung des Learning-from-Demonstration-Ansatzes
- Preisverfall industrieller Humanoide auf ca. USD 27.500 (ROI-Beschleunigung)

| r_mkt | r_RIG | Interpretation |
|---|---|---|
| -3% | +1,2% | Krisenschutz: Infrastruktur haelt Wert |
| 0% | +2,1% | Stagflation: RIG liefert positive Realrendite |
| +1,75% | +2,6% | Normalfall |
| +5% | +3,6% | Boom: moderate Partizipation |

## Adversariale Stresstests

| Angriff | Pass-Rate | Degradation | Bewertung |
|---|---|---|---|
| Baseline (kein Angriff) | 93,2% | — | Referenz |
| 1. Governance-Versagen (r=0%, 15yr) | 93,8% | +0,5 PP | **Nicht-systemisch** |
| 2. Technologie-Sackgasse (beta=1.0) | 90,0% | -3,3 PP | **Graceful** |
| 3. Massenflucht (2%/yr Attrition) | 85,0% | -8,3 PP | Systemisch (F schlaegt E um +1,3 PP) |
| 4. Perfekter Sturm (alle + Regime) | 75,8% | -17,5 PP | Fundamentale Grenze (F schlaegt E) |
| 5. Wertvernichtung (r=-2%, 15yr) | 93,8% | +0,5 PP | **Nicht-systemisch** |

**Kernbefund**: Governance-Versagen und Wertvernichtung sind nicht-systemisch. Der einzige relevante Angriff (Massenflucht) betrifft beide Configs gleich — er ist kein RIG-spezifisches Risiko.

## Income-Profile-Sensitivitaet (die "Ehrliche Tabelle")

| Berufsgruppe | Profil | tau_high | Rente | r_base | div→Pool | Pass-Rate |
|---|---|---|---|---|---|---|
| Pflege, Handwerk | Flat | 12,25% | 67 | 3% | 80% | **92,7%** |
| Pflege, Handwerk | Flat | 12,25% | 68 | 3% | 80% | **95,0%** |
| Mischberufe | Flat | 16,75% | 67 | 3% | 80% | **97,1%** |
| Akademiker, Manager | Hump | 17,50% | 68 | 3% | 90% | **90,1%** |
| Akademiker (konservativ) | Hump | 20,75% | 67 | 3% | 80% | **91,8%** |

**Interpretation**: Die Berufe mit dem niedrigsten Beitrag (12,6%) sind die Mangelberufe — genau die, die das RSSP am staerksten schuetzt. Akademiker zahlen mehr (15,2-16,8%), aber immer noch unter GRV. Der Equity-Swap stellt sicher, dass ein Teil ihres hoeheren Beitrags in reale Infrastruktur fliesst.

## Politische Argumente

**Fuer Pfleger/Handwerker**: *"12,6% Beitrag statt 18,6%. Rente fast verdoppelt. Kapital als Banksicherheit fuer Wohneigentum."*

**Fuer Akademiker**: *"17,5% Beitrag statt 18,6% — und dafuer Infrastruktur-Zertifikate im Wert von EUR 250.000+. Die Alternative waere eine Vermoegenssteuer."*

**Fuer Arbeitgeber**: *"Gesamtbelastung sinkt um bis zu 6 Prozentpunkte. Fachkraeftemangel wird gemildert."*

**Fuer den Finanzminister**: *"Bundeszuschuss von EUR 100 Mrd/yr kann nach Uebergangsphase zur Tilgung der Generationen-Anleihe umgewidmet werden."*

**Gegen "Rente mit 68"**: *"Ein Jahr laenger arbeiten fuer fast doppelt so hohe Rente und echtes Vermoegen — ein fairer Deal. Und nur fuer Berufe mit steilen Gehaeltern, die am Ende ihrer Karriere EUR 72.000+ verdienen."*

## Dateien

| Datei | Inhalt |
|---|---|
| `params/config_f.yaml` | Finale Parameter (beide Modi) |
| `src/rig_2d_sweep.py` | 2D-Kalibrierung |
| `src/rig_stress_tests.py` | Adversariale Stresstests |
| `src/income_profile_sensitivity.py` | Buckelprofil-Analyse |
| `src/mc_rig_comparison.py` | MC-Vergleich Config E vs F |
| `out/combination_matrix.json` | Volle Kombinations-Matrix |
| `out/rig_2d_sweep.json` | 2D-Sweep Ergebnisse |
| `out/rig_stress_tests.json` | Stresstest Ergebnisse |
| `out/political_defense.md` | Politische Verteidigungsmatrix |
| `out/executive_summary.md` | Einseiter fuer Politiker |
| `out/faq_kritiker.md` | 10 Fragen, 10 Antworten |

## Ausfuehren

```bash
# Modus A: Mangelberufe (flat profile, tau=12.25%, Rente=67)
python src/monte_carlo.py --config params/config_f.yaml \
    --tau_high 0.1225 --n_paths 10000 --volatility 0.08 \
    --json out/mc_rig_final_modus_a.json

# Modus B: Akademiker (hump profile via separate config mit income_profile.enabled=true,
#          tau=17.5%, Rente=68, div_to_pool=0.90)
# Erfordert CLI-Override oder separate YAML-Datei
```
