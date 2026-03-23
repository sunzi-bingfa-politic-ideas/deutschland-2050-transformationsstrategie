# Teil III: Ergebnisse, Sensitivitaet und Verteilungswirkungen

---

## 4. Baseline-Ergebnisse (Config D)

### 4.1 Parameterueberblick

Die Referenzkonfiguration (Config D) wurde durch systematische Optimierung ueber 220 Parameterkombinationen ermittelt. Sie repraesentiert den Punkt, an dem mathematische Robustheit und politische Machbarkeit konvergieren. Tabelle 4.1 fasst die zentralen Parameter zusammen.

**Tabelle 4.1: Config D -- Zentrale Parameter**

| Parameter | Wert | Begruendung |
|---|---|---|
| Simulationshorizont | 100 Jahre | Volle Generationenfolge + Steady-State-Pruefung |
| Erwerbsbeginn / Rentenalter | 20 / 67 Jahre | Gesetzliches Rentenalter, konservativer Eintritt |
| Annuitaetsphase | 20 Jahre (67--87) | Approximation der Restlebenserwartung ab 67 (~18 J.) |
| Post-Annuitaet (Longevity Pool) | 87--95 | Grundsicherungs-Floor EUR 10.000/Jahr |
| Realrendite (Basis) | 1,735% | Konservativ; vgl. globale Anleihenrendite 1900--2024: 1,7% |
| Beitragssatz Low / Mid / High | 12% / 13% / 12,25% | Effektiver Systemsatz: 12,6% |
| Garantie Low / Mid | 85% / 60% | Ersatzrate bezogen auf Einkommen bei Renteneintritt |
| Kohortengroesse | 831.435 | Auf Basis der Geburtskohorte; Sensitivitaet geprueft |
| Mortalitaet | Destatis-kalibriert | qx: 0,018 / 0,045 / 0,12 / 0,28 (altersgestuft) |

### 4.2 Szenarioergebnisse im Ueberblick

Config D wurde gegen sieben Szenarien getestet: vier mit konstanter Realrendite und drei mit pfadabhaengigen Schocks. Tabelle 4.2 dokumentiert die vollstaendigen Ergebnisse.

**Tabelle 4.2: Config D -- Ergebnisse aller sieben Szenarien**

| Szenario | Realrendite | Bestanden | Pool-Depletion | Backstop (Mrd EUR) | Steady-State-Saldo (Mrd/yr) | Strukturell nachhaltig |
|---|---|---|---|---|---|---|
| base_1p7 | 1,735% | Ja | Nie | 0 | +53,9 | **Ja** |
| realistic_2p5 | 2,5% | Ja | Nie | 0 | +68,9 | **Ja** |
| low_1p0 | 1,0% | Ja | Nie | 0 | +28,9 | **Ja** |
| hard_0p5 | 0,5% | Ja | Nie | 0 | -2,1 | Nein |
| flat_0p0 | 0,0% | Ja | Jahr 80 | 522,6 | -27,4 | Nein |
| drawdown_5y | -3%/yr 5J, dann 1,5% | Ja | Nie | 0 | +49,0 | **Ja** |
| crash_recover | -10% Schock, Erholung | Ja | Nie | 0 | +53,1 | **Ja** |

**Alle sieben Szenarien bestehen den Garantietest** (beide Garantien in den letzten 10 Jahren des 100-Jahres-Horizonts eingehalten). Fuenf von sieben Szenarien sind darueber hinaus *strukturell nachhaltig*, d.h. die jaehrlichen Zuefluesse uebersteigen die Abfluesse im Steady State.

### 4.3 Dynamik kritischer Szenarien

#### 4.3.1 Baseline (1,735% Realrendite)

Im Basisszenario akkumuliert das System waehrend der 47-jaehrigen Aufbauphase Kapital ohne Auszahlungen. Mit Renteneintritt der ersten vollstaendigen RSSP-Kohorte (Jahr 48) beginnen die Auszahlungen. Der Steady-State-Ueberschuss von +53,9 Mrd EUR/Jahr sichert die langfristige Stabilitaet. Der Garantiepool ist zu keinem Zeitpunkt auf staatliche Unterstuetzung angewiesen.

Bei 1,735% Realrendite erzielt die Low-Gruppe eine Ersatzrate von 85% (exakt die Garantie), waehrend die Mid-Gruppe 70% erreicht (ueber der 60%-Garantie, da der Pool Ueberschuesse anteilig verteilt).

#### 4.3.2 Realistic (2,5% Realrendite)

Bei 2,5% Realrendite -- einem Wert, der historisch dem langfristigen Durchschnitt konservativer Mischportfolios entspricht -- ueberperformt das System die Garantien deutlich:

| Gruppe | Garantie | Tatsaechliche Ersatzrate | Ueberperformance |
|---|---|---|---|
| Low | 85% | 100,0% (gedeckelt) | +15,0 PP |
| Mid | 60% | 88,0% | +28,0 PP |

Die Low-Gruppe erreicht bei 2,5% eine Ersatzrate von mindestens 100%, da die eigenen Kontobeitraege bereits einen grossen Teil der Garantie decken und Pool-Ueberschuesse zusaetzlich aufstocken. Die Mid-Gruppe erhaelt 88% statt der garantierten 60% -- eine massive Uebererfuellung, die den konservativen Charakter der Kalibrierung unterstreicht.

#### 4.3.3 Hard (0,5% Realrendite)

Das hard-Szenario markiert die Grenze der Selbsttragfaehigkeit. Der Steady-State-Saldo wird leicht negativ (-2,1 Mrd/yr), aber das waehrend der Aufbauphase akkumulierte Puffervermoegen reicht aus, um die Garantien ueber den gesamten 100-Jahres-Horizont einzuhalten. Kein Backstop-Darlehen wird benoetigt.

