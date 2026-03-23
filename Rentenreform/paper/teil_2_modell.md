# 3. Formale Modellbeschreibung

## 3.1 Designprinzipien und Modellarchitektur

Das RSSP v2-Modell simuliert ein kapitalgedecktes Drei-Schichten-Rentensystem ueber einen konfigurierbaren Zeithorizont $T$ (Config D: 100 Jahre). Die Architektur basiert auf drei Grundprinzipien:

1. **Individuelle Kapitalkonten fuer Low und Mid**: Beitraege fliessen in persoenliche Konten, die ueber die Erwerbsphase aufgebaut und in der Rentenphase deterministisch abgebaut werden.

2. **Solidaritaetsfinanzierung durch High**: Die High-Einkommensgruppe leistet einen Beitragssatz $\tau_H$ ohne eigene Leistungsansprueche. Diese Mittel speisen einen gemeinsamen Garantie-Pool, der Ersatzraten-Garantien fuer Low und Mid finanziert.

3. **Acht Haertungen**: Das Modell integriert systematisch Mortalitaet, demografischen Wandel, staatliche Kreditlinien, altersabhaengige Einkommensprofile, post-annuitaere Langlebigkeitsabsicherung, Tontine-Mechanismus, symmetrische Reserve-Regel und Monte-Carlo-Simulation als unabhaengig schaltbare Module. Die Haertungen 1--5 definieren Config D; Config E aktiviert zusaetzlich die Haertungen 6--8.

## 3.2 Notation und Indexmengen

### Zeitstruktur
- $t \in \{0, 1, \ldots, T-1\}$: Simulationsperioden (Jahre)
- $T$: Simulationshorizont (Config D: 100 Jahre)

### Altersstruktur
- $a_0 = 20$: Eintrittsalter
- $a_R = 67$: Rentenalter
- $W = a_R - a_0 = 47$: Beitragsjahre (Erwerbsphase)
- $R = 20$: Annuitaetsdauer (regulaere Rentenphase, Alter 67--86)
- $a_{\max} = 95$: Maximalalter fuer Langlebigkeitsabsicherung

### Einkommensgruppen
- $g \in \{L, M, H\}$: Low, Mid, High
- Bevoelkerungsanteile: $s_L = 0{,}30$, $s_M = 0{,}50$, $s_H = 0{,}20$

### Kohortenstruktur
Jede Kohorte $c$ wird durch ihr Eintrittsjahr $i \in \{0, \ldots, T-1\}$ identifiziert. Die Kohortengroesse bei Eintritt betraegt:

$$N(i) = N_0 \quad \text{(Config D: } N_0 = 831.435 \text{, konstant)}$$

Die Gruppengroessen ergeben sich als:

$$N_g(i) = \lfloor N(i) \cdot s_g + 0{,}5 \rfloor$$

## 3.3 Einkommens- und Beitragsstruktur

### Einkommen

Die realen Jahreseinkommen bei Renteneintritt sind exogen vorgegeben:

| Gruppe | Symbol | Config D |
|--------|--------|----------|
| Low | $Y_L$ | EUR 22.000 |
| Mid | $Y_M$ | EUR 40.000 |
| High | $Y_H = Y_M \cdot f_H$ | EUR 72.000 ($f_H = 1{,}8$) |

In der Basiskonfiguration (Config D: `income_profile_enabled = false`) werden Beitraege ueber die gesamte Erwerbsphase auf dem Niveau des Einkommens bei Renteneintritt berechnet. Dies ist eine konservative Vereinfachung, die fruehe Beitraege leicht ueberschaetzt (vgl. Haertung 4).

### Beitragssaetze

Die Gesamtbeitragssaetze fuer die drei Gruppen:

| Gruppe | Symbol | Config D | Verwendung |
|--------|--------|----------|------------|
| Low | $\tau_L$ | 12% | Individuelles Konto |
| Mid | $\tau_M$ | 13% | Individuelles Konto |
| High | $\tau_H$ | 12,25% (optimiert) | Garantie-Pool (kein Konto) |

Die Saetze $\tau_L$ und $\tau_M$ umfassen Arbeitnehmer-, Arbeitgeber- und ggf. staatliche Anteile als aggregierten Gesamtbeitrag. Der High-Beitrag $\tau_H$ wird durch den Optimierer als minimaler Satz bestimmt, der alle Szenario-Anforderungen erfuellt (vgl. Abschnitt 3.11).

### Jaehrliche Beitraege

Fuer eine Kohorte $i$, die sich im Simulationsjahr $t$ im Arbeitsjahr $w = t - i$ befindet ($0 \le w < W$), gilt:

$$B_g(i, t) = N_g(i) \cdot Y_g \cdot f_{\text{inc}}(w) \cdot \tau_g$$

wobei $f_{\text{inc}}(w)$ der Einkommensprofilfaktor ist (bei deaktiviertem Profil: $f_{\text{inc}}(w) = 1{,}0$ fuer alle $w$).

Die High-Beitraege fliessen nicht in individuelle Konten, sondern direkt in den Garantie-Pool:

$$B_H^{\text{pool}}(t) = \sum_{\substack{i: \; 0 \le t-i < W}} N_H(i) \cdot Y_H \cdot f_{\text{inc}}(t-i) \cdot \tau_H$$

## 3.4 Kontodynamik

### Individuelle Konten (Low und Mid)

Jede Kohorte $i$ fuehrt fuer die Gruppen $g \in \{L, M\}$ ein aggregiertes Kohortenkonto $K_g(i, t)$. Die Dynamik gliedert sich in zwei Phasen:

**Erwerbsphase** ($0 \le t - i < W$):

Beitraege werden eingezahlt, anschliessend wird die Anlagerendite angewendet:

$$K_g(i, t) \leftarrow K_g(i, t) + B_g(i, t)$$
$$K_g(i, t) \leftarrow K_g(i, t) \cdot (1 + r_t)$$

wobei $r_t$ die reale Portfoliorendite im Jahr $t$ ist.

**Rentenphase** ($W \le t - i < W + R$):

