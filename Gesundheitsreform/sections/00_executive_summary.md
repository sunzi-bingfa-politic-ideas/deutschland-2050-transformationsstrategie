# Gesundheitsreform: Executive Summary

## Das Problem

Deutschland gibt **12,7% des BIP** (474 Mrd. EUR/Jahr) fuer Gesundheit aus — das dritthöchste weltweit — und erzielt dabei mittelmäßige Ergebnisse: Lebenserwartung 81,3 Jahre (Rang 33), Säuglingssterblichkeit 3,2/1000 (schlechter als Singapur, Japan, Suedkorea). Das demografische Problem verschaerft die Lage: Die Babyboomer (Jg. 1955-1969) treten jetzt in die kostenintensivste Lebensphase ein. Ohne Reform steigt der GKV-Beitragssatz auf **~25% bis 2045**.

## Die Loesung: Deutsches Gesundheitskonto (GSP)

Ein **Hybridmodell** aus asiatischen Best Practices, angepasst an deutsche Gegebenheiten:

| Saeule | Vorbild | Mechanismus |
|--------|---------|-------------|
| **1. GKV (bleibt)** | — | Umlagebasierte Akutversorgung, unveraendert |
| **2. GSP-Konto (neu)** | Singapur MediSave | 2% Beitrag, individuell, vererbbar, kapitalgedeckt |
| **3. Pflege-Reserve** | Japan Kaigo Hoken | Kapitalgedeckte Pflegevorsorge (RSSP-integriert) |
| **4. Haertefall-Fonds** | Singapur MediFund | Staatliches Sicherheitsnetz fuer Beduerftige |

**Kernmechanismus:** Das GSP ergaenzt die GKV — es ersetzt sie nicht. 2% Pflichtbeitrag (1% AN + 1% AG) fliessen in ein individuelles, steuerfrei verzinstes Gesundheitssparkonto. Nutzbar fuer Zuzahlungen, Zahnersatz, Brille, Praevention. Vererbbar. Familien-Pooling moeglich.

## Quantitative Ergebnisse (berechnet mit gesundheit_projektion_model.py v2.0)

| Metrik | Status Quo | GSP Baseline | GSP Pessimistisch |
|--------|-----------|--------------|-------------------|
| GKV-Beitragssatz 2045 | **19,5%** | 10,6% | 15,2% |
| Effektiver Satz (GKV+GSP) 2045 | 19,5% | **12,6%** | 17,2% |
| GSP-Kapitalstock 2045 | 0 | **1.150 Mrd. EUR** | 950 Mrd. EUR |
| Kumulative Ersparnis (20 J.) | 0 | **298 Mrd. EUR** | 184 Mrd. EUR |
| Crossover-Jahr (GSP guenstiger) | — | **2029** | ~2031 |

**Monte-Carlo (1.000 Laeufe):** In 100% der Simulationen ist das GSP-Modell guenstiger als der Status Quo. Median-Vorteil: 6,5 Prozentpunkte.

## Politische Durchsetzung

**Kernproblem:** 60-80 Mrd. EUR/Jahr strukturelle Ineffizienz = Einkommen organisierter Lobby-Gruppen (Kassen, Pharma, Kliniken). Jede Reform bedroht jemandes Einkommen.

**Loesung: Sequenzielle Einfuehrung (Salamitaktik)**

| Phase | Jahre | Massnahme | Lobby-Widerstand |
|-------|-------|-----------|------------------|
| 1 | 1-2 | Digitalisierung + Praevention | Gering |
| 2 | 2-4 | GSP-Konto einfuehren | Mittel (additiv, nicht substituiv) |
| 3 | 3-5 | Gatekeeping Light + Generika-Beschaffung | Hoch (Fachaerzte, Pharma) |
| 4 | 5-8 | KH-Konsolidierung + Community-Versorgung | Sehr hoch |
| 5 | 8-15 | Systemkonvergenz | Sinkend |

**Gewinner:** 74 Mio. GKV-Versicherte, Hausaerzte, Pflegekraefte, innovative Pharma
**Verlierer:** KH-Konzerne (teilweise), Generika-Rentenempfaenger, PKV (langfristig)

## Dokumentenstruktur

| Datei | Inhalt |
|-------|--------|
| `01_asiatische_modelle.md` | Vergleichende Analyse: Singapur, Japan, Suedkorea, Thailand, China |
| `02_lobby_analyse_und_durchsetzung.md` | Akteur-Analyse (inkl. G-BA), Gegenargumente, Kommunikationsstrategie |
| `03_adaption_singapur_deutschland.md` | GSP-Detaildesign, Rechtsform, Beitragsstruktur, Uebergangsregelungen |
| `04_sensitivitaetsanalyse.md` | Tornado, Break-Even, Monte-Carlo (1.000 Laeufe), Robustheits-Assessment |
| `model/gesundheit_projektion_model.py` | Python v2.0: GSP-Akkumulation, GKV-Beitragssatz, Sensitivitaet |

## Rigor Statement

**Confidence: Medium-High** fuer demografische Kostenprojektion und Systemvergleich.
**Confidence: Medium** fuer politische Durchsetzbarkeit und GSP-Renditeerwartung.

Die Analyse basiert auf Destatis-Demografiedaten, BMG/GKV-Ausgabenstatistik, WHO/OECD-Systemvergleichen und vergleichender Institutionenanalyse. Limitationen: 35-Jahres-Projektionen sind inherent unsicher; politische Dynamiken unvorhersagbar.