#### 4.3.4 Flat (0,0% Realrendite)

Das Extremszenario einer dauerhaften Nullrendite stellt den haertesten Test dar. Selbst Japans "verlorene Dekaden" (1989--2024) erzielten auf diversifizierten Portfolios eine positive Realrendite von ~0,8%. Bei 0% Realrendite:

- **Pool-Depletion**: Im Jahr 80 der Simulation erschoepft sich der Garantiepool.
- **Backstop-Aktivierung**: Der Staat gewaehrt ein Darlehen von maximal EUR 522,6 Mrd.
- **Garantien werden eingehalten**: Trotz Pool-Depletion erhalten Low- und Mid-Gruppe ihre vollen Garantien.
- **Nichtrueckzahlung**: Der Backstop-Kredit wird bei 0% Rendite nicht zurueckgezahlt; dies repraesentiert eine implizite Staatsgarantie, die jedoch nur im absoluten Extremfall aktiviert wird.

Entscheidend ist: Selbst dieses Szenario *besteht den Garantietest*. Das RSSP-Design trennt Garantieerfuellung (stets gesichert) von Selbsttragfaehigkeit (ab 0,5% Rendite gefaehrdet).

#### 4.3.5 Pfadabhaengige Szenarien

Die drei pfadabhaengigen Szenarien testen die Resilienz gegenueber sequenziellen Schocks:

| Szenario | Schockcharakter | Ergebnis |
|---|---|---|
| drawdown_5y | 5 Jahre -3%/yr, dann 1,5% | Strukturell nachhaltig (+49,0 Mrd/yr) |
| crash_recover | Einmaliger -10%-Schock, Erholung | Strukturell nachhaltig (+53,1 Mrd/yr) |

Beide pfadabhaengigen Szenarien, die einen Crash mit anschliessender Erholung modellieren, verhalten sich fast identisch zum Basisszenario. Die 47-jaehrige Aufbauphase bietet genuegend Zeit, temporaere Verluste auszugleichen -- ein wesentlicher Vorteil gegengrueber kurzfristig orientierten DC-Systemen.

### 4.4 Vergleich mit dem Status Quo (GRV)

**Tabelle 4.3: RSSP Config D vs. Gesetzliche Rentenversicherung**

| Kennzahl | GRV (aktuell) | RSSP Config D |
|---|---|---|
| Beitragssatz (gesamt) | 18,6% (steigend auf ~21%) | 12,6% (effektiv, fix) |
| Ersatzrate Low | ~48% | 85% (garantiert) |
| Ersatzrate Mid | ~48% | 60% (garantiert) |
| Ersatzrate High | ~48% (bis BBG) | 0% (Solidarbeitrag) |
| Finanzierungsform | Umlageverfahren | Kapitaldeckung + Garantiepool |
| Demografieresistenz | Niedrig (OAD steigt) | Hoch (kapitalgedeckt) |
| Altersarmutsrisiko | 19,6% (65+, 2024) | ~0% (Garantie > Armutsschwelle) |
| Post-87-Absicherung | Lebenslang (mit sinkendem Niveau) | Longevity Pool (EUR 833/Mo) |
| Stresstest 0% Realrendite | Beitragssatz muesste steigen | Bestanden (Backstop) |

Der zentrale Befund: Das RSSP erreicht bei einem um 6 Prozentpunkte niedrigeren Beitragssatz eine annaehernd doppelt so hohe Ersatzrate fuer Niedrigverdiener. Dies ist moeglich, weil (a) Kapitaldeckung die Rendite des Arbeitsmarktes durch die Rendite der Kapitalmaerkte substituiert, (b) eine 47-jaehrige Ansparphase den Zinseszinseffekt maximiert, und (c) die gestaffelte Garantie gezielt die unteren Einkommensgruppen schuetzt.

### 4.5 Peak Longevity Retirees

Im Steady State erreicht die Zahl der gleichzeitig im Longevity Pool befindlichen Rentner (Alter 87--95) einen Hoechststand von **1.499.879 Personen**. Dieser Wert reflektiert die Sterbetafelkalibrierung: Von einer Eintrittskohorte von 831.435 Personen ueberleben ca. 45% bis zum Alter 87, und davon wiederum ein abnehmender Anteil bis 95. Der Longevity Pool zahlt diesen Ueberlebenden einen Grundsicherungs-Floor von EUR 10.000/Jahr (EUR 833/Monat).

---

## 5. Erweiterte Ergebnisse: Config E (Tontine, Reserve-Regel, Monte Carlo)

### 5.1 Deterministische Ergebnisse

Config E aktiviert drei zusaetzliche Module gegenueber Config D: den Tontine-Longevity-Mechanismus, die symmetrische Reserve-Regel und die Monte-Carlo-Simulation. Der optimierte Solidarbeitragssatz steigt um 0,50 Prozentpunkte auf $\tau_H = 12{,}75\%$ (effektiver Gesamtbeitragssatz: 13,4%). Tabelle 5.1 zeigt die deterministischen Ergebnisse.

**Tabelle 5.1: Config E -- Deterministische Ergebnisse (fuenf Szenarien)**

| Szenario | Realrendite | Bestanden | Min RR Low | Min RR Mid | Longevity/Kopf | Pool-Depletion | Backstop (Mrd) | Strukturell nachhaltig |
|---|---|---|---|---|---|---|---|---|
| base_1p7 | 1,735% | Ja | 85,0% | 73,1% | EUR 30.000 | Nie | 0 | **Ja** |
| realistic_2p5 | 2,5% | Ja | 90,3% | 97,8% | EUR 30.000 | Nie | 0 | **Ja** |
| low_1p0 | 1,0% | Ja | 85,0% | 60,0% | EUR 30.000 | Nie | 0 | **Ja** |
| hard_0p5 | 0,5% | Ja | 85,0% | 60,0% | EUR 30.000 | Nie | 0 | **Ja** |
| flat_0p0 | 0,0% | Ja | 85,0% | 60,0% | EUR 29.864 | Jahr 84 | 393 | Nein |

