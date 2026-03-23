# Lastenheft: Material-KI-Taskforce "Operation GNoME-DFR"

## 1. Programmziel

Entdeckung und Validierung eines Werkstoffs fuer den DFR-Waermetauscher der gleichzeitig:
- 1000°C Betriebstemperatur in fluessigem Blei uebersteht
- Schnellen Neutronen (>100 dpa Lebensdosis) widersteht
- Thermische Zyklen ueber 5+ Jahre ohne kritische Degradation aushalt
- Industriell fertigbar ist (3D-Druck oder Giessen in Grossbauteilen >1m)

**Erfolgskriterium ("First-to-Material"):** Physisch validierter Werkstoff mit <20% Degradation nach 5.000 aequivalenten Betriebsstunden unter DFR-Bedingungen.

**Zeitziel:** 18-24 Monate vom Programmstart bis zum validierten Material.

---

## 2. Programmstruktur

```
OPERATION GNoME-DFR — ABLAUFPLAN

Monat 0-2:     SETUP
                → KI-Modell-Architektur festlegen
                → NOMAD-Datensatz fuer Pb-Korrosion+Neutronen kuratieren
                → Autonomes Labor spezifizieren und beschaffen
                → Bestrahlungskapazitaet reservieren (FRM II, HZDR)

Monat 2-8:     PHASE 1 — DIGITALES SCREENING
                → GNoME-DFR-Modell trainieren (Stabilitaet bei 1000°C+Pb)
                → MACE-Simulationen: Korrosionsdynamik Top-10.000
                → PKA-Simulationen: Neutronenschaeden Top-1.000
                → Down-Selection auf Top-50 Kandidaten

Monat 8-18:    PHASE 2 — AUTONOME SYNTHESE + TEST
                → A-Lab synthetisiert Top-50 Materialien
                → Non-nuklearer Korrosionstest: 1000°C Pb-Bad
                → Beschleunigte Bestrahlung: Ionenstrahl (HZDR)
                → Mechanische Pruefung nach Bestrahlung
                → Down-Selection auf Top-3 Kandidaten

Monat 18-24:   PHASE 3 — PROTOTYP-VALIDIERUNG
                → Top-3 als Waermetauscher-Segment fertigen
                → Test im non-nuklearen Kreislauf (1000°C Pb, thermische Zyklen)
                → 5.000h aequivalenter Betrieb
                → FINAL-AUSWAHL: 1 Material

Monat 24+:     UEBERGABE an DFR-Hauptprogramm (Phase 2: Non-Nuklearer Prototyp)
```

---

## 3. Arbeitspakete

### AP1: KI-Modell-Entwicklung (Monate 0-8)

**Verantwortlich:** MPI fuer Intelligente Systeme (Tuebingen) + MPI fuer Eisenforschung (Duesseldorf)

| Teilaufgabe | Beschreibung | Deliverable |
|-------------|-------------|-------------|
| AP1.1 Datenkuration | NOMAD-Daten filtern fuer T>800°C + Uebergangsmetall-Oxide/Karbide/Nitride; ergaenzen mit experimentellen Korrosionsdaten aus ENEA (IT) und IPPE (RU, Literatur) | Kuratierter Trainingsdatensatz (~500.000 Eintraege) |
| AP1.2 GNoME-DFR-Modell | Fine-Tuning eines GNoME-Derivats auf DFR-spezifische Constraints: Thermische Stabilitaet + Pb-Resistenz + Neutronenquerschnitt | Trainiertes Modell, validiert gegen bekannte Referenzen (SiC, MAX-Phasen, ODS) |
| AP1.3 MACE-Korrosion | ML-Interatom-Potenziale fuer Pb-Material-Grenzflaeche; Simulation von Korrosionsmechanismen ueber virtuelle Monate | Korrosionsraten-Vorhersage fuer Top-10.000 Kandidaten |
| AP1.4 PKA-Neutronenschaden | Monte-Carlo-Simulation der Primary Knock-on Atom Kaskaden in Top-1.000 Kandidaten; Vorhersage von Schwellung, Versproedung, Transmutation | Neutronenresistenz-Ranking |
| AP1.5 Down-Selection | Multi-Objective-Optimierung: Korrosion × Neutronenresistenz × Fertigbarkeit × Kosten | **Top-50 Kandidatenliste** mit vorhergesagten Eigenschaften |

