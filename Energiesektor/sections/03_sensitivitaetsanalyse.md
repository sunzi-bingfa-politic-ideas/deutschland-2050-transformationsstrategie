# 3. Sensitivitaetsanalyse: Schwerkraftspeicher-Hub

## 3.1 Methodik

Die Sensitivitaetsanalyse untersucht systematisch die Robustheit der Baseline-Ergebnisse gegenueber Parameterunsicherheiten.

### Untersuchte Parameter

| Parameter | Low | Baseline | High | Einheit |
|-----------|-----|----------|------|---------|
| **Physik** | | | | |
| Gesteinsdichte | 2.400 | 2.600 | 2.800 | kg/m³ |
| Wirkungsgrad (Roundtrip) | 70% | 80% | 85% | % |
| **Kapitalkosten** | | | | |
| Aushubkosten | 30 | 50 | 80 | EUR/m³ |
| Dichtungskosten | 300 | 500 | 800 | EUR/m² |
| Pump-Turbine | 300.000 | 500.000 | 700.000 | EUR/MW |
| **Finanzierung** | | | | |
| Diskontrate | 3% | 5% | 8% | % |
| Lebensdauer | 30 | 50 | 60 | Jahre |
| Zyklen/Jahr | 200 | 300 | 365 | Zyklen |
| **Einnahmen** | | | | |
| Stromeinkauf | 20 | 30 | 50 | EUR/MWh |
| Stromverkauf | 60 | 80 | 120 | EUR/MWh |
| Kapazitaetsmarkt | 30.000 | 50.000 | 80.000 | EUR/MW/a |

## 3.2 Tornado-Analyse: LCOS

Die Levelized Cost of Storage (LCOS) reagiert auf verschiedene Parameter unterschiedlich stark:

| Parameter | Low | Baseline | High | Max. Abweichung |
|-----------|-----|----------|------|-----------------|
| **Zyklen/Jahr** | 59 | 40 | 33 | **±20 EUR/MWh** |
| **Diskontrate** | 30 | 40 | 56 | **±17 EUR/MWh** |
| **Pump-Turbine Kosten** | 29 | 40 | 50 | **±11 EUR/MWh** |
| Lebensdauer | 46 | 40 | 38 | ±6 EUR/MWh |
| Dichtungskosten | 39 | 40 | 40 | ±1 EUR/MWh |
| Gesteinsdichte | 40 | 40 | 39 | <1 EUR/MWh |
| Aushubkosten | 40 | 40 | 40 | <1 EUR/MWh |

**Erkenntnis**: Die LCOS wird primaer von **Auslastung** (Zyklen/Jahr), **Finanzierungskosten** (Diskontrate) und **Pump-Turbine-Kosten** bestimmt. Geologische Parameter (Dichte, Aushub) haben minimalen Einfluss.

## 3.3 Tornado-Analyse: NPV

Der Net Present Value ueber 50 Jahre reagiert sensitiv auf Einnahmeparameter:

| Parameter | Low | Baseline | High | Max. Abweichung |
|-----------|-----|----------|------|-----------------|
| **Stromeinkauf** | +14,3 | +5,8 | -11,4 | **±17 Mrd. EUR** |
| **Stromverkauf** | -1,8 | +5,8 | +21,0 | **±15 Mrd. EUR** |
| **Kapazitaetsmarkt** | -2,2 | +5,8 | +17,7 | **±12 Mrd. EUR** |
| Diskontrate | +14,7 | +5,8 | -1,4 | ±9 Mrd. EUR |
| Pump-Turbine | +10,9 | +5,8 | +0,6 | ±5 Mrd. EUR |
| Lebensdauer | +2,3 | +5,8 | +6,6 | ±3 Mrd. EUR |
| Wirkungsgrad | +2,9 | +5,8 | +7,5 | ±3 Mrd. EUR |

**Erkenntnis**: Der NPV haengt stark von den **Marktpreisen** (Strom, Kapazitaet) ab. Das Projekt ist profitabel bei positiver Preisspanne, aber empfindlich gegenueber Marktveraenderungen.

## 3.4 Amortisations-Sensitivitaet

| Parameter | Low | Baseline | High | Max. Abweichung |
|-----------|-----|----------|------|-----------------|
| **Stromeinkauf** | 9,6 | 13,4 | 50+ | **±37 Jahre** |
| **Kapazitaetsmarkt** | 21,1 | 13,4 | 8,6 | **±8 Jahre** |
| **Stromverkauf** | 20,6 | 13,4 | 7,9 | **±7 Jahre** |
| Pump-Turbine | 9,4 | 13,4 | 17,7 | ±4 Jahre |
| Wirkungsgrad | 15,2 | 13,4 | 12,7 | ±2 Jahre |