**Alle fuenf deterministischen Szenarien bestehen den Garantietest.** Vier von fuenf sind strukturell nachhaltig (positiver Steady-State-Ueberschuss). Im 0%-Szenario erschoepft sich der Pool in Jahr 84 (Config D: Jahr 80); der Backstop-Bedarf sinkt von EUR 523 Mrd. (Config D) auf EUR 393 Mrd., da die hoehere Beitragsbasis laenger traegt.

### 5.2 Vergleich Config D vs. Config E

**Tabelle 5.2: Direkter Vergleich der Konfigurationen**

| Kennzahl | Config D | Config E | Delta |
|---|---|---|---|
| Solidarbeitrag $\tau_H$ | 12,25% | 12,75% | +0,50 PP |
| Effektiver Gesamtbeitrag | 12,6% | 13,4% | +0,8 PP |
| Longevity-Payout/Kopf/Jahr | EUR 10.000 | EUR 30.000 | **+200%** |
| Backstop (0%-Szenario) | EUR 523 Mrd. | EUR 393 Mrd. | -25% |
| Pool-Depletion (0%-Szenario) | Jahr 80 | Jahr 84 | +4 Jahre |
| Stoch. Pass-Rate (8% vol) | -- | 94,0% | -- |
| Reserve Peak (Median) | -- | EUR 203 Mrd. | -- |

**Interpretation**: Config E erzielt bei einem Aufpreis von 0,80 Prozentpunkten auf den effektiven Gesamtbeitrag eine dreifache Longevity-Payout-Steigerung und eine stochastische Validierung, die das Sequence-of-Returns-Risiko quantifiziert. Der Backstop-Bedarf im 0%-Extremszenario sinkt um 25%.

### 5.3 Tontine-Wirkung

Der Tontine-Mechanismus transformiert den Longevity Pool von einer reinen Grundsicherung zu einem an den Anlageerfolg gekoppelten Instrument:

| Szenario | Longevity/Kopf (Config D) | Longevity/Kopf (Config E) | Multiplikator |
|---|---|---|---|
| base_1p7 | EUR 10.000 | EUR 30.000 (Cap) | 3,0x |
| realistic_2p5 | EUR 10.000 | EUR 30.000 (Cap) | 3,0x |
| low_1p0 | EUR 10.000 | EUR 30.000 (Cap) | 3,0x |
| hard_0p5 | EUR 10.000 | EUR 30.000 (Cap) | 3,0x |
| flat_0p0 | EUR 10.000 | EUR 29.864 | 3,0x |

Bei allen Szenarien mit positiver Realrendite wird der 3x-Cap (EUR 30.000) erreicht. Selbst bei 0% Realrendite liegt der per-capita-Payout bei EUR 29.864 -- nur EUR 136 unter dem Cap. Der Nachhaltigkeits-Constraint verhindert dabei eine Ueberauszahlung aus dem Pool.

Die Kosten dieser Verbesserung sind moderat: 0,50 Prozentpunkte hoehere Solidarbeitraege fuer die High-Gruppe (EUR 360/Jahr bei EUR 72.000 Einkommen) erzeugen eine Verdreifachung der Langlebigkeitsabsicherung.

---

## 6. Monte-Carlo-Ergebnisse (Config E)

### 6.1 Methodik

Die Monte-Carlo-Simulation generiert stochastische Renditepfade und fuehrt fuer jeden Pfad die vollstaendige 100-Jahres-Simulation durch. Die Basis-Parametrisierung verwendet den Config-E-Parametersatz ($\tau_H = 12{,}75\%$, Tontine aktiviert, Reserve-Regel aktiviert) mit einer mittleren Realrendite von 1,75% und variabler Volatilitaet.

### 6.2 Volatilitaets-Sweep (log-normale Pfade)

**Tabelle 6.1a: Monte-Carlo-Ergebnisse nach Volatilitaet (Config E, $\tau_H = 12{,}75\%$)**

| Volatilitaet | N Pfade | Pass-Rate | Low P5 | Mid P5 | Pool-Depletion | Strukturell nachhaltig |
|---|---|---|---|---|---|---|
| 5% | 10.000 | **100,0%** | 85,0% | 60,0% | 3,0% | 97,5% |
| 8% | 10.000 | **94,0%** | 70,4% | 53,4% | 14,0% | 84,9% |
| 10% | 1.000 | **88,5%** | 56,5% | 44,9% | 25,0% | 72,3% |
| 15% | 1.000 | **67,1%** | 34,4% | 27,1% | 51,3% | 56,2% |

Die Ergebnisse offenbaren eine **kritische Volatilitaetsschwelle bei 8%**: Unterhalb dieser Schwelle besteht das System nahezu alle stochastischen Pfade (100% bei 5%). Oberhalb faellt die Pass-Rate steil ab -- bei 15% Volatilitaet bestehen nur noch zwei Drittel der Pfade.

**Implikation fuer das Anlagemandat**: Eine Portfolio-Volatilitaet von maximal 8% erfordert eine ausgewogene Allokation von circa 40--60% Aktien und 40--60% Anleihen/Immobilien/Sachwerte. Eine rein aktienbasierte Allokation (Volatilitaet 15--20%) wuerde die Systemstabilitaet gefaehrden.

### 6.3 Regime-Switching

Die Regime-Switching-Analyse modelliert persistente Marktregime (Bull/Bear) mit Markov-Transitionen, um geclusterte Renditeeinbrueche zu erfassen -- ein realistischeres Szenario als i.i.d.-Annahmen.

