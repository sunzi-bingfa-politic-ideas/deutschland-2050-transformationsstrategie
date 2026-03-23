# Config F — finale, gehaertete Konfiguration

## Ueberblick

Config F ist die derzeit robusteste Ausbaustufe des RSSP-Modells. Sie erweitert die fruehere Konfiguration um eine realwirtschaftliche Absicherung ueber die Robotik-Infrastrukturgesellschaft (RIG) sowie um eine Solidaritaetskomponente fuer hoehere Einkommen.

Die Kalibrierung basiert auf:

- einem zweidimensionalen Parametersweep,
- adversarialen Stresstests,
- einer Sensitivitaetsanalyse nach Einkommensprofilen,
- und einer zusaetzlichen Pruefung ueber unterschiedliche Renteneintritts- und Beitragsannahmen.

Die Konfiguration ist nicht als endgueltige Wahrheit zu verstehen, sondern als die bisher belastbarste modellierte Variante.

---

## Zwei Betriebsmodi

Das System unterscheidet zwei typische Einkommensverlauefe, weil sich daraus unterschiedliche Beitrags- und Sicherungslogiken ergeben.

| | Modus A: stabile Berufsverlauefe | Modus B: steilere Karriereverlauefe |
|---|---|---|
| Zielgruppe | Pflege, Handwerk, Einzelhandel, Erziehung | Ingenieurwesen, Recht, Medizin, Management |
| Einkommensprofil | eher konstant | eher ansteigend |
| tau_high | 12,25% | 17,50% |
| effektiver Gesamtbeitrag | ca. 12,6% | ca. 15,2% |
| Renteneintritt | 67 | 68 |
| Anteil in den Pool | 80% | 90% |
| Monte-Carlo-Ergebnis (8% Volatilitaet) | 92,7% | 90,1% |
| gegenueber GRV | deutlich niedriger | niedriger |

Beide Modi bleiben unter dem heutigen GRV-Beitragssatz. Die Konfigurationen unterscheiden sich vor allem darin, wie stark sie auf Stabilitaet, Solidaritaet und reale Absicherung gewichten.

---

## Solidaritaets- und Infrastrukturkomponente

Der Beitrag der hoeheren Einkommensgruppen wird in zwei Teile aufgeteilt:

| Komponente | Modus A (12,25%) | Modus B (17,50%) | Funktion |
|---|---|---|---|
| Versicherungsteil | 8,50 PP | 12,14 PP | Finanzierung der Garantie- und Sicherungsmechanik |
| Infrastrukturteil | 3,75 PP | 5,36 PP | Aufbau eines realen Vermoegenstocks ueber die RIG |

Damit wird ein Teil der Belastung nicht nur umverteilt, sondern in reale Werte ueberfuehrt, die das System zusaetzlich stuetzen sollen.

---

## RIG-Modell

Die RIG dient als realwirtschaftlicher Anker des Systems. Sie soll Vermoegenswerte aufbauen, die weniger direkt von kurzfristigen Marktschwankungen abhaengen als rein finanzielle Positionen.

Das zugrunde liegende Renditemodell ist bewusst konservativ kalibriert:

```
r_RIG = 0.03 + 0.30 × (r_mkt - 0.03)
```

Die Basisrendite von 3% real orientiert sich an der langfristigen Wachstumsrate des deutschen Robotik- und Automatisierungsmarktes (Quellen: IndexBox 2026, Morgan Stanley Robotics Research; realer CAGR ~3-4% nach Kostenabzug). Der Faktor 0,30 begrenzt die Beteiligung an Marktschwankungen — damit bleibt die RIG auch bei fallenden Maerkten im positiven Bereich. Diese Annahme ist eine der zentralen Stellschrauben des Modells; eine Variation der Basisrendite zwischen 2% und 4% ist in der Sensitivitaetsanalyse dokumentiert (`out/rig_2d_sweep.json`).

| Marktsituation | RIG-Rendite | Einordnung |
|---|---|---|
| Schwache Maerkte (-3%) | +1,2% | Stabilitaetsfunktion: Infrastruktur haelt Wert |
| Nullwachstum (0%) | +2,1% | Krisenpuffer: Positive Realrendite bleibt |
| Normalfall (+1,75%) | +2,6% | Basisszenario |
| Boomphase (+5%) | +3,6% | Partielle Beteiligung, aber begrenzt |

Die RIG ist damit nicht als spekulatives Zusatzvehikel gedacht, sondern als dauerhafter realer Anker fuer das Gesamtsystem.