**Budget AP1:** 80 Mio. EUR
**Personal:** ~40 KI-Forscher + ~30 Computational Materials Scientists

---

### AP2: Autonome Synthese und Test (Monate 8-18)

**Verantwortlich:** Fraunhofer IKTS (Dresden) + KIT (Karlsruhe) + HZDR (Dresden-Rossendorf)

| Teilaufgabe | Beschreibung | Deliverable |
|-------------|-------------|-------------|
| AP2.1 Autonomes Labor | Robotik-Plattform fuer automatisierte Materialsgenerierung: Sinteroefen, Heiss-Isostat-Pressen, Pulveraufbereitung — KI-gesteuert, 24/7 | Betriebsbereites autonomes Labor |
| AP2.2 Synthese Top-50 | Herstellung aller 50 KI-Kandidaten als Probekoerper (Standardgeometrie: Staebe, Scheiben, Rohrabschnitte) | 50 Materialproben in Testqualitaet |
| AP2.3 Pb-Korrosionstest | 1000°C fluessiges Blei, 1.000h Standzeit je Probe; Massenverlussmessung, Oberflaechenanalyse (REM/EDX), mech. Restfestigkeit | Korrosionsraten + Degradationsprofile |
| AP2.4 Ionenstrahl-Bestrahlung | Beschleunigte Neutronenschaden-Simulation an HZDR (Ionenstrahlen simulieren 5 Jahre Reaktorbetrieb in Wochen) | Bestrahlungsschaeden-Bewertung fuer alle 50 Kandidaten |
| AP2.5 Mechanische Pruefung | Zugversuch, Kriechversuch, Ermuedung — an bestrahlten und korrodierten Proben | Mechanische Kennwerte nach Belastung |
| AP2.6 Down-Selection | Ranking nach realem Verhalten vs. KI-Vorhersage; Kalibrierung des Modells | **Top-3 Kandidaten** + aktualisiertes KI-Modell |

**Budget AP2:** 80 Mio. EUR
**Personal:** ~50 Materialwissenschaftler + ~20 Labortechniker + ~10 Robotik-Ingenieure

---

### AP3: Prototyp-Validierung (Monate 18-24)

**Verantwortlich:** KIT (Karlsruhe) + Industriepartner (Schott/Heraeus/EOS)

| Teilaufgabe | Beschreibung | Deliverable |
|-------------|-------------|-------------|
| AP3.1 Waermetauscher-Segment | Fertigung von 3 Waermetauscher-Segmenten (je ~50cm) aus den Top-3 Materialien; additive Fertigung (EOS/TRUMPF) oder Feinguss (Heraeus) | 3 Prototyp-Segmente |
| AP3.2 Non-Nuklearer Kreislauf-Test | Integration in elektrisch beheizten Pb-Kreislauf bei 1000°C; 5.000 Betriebsstunden mit thermischen Zyklen (Aufheizen/Abkuehlen 1x/Woche) | Langzeit-Betriebsdaten |
| AP3.3 Verbindungstechnik | Loesen des CMC↔Stahl-Uebergangsproblems: Gradierte Verbindungen, Weichlot-Adaptionen, mechanische Klemmung | Validierte Verbindungsloesung |
| AP3.4 Skalierbarkeits-Bewertung | Kann das Material in 2m-Bauteilen gefertigt werden? Kosten pro Waermetauscher-Einheit? Lieferkette? | Fertigungsbewertung + Stueckkosten-Schaetzung |
| AP3.5 Finale Auswahl | Entscheidung: 1 Material fuer DFR-Hauptprogramm | **Validierter Werkstoff + Fertigungsrezept** |

**Budget AP3:** 40 Mio. EUR
**Personal:** ~30 Ingenieure + ~20 Fertigungstechniker