**Tabelle 6.1b: Regime-Switching-Ergebnisse (Config E, $\tau_H = 12{,}75\%$, $\sigma = 8\%$)**

| Kennzahl | Wert |
|---|---|
| N Pfade | 1.000 |
| Pass-Rate | **80,8%** |
| Low P5 / P50 / P95 | 34,3% / 85,0% / 302,2% |
| Mid P5 / P50 / P95 | 27,1% / 66,6% / 327,4% |
| Pool-Depletions-Rate | 32,3% |
| Strukturelle Nachhaltigkeit | 75,2% |
| Backstop P95 | EUR 611 Mrd. |
| Reserve Peak (Median) | EUR 825 Mrd. |
| Longevity per Capita (P50) | EUR 30.000 |
| Kredit jemals getilgt | 74,9% |

Die Regime-Switching-Pass-Rate von 80,8% liegt 13,2 Prozentpunkte unter der i.i.d.-Rate (94,0%). Die Differenz entsteht durch persistente Bear-Maerkte: Ein Bear-Regime dauert im Modell durchschnittlich 5 Jahre ($1 / (1 - 0{,}80)$), waehrend dessen Renditen bei $-2\% \pm 8\%$ liegen. Solche Cluster reduzieren die Pool-Akkumulation ueberproportional.

### 6.4 Fundamentale Grenze kapitalgedeckter Systeme

Eine Sensitivitaetsanalyse des Beitragssatzes unter Regime-Switching zeigt eine Saettigungskurve:

| $\tau_H$ | Pass-Rate (Regime-Switching, 8% vol) |
|---|---|
| 10% | ~70% |
| 12,75% | 80,8% |
| 15% | ~85% |
| 20% | ~90% |

**Selbst bei $\tau_H = 20\%$ erreicht das System unter Regime-Switching nur circa 90% Pass-Rate.** Die verbleibenden ~10% sind Pfade mit anhaltend negativen Realrenditen ueber mehr als 5 Jahre -- ein Szenario, das kein rein kapitalgedecktes System ueberstehen kann, da die Kapitalsubstanz irreversibel aufgezehrt wird. Dieses Ergebnis repraesentiert eine **fundamentale, nicht systemspezifische Grenze** kapitalgedeckter Altersvorsorge.

Moegliche Ergaenzungen fuer die verbleibenden Extrempfade:
- Lifecycle-Investing: Altersabhaengige Risikoreduktion (hohe Aktienquote in jungen Jahren, konservativ nahe Renteneintritt).
- Dynamische Garantieanpassung: Absenkung der Garantieniveaus in Extremszenarien mit vordefiniertem Trigger.
- Hybridkomponente: Teilweises Umlageverfahren als Puffer gegen Kapitalmarktrisiken.

### 6.5 Reserve-Regel in der Monte Carlo

Die symmetrische Reserve-Regel entfaltet ihre Wirkung ausschliesslich in stochastischen Umgebungen:

| Kennzahl | Wert (8% vol, 10k Pfade) |
|---|---|
| Peak Reserve (Median) | EUR 203 Mrd. |
| Peak Reserve (P95) | EUR 681 Mrd. |
| Reserve im 0%-Deterministic | EUR 0 (Trigger nie erreicht) |

Die Reserve akkumuliert waehrend Phasen mit Renditen ueber 3% und stabilisiert den Pool waehrend Phasen mit Renditen unter 1%. Die mediane Peak-Reserve von EUR 203 Mrd. entspricht etwa 1,4% des modellierten Systemvermoegens -- ein moderater, aber wirksamer Puffer gegen Sequenzrisiken.

### 6.6 Zusammenfassung der stochastischen Analyse

1. **Kritische Schwelle**: Portfolio-Volatilitaet $\le 8\%$ ist erforderlich fuer $\ge 94\%$ Pass-Rate (i.i.d.) bzw. $\ge 81\%$ (Regime-Switching).

2. **Fundamentale Grenze**: Kein Beitragssatz erzielt 100% Pass-Rate unter Regime-Switching. Die verbleibenden $\sim 10\%$ repraesentieren persistente Bear-Maerkte, die ausserhalb der Reichweite kapitalgedeckter Systeme liegen.

3. **Anlagemandat-Implikation**: Die Ergebnisse begrenzen den zulaessigen Aktienanteil auf circa 40--60% und fordern einen substanziellen Anteil an Anleihen, Immobilien und Sachwerten mit niedrigerer Volatilitaet.

4. **Reserve-Regel wirkt**: In stochastischen Umgebungen akkumuliert die Reserve im Median EUR 203 Mrd. und glaettet Pool-Schwankungen -- unsichtbar in deterministischen Szenarien, aber materiell in der Monte Carlo.

5. **Tontine robust**: Der Longevity per Capita erreicht in 50% der stochastischen Pfade den vollen 3x-Cap (EUR 30.000).

**Rigor: Medium-High** -- Die Monte-Carlo-Ergebnisse basieren auf 10.000 (i.i.d.) bzw. 1.000 (Regime-Switching) Pfaden mit vollstaendiger Simulation pro Pfad. Die Pass-Rate-Konfidenzintervalle sind eng (94,0% ± 0,5% bei N=10.000). Die Hauptunsicherheit liegt in der Wahl der Renditeverteilung (log-normal vs. Fat Tails) und der Regime-Kalibrierung.

---

## 7. Sensitivitaetsanalyse

### 7.1 Methodik des Multi-Dimensionalen Sweeps

Die Sensitivitaetsanalyse untersucht systematisch die Robustheit des RSSP ueber einen vierdimensionalen Parameterraum:

1. **tau_high** (Solidarbeitragssatz High): 5,0% bis 30,0% (11 Stufen)
2. **Realrendite**: 0,0%, 0,5%, 1,0%, 1,735%, 2,5% (5 Stufen)
3. **Einkommensprofil**: an/aus (Buckelprofil vs. flat income)
4. **Longevity Pool**: an/aus

