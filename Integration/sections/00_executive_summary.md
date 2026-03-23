# DASDIS - Daten- und Statistikgetriebenes Integrationssystem

## Executive Summary

### Das Problem

Deutschlands Integrationssystem ist ineffizient und langsam:

| Kennzahl | Wert | Problem |
|----------|------|---------|
| Schutzstatus gesamt | **3,2 Mio.** | Grosse Zielgruppe |
| Asyl-Erstantraege/Jahr | 300.000 | Kontinuierlicher Zustrom |
| Bundesausgaben/Jahr | **30 Mrd. EUR** | Hohe Kosten |
| Zeit bis Beschaeftigung | **4,5 Jahre** | Zu langsam |
| Beschaeftigung Jahr 8 | 68% | Potential nicht ausgeschoepft |
| Frauenbeschaeftigung | **33%** | Extremer Gender-Gap |
| Kursabschlussrate | 65% | 35% brechen ab |

**Kernproblem**: Integration dauert zu lange und ist zu wenig personalisiert. Jedes Jahr Verzoegerung kostet ~8.000 EUR pro Migrant an verlorener Produktivitaet.

### Die Loesung: DASDIS

Ein datengetriebenes, KI-gestuetztes Integrationssystem:

| Komponente | Funktion |
|------------|----------|
| **Integrationslotse-App** | Mobile Anlaufstelle, personalisierte Empfehlungen |
| **KI-Erfassungsfragebogen** | Intelligente Bedarfsermittlung |
| **Datenbasiertes Entscheidungsmodul** | Optimierte Zuweisungen |
| **Fallmanagement-Plattform** | Digitale Koordination |
| **Spezialisierte Zentren** | Fuer komplexe Faelle |
| **Mehrstufiges Supportsystem** | Bedarfsgerechte Ressourcen |

### Kernergebnisse der Simulation

| Kennzahl | Status Quo | DASDIS | Verbesserung |
|----------|------------|--------|--------------|
| Zeit bis Job | 4,5 Jahre | **3,0 Jahre** | **-1,5 Jahre** |
| Beschaeftigung Jahr 8 | 68% | **83%** | **+15%** |
| Frauenbeschaeftigung | 33% | **40%** | **+7%** |
| Kursabschlussrate | 65% | **85%** | **+20%** |
| Gender-Gap | 53% | **40%** | **-25%** |

### Investition und Return

| Kennzahl | Wert |
|----------|------|
| Einmalige Investition | **400 Mio. EUR** |
| Laufende Kosten | **145 Mio. EUR/Jahr** |
| Zusatzkosten vs. Status Quo | **+0,5%** |

### Wirtschaftliche Effekte (10 Jahre)

| Kennzahl | Wert |
|----------|------|
| NPV Produktivitaetsgewinn | **125 Mrd. EUR** |
| NPV Steuereinnahmen | **37 Mrd. EUR** |
| Welfare-Einsparungen | **2,3 Mrd. EUR/Kohorte** |
| Zusaetzliche Beschaeftigte | **45.000/Kohorte** |

### Fiskalische Bilanz (konservativ)

| Posten | 10 Jahre |
|--------|----------|
| Kosten (Investition + Betrieb) | -1,9 Mrd. EUR |
| Steuer-Mehreinnahmen | +37 Mrd. EUR |
| Welfare-Einsparungen | +20 Mrd. EUR |
| **Nettogewinn fuer Staat** | **+55 Mrd. EUR** |

### Robustheit

| Szenario | Beschaeftigungs-Plus | Fiskal-Effekt |
|----------|---------------------|---------------|
| Pessimistisch | +5% | +15 Mrd. EUR |
| **Baseline** | **+15%** | **+55 Mrd. EUR** |
| Optimistisch | +25% | +100 Mrd. EUR |

Selbst im pessimistischen Szenario ist DASDIS **fiskalisch positiv in allen modellierten Szenarien**.

### Kritische Erfolgsfaktoren

| Faktor | Einfluss | Mitigation |
|--------|----------|------------|
| App-Adoption | HOCH | Verpflichtende Nutzung, gute UX |
| Datenqualitaet | HOCH | Qualitaetssicherung, Validierung |
| Datenschutz | HOCH | DSGVO-Konformitaet, Transparenz |
| Personal-Akzeptanz | MITTEL | Schulung, Change-Management |
| Politische Kontinuitaet | MITTEL | Parteiuebergreifender Konsens |

### Vergleich international

| Land | System | Ergebnis |
|------|--------|----------|
| **Daenemark** | Datengetriebene Zuweisung | +20% Beschaeftigung |
| **Kanada** | Express Entry | Schnelle Fachkraefte-Integration |
| **Australien** | Points-based | Optimierte Selektion |
| **Deutschland (DASDIS)** | Personalisiert + KI | Erwartung: +15% |

### Empfehlung

DASDIS ist eine **hochrentable Investition** in Deutschlands Integrationssystem:

1. **Minimale Kosten**: +0,5% der bestehenden Ausgaben
2. **Massive Wirkung**: 1,5 Jahre schnellere Integration
3. **Hoher ROI**: Jeder investierte Euro ergibt im Modell ~30 EUR zurueck (fiskalisch)
4. **Skalierbar**: Fuer 300.000+ Migranten/Jahr ausgelegt
5. **Menschenzentriert**: Personalisierte Unterstuetzung, nicht Kontrolle

**Das Nicht-Handeln kostet ~5 Mrd. EUR/Jahr** (modellierte Opportunitaetskosten) an verlorener Produktivitaet und Sozialkosten.

---

## Dokumentenstruktur

| Sektion | Inhalt |
|---------|--------|
| 01 | Literaturuebersicht und Datenbasis |
| 02 | Baseline-Ergebnisse der Simulation |
| 03 | Sensitivitaetsanalyse |
| Model | Python-Simulation (dasdis_model.py) |

---

**Rigor: Medium** - Basiert auf BAMF/IAB-Daten und internationalen Vergleichen. Beschaeftigungseffekte geschaetzt basierend auf daenischen Erfahrungen. Wirtschaftseffekte konservativ berechnet.