**Erkenntnis**: Die Amortisation ist bei niedrigen Strompreisen und gutem Kapazitaetsmarkt unter 10 Jahren moeglich. Bei ungünstigen Bedingungen kann sie sich auf >30 Jahre verlaengern.

## 3.5 Szenario-Vergleich

### Szenarien-Definition

| Szenario | Beschreibung |
|----------|--------------|
| **Pessimistisch** | Hohe Kosten, niedrige Preise, kurze Lebensdauer |
| **Baseline** | Mittlere Annahmen basierend auf aktuellen Daten |
| **Optimistisch** | Lernkurve, hohe Volatilitaet, lange Lebensdauer |

### Ergebnisse (Gross-Szenario: 5 × 250m)

| Kennzahl | Pessimistisch | Baseline | Optimistisch |
|----------|---------------|----------|--------------|
| Kapazitaet | 70 GWh | 87 GWh | 100 GWh |
| CAPEX | 16,9 Mrd. | 15,9 Mrd. | 12,9 Mrd. |
| CAPEX/kWh | 241 EUR | 183 EUR | 129 EUR |
| **LCOS** | **110 EUR/MWh** | **40 EUR/MWh** | **17 EUR/MWh** |
| Amortisation | >50 Jahre | 13,4 Jahre | 3,1 Jahre |
| **NPV** | **-19,9 Mrd.** | **+5,8 Mrd.** | **+95,7 Mrd.** |
| Nettogewinn/Jahr | -246 Mio. | +1.188 Mio. | +4.221 Mio. |

**Erkenntnis**: Im pessimistischen Szenario ist das Projekt **nicht rentabel** (NPV negativ). Im optimistischen Szenario sind **exzellente Renditen** moeglich. Die Bandbreite ist erheblich.

## 3.6 Break-Even-Analyse

### Strompreis-Spread Break-Even

| Spread (EUR/MWh) | NPV (Mrd. EUR) | Amortisation |
|------------------|----------------|--------------|
| 10 | -9,5 | 45 Jahre |
| 20 | -5,7 | 28 Jahre |
| 30 | -1,8 | 21 Jahre |
| **40** | **+2,0** | **16 Jahre** |
| **50** (Baseline) | **+5,8** | **13 Jahre** |
| 60 | +9,6 | 11 Jahre |
| 80 | +17,2 | 9 Jahre |

**Break-Even**: NPV wird bei **~35 EUR/MWh Spread** positiv.

### Kapazitaetsmarkt Break-Even

| Verguetung (EUR/MW/a) | NPV (Mrd. EUR) | Amortisation |
|-----------------------|----------------|--------------|
| 0 | -14,1 | >100 Jahre |
| 20.000 | -6,1 | 30 Jahre |
| **35.000** | **~0** | **20 Jahre** |
| **50.000** (Baseline) | **+5,8** | **13 Jahre** |
| 70.000 | +13,7 | 10 Jahre |

**Break-Even**: NPV wird bei **~35.000 EUR/MW/a** positiv.

### Groessen-Break-Even

| Durchmesser | LCOS | Kapazitaet |
|-------------|------|------------|
| 100 m | 49 EUR/MWh | 0,4 GWh |
| 150 m | 43 EUR/MWh | 2,3 GWh |
| 200 m | 41 EUR/MWh | 7,1 GWh |
| **250 m** | **40 EUR/MWh** | **17,4 GWh** |
| 300 m | 39 EUR/MWh | 36,1 GWh |

**Erkenntnis**: LCOS sinkt mit Groesse, aber der Effekt flacht ab 200m ab. Grossanlagen sind klar vorteilhaft.

## 3.7 Monte-Carlo-Simulation

### Methodik

1.000 Iterationen mit gleichverteilten Zufallsparametern innerhalb der Low-High-Grenzen.

### Ergebnisse

| Metrik | P5 | P25 | Median | P75 | P95 |
|--------|-----|-----|--------|-----|-----|
| LCOS (EUR/MWh) | 27 | 36 | **44** | 55 | 73 |
| NPV (Mrd. EUR) | -11,7 | -2,6 | **+4,5** | +12,9 | +27,9 |
| Payback (Jahre) | 6,6 | 9,5 | **13,0** | 19,7 | 50+ |

### Risikometriken

| Metrik | Wahrscheinlichkeit |
|--------|-------------------|
| NPV > 0 | **65,5%** |
| Payback < 15 Jahre | **59,7%** |
| LCOS < 50 EUR/MWh | **64,4%** |

