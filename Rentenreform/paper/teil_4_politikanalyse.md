# Teil IV: Politikfeldanalysen

## 9. Arbeitsmarkteffekte: RSSP und Mangelberufe

### 9.1 Problemstellung: Fachkraeftemangel im Niedriglohnsektor

Deutschland leidet unter einem strukturellen Fachkraeftemangel, der sich auf spezifische Berufsgruppen im unteren und mittleren Einkommenssegment konzentriert. Die Bundesagentur fuer Arbeit identifiziert jaehrlich 163 Engpassberufe (Stand 2024), in denen offene Stellen nur schwer oder gar nicht besetzt werden koennen (BA 2024).

**Tabelle 9.1: Kennzahlen ausgewaehlter Engpassberufe 2024**

| Sektor | Beispielberuf | Vakanzzeit (Tage) | Medianlohn (EUR/Monat) |
|--------|---------------|-------------------|------------------------|
| Pflege | Altenpflege (Fachkraft) | 286 | 3.901 |
| Pflege | Altenpflege (Hilfskraft) | 250 | 2.800 |
| Handwerk | Sanitaer/Heizung/Klima | 280 | 3.331 |
| Handwerk | Elektrotechnik | 260 | 3.500 |
| Transport | Berufskraftfahrer | 220 | 2.800 |
| Soziales | Erzieher/in | 210 | 3.600 |

*Quellen: Bundesagentur fuer Arbeit (2024); Statista.*

Eine Studie der Bertelsmann-Stiftung (2025) dokumentiert ein strukturelles Abwanderungsmuster: Von 2022 bis 2023 verliessen etwa 191.000 Personen Engpassberufe zugunsten von Taetigkeiten ohne Fachkraeftemangel. Im Pflegebereich orientierten sich zwei Drittel der Abwanderer vollstaendig beruflich um. Unter den haeufig genannten Ursachen befindet sich neben schlechten Arbeitsbedingungen, zu geringen Loehnen und mangelnder Wertschaetzung auch die unzureichende Altersvorsorge-Perspektive. Letztere wird in der arbeitsmarktpolitischen Diskussion systematisch unterschaetzt.

Bei einem Medianlohn von 3.901 EUR brutto (Altenpflege Fachkraft) erreicht eine Pflegekraft nach 45 Beitragsjahren in der GRV eine Ersatzrate von lediglich 48%. Dies entspricht einer monatlichen Bruttorente von etwa 1.880 EUR -- ein Betrag nahe der Armutsgefaehrdungsschwelle.

### 9.2 Effektive Verguetung unter dem RSSP

Die Attraktivitaet eines Berufs haengt nicht allein vom Bruttogehalt ab, sondern von der *effektiven Verguetung*, die den impliziten Barwert der Rentenanwartschaft einbezieht:

$$\text{Effektive Verguetung} = \text{Jahresbrutto} + \text{Barwert}(\text{Rentenanspruch pro Arbeitsjahr})$$

Fuer einen Arbeitnehmer, der rational zwischen Berufen waehlt, ist diese Gesamtbetrachtung entscheidungsrelevant.

Wir analysieren die effektive Verguetung in 14 typischen Mangelberufen und vergleichen das GRV-System mit dem RSSP unter Config-D-Parametern (Garantie: 85% Low / 60% Mid; effektiver Beitragssatz: 12,6%).

**Tabelle 9.2: Effektive Verguetung nach Einkommensgruppe -- GRV vs. RSSP (Config D)**

| Kennzahl | GRV | RSSP (Config D) | Delta |
|----------|-----|-----------------|-------|
| **Low-Gruppe (< 30.000 EUR/Jahr)** | | | |
| Durchschnittliche Ersatzrate | 48% | 85% | **+37 PP** |
| Effektive Verguetung (Aufschlag) | +21% | +38% | **+16 PP** |
| Erwartete Vakanzzeit-Reduktion | -- | -- | **-11 Tage** |
| **Mid-Gruppe (30.000--55.000 EUR/Jahr)** | | | |
| Durchschnittliche Ersatzrate | 48% | 60% | **+12 PP** |
| Effektive Verguetung (Aufschlag) | +21% | +27% | **+5 PP** |
| Erwartete Vakanzzeit-Reduktion | -- | -- | **-4 Tage** |

*Anmerkung: Aufschlag auf effektive Verguetung berechnet als Barwert des jaehrlichen Rentenanspruchszuwachses relativ zum Jahresbrutto. Elastizitaet 0,3 (konservativ).*

Im Vergleich zur Vorgaengerversion (v1: 100%/70%-Garantie) fallen die Aufschlaege moderater aus. Die Differenz bleibt gleichwohl substanziell: Fuer die Low-Gruppe entspricht die RSSP-Garantie einem Aufschlag von 38% auf die effektive Verguetung -- gegenueber 21% unter dem GRV-System. Dieser Unterschied von 16 Prozentpunkten repraesentiert einen signifikanten nicht-lohnbasierten Attraktivitaetshebel.

### 9.3 Fallstudie: Altenpflege

Die Altenpflege ist der paradigmatische Fall eines Mangelberufs mit strukturell unzureichender Altersvorsorge-Perspektive.

**Tabelle 9.3: Altersvorsorge-Vergleich -- Altenpflege Fachkraft (3.901 EUR brutto/Monat)**

| System | Ersatzrate | Geschaetzte monatl. Rente | Effektive Verguetung |
|--------|------------|--------------------------|---------------------|
| GRV | 48% | 1.884 EUR | 56.850 EUR/Jahr |
| RSSP (Config D) | 60% | 2.341 EUR | 59.500 EUR/Jahr |
| **Delta** | **+12 PP** | **+457 EUR** | **+4,7%** |

*Anmerkung: Altenpflege Fachkraft faellt in die Mid-Gruppe. Die 60%-Garantie bezieht sich auf das Referenzeinkommen der Mid-Gruppe (EUR 40.000/Jahr), ergibt EUR 24.000/Jahr = EUR 2.000/Monat Mindestpension. Da das individuelle Einkommen (EUR 46.812/Jahr) ueber dem Referenzeinkommen liegt, erreicht die eigene Kapitalakkumulation im Regelfall einen hoeheren Wert.*

Fuer eine Pflegekraft bedeutet das RSSP unter Config D:
- Eine um ca. 457 EUR hoehere monatliche Rente gegenueber der GRV
- 12 Prozentpunkte mehr Ersatzrate
- 4,7% hoehere effektive Verguetung ohne Gehaltsaenderung

Diese Verbesserung ist geringer als unter der v1-Konfiguration (100%/70%), aber repraesentiert einen strukturellen Vorteil, der ueber die gesamte Erwerbsbiographie wirkt.

### 9.4 Arbeitsangebots-Elastizitaet und erwartete Effekte

Die Arbeitsangebotselastizitaet misst, wie stark das Arbeitsangebot auf Verguetungsaenderungen reagiert. Empirische Schaetzungen fuer Deutschland liegen bei:
- Extensive margin (Teilnahme): 0,2--0,5
- Intensive margin (Stunden): 0,1--0,3
- Berufswahl-Elastizitaet: 0,2--0,4