Die regulaere Annuitaet wird entnommen (vgl. Abschnitt 3.5), danach wird die Rendite angewendet:

$$K_g(i, t) \leftarrow \max\!\big(0, \; K_g(i, t) - P_g^{\text{raw}}(i, t)\big) \cdot (1 + r_t)$$

**Implementierungshinweis**: Im Code (`model.py`, Zeilen 328--331) werden Beitraege zuerst akkumuliert und die Rendite dann einheitlich auf alle Konten angewendet. Dies entspricht der Konvention, dass Beitraege zu Jahresbeginn eingehen und die Rendite auf den gesamten Jahresanfangsbestand wirkt.

### Garantie-Pool

Der Garantie-Pool akkumuliert die High-Beitraege und finanziert Topup-Zahlungen:

$$\text{Pool}(t) \leftarrow \Big[\text{Pool}(t-1) + B_H^{\text{pool}}(t)\Big] \cdot (1 + r_t) - \text{Topup}(t) - \text{Transfer}_{\text{longevity}}(t) - \text{Tilgung}(t)$$

Die Abzuege fuer Topup, Longevity-Transfer und Kreditrueckzahlung werden in den Abschnitten 3.6, 3.9 und 3.8 spezifiziert.

## 3.5 Auszahlungsberechnung (Annuitaeten)

### Regulaere Annuitaet

Fuer eine Kohorte $i$, die sich im Rentenjahr $j = (t - i) - W$ befindet ($0 \le j < R$), betraegt die rohe Annuitaet:

$$P_g^{\text{raw}}(i, t) = \frac{K_g(i, t)}{R - j}$$

Dies ist eine deterministische Entnahme ueber die verbleibenden Rentenjahre. Die Division durch $R - j$ gewaehrleistet, dass das Konto am Ende der Annuitaetsperiode erschoepft ist, wobei in jedem Jahr der gleiche Anteil des verbleibenden Kapitals entnommen wird.

### Aggregation ueber Kohorten

Da im stationaeren Zustand bis zu $R$ Kohorten gleichzeitig Rente beziehen, werden die pro-Kopf-Auszahlungen kohortenuebergreifend aggregiert:

$$P_g^{\text{total}}(t) = \sum_{\substack{i: \; W \le t-i < W+R}} P_g^{\text{raw}}(i, t)$$

Die pro-Kopf-Auszahlung ergibt sich unter Beruecksichtigung der ueberlebenden Rentner (vgl. Haertung 1):

$$P_g^{\text{pc}}(t) = \frac{P_g^{\text{total}}(t)}{N_g^{\text{ret}}(t)}$$

wobei $N_g^{\text{ret}}(t)$ die Gesamtzahl der ueberlebenden Rentner der Gruppe $g$ im Jahr $t$ ist.

## 3.6 Gestaffelte Kaufkraftgarantie

### Garantiesaetze (Config D)

| Gruppe | Garantierate $\gamma_g$ | Ziel-Auszahlung $P_g^{\text{target}}$ |
|--------|------------------------|---------------------------------------|
| Low | $\gamma_L = 0{,}85$ | EUR 18.700/Jahr (EUR 1.558/Monat) |
| Mid | $\gamma_M = 0{,}60$ | EUR 24.000/Jahr (EUR 2.000/Monat) |

### Ziel-Auszahlung

$$P_g^{\text{target}} = \gamma_g \cdot Y_g$$

### Topup-Mechanismus

Falls die regulaere pro-Kopf-Annuitaet unter dem Garantieniveau liegt, wird die Differenz als Topup aus dem Garantie-Pool gedeckt:

$$\text{Topup}_g^{\text{need}}(t) = \max\!\big(0, \; P_g^{\text{target}} - P_g^{\text{pc}}(t)\big) \cdot N_g^{\text{ret}}(t)$$

$$\text{Topup}^{\text{need}}(t) = \text{Topup}_L^{\text{need}}(t) + \text{Topup}_M^{\text{need}}(t)$$

Die tatsaechlich geleistete Topup-Zahlung ist durch den verfuegbaren Pool begrenzt:

$$\text{Topup}^{\text{paid}}(t) = \min\!\big(\text{Pool}(t), \; \text{Topup}^{\text{need}}(t)\big)$$

Die verbleibende Luecke $\text{Gap}(t) = \text{Topup}^{\text{need}}(t) - \text{Topup}^{\text{paid}}(t)$ wird durch den Staats-Backstop adressiert (Haertung 3).

### Proportionale Verteilung

Die Topup-Zahlung wird proportional zum Bedarf auf Low und Mid verteilt:

$$\text{Topup}_g^{\text{paid}}(t) = \text{Topup}^{\text{paid}}(t) \cdot \frac{\text{Topup}_g^{\text{need}}(t)}{\text{Topup}^{\text{need}}(t)}$$

Die effektive pro-Kopf-Auszahlung nach Topup:

$$P_g^{\text{eff}}(t) = P_g^{\text{pc}}(t) + \frac{\text{Topup}_g^{\text{paid}}(t)}{N_g^{\text{ret}}(t)}$$

### Ersatzrate

$$\text{RR}_g(t) = \frac{P_g^{\text{eff}}(t)}{Y_g}$$

Das Pass-Kriterium verlangt $\text{RR}_L(t) \ge \gamma_L$ und $\text{RR}_M(t) \ge \gamma_M$ fuer alle $t$ in den letzten 10 Simulationsjahren.

## 3.7 Haertung 1: Mortalitaet

### Sterblichkeitsbuckets

Die Mortalitaet wird ueber altersabhaengige Ueberlebenswahrscheinlichkeiten modelliert. Die Altersachse wird in Buckets unterteilt, wobei jeder Bucket eine jaehrliche Ueberlebensrate $\sigma_b$ definiert:

| Bucket $b$ | Altersbereich | $\sigma_b$ (Config D) | Jaehrliche Sterbewahrscheinlichkeit $q_b = 1 - \sigma_b$ |
|------------|---------------|----------------------|----------------------------------------------------------|
| 1 | 67--74 | 0,982 | 1,8% |
| 2 | 75--84 | 0,955 | 4,5% |
| 3 | 85--95 | 0,88 | 12,0% |
| 4 | 96+ | 0,72 | 28,0% |

Diese Werte sind nach der Destatis-Sterbetafel 2022/2024 korrigiert. Die Originalwerte des Basismodells ($\sigma = 0{,}99 / 0{,}975 / 0{,}95 / 0{,}92$) ueberschaetzten die Lebenserwartung erheblich (29% Ueberlebensrate bis Alter 100 gegenueber realistischen 3,6%).

### Kumulative Ueberlebenswahrscheinlichkeit

Die Wahrscheinlichkeit, im $k$-ten Rentenjahr noch am Leben zu sein (bedingt auf Ueberleben bis Renteneintritt), ergibt sich als:

$$S(k) = \prod_{j=0}^{k-1} \sigma\!\big(\text{bucket}(a_R + j)\big)$$

mit $S(0) = 1{,}0$ (alle Kohortenangehoerigen leben bei Renteneintritt). Die Funktion $\sigma(\text{bucket}(a))$ ordnet jedem Alter $a$ die Ueberlebensrate des zugehoerigen Buckets zu.

### Tontine-Effekt innerhalb der Kohorten

Da die Annuitaet auf dem Gesamtkontostand der Kohorte basiert und die Entnahme $P_g^{\text{raw}}(i, t)$ unabhaengig von der Kopfzahl der Ueberlebenden erfolgt, entsteht ein impliziter Tontine-Mechanismus: Das Vermoegen der Verstorbenen verbleibt im Kohortenkonto und erhoet die pro-Kopf-Auszahlung der Ueberlebenden. Die ueberlebende Rentnerzahl einer Kohorte $i$ im Rentenjahr $j$ betraegt:

$$N_g^{\text{surv}}(i, j) = \lfloor N_g(i) \cdot S(j) + 0{,}5 \rfloor$$

## 3.8 Haertung 2: Demografiepfade

### Konfigurierbare Kohortengroessen

Im Modus `constant` ist $N(i) = N_0$ fuer alle $i$. Im Modus `path` wird ein exogener Vektor $\mathbf{N} = (N_0^{\text{path}}, N_1^{\text{path}}, \ldots)$ vorgegeben. Falls der Vektor kuerzer als $T$ ist, wird der letzte Wert fortgeschrieben:

$$N(i) = \begin{cases} N_i^{\text{path}} & \text{falls } i < |\mathbf{N}| \\ N_{|\mathbf{N}|-1}^{\text{path}} & \text{sonst} \end{cases}$$

### Stress-Szenario: Moderate Schrumpfung

Das vordefinierte Stress-Szenario modelliert eine deutsche demografische Schrumpfung ueber 80 Jahre:

| Phase | Jahre | Jaehrliche Schrumpfung | Kumulative Veraenderung |
|-------|-------|----------------------|------------------------|
| Demografische Traegheit | 0--20 | $-0{,}5\%$ | $-9{,}5\%$ |
| Peak Alterung | 20--50 | $-0{,}8\%$ | $-28{,}9\%$ |
| Stabilisierung | 50--80 | $-0{,}4\%$ | $-36{,}7\%$ |

Dies fuehrt zu einer Reduktion der Kohortenstaerke von 831.435 auf ca. 526.000 Eintritte pro Jahr.

### Wirkungsmechanismus

Die demografische Schrumpfung wirkt asymmetrisch: Die Beitraege der High-Kohorte sinken proportional zur Kohortengroesse, waehrend die Garantieverpflichtungen gegenueber aelteren (groesseren) Kohorten bestehen bleiben. Dies erhoet den erforderlichen Beitragssatz $\tau_H$ und stellt eine strukturelle Belastungsprobe fuer den Garantie-Pool dar.

**Hinweis**: In Config D ist der Demografiepfad deaktiviert (`mode = constant`). Die Schrumpfung wird als eigenstaendiges Stress-Szenario analysiert.

## 3.9 Haertung 3: Staats-Backstop (Kreditlinie)

### Mechanismus

Verbleibt nach Topup-Zahlung aus dem Pool eine Garantieluecke $\text{Gap}(t) > 0$, kann der Staat diese durch eine Kreditlinie schliessen. Der Backstop ist kein Zuschuss, sondern ein rueckzahlbares Darlehen:

$$L^{\text{add}}(t) = \min\!\big(\text{room}(t), \; \text{Gap}(t)\big)$$

mit dem verfuegbaren Kreditspielraum:

$$\text{room}(t) = \max\!\big(0, \; \text{cap}(t) - L(t)\big)$$

### Kreditobergrenze

Die Obergrenze ist als Anteil am Gesamtvermoegen des Systems definiert:

$$\text{cap}(t) = \alpha \cdot A^{\text{total}}(t)$$

wobei $\alpha = 0{,}10$ (Config D) und:

$$A^{\text{total}}(t) = \max\!\Big(1, \; \text{Pool}(t) + \text{LongevityPool}(t) + \sum_i K_L(i, t) + \sum_i K_M(i, t)\Big)$$

### Darlehensdynamik

$$L(t+1) = L(t) + L^{\text{add}}(t) - L^{\text{repay}}(t)$$

### Tilgung aus Pool-Ueberschuss

Die Tilgung erfolgt, sobald der Pool einen Reservepuffer uebersteigt:

$$\bar{D}(t) = \frac{1}{\min(5, t+1)} \sum_{k=t-\min(5,t+1)+1}^{t} \text{Topup}^{\text{need}}(k)$$

$$\text{Reserve}(t) = n_{\text{res}} \cdot \bar{D}(t)$$

wobei $n_{\text{res}} = 3$ (Config D) die Reservejahre angibt. Uebersteigt der Pool die Reserve:

$$L^{\text{repay}}(t) = \min\!\big(L(t), \; \rho \cdot [\text{Pool}(t) - \text{Reserve}(t)]\big)$$