Insgesamt wurden **220 Konfigurationen** getestet, jeweils gegen alle sieben Szenarien. Das Passkriterium erfordert, dass beide Garantien (85% Low, 60% Mid) in den letzten 10 Jahren des 100-Jahres-Horizonts eingehalten werden. Als *strukturell nachhaltig* gilt eine Konfiguration, wenn der Steady-State-Saldo (Zuefluesse minus Abfluesse) nicht negativ ist.

### 7.2 Bestehensquoten

**Tabelle 7.1: Bestehensquote nach tau_high und Realrendite (gemittelt ueber Feature-Kombinationen, jeweils 0--4 von 4)**

| tau_high | 0,0% | 0,5% | 1,0% | 1,7% | 2,5% |
|---|---|---|---|---|---|
| 5,0% | 0/4 | 0/4 | 0/4 | 2/4 | 3/4 |
| 7,5% | 0/4 | 0/4 | 0/4 | 2/4 | 4/4 |
| 10,0% | 0/4 | 0/4 | 1/4 | 2/4 | 4/4 |
| 12,5% | 0/4 | 1/4 | 1/4 | 3/4 | 4/4 |
| 15,0% | 0/4 | 1/4 | 2/4 | 3/4 | 4/4 |
| 17,5% | 1/4 | 2/4 | 3/4 | 4/4 | 4/4 |
| 20,0% | 1/4 | 2/4 | 3/4 | 4/4 | 4/4 |
| 22,5% | 2/4 | 3/4 | 3/4 | 4/4 | 4/4 |
| 25,0% | 3/4 | 3/4 | 4/4 | 4/4 | 4/4 |
| 27,5% | 3/4 | 3/4 | 4/4 | 4/4 | 4/4 |
| 30,0% | 3/4 | 4/4 | 4/4 | 4/4 | 4/4 |

Drei Befunde sind erkennbar: (1) Bei Realrenditen ab 1,7% genuegt bereits ein moderater tau_high von 12,5%, um die Mehrzahl der Konfigurationen zum Bestehen zu bringen. (2) Bei 0% Realrendite erfordert selbst ein tau_high von 30% die Deaktivierung kostensteigernder Features (Einkommensprofil, Longevity). (3) Die Grenze zwischen Bestehen und Nichtbestehen verlaeuft diagonal im (tau_high, Rendite)-Raum -- ein hoeher tau_high kompensiert niedrigere Renditen und umgekehrt.

### 7.3 Strukturelle Nachhaltigkeit

**Tabelle 7.2: Strukturell nachhaltige Konfigurationen (Steady-State-Ueberschuss >= 0, jeweils 0--4 von 4)**

| tau_high | 0,0% | 0,5% | 1,0% | 1,7% | 2,5% |
|---|---|---|---|---|---|
| 5,0% | 0/4 | 0/4 | 0/4 | 0/4 | 2/4 |
| 7,5% | 0/4 | 0/4 | 0/4 | 0/4 | 2/4 |
| 10,0% | 0/4 | 0/4 | 0/4 | 2/4 | 2/4 |
| 12,5% | 0/4 | 0/4 | 0/4 | 2/4 | 4/4 |
| 15,0% | 0/4 | 0/4 | 0/4 | 2/4 | 4/4 |
| 17,5% | 0/4 | 0/4 | 0/4 | 2/4 | 4/4 |
| 20,0% | 0/4 | 0/4 | 2/4 | 2/4 | 4/4 |
| 25,0% | 0/4 | 2/4 | 2/4 | 4/4 | 4/4 |
| 30,0% | 2/4 | 2/4 | 2/4 | 4/4 | 4/4 |

Die Schwelle fuer strukturelle Nachhaltigkeit liegt systematisch hoeher als die Bestehens-Schwelle. Waehrend eine Konfiguration den Garantietest bestehen kann, indem sie akkumuliertes Puffervermoegen aufzehrt, erfordert Nachhaltigkeit, dass die laufenden Einnahmen die laufenden Ausgaben decken. Config D (tau_high = 12,25%) ist bei der Basisrendite von 1,735% strukturell nachhaltig -- aber nur knapp: Der Ueberschuss betraegt +53,9 Mrd/yr bei ausgeschaltetem Einkommensprofil und aktiviertem Longevity Pool.

### 7.4 Break-Even-Analyse

**Tabelle 7.3: Minimaler tau_high fuer Bestehen aller 7 Szenarien, nach Feature-Kombination**

| Einkommensprofil | Longevity Pool | Min. tau_high (alle 7) | Min. Realrendite (nachhaltig, tau=20%) | Min. Realrendite (nachhaltig, tau=15%) |
|---|---|---|---|---|
| Aus | Aus | 16,00% | 1,00% | 1,40% |
| Aus | An | 21,75% | 1,00% | 1,40% |
| An | Aus | 24,50% | 2,00% | 2,30% |
| An | An | 32,25% | 2,00% | 2,30% |

Die Break-Even-Analyse offenbart die Kostenstruktur der einzelnen Modellkomponenten. Mit allen Features deaktiviert (Baseline) genuegt ein tau_high von 16%; jede Haertung erhoeht die Anforderung. Das Einkommensprofil (Buckelverlauf statt flat income) ist dabei der kostenintensivste Faktor.

### 7.5 Hebel-Wirkungsanalyse (Lever Impact)

Tabelle 7.4 quantifiziert den marginalen Einfluss jedes Design-Hebels auf den minimal erforderlichen tau_high. Die Berechnung erfolgt als Differenz des Break-Even-tau_high bei Aktivierung vs. Deaktivierung des jeweiligen Features.