Wir verwenden konservativ 0,3 als Elastizitaet.

**Tabelle 9.4: Erwartete Arbeitsmarkteffekte (Config D)**

| Einkommensgruppe | Eff. Verguetung Aufschlag | Elastizitaet | Arbeitsangebot-Steigerung |
|------------------|--------------------------|-------------|--------------------------|
| Low | +16% | 0,3 | **+4,9%** |
| Mid | +5% | 0,3 | **+1,6%** |

*Anmerkung: Berechnung: Arbeitsangebot-Steigerung = Eff. Verguetung Aufschlag × Elastizitaet. Die Aufschlaege beziehen sich auf die Differenz der RSSP-effektiven Verguetung gegenueber der GRV-effektiven Verguetung.*

**Tabelle 9.5: Geschaetzte Vakanzzeit-Reduktion (Config D)**

| Sektor | Aktuelle Vakanzzeit | Erwartete Reduktion | Neue Vakanzzeit |
|--------|---------------------|---------------------|-----------------|
| Altenpflege | 286 Tage | -5 Tage | ~281 Tage |
| Handwerk | 260--280 Tage | -4 bis -5 Tage | ~256--275 Tage |
| Logistik | 180--220 Tage | -3 bis -4 Tage | ~177--216 Tage |

Diese Schaetzungen sind konservativ und beruecksichtigen ausschliesslich den monetaeren Kanal. Signaleffekte (gesellschaftliche Wertschaetzung, Imageverbesserung) sind nicht quantifiziert.

### 9.5 Wohneigentums-Effekt als Zusatzfaktor

Neben der hoeheren Ersatzrate verstaerkt der Wohneigentums-Effekt (vgl. Abschnitt 10) die Attraktivitaet fuer die Low-Gruppe:

- Die Eigentumsquote der unteren 30% liegt bei praktisch 0% (Bundesbank-Daten).
- Das RSSP-Beleihungsmodell (vgl. Abschnitt 10.2) ermoeglicht durch Verpfaendung von bis zu 20% des RSSP-Guthabens eine Verbesserung der Kreditwuerdigkeit.
- Die 85%-Kaufkraftgarantie (Config D) reduziert das Langfristrisiko fuer Kreditgeber -- wenngleich weniger stark als bei einer 100%-Garantie.

Fuer einen Low-Income-Arbeitnehmer, der durch das RSSP zum Wohneigentum kommt, ergibt sich ein kombinierter Effekt aus hoeherer Ersatzrate und Mietersparnis:

| Szenario | Ersatzrate | Jaehrl. Rentenanspruch | Mietersparnis | Effektive Ersatzrate |
|----------|------------|------------------------|---------------|---------------------|
| GRV (Mieter) | 48% | 10.560 EUR | 0 EUR | **48%** |
| RSSP Config D (Eigentuemer) | 85% | 18.700 EUR | +6.000 EUR | **112%** |

Die effektive Ersatzrate von 112% uebersteigt das urspruengliche Erwerbseinkommen und bietet eine substanzielle Absicherung im Alter. Bei der v1-Konfiguration (100%-Garantie) lag dieser Wert bei 123% -- die Reduktion um 11 Prozentpunkte ist moderat.

### 9.6 Sekundaereffekte

**Reduktion der Berufsabwanderung.** Die jaehrliche Abwanderungsrate aus Mangelberufen von 191.000 Personen (Bertelsmann-Stiftung 2025) koennte sinken, wenn die langfristige Absicherung verbessert wird. Besonders relevant: In der Pflege orientieren sich zwei Drittel der Abwanderer vollstaendig um; im Handwerk ist die Abwanderung in den tertiaeren Sektor hoch.

**Signalwirkung fuer Berufswahl.** Das RSSP signalisiert gesellschaftliche Wertschaetzung fuer Berufe, die bisher als schlecht abgesichert galten. Dies koennte die Berufswahl junger Menschen beeinflussen: Eine Handwerksausbildung wird attraktiver gegenueber einem Studium, eine Pflegeausbildung gewinnt durch die hoehere Einkommensgarantie.

**Fachkraefteeinwanderung.** Das RSSP koennte auch fuer auslaendische Fachkraefte ein Argument darstellen: klare Altersabsicherung (vs. komplexes GRV-System), relativ hohe Ersatzrate auch bei kurzer Beitragsdauer, Wohneigentums-Perspektive.

### 9.7 Limitationen

1. **Vereinfachte Elastizitaet**: Die verwendete Berufswahl-Elastizitaet von 0,3 ist stark kontextabhaengig und schwer praezise zu schaetzen.
2. **Langfristiger Effekt**: Die Verhaltensaenderung tritt erst ein, wenn das RSSP etabliert und bekannt ist (Verzoegerung 5--10 Jahre).
3. **Keine Interaktionseffekte**: Wechselwirkungen mit Lohnaenderungen, Arbeitszeitmodellen und anderen arbeitsmarktpolitischen Instrumenten sind nicht modelliert.
4. **Keine empirische Kalibrierung**: Die Schaetzungen sind theoretisch abgeleitet, nicht an Beobachtungsdaten kalibriert.
5. **Verhaltensannahmen**: Die Analyse setzt voraus, dass Arbeitnehmer die effektive Verguetung verstehen und in Berufswahlentscheidungen einbeziehen.

### 9.8 Zusammenfassung

Das RSSP unter Config D erzielt signifikante positive Arbeitsmarkteffekte fuer Mangelberufe, wenngleich moderater als unter der v1-Konfiguration:

1. **Ersatzraten-Steigerung**: +12 bis +37 Prozentpunkte (je nach Einkommensgruppe; v1: +23 bis +55 PP)
2. **Effektive Verguetung**: +5 bis +16% ohne direkte Lohnerhoehung (v1: +8 bis +20%)
3. **Erwartete Angebotseffekte**: +1,6 bis +4,9% Arbeitsangebot in Mangelberufen (v1: +2,5 bis +6,0%)
4. **Wohneigentums-Effekt**: Zusaetzlicher Anreiz durch verbesserte Eigentumsquote (unveraendert)

Die Reduktion der Garantieniveaus von 100%/70% auf 85%/60% verringert die quantitativen Effekte um etwa 20--30%, eliminiert sie jedoch nicht. Die qualitative Schlussfolgerung bleibt erhalten: Das RSSP adressiert einen bisher vernachlaessigten Faktor der Berufsattraktivitaet -- die langfristige Altersabsicherung -- und bietet einen nachhaltigen strukturellen Vorteil fuer Mangelberufe.

---

## 10. Wohnungsmarkteffekte: Das Beleihungsmodell

### 10.1 Mechanismus: Zweckgebundene Verpfaendung statt Kapitalentnahme

Das RSSP unterstuetzt den Wohneigentumserwerb nicht durch direkte Kapitalentnahme -- die die Rente gefaehrden wuerde --, sondern durch ein *Beleihungsmodell* (zweckgebundene Verpfaendung). Dieses Modell adressiert das zentrale Hindernis fuer Wohneigentum im unteren und mittleren Einkommenssegment: nicht primaer fehlendes Eigenkapital, sondern mangelnde Kreditwuerdigkeit.