mit Tilgungsrate $\rho = 0{,}50$ (Config D).

| Parameter | Symbol | Config D |
|-----------|--------|----------|
| Kreditobergrenze | $\alpha$ | 10% des Systemvermoegens |
| Tilgungsrate | $\rho$ | 50% des Ueberschusses |
| Reservejahre | $n_{\text{res}}$ | 3 Jahre |

### Interpretation

Der Backstop fungiert als antizyklischer Puffer in der Aufbauphase des Systems, wenn der Pool noch nicht ausreichend gefuellt ist, um saemtliche Garantien zu bedienen. Im stationaeren Zustand soll der Kredit vollstaendig getilgt sein. Die Kennzahl `loan_ever_repaid` ueberprueft, ob der Kredit nach erstmaliger Inanspruchnahme wieder auf null zurueckkehrt.

## 3.10 Haertung 4: Alters-Einkommensprofile

### Buckelfoermiges Einkommensprofil

Bei Aktivierung (`income_profile_enabled = true`) wird der Beitrag in jedem Arbeitsjahr $w$ mit einem altersabhaengigen Faktor $f_{\text{inc}}(w) \in (0, 1]$ skaliert:

$$B_g(i, t) = N_g(i) \cdot Y_g \cdot f_{\text{inc}}(t - i) \cdot \tau_g$$

Das Standardprofil approximiert eine typische deutsche Erwerbsbiografie:

| Alter | Karrierephase | Faktor $f_{\text{inc}}$ |
|-------|--------------|------------------------|
| 20--24 | Berufseinstieg | 0,35 -- 0,45 |
| 25--34 | Fruehe Karriere | 0,50 -- 0,78 |
| 35--44 | Mittlere Karriere | 0,80 -- 0,95 |
| 45--55 | Spitzenverdienst | 0,95 -- 1,00 |
| 56--66 | Spaete Karriere | 0,95 -- 0,90 |

Der Faktor wird stueckweise linear interpoliert (`model.py`, Zeilen 92--102):

$$f_{\text{inc}}(a) = \begin{cases}
0{,}35 + (a - 20) \cdot 0{,}025 & 20 \le a \le 24 \\
0{,}50 + (a - 25) \cdot 0{,}028 & 25 \le a \le 34 \\
0{,}80 + (a - 35) \cdot 0{,}015 & 35 \le a \le 44 \\
0{,}95 + (a - 45) \cdot 0{,}005 & 45 \le a \le 55 \\
0{,}95 - (a - 56) \cdot 0{,}005 & 56 \le a \le 66
\end{cases}$$

### Auswirkung

Die Aktivierung des Einkommensprofils reduziert die kumulierten Lebensbeitraege erheblich, da fruehe Arbeitsjahre weit unter dem Einkommen bei Renteneintritt liegen. Die resultierenden Kontostaende bei Renteneintritt sinken, was den Topup-Bedarf und damit den erforderlichen High-Beitrag $\tau_H$ um ca. 8--12 Prozentpunkte erhoeht.

**Config D deaktiviert dieses Modul.** Die flache Einkommenannahme ($f_{\text{inc}} = 1{,}0$) ueberschaetzt die fruehen Beitraege leicht, vermeidet aber die extreme Kostensteigerung des realistischen Profils. Diese konservative Wahl wird im Abschnitt Sensitivitaetsanalyse quantifiziert.

## 3.11 Haertung 5: Langlebigkeits-Pool (Longevity Pool)

### Motivation

Die regulaere Annuitaet endet mit dem Annuitaetsalter $a_R + R = 87$. Fuer Ueberlebende jenseits dieses Alters besteht ein Versorgungsbedarf, der weder durch die individuellen Konten noch durch die Kaufkraftgarantie abgedeckt ist. Der Longevity Pool schliesst diese Luecke.

### Post-Annuitaeres Fenster

$$L_{\text{years}} = a_{\max} - (a_R + R)$$

In Config D: $L_{\text{years}} = 95 - 87 = 8$ Jahre (Alter 87--95).

### Finanzierungsquellen

Der Longevity Pool wird aus drei Quellen gespeist:

**1. Residualguthaben bei Annuitaetsende**

Wenn eine Kohorte $i$ das Annuitaetsende erreicht (Rentenjahr $j = R$), wird das verbleibende Kontoguthaben in den Longevity Pool transferiert:

$$\text{Residual}(i) = K_L(i, t) + K_M(i, t) \quad \text{bei } t - i = W + R$$
$$\text{LongevityPool}(t) \leftarrow \text{LongevityPool}(t) + \text{Residual}(i)$$

Die individuellen Konten werden anschliessend auf null gesetzt. Dieser Transfer erfolgt pro Kohorte genau einmal (`model.py`, Zeilen 376--381).

**2. Ueberschussanteil des Garantie-Pools**

Uebersteigt der Garantie-Pool die Topup-Reserve, wird ein Anteil $\lambda$ des Ueberschusses in den Longevity Pool umgeleitet:

$$\text{Transfer}_{\text{longevity}}(t) = \lambda \cdot \max\!\big(0, \; \text{Pool}(t) - \text{Reserve}(t)\big)$$

mit $\lambda = 0{,}05$ (Config D). Dieser Transfer erfolgt nach der Kreditrueckzahlung (`model.py`, Zeilen 464--471).

**3. Staats-Backstop als letzte Instanz**

Reicht der Longevity Pool nicht aus, greift derselbe Backstop-Mechanismus wie bei den Garantie-Topups (gleiche Obergrenze $\alpha \cdot A^{\text{total}}(t)$, gleicher Kreditbestand $L(t)$).

### Auszahlung

Alle post-annuitaeren Ueberlebenden (Low und Mid, Alter $a_R + R$ bis $a_{\max} - 1$) erhalten eine jaehrliche Mindestpension (Floor):

$$P^{\text{floor}} = \text{EUR } 10.000/\text{Jahr} \quad (\approx \text{EUR } 833/\text{Monat})$$

Der Gesamtbedarf im Jahr $t$:

$$\text{LongevityNeed}(t) = P^{\text{floor}} \cdot N^{\text{long}}(t)$$

wobei $N^{\text{long}}(t)$ die Gesamtzahl der ueberlebenden post-annuitaeren Rentner (Low + Mid) ist, berechnet ueber die kumulativen Ueberlebensfaktoren $S(k)$ fuer $k \ge R$.

Die Auszahlung wird durch den verfuegbaren Pool begrenzt:

$$\text{LongevityPaid}(t) = \min\!\big(\text{LongevityPool}(t), \; \text{LongevityNeed}(t)\big)$$

### Rendite

Der Longevity Pool waechst mit derselben realen Rendite $r_t$ wie alle anderen Vermoegensbestandteile (`model.py`, Zeile 334):

$$\text{LongevityPool}(t) \leftarrow \text{LongevityPool}(t) \cdot (1 + r_t)$$

### Haertung 6: Tontine-Longevity-Mechanismus (Config E)

#### Motivation

Der statische Floor von EUR 10.000/Jahr liefert eine Grundsicherung, nutzt aber den Longevity Pool nur auf Mindestniveau. In positiven Renditeumgebungen akkumuliert der Pool erhebliche Ueberschuesse, die an die Ueberlebenden verteilt werden koennten -- ein klassischer Tontine-Gedanke: Je weniger Anspruchsberechtigte ueberleben, desto hoeher die pro-Kopf-Auszahlung.

#### Nachhaltigkeits-Constraint

Der Tontine-Bonus wird nur ausgeschuettet, wenn der Longevity Pool die kumulierten Floor-Verpflichtungen aller verbleibenden Langlebigkeitsrentner uebersteigt. Die verbleibende Floor-Verpflichtung wird als gewichtete Summe ueber die erwarteten Restjahre berechnet:

$$\text{FloorNeed}^{\text{total}}(t) = \sum_{k} n_k(t) \cdot \bar{R}_k(t) \cdot P^{\text{floor}}$$

wobei $n_k(t)$ die Anzahl der Ueberlebenden der Kohorte $k$ im Longevity-Fenster und $\bar{R}_k(t)$ deren erwartete Restjahre bis $a_{\max}$ bezeichnen.

#### Tontine-Formel

Sei $N^{\text{long}}(t)$ die Gesamtzahl der Longevity-Rentner, $\bar{R}(t)$ die durchschnittliche Restlebenszeit und $c_T = 3{,}0$ der Tontine-Cap-Multiplikator:

$$\text{Payout}^{\text{pc}}(t) = \begin{cases}
\min\!\Big(P^{\text{floor}} + \dfrac{\text{LongevityPool}(t) - \text{FloorNeed}^{\text{total}}(t)}{N^{\text{long}}(t) \cdot \max(1, \bar{R}(t))}, \; c_T \cdot P^{\text{floor}}\Big) & \text{falls } \text{LongevityPool}(t) > \text{FloorNeed}^{\text{total}}(t) \\[8pt]
P^{\text{floor}} & \text{sonst}
\end{cases}$$

In Config E ($c_T = 3{,}0$, $P^{\text{floor}} = 10.000$) ergibt sich ein maximaler Tontine-Payout von EUR 30.000/Jahr pro Kopf.

#### Backstop-Interaktion

Der Staats-Backstop garantiert nur den Floor, nicht den Tontine-Aufschlag:

$$\text{LongevityGap}(t) = \max\!\big(0, \; P^{\text{floor}} \cdot N^{\text{long}}(t) - \text{LongevityPaid}^{\text{pool}}(t)\big)$$

Der Tontine-Aufschlag ist "best effort" aus Pool-Mitteln. Dies stellt sicher, dass die Tontine-Erweiterung den Staats-Backstop nicht ueber den Floor hinaus belastet.

#### Wirkung

Bei positiven Renditen steigt die per-capita-Auszahlung von EUR 10.000 auf EUR 30.000 (3x Cap). Im 0%-Szenario verbleibt die Auszahlung bei EUR 29.864 (knapp unter dem Cap), da der Nachhaltigkeits-Constraint den Bonus bereits in fruehen Perioden begrenzt. Der Preis: Config E erfordert einen um 0,50 Prozentpunkte hoeheren Solidarbeitragssatz ($\tau_H = 12{,}75\%$ statt $12{,}25\%$).

### Haertung 7: Symmetrische Reserve-Regel (Config E)

#### Motivation

In deterministischen Szenarien mit konstanter Rendite ist der Garantie-Pool-Verlauf glatt. In stochastischen Umgebungen fuehren hochvolatile Renditesequenzen zu uebermaessigem Pool-Wachstum in guten Jahren und zu Depletion-Risiken in schlechten Jahren. Die symmetrische Reserve-Regel glaettet diese Dynamik durch antizyklische Pufferung.

#### Mechanismus

Sei $r_t$ die Rendite im Jahr $t$, $r^{\text{high}} = 0{,}03$, $r^{\text{low}} = 0{,}01$ die Trigger-Schwellen, $r^{\text{target}} = 0{,}02$ die Zielrendite, $\phi^{\text{skim}} = 0{,}30$ die Skim-Fraktion, $\phi^{\text{inject}} = 0{,}30$ die Inject-Fraktion und $r^{\text{safe}} = 0{,}005$ der sichere Zins auf die Reserve.

**Skim (Abschoepfung bei Ueberrendite):** Falls $r_t > r^{\text{high}}$:

$$\text{Excess}(t) = \text{Pool}_{\text{vor}}(t) \cdot (r_t - r^{\text{target}})$$
$$\text{Skim}(t) = \min\!\big(\phi^{\text{skim}} \cdot \max(0, \text{Excess}(t)), \; 0{,}10 \cdot \text{Pool}(t)\big)$$
$$\text{Pool}(t) \leftarrow \text{Pool}(t) - \text{Skim}(t); \quad \text{Reserve}(t) \leftarrow \text{Reserve}(t) + \text{Skim}(t)$$