**Tabelle 7.4: Hebelwirkung einzelner Design-Entscheidungen auf tau_high**

| Hebel | Aenderung tau_high (Prozentpunkte) | Richtung |
|---|---|---|
| Mortalitaetskorrektur (Destatis-Kalibrierung) | **-4,0 PP** | Senkend |
| Garantie Low: 100% -> 85% | **-1,75 PP** | Senkend |
| Garantie Mid: 70% -> 60% | **-3,75 PP** | Senkend |
| Ausschluss Einkommensprofil (flat income) | **-8,5 PP** | Senkend |
| Longevity Pool aktivieren | **+5,75 PP** | Steigernd |

**Interpretation**: Die groessten Einsparungen ergeben sich aus dem Ausschluss des Einkommensprofils (-8,5 PP). In der Realitaet folgen Einkommen einem Buckelverlauf (niedrig in jungen Jahren, hoeher im mittleren Alter, leichter Rueckgang vor der Rente). Wird dies modelliert, sinken die fruehen Beitraege erheblich, waehrend die Garantie auf dem Spitzeneinkommen basiert -- ein teurer Mismatch. Config D verwendet bewusst flat income als konservative Vereinfachung, die fruehe Beitraege leicht ueberschaetzt, dafuer aber die politische Machbarkeit des Beitragssatzes sichert.

Die Mortalitaetskorrektur senkt tau_high um 4 PP, weil realistischere (hoehere) Sterberaten die Anzahl der Rentenempfaenger reduzieren. Die Absenkung der Garantieniveaus von 100%/70% auf 85%/60% spart zusammen 5,5 PP -- der Preis fuer den Uebergang von einem "Weltrekord"-Garantieniveau zu einem realistischen, aber immer noch ueberdurchschnittlichen Niveau.

### 7.6 Fundamentale Arithmetik: Selbstfinanzierung nach Rendite

Die folgende Analyse beantwortet eine Kernfrage: Welcher Beitragssatz waere noetig, damit die Low-Gruppe ihre Garantie *ohne jede Quersubventionierung* selbst finanziert? Tabelle 7.5 berechnet dies fuer verschiedene Realrenditen.

**Tabelle 7.5: Selbstfinanzierungs-Arithmetik der Low-Gruppe (85%-Garantie, 47 J. Beitraege, 20 J. Auszahlung)**

| Realrendite | tau benoetig (Selbstfinanzierung) | Tatsaechliches tau_low | Selbstfinanzierungsquote | Defizit p.a. pro Person |
|---|---|---|---|---|
| 0,0% | 36,2% | 12,0% | 33,2% | EUR 12.510 |
| 0,5% | 30,6% | 12,0% | 39,3% | EUR 11.363 |
| 1,0% | 25,7% | 12,0% | 46,6% | EUR 9.990 |
| **1,735%** | **19,9%** | **12,0%** | **60,4%** | **EUR 7.414** |
| 2,5% | 15,1% | 12,0% | 79,4% | EUR 3.853 |
| 3,5% | 10,5% | 12,0% | 114,6% | -- (Ueberschuss) |
| 5,0% | 6,0% | 12,0% | 201,8% | -- (Ueberschuss) |

**Zentraler Befund**: Bei der konservativen Basisrendite von 1,735% finanziert die Low-Gruppe nur **60,4%** ihrer eigenen Garantie durch eigene Beitraege. Die verbleibenden 39,6% -- ein jaehrliches Defizit von EUR 7.414 pro Person -- muessen aus dem Solidarbeitrags-Pool der High-Gruppe finanziert werden.

Erst ab einer Realrendite von ca. 3,5% wird die Low-Gruppe vollstaendig selbsttragend. Bei 2,5% Rendite -- dem realistischen Szenario -- betraegt die Selbstfinanzierungsquote 79,4%, was einer selbst finanzierten Ersatzrate von 67,5% entspricht (gegenueber der 85%-Garantie).

**Zum Vergleich: 100%-Garantie (alte Konfiguration)**. Bei einer Garantie von 100% statt 85% sinkt die Selbstfinanzierungsquote bei 1,735% auf lediglich **51,3%**. Fast die Haelfte der Rentenleistung muesste quersubventioniert werden -- ein wesentlicher Grund fuer die Absenkung auf 85% in Config D.

### 7.7 Selbstfinanzierung der Mid-Gruppe

Die Mid-Gruppe (EUR 40.000, tau_mid = 13%, Garantie 60%) zeigt ein deutlich guenstigeres Bild:

| Realrendite | Selbstfinanzierungsquote | Jaehrl. Defizit pro Person |
|---|---|---|
| 1,735% | 92,6% | EUR 1.769 |
| 2,5% | > 100% | -- (selbsttragend + Ueberschuss) |

Bei der Basisrendite finanziert die Mid-Gruppe 92,6% ihrer Garantie selbst; das Restdefizit von EUR 1.769 pro Person und Jahr ist moderat. Ab 2,5% Realrendite ist die Mid-Gruppe vollstaendig selbsttragend.

### 7.8 Wirkung korrigierter Destatis-Parameter

Tabelle 7.6 zeigt die Auswirkung der Parameterkorrektur (realistische Mortalitaet, korrigierte Kohortengroesse, hoehere Einkommen) auf den Break-Even-tau_high.

**Tabelle 7.6: Break-Even-tau_high vor und nach Destatis-Korrektur**

| Konfiguration | tau_high (original) | tau_high (korrigiert) | Aenderung |
|---|---|---|---|
| Alle Features an | 32,25% | 28,00% | -4,25 PP |
| Longevity an, Einkommensprofil aus | 21,75% | 18,25% | -3,50 PP |
| Einkommensprofil an, Longevity aus | 24,50% | 21,50% | -3,00 PP |
| Baseline (beide aus) | 16,00% | 14,00% | -2,00 PP |