**Der Mechanismus im Detail:**

1. **Sperrvermerk und Verpfaendung.** Der RSSP-Teilnehmer verpfaendet einen Teil seines angesparten Kapitals (maximal 20% des Portfoliowerts) an die finanzierende Bank.

2. **Eigenkapital-Ersatz.** Die Bank akzeptiert den verpfaendeten Teil regulatorisch als harte Sicherheit. Dies senkt den Beleihungsauslauf (Loan-to-Value) der Restschuld und verbessert die regulatorische Eigenkapitalbehandlung.

3. **Nachrangiges Darlehen.** Die Bank gewaehrt ein Zusatzdarlehen in Hoehe der Verpfaendung. Im Verwertungsfall (Default) hat die Bank Zugriff auf den verpfaendeten RSSP-Teil -- aber *ausschliesslich* auf diesen.

4. **Kapital bleibt investiert.** Anders als bei Riester-Wohn-Entnahmen bleibt das RSSP-Kapital im Portfolio investiert und generiert weiterhin Rendite. Nur im Verwertungsfall wird die Sicherheit liquidiert.

**Beispielrechnung (Low-Earner Familie):**

| Position | Betrag |
|----------|--------|
| Kaufpreis | 250.000 EUR |
| Nebenkosten (10%) | 25.000 EUR |
| Benoetiges Kapital | 275.000 EUR |
| Vorhandenes Cash | 5.000 EUR |
| **Ohne RSSP** | **Finanzierung scheitert (>100% LTV)** |
| RSSP-Kontostand | 60.000 EUR |
| Verpfaendung (20%) | 12.000 EUR Sicherheit |
| Effekt | Zinssatz sinkt um 0,5--0,8 PP; Kreditgenehmigung ermoeglicht |

### 10.2 Regulatorische Sicherheitsschranken

Um die Rentenfunktion des RSSP zu schuetzen, gelten strenge Limits:

1. **Cap**: Maximal 20% des RSSP-Guthabens verpfaendbar.
2. **Zweckbindung**: Ausschliesslich fuer selbstgenutztes Wohneigentum (Ersterwerber).
3. **Verwertungstrigger**: Die Sicherheit darf erst liquidiert werden, wenn die Immobilienzwangsversteigerung die Restschuld nicht deckt.

### 10.3 Ausgangslage: Eigentumsquoten in Deutschland

Deutschland hat mit 47,3% die niedrigste Wohneigentumsquote in der EU. Entscheidend ist die extreme Einkommensabhaengigkeit:

**Tabelle 10.1: Eigentumsquoten nach Einkommensgruppe**

| Einkommensgruppe | Eigentumsquote (IST) | RSSP-Zielquote |
|------------------|---------------------|----------------|
| Untere 30% (Low) | ~0% | 20% |
| Mittlere 50% (Mid) | ~35% | 50% |
| Obere 20% (High) | >65% | (nicht im RSSP) |

*Quelle: Deutsche Bundesbank.*

Das Kernproblem: Die Low-Gruppe hat praktisch keinen Zugang zu Wohneigentum. Das RSSP-Beleihungsmodell adressiert dieses Zugangsdefizit, indem es aus bis zur Rente gesperrtem Kapital aktives Collateral macht -- ohne den Zinseszinseffekt des Portfolios zu unterbrechen.

### 10.4 Quantitative Ergebnisse

Der Beleihungsmechanismus ist unabhaengig von der Hoehe der Kaufkraftgarantie (85%/60% in Config D). Die Verpfaendbarkeit bezieht sich auf den tatsaechlichen Kontostand, nicht auf die Garantieniveaus. Die nachfolgenden Schaetzungen gelten daher unveraendert fuer Config D.

**Tabelle 10.2: Neue Eigentuemer durch RSSP-Beleihungsmodell**

| Kennzahl | Wert |
|----------|------|
| Neue Eigentuemer Low-Gruppe | 1,41 Mio. Haushalte |
| Neue Eigentuemer Mid-Gruppe | 1,76 Mio. Haushalte |
| **Gesamt** | **3,17 Mio. Haushalte** |

**Tabelle 10.3: Effekte auf den Mietmarkt**

| Kennzahl | Wert |
|----------|------|
| Freigewordene Mietwohnungen | 3,17 Mio. |
| Mietmarkt-Bestand (58% von 43,8 Mio.) | 25,4 Mio. |
| Angebotssteigerung | +12,5% |
| Mietpreiseffekt (Elastizitaet -0,19) | **-2,4%** |

Die verwendete Miet-Elastizitaet (-0,19) stammt aus einer Studie im *Journal of Political Economy Macroeconomics* (2024): Ein Prozent mehr Wohnungsangebot fuehrt zu 0,19% niedrigeren Mieten. Der Mechanismus wirkt ueber "Moving Chains" -- wenn Haushalte in Eigentum wechseln, wird die bisherige Mietwohnung frei und kann von anderen Mietern bezogen werden, mit Kaskaden-Effekten ueber alle Marktsegmente.

**Tabelle 10.4: Szenario-Analyse**

| Szenario | Neue Eigentuemer | Angebot +% | Mietreduktion | Ersparnis/Mieter/Jahr |
|----------|-----------------|-----------|---------------|----------------------|
| Konservativ (Low: 15%) | 2,23 Mio. | 8,8% | 1,7% | 2.196 EUR |
| **Moderat (Low: 20%)** | **3,17 Mio.** | **12,5%** | **2,4%** | **3.121 EUR** |
| Optimistisch (Low: 25%) | 4,11 Mio. | 16,2% | 3,1% | 4.046 EUR |

### 10.5 Doppel-Effekt fuer die Low-Gruppe

Die Low-Gruppe profitiert zweifach:

**Effekt 1: Eigentuemer werden mietfrei.** Fuer die 20% der Low-Gruppe, die dank RSSP Eigentum erwerben: Ersparnis ca. 4.000 EUR/Jahr (entfallene Miete), Vermoegensaufbau durch Immobilie.

**Effekt 2: Mieter profitieren von mehr Angebot.** Fuer die 80% der Low-Gruppe, die weiterhin mieten: Ersparnis ca. 3.121 EUR/Jahr (niedrigere Mieten durch freigewordene Wohnungen).

**Tabelle 10.5: Gewichteter Gesamteffekt (Low-Gruppe)**

| Anteil | Effekt | Jaehrliche Ersparnis |
|--------|--------|---------------------|
| 20% Eigentuemer | Mietfreiheit | 4.000 EUR |
| 80% Mieter | Niedrigere Mieten | 3.121 EUR |
| **Gewichteter Durchschnitt** | | **3.297 EUR/Jahr** |

### 10.6 Zeitliche Entwicklung

Der Effekt baut sich ueber ca. 20 Jahre auf, da RSSP-Kontostande erst akkumulieren muessen:

**Tabelle 10.6: Zeitpfad der Wohnungsmarkteffekte**

