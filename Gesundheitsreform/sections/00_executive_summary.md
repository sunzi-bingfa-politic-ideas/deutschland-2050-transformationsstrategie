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

## Quantitative Ergebnisse

| Metrik | Ohne Reform | Mit GSP-Modell |
|--------|------------|----------------|
| GKV-Beitragssatz 2045 | ~24,5% | ~16,5% (+2% GSP = 18,5% effektiv) |
| GSP-Kapitalstock 2045 | 0 | ~1.500 Mrd. EUR |
| Kumulative Ersparnis (35 J.) | — | ~550 Mrd. EUR |
| Schuldenfinanzierungsbedarf | ~2 Bio. EUR | Deutlich reduziert durch GSP-Ertraege |

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
| `02_lobby_analyse_und_durchsetzung.md` | Akteur-Analyse, Gegenargumente, Kommunikationsstrategie |
| `03_adaption_singapur_deutschland.md` | GSP-Detaildesign, Rechtsform, Beitragsstruktur, Uebergangsregelungen |
| `model/gesundheit_projektion_model.py` | Python-Simulationsmodell (demografische Kosten, Szenarien, GSP-Akkumulation) |

## Rigor Statement

**Confidence: Medium-High** fuer demografische Kostenprojektion und Systemvergleich.
**Confidence: Medium** fuer politische Durchsetzbarkeit und GSP-Renditeerwartung.

Die Analyse basiert auf Destatis-Demografiedaten, BMG/GKV-Ausgabenstatistik, WHO/OECD-Systemvergleichen und vergleichender Institutionenanalyse. Limitationen: 35-Jahres-Projektionen sind inherent unsicher; politische Dynamiken unvorhersagbar.