---

## 4. Gesamtbudget und Personal

| Posten | Budget | Personal (Vollzeit-Aequivalent) |
|--------|--------|---------------------------------|
| AP1: KI-Modell | 80 Mio. EUR | 70 FTE |
| AP2: Autonome Synthese | 80 Mio. EUR | 80 FTE |
| AP3: Prototyp-Validierung | 40 Mio. EUR | 50 FTE |
| Programmleitung + Overhead | 10 Mio. EUR | 10 FTE |
| Supercomputing (Juelich) | 15 Mio. EUR | — (Rechenzeit) |
| Bestrahlungszeit (HZDR/FRM II) | 10 Mio. EUR | — (Strahlzeit) |
| Industriepartner (Schott/EOS/Heraeus) | 15 Mio. EUR | 20 FTE (bei Partnern) |
| Reserve (15%) | 35 Mio. EUR | — |
| **Gesamt** | **~285 Mio. EUR** | **~230 FTE** |
| **Laufzeit** | **24 Monate** | |

**Kontext:** 285 Mio. EUR = der Preis von 2 Eurofighter-Flugzeugen. Fuer die potenzielle Loesung von Deutschlands Energieabhaengigkeit.

---

## 5. Governance

### Organisationsstruktur

```
BUNDESREGIERUNG (Auftraggeber)
         |
         v
    PROGRAMMLEITER (1 Person)
    → Rang: Staatssekretaer oder Sonderbeauftragter
    → Berichtet direkt an BK-Amt
    → Vollmacht fuer Direktvergabe bis 50 Mio. EUR
         |
    +────+────+
    |         |
    v         v
WISSENSCHAFTLICHER     INDUSTRIELLER
BEIRAT (7 Pers.)       BEIRAT (5 Pers.)
- 2× MPI               - Schott
- 1× Fraunhofer         - Heraeus
- 1× KIT                - EOS/TRUMPF
- 1× DLR                - SGL Carbon
- 1× Juelich            - Plansee
- 1× Extern (MIT/ETH)
         |
         v
    3 ARBEITSPAKETE (AP1/AP2/AP3)
    → Je 1 AP-Leiter (Prof. oder Abteilungsleiter)
    → Quartalsmaessige Meilenstein-Reviews
    → Go/No-Go nach 9 Monaten (Ende AP1)
    → Go/No-Go nach 18 Monaten (Ende AP2)
```

### Go/No-Go-Kriterien

| Checkpoint | Zeitpunkt | Go-Kriterium | No-Go-Konsequenz |
|-----------|-----------|-------------|-----------------|
| **Gate 1** | Monat 9 | KI-Modell erreicht >80% Vorhersagegenauigkeit fuer bekannte Referenzmaterialien UND Top-50 Liste steht | Modell-Architektur ueberarbeiten; +3 Monate |
| **Gate 2** | Monat 18 | Min. 3 von 50 Kandidaten ueberstehen 1.000h Pb-Test bei 900+°C mit <15% Degradation | Temperaturziel auf 800°C senken; Phase 3 anpassen |
| **Gate 3** | Monat 24 | 1 Material uebersteht 5.000h im Kreislauf; Verbindungstechnik funktioniert; Skalierung machbar | Uebergabe an DFR-Hauptprogramm; Serienentwicklung starten |
| **Abbruch** | Jederzeit | Kein Kandidat uebersteht 500h bei 800°C | Programm umschwenken auf konventionellen MSR (650°C, bewiesene Materialien) |

---

## 6. Kooperationsstruktur DeepMind-Algorithmen ↔ Deutsche Daten

### Das Modell: Algorithmen lizenzieren, Daten behalten