| Jahr | Low Uplift | Mid Uplift | Neue Eigentuemer | Miete Baseline | Miete RSSP |
|------|------------|------------|------------------|----------------|------------|
| 2025 | 0% | 0% | 0 | 9,50 EUR/qm | 9,50 EUR/qm |
| 2035 | 10% | 7,5% | 1,59 Mio. | 15,47 EUR/qm | 15,29 EUR/qm |
| 2045 | 20% | 15% | 3,17 Mio. | 25,21 EUR/qm | 24,61 EUR/qm |
| 2055 | 20% | 15% | 3,17 Mio. | 41,06 EUR/qm | 40,08 EUR/qm |

### 10.7 Vergleich mit bestehenden Instrumenten

**Tabelle 10.7: Instrumente zur Wohneigentumsfoerderung**

| Instrument | Mechanismus | Kapitalentnahme | Risiko fuer Rente |
|------------|-------------|-----------------|-------------------|
| Riester-Wohn | Entnahme fuer Eigentum | Ja | Rentenluecke |
| Bausparvertrag | Zwecksparen | Ja | Niedrige Rendite |
| **RSSP-Beleihung** | **Verpfaendung** | **Nein** | **Kein Rentenrisiko** |

Der RSSP-Vorteil: Die Altersvorsorge bleibt vollstaendig erhalten. Nur die Information ueber den Kontostand -- und im Ernstfall der Zugriff auf maximal 20% -- wird genutzt. Das Kapital bleibt investiert und generiert weiterhin Rendite.

### 10.8 Gesamtnutzen

**Tabelle 10.8: Langfristiger Gesamtnutzen**

| Gruppe | Anteil Eigentuemer | Jaehrl. Ersparnis (Durchschnitt) | 40-Jahres-Nutzen |
|--------|-------------------|----------------------------------|------------------|
| Low (20% Eigentum) | 1,41 Mio. Haushalte | 3.297 EUR | ~132.000 EUR |
| Mid (50% Eigentum) | 1,76 Mio. Haushalte | 2.800 EUR | ~112.000 EUR |
| Kumulierte Gesamtersparnis (60 Jahre) | | | **1.438 Mrd. EUR** |

### 10.9 Limitationen

1. **Eigentumsquoten-Uplift** (geschaetzt +20 PP fuer Low): Abhaengig von der tatsaechlichen Kreditvergabepraxis der Banken und der Akzeptanz des RSSP-Pfandrechts.
2. **Miet-Elastizitaet** (-0,19): Regional unterschiedlich; in Ballungsraeumen moeglicherweise niedriger.
3. **Ramp-up-Zeit** (20 Jahre): Koennte bei langsamerer RSSP-Akkumulation laenger dauern.
4. **Baulandverfuegbarkeit**: Ohne verfuegbares Bauland keine neuen Eigenheime.
5. **Regionale Variation**: Die Effekte unterscheiden sich erheblich zwischen Muenchen und Sachsen-Anhalt.
6. **Crowding-Out**: Mehr Kaeufer koennten Kaufpreise erhoehen und den Wohneigentumseffekt teilweise konterkarieren.

---

## 11. Gender-Aspekte: RSSP-Wirkung auf den Gender Pension Gap

### 11.1 Ausgangslage: Der Gender Pension Gap in Deutschland

Der Gender Pension Gap beschreibt die Rentenluecke zwischen Frauen und Maennern. In Deutschland ist diese Luecke besonders ausgepraegt:

**Tabelle 11.1: Gender Pension Gap in Deutschland**

| Kennzahl | Wert |
|----------|------|
| Gender Pension Gap (gesamt) | 27% |
| West-Deutschland | 37--43% |
| Ost-Deutschland | 10--18% |
| Ohne Hinterbliebenenrente | 42% |

*Quellen: WSI; OECD Pensions at a Glance 2023.*

Die Ursachen sind strukturell und kumulieren sich ueber das Erwerbsleben:

**Tabelle 11.2: Strukturelle Ursachen des Gender Pension Gap**

| Faktor | Frauen | Maenner | Differenz |
|--------|--------|---------|-----------|
| Teilzeitquote | 47,4% | 10,6% | 36,8 PP |
| Teilzeitquote (mit Kindern) | 63,6% | 7,3% | 56,3 PP |
| Gender Pay Gap (Stundenlohn) | -21% | -- | 21% |
| Karriereunterbrechung | +4,2 Jahre | -- | 4,2 Jahre |
| Motherhood Penalty | -40% bis -70% | -- | Lebenseinkommen |

*Quellen: Destatis; Eurostat.*

Die Kausalitaetskette: Geburt eines Kindes → Elternzeit (ueberproportional Muetter) → Karriereunterbrechung (2--8 Jahre) → Wiedereinstieg in Teilzeit → niedrigeres Stundeneinkommen (Pay Gap) → geringere Beitragszahlung → niedrigere Rente → Gender Pension Gap von 27--42%.

### 11.2 Typische Erwerbsprofile

Fuer die Analyse definieren wir fuenf typische Profile:

**Tabelle 11.3: Erwerbsprofile fuer die Gender-Analyse**

| Profil | Teilzeitanteil | Karriereluecke | Lohnfaktor |
|--------|---------------|----------------|------------|
| Mann, Vollzeit | 0% | 0 Jahre | 1,00 |
| Frau, kinderlos | 20% | 0 Jahre | 0,87 |
| Mutter, 1 Kind | 40% | 3 Jahre | 0,82 |
| Mutter, 2 Kinder | 50% | 6 Jahre | 0,78 |
| Mutter, 3+ Kinder | 60% | 10 Jahre | 0,75 |

*Anmerkung: Teilzeitanteil bedeutet den Anteil der Karriere, der in Teilzeit (50% der Stunden) gearbeitet wird. Der Lohnfaktor reflektiert den Gender Pay Gap und teilzeitbedingte Lohnabschlaege.*

### 11.3 RSSP-Ergebnisse nach Profil (Config D: 85%/60%)

Unter der Config-D-Konfiguration (85% Garantie fuer Low, 60% fuer Mid) ergeben sich die folgenden Pensionsniveaus:

**Tabelle 11.4: Jaehrliche Rente nach Profil und Einkommensgruppe (Config D)**

| Profil | Eigene Akkumulation (EUR/Jahr) | Mit 85%/60%-Garantie (EUR/Jahr) | Differenz |
|--------|-------------------------------|-------------------------------|-----------|
| Mann, Vollzeit, Low | 15.744 | **18.700** | +2.956 |
| Mann, Vollzeit, Mid | 28.864 | **28.864** | 0 (eigene > Garantie) |
| Frau, kinderlos, Low | 9.227 | **18.700** | +9.473 |
| Frau, kinderlos, Mid | 17.593 | **24.000** | +6.407 |
| Mutter, 1 Kind, Low | 7.190 | **18.700** | +11.510 |
| Mutter, 1 Kind, Mid | 14.007 | **24.000** | +9.993 |
| Mutter, 2 Kinder, Low | 6.115 | **18.700** | +12.585 |
| Mutter, 2 Kinder, Mid | 12.388 | **24.000** | +11.612 |
| Mutter, 3+ Kinder, Low | 4.958 | **18.700** | +13.742 |

