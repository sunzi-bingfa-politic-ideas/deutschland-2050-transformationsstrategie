# RSSP — Renten-Spar- und Sicherungsprogramm

Das RSSP ist ein kapitalgedecktes Alterssicherungssystem mit individueller Kontofuehrung, einer Solidaritaetskomponente und einer ergaenzenden realwirtschaftlichen Absicherung ueber die Robotik-Infrastrukturgesellschaft (RIG).

Das Modell wurde ueber 100 Jahre, 220 Parameterkonfigurationen und mehr als 10.000 Monte-Carlo-Pfade untersucht. Es ist als Arbeitsmodell gedacht: transparent, ueberpruefbar und offen fuer Kritik.

## Worum es geht

Die gesetzliche Rentenversicherung steht vor einem langfristigen demografischen Druck. Die Zahl der Beitragszahler sinkt relativ zur Zahl der Rentner, waehrend die Lebenserwartung steigt und die Erwerbsbiografien unregelmaessiger werden.

Besonders betroffen sind Menschen mit niedrigen und mittleren Einkommen sowie Berufe, die fuer das Funktionieren der Gesellschaft zentral sind, aber oft keine ueberdurchschnittlichen Rentenansprueche aufbauen.

Das RSSP versucht, auf diese Entwicklung mit einem anderen Finanzierungsprinzip zu reagieren: nicht ausschliesslich umlagefinanziert, sondern teilweise kapitalgedeckt und langfristig abgesichert.

---

## Der Ansatz

Die Grundidee ist einfach:

- Ein Teil der Beitraege fliesst in individuelle Kapitalkonten.
- Das Kapital wird breit diversifiziert angelegt.
- Ueber die Zeit entsteht ein Vermoegensstock, der zusaetzliche Rentenleistungen traegt.
- Eine Solidaritaetskomponente sorgt dafuer, dass hohe Einkommen nicht nur fuer sich selbst sparen, sondern auch die Stabilitaet des Gesamtsystems mittragen.

Ergaenzt wird das durch die RIG, die reale Infrastruktur- und Robotikwerte als zusaetzlichen Stabilitaetsanker aufbaut.

Das Ziel ist kein radikaler Bruch mit dem bestehenden System, sondern eine strukturelle Ergaenzung, die langfristig tragfaehiger sein soll.

---

## Zentrale Ergebnisse

Unter den modellierten Annahmen zeigt das RSSP:

- einen deutlich stabileren Beitragspfad als das heutige Umlagesystem,
- hoehere Ersatzraten fuer Personen mit niedrigen und mittleren Einkommen,
- eine bessere Pufferung gegen demografische und marktbezogene Belastungen,
- und eine zusaetzliche reale Absicherung ueber Infrastrukturwerte.

Die konkreten Zahlen haengen von den Parametern ab und sind deshalb als Modellresultate zu verstehen, nicht als Garantien.

---

## Die drei Konfigurationen

Das Projekt wurde in mehreren Ausbaustufen kalibriert. Die finale Konfiguration ist nicht als endgueltige Wahrheit zu verstehen, sondern als die bisher robusteste Variante.

| | Config D | Config E | Config F |
|---|---|---|---|
| **Fokus** | Basiskalibrierung | Erweiterung mit Reserve und Monte Carlo | Erweiterung mit RIG und Equity-Swap |
| **Beitragspfad** | variabel | stabilisiert | weiter gehaertet |
| **Monte-Carlo-Ergebnis** | gut | gut | am robustesten |
| **Rolle der RIG** | noch keine | vorbereitet | integriert |
| **Dokumentation** | [CONFIG_D.md](CONFIG_D.md) | [CONFIG_E.md](CONFIG_E.md) | [CONFIG_F.md](CONFIG_F.md) |

**Config F** ist die derzeit vollstaendigste Fassung. Sie kombiniert:

- individuelle Konten,
- eine Solidaritaetskomponente,
- reale Absicherung ueber Infrastrukturwerte,
- und mehrere Stresstests fuer politische und oekonomische Schocks.

---

## Was das Projekt praktisch enthaelt