**Inject (Zufuehrung bei Unterrendite):** Falls $r_t < r^{\text{low}}$:

$$\text{Shortfall}(t) = \text{Pool}_{\text{vor}}(t) \cdot (r^{\text{target}} - r_t)$$
$$\text{Inject}(t) = \min\!\big(\phi^{\text{inject}} \cdot \max(0, \text{Shortfall}(t)), \; \text{Reserve}(t)\big)$$
$$\text{Reserve}(t) \leftarrow \text{Reserve}(t) - \text{Inject}(t); \quad \text{Pool}(t) \leftarrow \text{Pool}(t) + \text{Inject}(t)$$

**Reserve-Verzinsung:** In jedem Jahr:

$$\text{Reserve}(t) \leftarrow \text{Reserve}(t) \cdot (1 + r^{\text{safe}})$$

#### Wirkung

In deterministischen Konstant-Rendite-Szenarien ist die Reserve-Regel wirkungslos, da Renditen die Trigger nicht dynamisch durchkreuzen. Ihre Wirkung entfaltet sich in der Monte-Carlo-Simulation: Die mediane Peak-Reserve betraegt EUR 203 Mrd. bei 8% Volatilitaet (P95: EUR 681 Mrd.). Die Reserve glaettet Pool-Volatilitaet und reduziert das Sequenzrisiko, insbesondere bei Renditeeinbruechen in der fruehen Rentenphase einer Kohorte.

| Config E Parameter | Symbol | Wert |
|---|---|---|
| Trigger High | $r^{\text{high}}$ | 3% |
| Trigger Low | $r^{\text{low}}$ | 1% |
| Zielrendite | $r^{\text{target}}$ | 2% |
| Skim-Fraktion | $\phi^{\text{skim}}$ | 30% |
| Inject-Fraktion | $\phi^{\text{inject}}$ | 30% |
| Sicherer Zins | $r^{\text{safe}}$ | 0,5% |

### Haertung 8: Monte-Carlo-Simulation (Config E)

#### Motivation

Die deterministische Szenarioanalyse (Abschnitt 3.12) testet das System gegen stilisierte Renditepfade. Dies erfasst weder Sequenzrisiken noch Fat-Tail-Ereignisse noch die stochastische Interaktion mehrerer Kohortenverlaeufe. Eine Monte-Carlo-Simulation adressiert diese Luecke.

#### Rendite-Generierung

**Log-normale Pfade.** Fuer ein Szenario mit mittlerer Rendite $\mu$ und Volatilitaet $\sigma$ wird der Renditepfad $(r_0, \ldots, r_{T-1})$ als unabhaengig identisch verteilt gezogen:

$$r_t = \exp\!\big((\mu - \tfrac{1}{2}\sigma^2) + \sigma \cdot \varepsilon_t\big) - 1, \quad \varepsilon_t \sim \mathcal{N}(0, 1)$$

Die Parametrisierung stellt sicher, dass $\mathbb{E}[1 + r_t] = e^\mu$, d.h. der Erwartungswert der geometrischen Rendite dem Zielwert $\mu$ entspricht.

**Regime-Switching.** Als Erweiterung wird ein 2-Zustand-Markov-Modell implementiert:

$$Z_t \in \{\text{Bull}, \text{Bear}\}, \quad P(Z_{t+1} | Z_t) = \begin{pmatrix} 0{,}95 & 0{,}05 \\ 0{,}20 & 0{,}80 \end{pmatrix}$$

Die zustandsabhaengigen Parameter sind:

| Zustand | $\mu_z$ | Stationaere Wkt. |
|---|---|---|
| Bull | $+6\%$ | $80\%$ |
| Bear | $-2\%$ | $20\%$ |

Die Gesamtmittelrendite im stationaeren Gleichgewicht betraegt $0{,}80 \cdot 6\% + 0{,}20 \cdot (-2\%) = 4{,}4\%$ (nominal); der gewaehlte reale Zielwert von 1,75% liegt deutlich darunter und reflektiert die konservative Kalibrierung.

#### Auswertung

Fuer jeden Pfad $j \in \{1, \ldots, N\}$ wird die vollstaendige Simulation (Abschnitte 3.2--3.11) durchgefuehrt. Die Ergebnismetriken werden ueber die $N$ Pfade aggregiert:

- **Pass-Rate**: Anteil der Pfade, die den Garantietest bestehen.
- **Ersatzraten-Perzentile**: P5, P25, P50, P75, P95 fuer $\text{RR}_L$ und $\text{RR}_M$.
- **Pool-Depletions-Rate**: Anteil der Pfade mit Pool-Erschoepfung.
- **Strukturelle Nachhaltigkeits-Rate**: Anteil der Pfade mit positivem Steady-State-Saldo.
- **Backstop-Kennzahlen**: P50 und P95 des maximalen Staatskredits.
- **Reserve-Kennzahlen**: P50 und P95 der Peak-Reserve.

#### Implementierung

Die Monte-Carlo-Simulation (`monte_carlo.py`) nutzt Python-Multiprocessing ueber alle verfuegbaren CPU-Kerne. Jeder Worker erhaelt einen Renditepfad und fuehrt eine vollstaendige Simulation durch. Bei 10.000 Pfaden betraegt die Laufzeit ca. 4,2 Sekunden auf 16 Kernen.

## 3.12 Optimierung: Bestimmung des minimalen $\tau_H$

### Grid-Search-Algorithmus

Der Optimierer (`optimize.py`) sucht den minimalen High-Beitragssatz $\tau_H^*$, bei dem alle Szenarien das Pass-Kriterium erfuellen:

$$\tau_H^* = \min\!\Big\{\tau_H \in \mathcal{G} \;\Big|\; \forall s \in \mathcal{S}: \text{passed}(\tau_H, s) = \text{true}\Big\}$$

Das Suchgitter ist:

$$\mathcal{G} = \{0{,}01, \; 0{,}0125, \; 0{,}015, \; \ldots, \; 0{,}25\}$$

mit Schrittweite $\Delta\tau = 0{,}0025$ (= 0,25 Prozentpunkte).