*Anmerkung: Die Garantie wirkt als Mindestpension (Floor). Low: 85% von EUR 22.000 = EUR 18.700/Jahr. Mid: 60% von EUR 40.000 = EUR 24.000/Jahr. Eigene Akkumulation basiert auf v1-Modelldaten (Einkommen, Beitraege, Portfoliorendite ueber 47 Jahre). Wenn die eigene Akkumulation die Garantie uebersteigt, wird der hoehere Wert ausgezahlt.*

**Ersatzraten (Config D):**

**Tabelle 11.5: Ersatzraten nach Profil**

| Profil | Eigene Ersatzrate | Mit Config-D-Garantie |
|--------|-------------------|----------------------|
| Mann, Vollzeit, Low | 68% | **85%** |
| Mann, Vollzeit, Mid | 68% | **68%** (eigene > 60%) |
| Frau, kinderlos, Low | 55% | **85%** |
| Frau, kinderlos, Mid | 56% | **60%** |
| Mutter, 1 Kind, Low | 50% | **85%** |
| Mutter, 1 Kind, Mid | 52% | **60%** |
| Mutter, 2 Kinder, Low | 45% | **85%** |
| Mutter, 2 Kinder, Mid | 48% | **60%** |
| Mutter, 3+ Kinder, Low | 38% | **85%** |

**Zentrale Erkenntnis**: In der Low-Gruppe erreichen alle Profile -- unabhaengig von Geschlecht oder Erwerbsverlauf -- die 85%-Garantie. Die Kaufkraftgarantie eliminiert den Gender Pension Gap innerhalb der Low-Gruppe vollstaendig. In der Mid-Gruppe erreichen die meisten Frauenprofile die 60%-Garantie, waehrend Maenner mit eigener Akkumulation von 68% darueberliegen. Hier bleibt ein residualer Gap bestehen.

### 11.4 Gender Pension Gap im Vergleich (Config D vs. GRV)

**Tabelle 11.6: Gender Pension Gap -- Systemvergleich**

| Vergleich (Mann Vollzeit vs.) | Ohne Garantie | RSSP Config D | GRV heute |
|-------------------------------|---------------|---------------|-----------|
| **Low-Gruppe** | | | |
| Frau kinderlos vs. Mann | 41% | **0%** | 27% |
| Mutter 1 Kind vs. Mann | 54% | **0%** | 40% |
| Mutter 2 Kinder vs. Mann | 61% | **0%** | 50% |
| Mutter 3+ Kinder vs. Mann | 69% | **0%** | 55% |
| **Mid-Gruppe** | | | |
| Frau kinderlos vs. Mann | 39% | **17%** | 27% |
| Mutter 1 Kind vs. Mann | 51% | **17%** | 40% |
| Mutter 2 Kinder vs. Mann | 57% | **17%** | 50% |
| Mutter 3+ Kinder vs. Mann | 65% | **17%** | 55% |

*Anmerkung: Low-Gruppe: Alle Profile treffen auf die 85%-Garantie, daher Gap = 0%. Mid-Gruppe: Die meisten Frauenprofile treffen auf die 60%-Garantie (EUR 24.000), waehrend der Mann Vollzeit EUR 28.864 aus eigener Akkumulation erzielt. Gap = (28.864 - 24.000)/28.864 = 17%. In der v1-Konfiguration (100%/70%) betrug der Mid-Gap ebenfalls ca. 17% (durch aehnlichen Mechanismus). Die Elimination des Gaps in der Low-Gruppe ist der entscheidende Unterschied zum GRV-System.*

**Interpretation:**

1. **Ohne Garantie** waere der Gender Gap im RSSP deutlich hoeher als in der GRV, da Kapitalakkumulation staerker von kontinuierlichen Beitraegen abhaengt als das Umlageverfahren.

2. **Mit Config-D-Garantie** wird der Gap in der Low-Gruppe vollstaendig eliminiert. In der Mid-Gruppe verbleibt ein residualer Gap von ca. 17%, der sich aus der Differenz zwischen eigener Akkumulation (68% fuer Maenner) und Garantiefloor (60%) ergibt.

3. **Vergleich mit GRV**: Fuer die Low-Gruppe ist das RSSP mit Config-D-Garantie besser als die GRV (0% vs. 27--55% Gap). Fuer die Mid-Gruppe ist das RSSP in den meisten Profilen besser als die GRV (17% vs. 27--55% Gap).

### 11.5 Lebenszeit-Rentenvergleich

Die laengere Rentenbezugsdauer von Frauen (22,1 vs. 18,8 Jahre; DRV) veraendert das Bild zugunsten von Frauen:

**Tabelle 11.7: Lebenszeit-Rentenvolumen (Config D)**

| Profil | Jaehrl. Rente (EUR) | Bezugsjahre | Lebenszeit-Rente (EUR) |
|--------|---------------------|-------------|------------------------|
| Mann, Vollzeit, Low | 18.700 | 18,8 | 351.560 |
| Mann, Vollzeit, Mid | 28.864 | 18,8 | 542.643 |
| Frau, kinderlos, Low | 18.700 | 22,1 | 413.270 |
| Frau, kinderlos, Mid | 24.000 | 22,1 | 530.400 |
| Mutter, 1 Kind, Low | 18.700 | 22,1 | 413.270 |
| Mutter, 1 Kind, Mid | 24.000 | 22,1 | 530.400 |
| Mutter, 2 Kinder, Low | 18.700 | 22,1 | 413.270 |
| Mutter, 2 Kinder, Mid | 24.000 | 22,1 | 530.400 |
| Mutter, 3+ Kinder, Low | 18.700 | 22,1 | 413.270 |

*Anmerkung: Alle Low-Frauenprofile erhalten identische Lebenszeit-Renten, da sie den 85%-Floor treffen.*

**Tabelle 11.8: Lebenszeit Gender Gap (Config D)**

| Vergleich | Jaehrlicher Gap | Lebenszeit Gap |
|-----------|-----------------|----------------|
| **Low-Gruppe** | | |
| Alle Frauenprofile vs. Mann | 0% | **-18%** (Frauen besser) |
| **Mid-Gruppe** | | |
| Alle Frauenprofile vs. Mann | 17% | **2%** |

In der Low-Gruppe kehrt sich der Gap bei Lebenszeitbetrachtung sogar um: Frauen erhalten ueber die gesamte Rentenbezugsdauer 18% *mehr* als Maenner, da sie bei gleicher Jahresrente (beide treffen den 85%-Floor) 3,3 Jahre laenger leben. In der Mid-Gruppe schrumpft der Gap von 17% (jaehrlich) auf 2% (Lebenszeit).

### 11.6 Care-Credits: Staatlich finanzierte Beitraege

Care-Credits sind staatlich finanzierte RSSP-Beitraege fuer Personen, die unbezahlte Care-Arbeit leisten. Sie belasten die Betroffenen nicht finanziell.

**Tabelle 11.9: Care-Credit-Struktur**