```
Rentenreform/
├── src/                        # Simulationscode (Python)
├── params/                     # YAML-Parameterdateien
├── out/                        # Auswertungen und Zusammenfassungen
├── paper/                      # Vollstaendige Ausarbeitung (6 Teile)
├── CONFIG_D.md
├── CONFIG_E.md
├── CONFIG_F.md
└── LICENSE
```

Fuer eine schnelle Orientierung gibt es:

- eine [Executive Summary](out/executive_summary.md),
- eine [FAQ fuer kritische Rueckfragen](out/faq_kritiker.md),
- und die [technische Dokumentation der finalen Konfiguration](CONFIG_F.md).

---

## Installation und Schnellstart

```bash
pip install -r requirements.txt

# Config F: Monte Carlo mit finalen RIG-Parametern (10.000 Pfade)
python src/monte_carlo.py --config params/config_f.yaml \
  --tau_high 0.1225 --n_paths 10000 --volatility 0.08 \
  --json out/mc_config_f_vol8.json
```

Abhaengigkeiten: `pyyaml >= 5.4`, `numpy >= 1.20`. Python 3.8+.

---

## Paper

Das vollstaendige Paper ist in `paper/` als Markdown verfuegbar:

- **Teil 1**: Einleitung und Problemstellung
- **Teil 2**: Modellbeschreibung
- **Teil 3**: Ergebnisse und stochastische Validierung
- **Teil 4**: Politikanalyse (Arbeitsmarkt, Wohneigentum, Gender, Verwaltungskosten)
- **Teil 5**: Vergleich und Uebergangsstrategie
- **Teil 6**: Strategie, Limitationen und Fazit

---

## Fuer wen das gedacht ist

Dieses Modul richtet sich an mehrere Zielgruppen:

- an Leser die den Grundgedanken verstehen wollen,
- an Kritiker die Annahmen und Zahlen pruefen moechten,
- und an Menschen die das Modell technisch nachvollziehen oder weiterentwickeln wollen.

---

## Grenzen und Risiken

Das Modell ist bewusst offen ueber seine Schwaechen:

- Es setzt politische Kontinuitaet ueber viele Jahre voraus.
- Es bleibt empfindlich gegenueber Kapitalmarktrisiken, vor allem in der Aufbauphase.
- Es enthaelt Annahmen ueber Stabilitaet, Renditen und institutionelle Absicherung, die nicht garantiert sind.
- Es ersetzt nicht die politische Frage, ob eine solche Reform in einer Demokratie durchsetzbar ist.

Das RSSP ist daher kein Versprechen, sondern ein strukturierter Vorschlag mit nachvollziehbaren Annahmen.

---

## Einordnung

Das RSSP ist das finanzielle Kernmodul des Gesamtprojekts. Wenn es funktioniert, kann es mehrere andere Bereiche stuetzen. Wenn es scheitert, verliert das Gesamtmodell einen wichtigen Teil seiner Tragfaehigkeit.

Gerade deshalb ist dieses Modul so zentral — und gerade deshalb muss es besonders sauber, ehrlich und ueberpruefbar beschrieben sein.

---

## Methodik

- Modellierung in Python (ausfuehrbarer Code im Repository)
- Monte-Carlo-Simulationen (bis 10.000 Pfade)
- Sensitivitaetsanalysen (220 Konfigurationen)
- Adversariale Stresstests (5 Szenarien)
- Dokumentierte Annahmen und Falsifizierungskriterien

Die Ergebnisse sind reproduzierbar.

---

## Offenheit

Kritik, Gegenargumente und bessere Modelle sind ausdruecklich willkommen.

Dieses Dokument versteht sich als Beitrag zu einer ernsthaften Diskussion, nicht als abschliessende Antwort.

---

*Maerz 2026*

---

# RSSP — Retirement Savings and Security Programme

A capital-funded pension system with tiered purchasing-power guarantees, a Robotics Infrastructure Company (RIG), and an explicit redistribution component.

Validated over 100 years, 220 parameter configurations, and 10,000+ Monte Carlo paths. Open source, reproducible, and open to critique.

See above for full documentation (in German).

## Quick Start

```bash
pip install -r requirements.txt
python src/monte_carlo.py --config params/config_f.yaml \
  --tau_high 0.1225 --n_paths 10000 --volatility 0.08 \
  --json out/mc_config_f_vol8.json
```

## License

MIT