```
KOOPERATIONSMODELL

DEEPMIND/GOOGLE                    DEUTSCHLAND
(Algorithmen)                      (Daten + Domaene)

  GNoME-Architektur ────→ Lizenz ────→ Fine-Tuning auf NOMAD-Daten
  (Open Source Paper,                    durch MPI Tuebingen/Duesseldorf
   Gewichte teilw. offen)
                                         ↓
                                   DFR-SPEZIFISCHES MODELL
                                   (deutsches IP, deutsche Server,
                                    NOMAD-Daten bleiben in DE)
                                         ↓
                                   ERGEBNISSE
                                   → Materialentdeckungen = deutsches IP
                                   → Patente = deutsche Anmeldung
                                   → Fertigungsverfahren = Industriepartner
```

**Warum dieses Modell funktioniert:**
- GNoME ist im Kern **open research** (Paper publiziert, Methodik offen) — die Architektur kann repliziert werden
- Der **Wert liegt in den Trainingsdaten** (NOMAD — gehosted in Deutschland) und der **Domaenenexpertise** (Pb-Korrosion, Neutronenschaeden — MPI, KIT, Juelich)
- DeepMind hat kein Interesse an DFR-Waermetauschern — es gibt keinen Wettbewerb um dieses spezifische Problem
- **Ergebnis:** Deutschland nutzt die beste KI-Architektur der Welt, behaelt aber alle Ergebnisse, Patente und Fertigungsverfahren

**Alternative falls DeepMind nicht kooperiert:**
- MACE (Cambridge) ist vollstaendig open source — kann sofort genutzt werden
- Eigenes Foundation Model trainieren auf NOMAD+Materials Project (~6 Monate Zusatzaufwand)
- MPI Tuebingen hat die Kapazitaet ein GNoME-aequivalentes Modell zu bauen

---

## 7. Risikomatrix

| Risiko | Wahrscheinlichkeit | Auswirkung | Minderung |
|--------|-------------------|-----------|-----------|
| **KI-Vorhersage versagt unter Neutronenbeschuss** (Transmutationseffekte in Trainingsdaten unterrepraesentiert) | 25% | Hoch — zurueck zu konventionellem Screening | Separate Neutronenschaden-Datenbank aufbauen (AP1.4); konservative Validierung |
| **Kein Kandidat uebersteht 1000°C** | 15% | Mittel — Fallback auf 800°C | DFR-800 ist immer noch revolutionaer (siehe Hauptdokument) |
| **Skalierungsproblem** (Labor→Grossbauteil) | 30% | Mittel — Verzoegerung +12 Monate | TRUMPF/EOS frueh einbinden (AP3.4); additive Fertigung statt Giessen |
| **Autonomes Labor funktioniert nicht zuverlaessig** | 20% | Niedrig — Fallback auf manuelle Synthese | Parallelbetrieb manuell + autonom; manuell als Backup |
| **Politische Streichung** | 15% | Existenziell — Programm endet | 285 Mio. EUR als Forschungsfoerderung, nicht als Nuklearprogramm deklarieren |
| **China loest Problem zuerst** | 20% | Mittel — Exportmarkt reduziert | Energiesouveraenitaet bleibt wertvoll unabhaengig von Export |

---

## Rigor Statement

**Confidence: Medium-High** fuer den KI-beschleunigten Screening-Ansatz (GNoME hat 2,2 Mio. Strukturen mit >80% Genauigkeit vorhergesagt; MACE ist peer-reviewed und open source).
**Confidence: Medium** fuer den 24-Monats-Zeitrahmen (abhaengig von Autonomie-Grad des Labors und Verfuegbarkeit von Bestrahlungszeit).
**Confidence: Low-Medium** fuer die KI-Vorhersagegenauigkeit unter Neutronenbeschuss (Trainingsdaten fuer kombinierte Pb+Neutronen+1000°C existieren kaum — das ist der "known unknown").

**Falsifizierbarkeit:** Das Programm ist gescheitert, wenn nach 18 Monaten kein einziger KI-vorhergesagter Kandidat die physischen Tests uebersteht (Gate 2 verfehlt) — das wuerde zeigen, dass die KI-Modelle fuer dieses spezifische Problemfeld unzureichend sind und die Kombination Pb+Neutronen+1000°C jenseits der aktuellen Vorhersagefaehigkeit liegt.