| Typ | Jahre pro Ereignis | Max. Jahre | Beitrag/Jahr |
|-----|-------------------|------------|--------------|
| Kindererziehung | 3 pro Kind | 12 (4 Kinder) | 5.280 EUR |
| Pflege Angehoeriger | 1 pro Jahr | 5 | 5.280 EUR |
| Eigene schwere Krankheit | 1 pro Jahr | 3 | 5.280 EUR |

*Basis: 12% des Durchschnittseinkommens (EUR 44.000/Jahr).*

**Vergleich mit GRV-Kindererziehungszeiten:**

| Kennzahl | GRV | RSSP Care-Credits |
|----------|-----|-------------------|
| Jahre pro Kind | 3 | 3 |
| Wert pro Jahr | 1 Entgeltpunkt | 5.280 EUR Kapital |
| Rente pro Kind (jaehrlich) | 1.416 EUR | 2.223 EUR |
| **Vorteil RSSP** | -- | **+57%** |

Der RSSP-Vorteil resultiert daraus, dass das eingezahlte Kapital ueber 30+ Jahre mit der Portfoliorendite waechst, waehrend GRV-Entgeltpunkte keine Kapitalakkumulation erfahren.

**Wirkung auf die Rente:** Da die Kaufkraftgarantie (85%/60%) bereits greift, erhoehen Care-Credits die Ersatzrate nicht direkt -- sie erhoehen jedoch das akkumulierte Kapital *oberhalb der Garantie* und reduzieren damit die Abhaengigkeit vom High-Pool fuer Garantie-Topups.

**Tabelle 11.10: Puffer-Effekt der Care-Credits**

| Profil | Garantie | Kapital ohne Credits | Kapital mit Credits | Puffer |
|--------|----------|---------------------|--------------------|----|
| Mutter, 1 Kind, Low | 85% | Knapp | Komfortabel | +15% |
| Mutter, 2 Kinder, Low | 85% | Knapp | Komfortabel | +25% |
| Mutter, 3+ Kinder, Low | 85% | Unter Garantie | Nahe Garantie | +35% |

**Kosten fuer den Staat:**

| Kategorie | Kosten/Jahr | Anteil |
|-----------|-------------|--------|
| Kindererziehung | 3,5 Mrd. EUR | 81% |
| Pflege Angehoeriger | 0,5 Mrd. EUR | 12% |
| Schwere Krankheit | 0,3 Mrd. EUR | 7% |
| **Gesamt** | **4,3 Mrd. EUR** | 100% |

Zum Vergleich: GRV Muetterrente ~12 Mrd. EUR/Jahr, Kindergeld ~50 Mrd. EUR/Jahr, Elterngeld ~8 Mrd. EUR/Jahr. Die RSSP-Care-Credits entsprechen 0,9% des Bundeshaushalts bzw. 0,1% des BIP.

**Implementierung**: Automatische Erfassung ohne Antragserfordernis (Standesamt → RSSP bei Geburt; Pflegekasse → RSSP bei Pflege; Krankenkasse → RSSP bei Krankheit). Finanzierung aus allgemeinen Steuermitteln, nicht aus dem High-Pool.

### 11.7 Strukturelle Vorteile des RSSP gegenueber der GRV

**Tabelle 11.11: Gender-Aspekte im Systemvergleich**

| Aspekt | GRV | RSSP (Config D) |
|--------|-----|-----------------|
| Teilzeitproblem | 1:1 niedrigere Punkte | 85%/60%-Garantie gleicht aus |
| Karriereluecken | 1:1 weniger Punkte | Garantie als Sicherheitsnetz |
| Laengere Lebenserwartung | Umlageproblem (weniger Beitragszahler) | Kapitalstock deckt laengere Laufzeit |
| Gender Pay Gap | Direkte Auswirkung auf Rente | Teilweise kompensiert durch Garantie |
| Hinterbliebenenrente | 55% der eigenen Rente | Kapitalstock vererbbar |

**Vererbbarkeit des Kapitalstocks:** Ein wichtiger gender-relevanter Vorteil. Szenario: Mann stirbt mit 70 (nach 3 Jahren Rentenbezug).

| System | Ergebnis fuer Witwe |
|--------|-------------------|
| GRV | 55% der Rente als Witwenrente (~12.000 EUR/Jahr) |
| RSSP | Restkapitalstock (~350.000 EUR) geht an Witwe |

### 11.8 Empfehlungen

1. **Kaufkraftgarantie beibehalten**: Die 85%/60%-Garantie ist das wichtigste Instrument zur Reduktion des Gender Gaps. Sie eliminiert den Gap in der Low-Gruppe vollstaendig.
2. **Care-Credits implementieren**: 3 Jahre pro Kind, Beitragshoehe auf Durchschnittseinkommens-Niveau, Finanzierung aus Bundesmitteln.
3. **Teilzeit-Aufwertung pruefen**: Optional: Teilzeitbeitraege koennten auf Vollzeit-Aequivalent aufgewertet werden (Schwedisches Modell).
4. **Splitting bei Scheidung**: RSSP-Anwartschaften sollten bei Scheidung haelftig geteilt werden (analog GRV-Versorgungsausgleich).
5. **Transparente Kommunikation**: Regelmaessige Information ueber erwarteten RSSP-Anspruch zur Foerderung eigenverantwortlicher Vorsorge.

### 11.9 Zusammenfassung

**Tabelle 11.12: Zusammenfassung der Gender-Ergebnisse (Config D)**

| Erkenntnis | Detail |
|------------|--------|
| Gender Pension Gap heute (GRV) | 27% (bis 42% ohne Hinterbliebenenrente) |
| RSSP ohne Garantie | Gap wuerde steigen auf 40--70% |
| **RSSP Config D (85%/60%)** | **Low: Gap = 0%; Mid: Gap = 17%** |
| Lebenszeit-Gap | Low: -18% (Frauen besser); Mid: 2% |
| Care-Credits | Reduzieren Abhaengigkeit vom High-Pool |
| Vererbbarkeit | Substanzieller Vorteil fuer Witwen |

Zentrale Erkenntnisse:

1. **Die Kaufkraftgarantie ist das entscheidende Instrument.** Ohne sie waere das RSSP fuer Frauen schlechter als die GRV, da Kapitalakkumulation staerker von kontinuierlichen Beitraegen abhaengt.

2. **Config D eliminiert den Gap in der Low-Gruppe vollstaendig.** Da alle Profile (Mann und Frau) den 85%-Floor treffen, gibt es innerhalb der Low-Gruppe keinen Gender Pension Gap -- ein Ergebnis, das unter der v1-Konfiguration (100%/70%) ebenfalls galt.

3. **In der Mid-Gruppe verbleibt ein residualer Gap von 17%.** Maenner akkumulieren ueber den 60%-Floor hinaus (68%), waehrend die meisten Frauenprofile auf dem Floor landen.

4. **Die Lebenszeitbetrachtung invertiert den Gap in der Low-Gruppe.** Frauen erhalten durch laengere Lebenserwartung insgesamt 18% mehr als Maenner.