---

## Stresstests

Die Konfiguration wurde gegen mehrere Belastungsszenarien geprueft:

| Szenario | Pass-Rate | Degradation | Einordnung |
|---|---|---|---|
| Baseline (kein Angriff) | 93,2% | — | Referenz |
| Governance-Versagen (15 Jahre Nullrendite) | 93,8% | +0,5 PP | Vom System absorbiert |
| Technologie-Verzoegerung (RIG-Rendite schwankt staerker mit dem Gesamtmarkt als angenommen) | 90,0% | -3,3 PP | Moderat; System bleibt funktionsfaehig |
| Staerkere Abwanderung (2%/Jahr) | 85,0% | -8,3 PP | Spuerbar; betrifft jedes kapitalgedeckte System |
| Kombinierter Ausfall (alle Faktoren gleichzeitig) | 75,8% | -17,5 PP | Extremszenario; grundsaetzliche Grenze |
| Wertvernichtung (-2% Rendite, 15 Jahre) | 93,8% | +0,5 PP | Vom System absorbiert |

Das Ergebnis ist nicht, dass das System unverwundbar waere. Das Ergebnis ist, dass es in mehreren relevanten Szenarien stabil bleibt und seine Grundfunktion weiterhin erfuellt. Besonders wichtig ist die Unterscheidung zwischen Risiken, die das Modell gut abfedern kann, und Risiken, die grundsaetzlich jedes kapitalgedeckte System belasten wuerden.

---

## Einkommensprofile

Die Sensitivitaetsanalyse zeigt, dass sich die Wirkung des Modells je nach Berufs- und Einkommensprofil unterscheidet:

| Berufsgruppe | Profil | tau_high | Renteneintritt | Pass-Rate |
|---|---|---|---|---|
| Pflege, Handwerk | stabil | 12,25% | 67 | 92,7% |
| Pflege, Handwerk | stabil | 12,25% | 68 | 95,0% |
| Mischberufe | stabil | 16,75% | 67 | 97,1% |
| Akademiker, Manager | ansteigend | 17,50% | 68 | 90,1% |
| Akademiker (konservativ) | ansteigend | 20,75% | 67 | 91,8% |

Die Kernaussage ist nicht, dass ein Profil bevorzugt oder benachteiligt wird, sondern dass das Modell unterschiedliche Einkommensverlauefe gezielt beruecksichtigt. Der niedrigste Beitragssatz gilt fuer die Berufsgruppen, deren Absicherung im heutigen System am schwaechsten ist.

---

## Politische Einordnung

Die politische Logik hinter Config F ist bewusst einfach gehalten:

- Beschaeftigte mit stabilen Erwerbsverlaufen sollen entlastet werden.
- Hoehere Einkommen sollen staerker zur Stabilitaet des Systems beitragen.
- Reale Vermoegenswerte sollen das Modell zusaetzlich absichern.
- Die Reform soll nicht maximal disruptiv, sondern anschlussfaehig sein.

Das macht die Konfiguration politisch realistischer als ein reines Idealmodell.

---

## Verweise

| Datei | Inhalt |
|---|---|
| `params/config_f.yaml` | Finale Parameter (beide Modi) |
| `src/rig_2d_sweep.py` | Kalibrierung |
| `src/rig_stress_tests.py` | Belastungstests |
| `src/income_profile_sensitivity.py` | Einkommenssensitivitaet |
| `src/mc_rig_comparison.py` | Vergleich zwischen Varianten |
| `out/combination_matrix.json` | Vollstaendige Matrix |
| `out/rig_2d_sweep.json` | Sweep-Ergebnisse |
| `out/rig_stress_tests.json` | Stresstest-Ergebnisse |
| `out/political_defense.md` | Politische Einordnung |
| `out/executive_summary.md` | Kurzfassung |
| `out/faq_kritiker.md` | Haeufige Einwaende |

---

## Ausfuehren

```bash
# Monte-Carlo-Simulation fuer Config F
python src/monte_carlo.py --config params/config_f.yaml \
  --tau_high 0.1225 --n_paths 10000 --volatility 0.08 \
  --json out/mc_config_f_vol8.json
```

---

## Einordnung

Config F ist die belastbarste bisher modellierte Variante des RSSP. Sie ersetzt nicht die politische Entscheidung, ob ein solches System eingefuehrt werden soll. Sie zeigt aber, unter welchen Annahmen eine stabile, kapitalgedeckte und realwirtschaftlich abgesicherte Ausgestaltung moeglich waere.