### Szenariomenge $\mathcal{S}$

Die Optimierung wird ueber eine Menge deterministischer Realrendite-Szenarien durchgefuehrt:

| Szenario | Reale Rendite $r$ |
|----------|-------------------|
| base_1p7 | 1,735% |
| realistic_2p5 | 2,5% |
| low_1p0 | 1,0% |
| hard_0p5 | 0,5% |
| flat_0p0 | 0,0% |

Zusaetzlich koennen pfadabhaengige Szenarien mit zeitvariablen Renditen getestet werden.

### Abbruchbedingung

Der Algorithmus bricht beim ersten $\tau_H$ ab, fuer das alle Szenarien bestanden werden (aufsteigend sortiert). Dies garantiert die Minimalitaet des gefundenen Satzes.

## 3.13 Pass-Kriterium und Nachhaltigkeitskennzahlen

### Pass-Kriterium

Eine Simulation besteht genau dann, wenn in den letzten $n = 10$ Simulationsjahren in jedem Jahr mit aktiven Rentnern beide Garantien eingehalten werden:

$$\forall t \in \{T - n, \ldots, T - 1\}: \quad \text{RR}_L(t) \ge \gamma_L - \varepsilon \;\;\wedge\;\; \text{RR}_M(t) \ge \gamma_M - \varepsilon$$

mit numerischer Toleranz $\varepsilon = 10^{-9}$.

### Nachhaltigkeitskennzahlen

Zusaetzlich zum Pass-Kriterium werden folgende Metriken erhoben:

| Kennzahl | Definition |
|----------|-----------|
| Pool-Depletionsjahr | Erstes $t$ mit $\text{Pool}(t) < 1$ EUR |
| Steady-State-Defizit | Durchschnittliches $(B_H^{\text{pool}}(t) - \text{Topup}^{\text{need}}(t))$ nach Aufbauphase ($t \ge W + R$) |
| Strukturelle Nachhaltigkeit | $\text{true}$ falls Steady-State-Defizit $\ge 0$ (ohne Backstop tragbar) |
| Kredit jemals getilgt | $\text{true}$ falls $L(t)$ nach Anstieg auf $> 1$ EUR wieder auf $< 1$ EUR faellt |
| Max. Kredit-Vermoegen-Quote | $\max_t \frac{L(t)}{A^{\text{total}}(t)}$ |

### Longevity-Kennzahlen

| Kennzahl | Definition |
|----------|-----------|
| Endbestand Longevity Pool | $\text{LongevityPool}(T-1)$ |
| Kumulative Longevity-Auszahlungen | $\sum_t \text{LongevityPaid}(t)$ |
| Kumulative Longevity-Backstop | $\sum_t \text{LongevityBackstop}(t)$ |
| Peak Longevity-Rentner | $\max_t N^{\text{long}}(t)$ |

## 3.14 Uebergangsmodell: Generationen-Anleihe

### Motivation

Der Uebergang vom Umlageverfahren (GRV) zum kapitalgedeckten System (RSSP) erzeugt eine Finanzierungsluecke: Waehrend der 47-jaehrigen Phase-in-Periode muessen sowohl die laufenden GRV-Renten (alte Ansprueche) als auch die RSSP-Kapitalaufbauten (neue Beitraege) finanziert werden. Das Uebergangsmodul quantifiziert diese Luecke und modelliert deren Finanzierung.

### Lueckenberechnung

Die jaehrliche Finanzierungsluecke $G(t)$ waechst linear waehrend der Phase-in-Periode und sinkt danach, da die freigewordenen GRV-Bundeszuschuesse zur Tilgung eingesetzt werden:

$$G(t) = \begin{cases}
G_{\max} \cdot t / W & 0 \le t < W \\
G_{\max} \cdot (1 - (t - W) / W) & W \le t < 2W \\
0 & t \ge 2W
\end{cases}$$

mit $G_{\max} = 250$ Mrd. EUR/Jahr (Spitzenluecke im Jahr $W = 47$).

### Anleihe-Dynamik

Die Luecke wird durch eine ewige Staatsanleihe finanziert, deren ausstehender Betrag $B(t)$ der folgenden Dynamik folgt:

$$B(t+1) = B(t) \cdot (1 + r^{\text{bond}}) + G(t) - \text{Tilgung}(t)$$

Die Tilgung beginnt nach Ende der Phase-in-Periode und nutzt den freigewordenen Bundeszuschuss (initial EUR 54 Mrd./Jahr, steigend auf EUR 120 Mrd./Jahr im reifen System). Optional wird ein Target2-Equity-Swap modelliert, der die Anfangsverschuldung um bis zu EUR 500 Mrd. reduziert.

### Parametrisierung

| Szenario | Realzins $r^{\text{bond}}$ | Target2-Swap | Peak Bond | Tilgung |
|---|---|---|---|---|
| Basis | 2,0% | 0 EUR | EUR 25,2 Bio. | nie |
| Optimistisch | 1,0% | EUR 500 Mrd. | EUR 8,6 Bio. | Jahr 116 |

## 3.15 Parameteruebersicht (Config D und Config E)