Die Korrektur senkt tau_high um 2--4,25 PP. Der Haupttreiber ist die realistischere Mortalitaet (hoehere Sterberaten reduzieren die Anzahl gleichzeitiger Rentenempfaenger). Die hoehere Einkommensannahme erhoet zwar die Garantiebetraege, wird aber durch den gleichzeitigen Anstieg der Beitragseinnahmen teilweise kompensiert.

### 7.9 Zusammenfassung der Sensitivitaetsergebnisse

1. **Config D ist robust**: tau_high = 12,25% besteht alle 7 Szenarien, 5 davon strukturell nachhaltig.
2. **Die Grenze liegt bei ~0,5% Realrendite**: Darunter wird das System von akkumulierten Puffern und dem Staats-Backstop getragen, bleibt aber garantiekonform.
3. **Einkommensprofil ist der teuerste Hebel**: Flat income statt Buckelprofil spart 8,5 PP auf tau_high. Diese Vereinfachung ist konservativ vertretbar.
4. **Die Selbstfinanzierungsluecke der Low-Gruppe** ist strukturell und erfordert dauerhaft die Quersubventionierung durch die High-Gruppe. Bei 1,735% decken eigene Beitraege nur 60,4% der Garantie; bei 2,5% immerhin 79,4%.
5. **Von 220 getesteten Konfigurationen bestehen 136 (61,8%)** den Garantietest -- das System hat einen breiten Funktionskorridor.

---

## 8. Verteilungswirkungen

### 8.1 Methodik

Die Verteilungsanalyse untersucht die Umverteilungsstroeme zwischen den drei Einkommensgruppen unter Config D. Im Gegensatz zur klassischen Verteilungsanalyse mit Gini-Koeffizienten konzentriert sich diese Untersuchung auf die *Transferbilanz*: Wer zahlt wie viel ein, wer erhaelt wie viel, und wie verhaelt sich dies zum Status Quo der GRV?

Die Analyse verwendet die folgenden Config-D-Parameter:

| Gruppe | Anteil | Einkommen/Jahr | Beitrag/Monat | Pension/Monat | Rendite auf Beitrag |
|---|---|---|---|---|---|
| Low (30%) | 30% | EUR 22.000 | EUR 220 | EUR 1.558 | Positiv (subventioniert) |
| Mid (50%) | 50% | EUR 40.000 | EUR 433 | EUR 2.000 | Positiv (teilsubventioniert) |
| High (20%) | 20% | EUR 72.000 | EUR 735 | EUR 0 | Negativ (Solidarbeitrag) |

### 8.2 Quersubventionierung: Quantitative Zerlegung

#### 8.2.1 Die Low-Gruppe als Netto-Empfaenger

Bei der Basisrendite von 1,735% finanziert die Low-Gruppe 60,4% ihrer Garantie selbst (vgl. Abschnitt 7.6). Der jaehrliche Zuschussbedarf pro Low-Rentner betraegt EUR 7.414.

Im Steady State befinden sich (bei 831.435 Eintritts-Kohorte) rund 20 Rentnerkohorten im System, reduziert um Mortalitaet. Der aggregierte Zuschussbedarf der Low-Gruppe ergibt sich aus:

- Lebende Low-Rentner im Steady State: ca. 30% x 831.435 x Ueberlebensrate(20 J.) ~ 161.000 pro Kohorte im Durchschnitt
- Aggregierter Zuschuss Low: ~ EUR 1.194 Mio/Jahr pro Kohorte

#### 8.2.2 Die Mid-Gruppe als partieller Empfaenger

Die Mid-Gruppe finanziert bei 1,735% Rendite 92,6% ihrer Garantie selbst. Das Defizit von EUR 1.769/Person/Jahr ist gering. Bei 2,5% Rendite entfaellt der Zuschussbedarf vollstaendig.

#### 8.2.3 Die High-Gruppe als alleiniger Netto-Zahler

Die High-Gruppe traegt die gesamte Quersubventionierung:

| Kennzahl | Wert |
|---|---|
| Solidarbeitrag pro Person/Jahr | EUR 8.820 |
| Solidarbeitrag pro Person/Monat | EUR 735 |
| Lebenszeitbeitrag (47 Erwerbsjahre) | **EUR 414.540** |
| Rentenanspruch | **EUR 0** |
| Implizite Transfersteuer | 12,25% des Bruttoeinkommens |

Der Lebenszeitbeitrag von EUR 414.540 *ohne jede Gegenleistung* ist der politisch sensibelste Aspekt des RSSP-Designs. Er wird in Abschnitt 14 (High-Earner-Kompensation) ausfuehrlich diskutiert.

### 8.3 Vergleich mit der GRV-Belastung fuer High Earner

**Tabelle 8.1: Belastungsvergleich High Earner -- RSSP vs. GRV**

| Kennzahl | GRV (Status Quo) | RSSP Config D |
|---|---|---|
| Einkommen | EUR 72.000/Jahr | EUR 72.000/Jahr |
| Arbeitnehmer-Beitrag | EUR 558/Monat (9,3%) | EUR 735/Monat (12,25%) |
| Arbeitgeber-Beitrag | EUR 558/Monat (9,3%) | Entfaellt (in tau_low/mid inkl.) |
| Gesamtbeitrag | EUR 1.116/Monat (18,6%) | EUR 735/Monat |
| Rentenanspruch | EUR 2.880/Monat (~48% Ersatzrate) | EUR 0 |
| Netto-Lebenszeitwert* | positiv (Rendite ~2-3%) | **-EUR 414.540** |

*\* Differenz zwischen Barwert der Rentenansprueche und Barwert der Beitraege.*

