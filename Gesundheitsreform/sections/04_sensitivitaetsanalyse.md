# Sensitivitaetsanalyse: GSP-Modell

Alle Ergebnisse berechnet mit `gesundheit_projektion_model.py` v2.0.

## 1. Szenarienvergleich (Zieljahr 2045)

| Szenario | GKV-Beitragssatz | Effektiv (GKV+GSP) | GSP-Kapitalstock | Kum. Ersparnis |
|----------|------------------|--------------------|------------------|----------------|
| **Status Quo** | **19,5%** | **19,5%** | 0 Mrd. EUR | 0 Mrd. EUR |
| GSP Pessimistisch | 15,2% | 17,2% | 950 Mrd. EUR | 184 Mrd. EUR |
| **GSP Baseline** | **10,6%** | **12,6%** | **1.150 Mrd. EUR** | **298 Mrd. EUR** |
| GSP Optimistisch | 8,2% | 10,2% | 1.292 Mrd. EUR | 330 Mrd. EUR |
| Vollintegration | 9,6% | 12,1% | 1.462 Mrd. EUR | 337 Mrd. EUR |

**Kernergebnis:** Selbst im pessimistischen Szenario (1% Effizienz, 2% GSP-Rendite, 2,5% med. Inflation) liegt der effektive Beitragssatz bei 17,2% — **2,3 Prozentpunkte unter dem Status Quo** (19,5%).

### Szenario-Annahmen

| Parameter | Pessimistisch | Baseline | Optimistisch |
|-----------|--------------|----------|-------------|
| Effizienzgewinn p.a. | 1,0% | 2,0% | 2,5% |
| Med. Inflation p.a. | 2,5% | 2,0% | 1,5% |
| Praevention (max.) | 5% | 10% | 15% |
| Praevention Ramp-up | 15 Jahre | 10 Jahre | 8 Jahre |
| GSP Nominalrendite | 2,0% | 3,5% | 4,5% |
| GSP Verwaltungskosten | 0,5% | 0,3% | 0,2% |
| GSP Entnahmerate | 1,5% | 1,0% | 0,8% |

---

## 2. Tornado-Analyse: Was treibt den GSP-Kapitalstock?

Einzelparameter-Variation bei allen anderen Parametern auf Baseline-Wert. Zieljahr: 2045.

| Parameter | Low-Wert | Baseline | High-Wert | Kapital Low | Kapital Base | Kapital High | Range |
|-----------|----------|----------|-----------|-------------|-------------|-------------|-------|
| **GSP Beitragssatz** | 1,0% | 2,0% | 3,0% | 575 | 1.150 | 1.724 | **1.150** |
| **GSP Rendite** | 2,0% | 3,5% | 5,0% | 1.008 | 1.150 | 1.316 | **308** |
| **Lohnwachstum** | 1,0% | 2,0% | 3,0% | 1.034 | 1.150 | 1.281 | **247** |
| GSP Entnahmerate | 0,5% | 1,0% | 2,0% | 1.202 | 1.150 | 1.053 | 149 |
| GSP Verwaltungskosten | 0,1% | 0,3% | 0,8% | 1.170 | 1.150 | 1.100 | 70 |

**Wichtigste Treiber (absteigend):**
1. **Beitragssatz** — dominanter Hebel. Jeder Prozentpunkt mehr verdoppelt den Kapitalstock.
2. **Nominalrendite** — zweitwichtigster Faktor. Differenz zwischen 2% und 5% = 308 Mrd. EUR.
3. **Lohnwachstum** — treibt die Beitragsbasis. Wenn die Wirtschaft waechst, wachsen die GSP-Einzahlungen.

**Nicht-Treiber:** Effizienzgewinn, medizinische Inflation und Praevention beeinflussen den GKV-Beitragssatz, aber *nicht* den GSP-Kapitalstock (der unabhaengig von Gesundheitskosten akkumuliert).

---

## 3. Break-Even-Analyse

### 3.1 Crossover-Jahr: Ab wann ist GSP+GKV guenstiger als Status Quo?

**Ergebnis: Jahr 2029** (4 Jahre nach Einfuehrung)

```
Beitragssatz-Entwicklung:

     Status Quo (nur GKV)
     ─────────────────────────────────────
20% ┤                         ╱──── 19,5%
    │                      ╱
19% ┤                   ╱
    │                ╱
18% ┤─────────────╱
    │          ╱
17% ┤       ╱
    │     ╱            GSP+GKV (Effektiv)
16% ┤──╱   ─────────────────────────────
    │╱  ╲
15% ┤    ╲
    │     ╲
14% ┤      ╲───────
    │              ╲
13% ┤               ╲──────── 12,6%
    │
12% ┤
    └──────────────────────────────────── Jahr
    2025   2029   2033   2037   2041  2045

    Crossover: 2029 (Pfeil)
```

**Bedeutung:** Nach nur 4 Jahren zahlen GKV-Versicherte mit GSP weniger als ohne GSP — trotz des zusaetzlichen 2%-Beitrags. Das ist das staerkste politische Argument: *"Die Reform kostet Sie 4 Jahre lang 2% mehr — danach sparen Sie dauerhaft."*

### 3.2 Minimale GSP-Rendite fuer positiven Kapitalstock 2045