5. **Care-Credits sind essentiell.** Sie reduzieren die Abhaengigkeit vom High-Pool und erhoehen den Kapitalpuffer oberhalb der Garantie.

---

## 12. Verwaltungskosten und Effizienz des RSSP

### 12.1 Bedeutung der Verwaltungskosten

Verwaltungskosten sind ein oft unterschaetzter Faktor bei Rentensystemen. Ueber Jahrzehnte akkumulieren sich selbst kleine Unterschiede zu erheblichen Betraegen:

**Tabelle 12.1: Kosteneffekt ueber 47 Jahre (EUR 100.000, 5% Bruttorendite)**

| Kosten p.a. | Nettorendite | Endkapital | Verlust durch Kosten |
|-------------|-------------|------------|---------------------|
| 0,00% | 5,00% | 990.608 EUR | -- |
| 0,13% (RSSP konservativ) | 4,87% | 934.565 EUR | -56.043 EUR (-5,7%) |
| 1,67% (Riester Durchschnitt) | 3,33% | 466.275 EUR | -524.333 EUR (-52,9%) |

1,54 Prozentpunkte Kostenunterschied fuehren ueber 47 Jahre zu einem Vermoegensverlust von ueber 50%.

### 12.2 Kostenstrukturen im Vergleich

**Deutsche Rentenversicherung (GRV):**

| Kennzahl | Wert |
|----------|------|
| Gesamtausgaben (2024) | 403 Mrd. EUR |
| Verwaltungskosten | 5,2 Mrd. EUR |
| Anteil an Ausgaben | 1,3% |
| Kosten pro Rentner | ~248 EUR/Jahr |
| Kosten pro Beitragszahler | ~116 EUR/Jahr |

Staerken: Niedrige Verwaltungskosten durch Groesse, kein Vertrieb (Pflichtmitgliedschaft), keine Kapitalverwaltung. Schwaeche: Keine Kapitalertraege (Umlageverfahren) -- Kosten sind zu 100% "verloren".

**Private Altersvorsorge (Riester):**

| Kennzahl | Durchschnitt | Spanne |
|----------|--------------|--------|
| Effektivkosten (% des Vermoegens) | 1,67% | 0,8--2,5% |
| Teure Produkte | 2,23% | Verbraucherzentrale-Studie |
| Anteil der Beitraege ueber Laufzeit | bis 38% | Finanzwende 2023 |

"Bei einem durchschnittlichen Vertrag fliesst nahezu jeder vierte eingezahlte Euro in die Kosten" (Finanzwende 2023).

**Internationale Best Practices:**

| System | Land | Kosten (% des Vermoegens) |
|--------|------|--------------------------|
| Government Pension Fund Global | Norwegen | 0,04% |
| AP-Fonds | Schweden | 0,10% |
| CPF | Singapur | ~0,05% |
| NZ Super Fund | Neuseeland | ~0,10% |

Erfolgsfaktoren: Staatliche Organisation (keine Gewinnmarge), zentrale Verwaltung (Skaleneffekte), keine Vertriebskosten (Pflichtmitgliedschaft), passive Anlagestrategien (Index-Tracking).

### 12.3 RSSP-Kostenschaetzung

**Tabelle 12.2: RSSP-Kostenstruktur**

| Kostenart | Anteil (% des Vermoegens) | Begruendung |
|-----------|--------------------------|------------|
| Kontoverwaltung | 0,03% | Automatisierte Prozesse |
| Kapitalverwaltung (Aktien 50%) | 0,02% | Passive ETF-Strategien |
| Kapitalverwaltung (Realwerte 50%) | 0,06% | Gold, Agrarland, Infrastruktur, Rohstoffe |
| IT-Infrastruktur | 0,02% | Zentrale Systeme |
| Compliance/Regulierung | 0,01% | Rechtliche Anforderungen |
| **Gesamt (konservativ)** | **0,13%** | |
| **Gesamt (optimistisch)** | **0,08%** | Mit Skaleneffekten |

**Tabelle 12.3: Absolute Kosten nach Phase**

| Phase | Vermoegen | Kostensatz | Jahreskosten | Pro Teilnehmer |
|-------|-----------|------------|--------------|----------------|
| Aufbauphase (Jahr 20) | 5 Bio. EUR | 0,13% | 6,5 Mrd. EUR | 144 EUR |
| Reifes System (Jahr 50) | 15 Bio. EUR | 0,08% | 12 Mrd. EUR | 267 EUR |

**Tabelle 12.4: Vergleich mit Referenzsystemen**

| System | Kosten (% Vermoegen) | Faktor relativ zu RSSP |
|--------|---------------------|----------------------|
| RSSP (konservativ) | 0,13% | 1,0x |
| Norway GPFG | 0,04% | 0,3x |
| Sweden AP | 0,10% | 0,8x |
| Riester | 1,67% | 12,8x |
| Typischer Aktienfonds | 1,50% | 11,5x |

Das RSSP ist etwa 10--15x guenstiger als private Altersvorsorge.

### 12.4 Langfristiger Kosteneffekt

**Tabelle 12.5: Endkapital nach 47 Jahren (5.500 EUR/Jahr Einzahlung, 5% Bruttorendite)**

| System | Kosten p.a. | Endkapital | Differenz |
|--------|-------------|------------|-----------|
| Ohne Kosten | 0,00% | 1.028.640 EUR | -- |
| RSSP (optimistisch) | 0,08% | 1.003.684 EUR | -24.955 EUR |
| RSSP (konservativ) | 0,13% | 988.428 EUR | -40.211 EUR |
| **Riester (Durchschnitt)** | **1,67%** | **625.104 EUR** | **-403.536 EUR** |

**Kostenvorteil RSSP vs. Riester:**

| Kennzahl | Wert |
|----------|------|
| Kostenvorteil pro Person | 363.000--379.000 EUR |
| Zusaetzliche Rentenjahre (bei 25.000 EUR/Jahr) | 14--15 Jahre |
| Kostenvorteil bei 45 Mio. Teilnehmern | 16--17 Bio. EUR |

### 12.5 Realwert-Allokation: Spezielle Kostenbetrachtung

Die diversifizierte Realwert-Allokation (15% Gold, 15% Agrarland, 13% Infrastruktur, 5% Rohstoffe, 2% Silber = 50% Realwerte) hat eine differenzierte Kostenstruktur:

**Tabelle 12.6: Kostenstruktur der Realwert-Allokation**

| Asset-Klasse | Kostensatz | Bemerkung |
|--------------|------------|-----------|
| Gold/Silber (17%) | 0,05--0,08% | Physische Lagerung, Versicherung |
| Agrarland (15%) | 0,15--0,25% | Bewirtschaftung, Pacht-Management |
| Infrastruktur (13%) | 0,20--0,30% | Fondsstruktur, komplexere Verwaltung |
| Rohstoffe (5%) | 0,10--0,15% | Lagerung, Rollkosten |
| **Gewichteter Durchschnitt Realwerte** | **0,12--0,18%** | |