In der GRV zahlt der High Earner bei EUR 72.000 Einkommen (unter der Beitragsbemessungsgrenze) insgesamt EUR 1.116/Monat und erhaelt dafuer ~EUR 2.880/Monat Rente. Die implizite Rendite des GRV-Beitrags ist fuer diese Gruppe positiv, da die GRV nicht primaer umverteilend wirkt (die Umverteilung erfolgt ueber die Steuern).

Im RSSP hingegen zahlt der High Earner EUR 735/Monat -- weniger als den GRV-Arbeitnehmeranteil -- erhaelt aber *keine* Pension. Der RSSP-Transfer ist transparent und direkt, waehrend die GRV-Quersubventionierung ueber den Steueranteil (derzeit ~EUR 100 Mrd/Jahr Bundeszuschuss) verborgen bleibt.

### 8.4 Umverteilungswirkung: RSSP vs. GRV

**Tabelle 8.2: Ersatzraten im Systemvergleich**

| Gruppe | GRV-Ersatzrate | RSSP-Garantie | RSSP bei 2,5% Rendite | Aenderung ggue. GRV |
|---|---|---|---|---|
| Low | ~48% | 85% | 100% (gedeckelt) | **+37 bis +52 PP** |
| Mid | ~48% | 60% | 88% | **+12 bis +40 PP** |
| High | ~48% | 0% | 0% | **-48 PP** |

Das RSSP vollzieht eine explizite Umverteilung zugunsten der unteren beiden Einkommensgruppen. Die GRV verteilt zwar implizit um (ueber Zurechnungszeiten, Mindestrente, Bundeszuschuss), aber die Grundstruktur bleibt beitragsaequivalent. Das RSSP bricht bewusst mit der Beitragsaequivalenz fuer die High-Gruppe zugunsten einer Absicherung gegen Altersarmut.

### 8.5 Altersarmutsreduktion

Die Armutsgefaehrdungsquote der ueber 65-Jaehrigen lag 2024 bei **19,6%** (Destatis). Die Grundsicherung im Alter erreichte 742.410 Empfaenger (Stand Maerz 2025).

Das RSSP eliminiert die Altersarmut fuer alle Teilnehmer per Konstruktion: Die Low-Garantie von 85% auf EUR 22.000 ergibt EUR 18.700/Jahr (EUR 1.558/Monat). Die Armutsschwelle (60% des Medianeinkommens) liegt bei ca. EUR 15.000-16.000/Jahr. Damit liegt die RSSP-Low-Garantie **ca. 17-25% ueber der Armutsschwelle**.

Selbst nach Ablauf der Annuitaetsphase (ab Alter 87) sichert der Longevity Pool einen Floor von EUR 10.000/Jahr (EUR 833/Monat) -- ein Niveau, das der aktuellen Grundsicherung entspricht.

### 8.6 Verteilungskompression

Die gestaffelte Garantie (85%/60%) komprimiert die Rentenverteilung im Vergleich zur Erwerbseinkommensverteilung:

| Mass | Erwerbseinkommen (Low/Mid) | RSSP-Renten (Low/Mid) |
|---|---|---|
| Einkommensspanne | EUR 22.000 -- EUR 40.000 | EUR 18.700 -- EUR 24.000 |
| Verhaeltnis Mid/Low | 1,82 | 1,28 |

Die Einkommensspreizung sinkt von 1:1,82 (Erwerbsleben) auf 1:1,28 (Rente). Dies repraesentiert eine erhebliche Einkommenskompression, die das RSSP gegenueber einem reinen DC-System ohne Garantien auszeichnet.

In einem reinen DC-System (ohne Garantien, ohne Quersubventionierung) wuerden die Ersatzraten proportional zum Einkommen und Beitragssatz ausfallen, und die Einkommensspreizung bliebe im Alter erhalten. Die gestaffelte Garantie des RSSP wirkt dem entgegen und ist insofern ein bewusstes umverteilungspolitisches Instrument.

### 8.7 Limitationen der Verteilungsanalyse

1. **Drei-Gruppen-Modell**: Die tatsaechliche Einkommensverteilung ist kontinuierlich; das Modell erfasst die Grunddynamik, unterschaetzt aber die Randeffekte an den Gruppengrenzen.

2. **Statische Verhaltensannahmen**: Es wird keine Verhaltensaenderung modelliert (z.B. Arbeitsangebotselastizitaet in Reaktion auf den Solidarbeitrag oder Einkommensverlagerungen der High-Gruppe).

3. **Kohortenuniformitaet**: Alle Kohorten werden identisch behandelt; generationenspezifische Effekte (Uebergangskohorte, historische Renditeunterschiede) werden nicht abgebildet.

4. **High-Gruppe exkludiert**: Die Rentenverteilung umfasst nur Low und Mid; die High-Gruppe erscheint ausschliesslich als Beitragszahler. In der Realitaet wuerde die High-Gruppe eine private oder betriebliche Altersvorsorge aufbauen, deren Interaktion mit dem RSSP hier nicht modelliert wird.

**Rigor: Medium** -- Das Drei-Gruppen-Modell erfasst die Grunddynamik der Quersubventionierung praezise, unterschaetzt aber die Heterogenitaet innerhalb der Gruppen und abstrahiert von Verhaltensreaktionen.

---

*Dieser Teil des Papiers basiert auf den Simulationsergebnissen des RSSP_v2-Modells (Config D und Config E, 220-Konfigurationen-Sweep, 100-Jahres-Horizont, 10.000-Pfade Monte Carlo). Die deterministischen Berechnungen sind reproduzierbar; die stochastischen Ergebnisse sind bei festem Random Seed reproduzierbar. Die zugrunde liegenden Daten finden sich in `out/sensitivity_sweep.csv`, `out/truth_table_const.csv`, `out/best_config_e.json`, `out/mc_config_e_10k.json` und `out/mc_config_e_regime.json`.*