**Ergebnis: 0,0%** — Selbst bei null Prozent Rendite bleibt der Kapitalstock positiv, weil die Beitraege allein genuegen. Der Kapitalstock waere dann ~620 Mrd. EUR statt 1.150 Mrd. EUR — immer noch substantiell.

**Bedeutung:** Das GSP ist kein Spekulationsmodell. Es funktioniert selbst wenn die Kapitalmaerkte null Rendite liefern. Die Rendite ist ein Bonus, kein Requirement.

---

## 4. Monte-Carlo-Simulation

1.000 Simulationslaeufe mit gleichverteilter Variation aller Parameter innerhalb ihrer Ranges. Zieljahr: 2045.

### GSP-Kapitalstock 2045

| Perzentil | Wert (Mrd. EUR) |
|-----------|----------------|
| P5 (Worst Case) | 872 |
| P25 | 1.022 |
| **Median** | **1.123** |
| P75 | 1.230 |
| P95 (Best Case) | 1.416 |
| **P(Kapital > 0)** | **100,0%** |

### GKV-Beitragssatz 2045 (nur GKV, ohne GSP-Anteil)

| Perzentil | Wert |
|-----------|------|
| P5 | 7,9% |
| **Median** | **11,0%** |
| P95 | 14,9% |
| **P(< 20%)** | **100,0%** |

### Effektiver Gesamtbeitrag (GKV + GSP) 2045

| Perzentil | Wert |
|-----------|------|
| P5 | 9,9% |
| **Median** | **13,0%** |
| P95 | 16,9% |

### Vergleich mit Status Quo (19,5% in 2045)

| Metrik | Wert |
|--------|------|
| P(GSP effektiv < Status Quo) | **100,0%** |
| Median-Vorteil | **6,5 Prozentpunkte** |
| Worst-Case-Vorteil (P95) | **2,6 Prozentpunkte** |

**Kernergebnis:** In keinem einzigen der 1.000 Simulationslaeufe ist das GSP-Modell teurer als der Status Quo. Der Vorteil betraegt im Median 6,5 Prozentpunkte — selbst im schlechtesten 5% der Faelle noch 2,6 PP.

---

## 5. Kritische Wuerdigung

### Was das Modell gut abbildet
- Demografischer Kostenberg mit Peak ~2045 und anschliessendem Rueckgang
- GSP-Kapitalakkumulation unter verschiedenen Marktbedingungen
- GKV-Beitragssatz-Dynamik unter Beruecksichtigung schrumpfender Erwerbsbevoelkerung
- Sensitivitaet gegenueber Rendite, Inflation und Effizienzannahmen

### Was das Modell NICHT abbildet
- **Verhaltensaenderungen:** Das Modell nimmt an, dass Versicherte ihr GSP rational nutzen. In der Realitaet koennte Moral Hazard (uebermassige Entnahmen) oder Nicht-Nutzung (Angst vor Kapitalverlust) auftreten.
- **Politische Dynamik:** Regierungswechsel, Lobby-Erfolge oder EU-Regulierung koennen das Modell jederzeit invalidieren.
- **Wechselwirkungen:** Der GSP-Kapitalstock interagiert mit dem RSSP (Renten-Modell) und der Eurozone-Strategie. Diese Interaktionen sind nicht modelliert.
- **Regionale Unterschiede:** Gesundheitskosten variieren stark zwischen Bundeslaendern (Bayern vs. NRW). Das Modell arbeitet mit Bundesdurchschnitten.
- **Technologiebrueche:** KI-Diagnostik, mRNA-Therapien oder Praezisionsmedizin koennten die Kostenstruktur fundamental veraendern — in beide Richtungen.

### Robustheit-Assessment

| Aspekt | Robustheit | Begruendung |
|--------|-----------|-------------|
| GSP-Kapitalstock > 0 | **Sehr hoch** | 100% in Monte Carlo; funktioniert selbst bei 0% Rendite |
| Effektiver Satz < Status Quo | **Sehr hoch** | 100% in Monte Carlo; kein einziger Gegenfall |
| Crossover in < 5 Jahren | **Hoch** | Modell zeigt 2029; auch pessimistisch < 2032 |
| Kapitalstock > 1 Bio. EUR | **Mittel-Hoch** | 75% in Monte Carlo (P25 = 1.022 Mrd.) |
| GKV-Satz < 15% in 2045 | **Mittel** | Abhaengig von Effizienzgewinnen, die nicht garantiert sind |

---

## Rigor Statement

**Confidence: Medium-High** fuer die qualitative Aussage (GSP ist in allen Szenarien besser als Status Quo).
**Confidence: Medium** fuer die absoluten Zahlen (Kapitalstock, Beitragssaetze), da 20-Jahres-Projektionen inherent unsicher sind.

Die Monte-Carlo-Simulation zeigt extreme Robustheit der Kernaussage, aber die gleichverteilte Parametrisierung koennte Korrelationen zwischen Parametern (z.B. niedrige Rendite bei hoher Inflation) unterschaetzen. Eine korrelierte Simulation (Copula-Ansatz) waere eine sinnvolle Erweiterung.

**Falsifizierbarkeit:** Das Modell waere falsifiziert, wenn ein realistisches Parameterset existiert, bei dem der effektive Beitragssatz (GKV+GSP) *hoeher* ist als der Status-Quo-GKV-Satz. Die Monte-Carlo-Analyse konnte kein solches Set finden.