**Erkenntnis**: Unter Beruecksichtigung aller Unsicherheiten ist das Projekt **mit ~65% Wahrscheinlichkeit rentabel**. Das ist ein akzeptables Risikoprofil fuer ein Infrastrukturprojekt.

## 3.8 Kritische Erfolgsfaktoren

### Faktor 1: Skalierung (Einfluss: HOCH)

| Groesse | LCOS | Kosten-Vorteil |
|---------|------|----------------|
| 100 m | ~50 EUR/MWh | Basis |
| 200 m | ~41 EUR/MWh | -18% |
| 250 m | ~40 EUR/MWh | -20% |

**Empfehlung**: Fokus auf Grossanlagen (>200m Durchmesser). Der Skalierungseffekt (Kapazitaet ~ r⁴, Kosten ~ r²) ist der staerkste Hebel zur Kostenreduktion.

### Faktor 2: Kapazitaetsmarkt (Einfluss: HOCH)

| Verguetung | Amortisation |
|------------|--------------|
| 0 EUR/MW/a | >100 Jahre |
| 30.000 EUR/MW/a | ~21 Jahre |
| 50.000 EUR/MW/a | ~13 Jahre |

**Empfehlung**: Politische Absicherung der Kapazitaetsmarkt-Verguetung ist **kritisch** fuer die Projektrentabilitaet.

### Faktor 3: Strompreis-Spread (Einfluss: HOCH)

| Spread | NPV |
|--------|-----|
| 30 EUR/MWh | Negativ |
| 50 EUR/MWh | +5,8 Mrd. |
| 80 EUR/MWh | +17 Mrd. |

**Empfehlung**: Langfristige Power Purchase Agreements (PPAs) zur Absicherung gegen Marktvolatilitaet.

### Faktor 4: Finanzierung (Einfluss: MITTEL)

| Diskontrate | NPV | Veraenderung |
|-------------|-----|--------------|
| 3% | +14,7 Mrd. | +150% |
| 5% | +5,8 Mrd. | Basis |
| 8% | -1,4 Mrd. | -124% |

**Empfehlung**: Staatliche/EU-Garantien zur Sicherung guenstiger Finanzierungskonditionen.

### Faktor 5: Baukosten (Einfluss: NIEDRIG)

| Kostenszenario | LCOS | Veraenderung |
|----------------|------|--------------|
| -40% (optimist.) | ~35 EUR/MWh | -13% |
| Baseline | ~40 EUR/MWh | Basis |
| +60% (pessimist.) | ~50 EUR/MWh | +25% |

**Empfehlung**: Standardisierung und Lernkurveneffekte durch Serienfertigung anstreben, aber Fokus auf wichtigere Faktoren legen.

## 3.9 Risikomatrix

| Risiko | Wahrscheinlichkeit | Auswirkung | Mitigation |
|--------|-------------------|------------|------------|
| Kapazitaetsmarkt faellt weg | Niedrig | KRITISCH | EU-Regulierung, langfristige Vertraege |
| Strompreis-Spread sinkt | Mittel | Hoch | PPAs, Diversifikation Einnahmen |
| Baukosten steigen | Mittel | Mittel | Festpreisvertraege, Pufferbudget |
| Technische Probleme | Niedrig | Mittel | Pilotprojekt, Qualitaetskontrolle |
| Politikwechsel | Niedrig | Hoch | Parteiuebergreifender Konsens, EU-Verankerung |
| Geologie ungeeignet | Niedrig | Hoch | Gruendliche Voruntersuchung |

## 3.10 Zusammenfassung

| Erkenntnis | Detail |
|------------|--------|
| Robustheit | **65% Wahrscheinlichkeit** fuer positiven NPV |
| Haupttreiber LCOS | Zyklen/Jahr, Diskontrate, Pump-Turbine-Kosten |
| Haupttreiber NPV | Strompreise, Kapazitaetsmarkt |
| Break-Even Spread | ~35 EUR/MWh |
| Break-Even Kap.-Markt | ~35.000 EUR/MW/a |
| Kritischster Faktor | Kapazitaetsmarkt-Verguetung |
| Staerkster Hebel | Anlagenskalierung (>200m) |

**Zentrale Erkenntnis**: Das Projekt ist robust gegenueber geologischen und technischen Unsicherheiten, aber **sensitiv gegenueber Marktbedingungen**. Die politische Absicherung des Kapazitaetsmarktes und langfristige Preisvertraege sind die wichtigsten Erfolgsfaktoren.

---

**Rigor: High** - Monte-Carlo-Simulation mit 1.000 Iterationen, systematische Tornado-Analyse aller Parameter, Break-Even-Berechnungen. Ergebnisse konsistent mit physikalischen und oekonomischen Grundprinzipien.