| Parameter | Symbol | Wert | Beschreibung |
|-----------|--------|------|--------------|
| Simulationshorizont | $T$ | 100 Jahre | |
| Eintrittsalter | $a_0$ | 20 | |
| Rentenalter | $a_R$ | 67 | |
| Beitragsjahre | $W$ | 47 | $= a_R - a_0$ |
| Annuitaetsdauer | $R$ | 20 Jahre | Alter 67--86 |
| Kohortenstaerke | $N_0$ | 831.435 | Pro Jahr bei $a_0$ |
| Low-Anteil | $s_L$ | 30% | |
| Mid-Anteil | $s_M$ | 50% | |
| High-Anteil | $s_H$ | 20% | |
| Einkommen Low | $Y_L$ | EUR 22.000 | Real, bei $a_R$ |
| Einkommen Mid | $Y_M$ | EUR 40.000 | Real, bei $a_R$ |
| Einkommen High | $Y_H$ | EUR 72.000 | $= Y_M \cdot 1{,}8$ |
| Beitrag Low | $\tau_L$ | 12% | Konto |
| Beitrag Mid | $\tau_M$ | 13% | Konto |
| Beitrag High | $\tau_H^*$ | 12,25% | Pool (optimiert) |
| Garantie Low | $\gamma_L$ | 85% | |
| Garantie Mid | $\gamma_M$ | 60% | |
| Mortalitaet 67--74 | $\sigma_1$ | 0,982 | Korrigiert Destatis |
| Mortalitaet 75--84 | $\sigma_2$ | 0,955 | |
| Mortalitaet 85--95 | $\sigma_3$ | 0,88 | |
| Mortalitaet 96+ | $\sigma_4$ | 0,72 | |
| Kreditobergrenze | $\alpha$ | 10% | Anteil Systemvermoegen |
| Tilgungsrate | $\rho$ | 50% | Anteil Ueberschuss |
| Reservejahre | $n_{\text{res}}$ | 3 | |
| Einkommensprofil | -- | deaktiviert | Flat income |
| Longevity Floor | $P^{\text{floor}}$ | EUR 10.000/Jahr | |
| Longevity Max-Alter | $a_{\max}$ | 95 | |
| Longevity Surplus-Anteil | $\lambda$ | 5% | Pool-Ueberschuss $\to$ Longevity |

**Zusaetzliche Parameter (Config E)**

| Parameter | Symbol | Wert | Beschreibung |
|-----------|--------|------|--------------|
| Solidarbeitrag High | $\tau_H^*$ | 12,75% | Pool (optimiert, +0,50 PP vs. Config D) |
| Tontine aktiviert | -- | ja | Dynamische per-capita-Verteilung |
| Tontine Cap-Multiplikator | $c_T$ | 3,0 | Max. Payout = $c_T \cdot P^{\text{floor}}$ |
| Reserve-Regel aktiviert | -- | ja | Symmetrische Skim/Inject-Regel |
| Reserve Trigger High | $r^{\text{high}}$ | 3% | Skim-Schwelle |
| Reserve Trigger Low | $r^{\text{low}}$ | 1% | Inject-Schwelle |
| Reserve Zielrendite | $r^{\text{target}}$ | 2% | Referenz fuer Excess/Shortfall |
| Reserve Skim-Fraktion | $\phi^{\text{skim}}$ | 30% | Anteil Excess $\to$ Reserve |
| Reserve Inject-Fraktion | $\phi^{\text{inject}}$ | 30% | Anteil Shortfall $\leftarrow$ Reserve |
| Reserve Sicherer Zins | $r^{\text{safe}}$ | 0,5% | Verzinsung der Reserve |
| Monte-Carlo Pfade | $N$ | 10.000 | Standard-Lauf |
| Monte-Carlo Volatilitaet | $\sigma$ | 8% | Basis-Volatilitaet |

## 3.16 Modellgrenzen und Vereinfachungen

Das v2-Modell adressiert mehrere Limitationen des v1-Modells, behaelt jedoch folgende Vereinfachungen bei:

1. **Stochastische Renditen (teilweise adressiert in Config E)**: Config D operiert deterministisch. Config E fuehrt Monte-Carlo-Simulation mit log-normalen Renditen und Regime-Switching ein (Haertung 8). Allerdings werden Korrelationsstrukturen zwischen Asset-Klassen, Fat Tails und autokorrelierte Volatilitaet (GARCH) nicht modelliert. Die Monte-Carlo-Analyse zeigt, dass bei Portfolio-Volatilitaet $\le 8\%$ eine Pass-Rate von $\ge 94\%$ erreicht wird; bei hoeherer Volatilitaet oder Regime-Switching sinkt die Rate auf 67--81%.

2. **Uebergangsphase (teilweise adressiert in Config E)**: Das Grundmodell startet als Greenfield-System. Config E ergaenzt ein Generationen-Anleihe-Modell (Abschnitt 3.14), das die Finanzierungsluecke quantifiziert. Im optimistischen Szenario (1% Realzins, EUR 500 Mrd. Target2-Swap) wird die Anleihe in Jahr 116 vollstaendig getilgt. Im Basisszenario (2% Realzins, kein Swap) ist die Anleihe nicht rueckzahlbar. Eine dynamische Mikrosimulation mit Kohortenprojektion bleibt als Forschungsbedarf bestehen.

3. **Vereinfachte Annuitaet**: Die Auszahlung erfolgt ueber eine deterministische Teilung durch verbleibende Jahre, nicht ueber versicherungsmathematisch korrekte Rentenbarwertfaktoren mit vollstaendigen Sterbetafeln.

4. **Keine Verhaltensreaktionen**: Arbeitsangebots-, Spar- und Migrationseffekte durch Einfuehrung des neuen Systems werden nicht modelliert.

5. **Aggregierte Konten**: Das Modell fuehrt ein Konto pro Kohorte und Einkommensgruppe, nicht pro Individuum. Heterogenitaet innerhalb der Gruppen wird nicht abgebildet.

6. **Konstante reale Einkommen**: In Config D wird davon ausgegangen, dass die realen Einkommen ueber die Lebensdauer konstant bleiben. Reale Lohnwachstumseffekte fehlen.

Punkt 1 der v1-Limitationen (konstante Kohortengroessen) wird durch Haertung 2 (Demografiepfade) adressiert. Die vereinfachte Annuitaet (Punkt 3) wird durch den Tontine-Effekt der Mortalitaetsmodellierung (Haertung 1) implizit verbessert. Die fehlende post-annuitaere Absicherung (Punkt 4 in v1) wird durch Haertung 5 (Longevity Pool) und deren Tontine-Erweiterung (Haertung 6) geschlossen. Die deterministische Limitation (Punkt 1) wird durch Haertung 8 (Monte-Carlo) teilweise adressiert, und die fehlende Uebergangsmodellierung (Punkt 2) durch das Generationen-Anleihe-Modul (Abschnitt 3.14).