Vorteile: Inflationsschutz ueber verschiedene Kanaele, geringe Korrelation mit Aktienmaerkten, keine Performance-Fees bei passiver Strategie. Nachteile: Hoehere Verwaltungskosten als reine Aktien-ETFs, Illiquiditaet bei Agrarland und Infrastruktur, keine bzw. geringe laufende Ertraege bei Gold/Silber.

### 12.6 Vergleich RSSP vs. GRV

**Tabelle 12.7: Direkter Kostenvergleich**

| Kennzahl | GRV | RSSP (reifes System) |
|----------|-----|---------------------|
| Verwaltungskosten | 5,2 Mrd. EUR | 12 Mrd. EUR |
| Kosten pro Teilnehmer | 116 EUR | 267 EUR |
| Vermoegen | 0 EUR | 15 Bio. EUR |
| Kapitalertraege (5%) | 0 EUR | 750 Mrd. EUR |
| **Kosten/Ertrag** | **100%** | **1,6%** |

Die GRV hat niedrigere absolute Verwaltungskosten, aber diese sind zu 100% verloren, da kein Kapital vorhanden ist, das Ertraege generiert. Das RSSP hat hoehere absolute Kosten (12 vs. 5,2 Mrd. EUR), aber diese stehen Kapitalertraegen von ~750 Mrd. EUR gegenueber. Das Kosten-Ertrags-Verhaeltnis betraegt nur 1,6%.

Analogie: Die GRV entspricht Mietkosten ohne Eigentum; das RSSP entspricht Hausverwaltungskosten mit Eigentum und Wertsteigerung.

### 12.7 Skaleneffekte

Das RSSP kann von erheblichen Skaleneffekten profitieren:

1. **Groesse**: Mit einem Zielvermoegen von 15 Bio. EUR waere der RSSP-Fonds einer der groessten Kapitalstocke weltweit. Norwegens GPFG (1,7 Bio. EUR) erreicht Kosten von 0,04% -- das RSSP waere 9x groesser.
2. **Pflichtmitgliedschaft**: Keine Vertriebs- und Akquisekosten (Riester: 3--6%).
3. **Passive Strategien**: Index-Tracking statt aktivem Management (Aktive Fonds: 1,0--2,0%; ETFs: 0,05--0,20%).
4. **Staatliche Traegerschaft**: Keine Gewinnmarge (Private Anbieter: 0,5--1,0%).

**Tabelle 12.8: Kostenprojektion mit Skaleneffekten**

| Jahr | Vermoegen | Kostensatz | Begruendung |
|------|-----------|------------|------------|
| 10 | 2 Bio. EUR | 0,15% | Aufbauphase |
| 20 | 5 Bio. EUR | 0,13% | Erste Skaleneffekte |
| 30 | 8 Bio. EUR | 0,10% | Schwedisches Niveau |
| 40 | 12 Bio. EUR | 0,08% | Reife Phase |
| 50 | 15 Bio. EUR | 0,06% | Maximale Effizienz |

### 12.8 Governance und Risiken

**Kostentreiber-Risiken:**

| Risiko | Wahrscheinlichkeit | Mitigation |
|--------|-------------------|------------|
| Politische Eingriffe | Mittel | Unabhaengige Governance |
| IT-Sicherheit | Mittel | Investition in Cybersecurity |
| Regulierung | Niedrig | Fruehzeitige Compliance |
| Goldpreis-Volatilitaet | Niedrig | Keine Auswirkung auf Lagerkosten |

**Governance-Empfehlungen:**
1. **Unabhaengiger Vorstand**: Wie bei der Bundesbank, nicht politisch besetzt.
2. **Transparenz**: Jaehrliche Veroeffentlichung aller Kosten.
3. **Benchmark**: Vergleich mit internationalen Best Practices.
4. **Kostendeckel**: Gesetzliche Obergrenze (z.B. 0,20%).

### 12.9 Zusammenfassung

**Tabelle 12.9: Zusammenfassung Verwaltungskosten**

| Erkenntnis | Detail |
|------------|--------|
| RSSP-Kosten (geschaetzt) | 0,08--0,13% des Vermoegens |
| Vergleich Riester | 10--15x guenstiger |
| Vergleich Norway GPFG | 2--3x teurer (realistisch erreichbar) |
| Kostenvorteil pro Person (vs. Riester) | ~365.000 EUR ueber 47 Jahre |
| Absolute Kosten (reifes System) | ~12 Mrd. EUR/Jahr |
| Kosten/Ertrag-Verhaeltnis | 1,6% (vs. 100% bei GRV) |

Zentrale Erkenntnisse:

1. **Kosteneffizienz**: Mit 0,08--0,13% liegt das RSSP im Bereich der besten internationalen Systeme.

2. **Massive Einsparungen gegenueber privater Vorsorge**: Pro Person etwa 365.000 EUR Kostenvorteil gegenueber Riester ueber die Ansparzeit.

3. **Skaleneffekte entscheidend**: Zentralisierung und Groesse ermoeglichen niedrige Kosten, die mit privaten Anbietern nicht erreichbar sind.

4. **GRV-Vergleich differenziert**: Die GRV hat niedrigere absolute Kosten, aber das Kosten-Ertrags-Verhaeltnis ist beim RSSP dramatisch besser (1,6% vs. 100%).

5. **Realwert-Allokation moderat teurer**: Die diversifizierten Realwerte kosten im Durchschnitt 0,12--0,18%, also etwas mehr als passive Aktien-ETFs (0,05--0,10%), bieten aber essenzielle Krisenresilienz und Inflationsschutz.

Die Verwaltungskostenanalyse ist unabhaengig von den Garantieniveaus (Config D: 85%/60%) und behaelt ihre volle Gueltigkeit gegenueber der Vorgaengerversion.

**Rigor: Medium** -- Die Kostenschaetzungen basieren auf internationalen Vergleichen und sind konservativ. Die genauen RSSP-Kosten haengen von der konkreten Implementierung ab. Die Groessenordnungen sind robust.

---

## Referenzen (Teil IV)

Bundesagentur fuer Arbeit (2024). Fachkraefteengpassanalyse 2024.

Bertelsmann Stiftung (2025). Pflege, Handwerk, IT: Abwanderung aus Engpassberufen.

Hans-Boeckler-Stiftung (2024). Verdienststruktur im Handwerk.

Deutsche Bundesbank (2023). Vermoegensverteilung privater Haushalte in Deutschland.

Journal of Political Economy Macroeconomics (2024). Housing Supply Elasticity and Rent Effects.

WSI (2024). Gender Pension Gap in Deutschland.

OECD (2023). Pensions at a Glance 2023: OECD and G20 Indicators.

Eurostat (2024). Gender Pay Gap Statistics.

Destatis (2024). Teilzeitquoten nach Geschlecht und Familienstand.

DRV (2024). Rentenbezugsdauer nach Geschlecht.

Norges Bank Investment Management (2024). Annual Report 2024.

Swedish Pension Agency (2020). Orange Report 2020.

Finanzwende (2023). Riester-Kosten: Wie viel von den Beitraegen kommt an?

Verbraucherzentrale (2024). Effektivkosten Riester-Vertraege.

OECD (2024). Pension Markets in Focus 2024.
