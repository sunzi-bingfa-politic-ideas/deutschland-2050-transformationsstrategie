# RSSP — Zusammenfassung

## Ausgangslage

Die gesetzliche Rentenversicherung (GRV) steht unter zunehmendem demografischem Druck. Der Altenquotient steigt von 37% (2024) auf voraussichtlich 55% (2050) — weniger Beitragszahler finanzieren mehr Rentner. Das fuehrt entweder zu steigenden Beitraegen oder sinkenden Leistungen. Besonders betroffen sind Berufe mit niedrigen und mittleren Einkommen: Pflege, Handwerk, Erziehung.

## Der Vorschlag

Das RSSP ergaenzt das bestehende System um eine kapitalgedeckte Komponente:

1. **Individuelle Kapitalkonten.** Beitraege werden nicht sofort umverteilt, sondern auf persoenlichen Konten langfristig angelegt. Ueber ein Berufsleben entsteht ein individueller Vermoegensstock.

2. **Gestufte Absicherung.** Das Modell sieht fuer die unteren 30% der Einkommen eine Garantie-Ersatzrate von 85% vor, fuer mittlere Einkommen 60%. Diese Garantien werden durch die Solidaritaetskomponente und einen staatlichen Backstop abgesichert.

3. **Solidaritaetskomponente.** Bezieher hoher Einkommen zahlen einen Beitrag ohne eigenen Rentenanspruch — aber zu einem niedrigeren Satz als im heutigen System. Ein Teil dieses Beitrags fliesst in ein Infrastruktur-Portfolio (RIG), das reale Vermoegenswerte aufbaut.

4. **Wohnraum-Effekt.** Das aufgebaute Kapital kann — ohne Entnahme — als Sicherheit fuer Immobilienkredite dienen. Das Modell schaetzt, dass dadurch mehrere Millionen Haushalte erstmals Zugang zu Wohneigentum erhalten koennten.

## Zentrale Modellergebnisse

| Kennzahl | GRV (aktuell) | RSSP (Modell) | Anmerkung |
|----------|--------------|---------------|-----------|
| Effektiver Beitragssatz | 18,6% (steigend) | 12,6–17% | Abhaengig vom Einkommensprofil |
| Ersatzrate Geringverdiener | ~48% (sinkend) | 85% (Garantie) | Modellresultat, nicht Versprechen |
| Ersatzrate mittleres Einkommen | ~48% (sinkend) | 60% (Garantie) | Abhaengig von Marktentwicklung |

**Zur Beitragsspanne:** Der niedrigere Satz (12,6%) gilt fuer Berufe mit stabilem Einkommensverlauf (Pflege, Handwerk, Einzelhandel). Fuer Berufe mit steilem Karriereverlauf (Akademiker, Management) liegt der Satz hoeher, bis maximal 17%. Auch das obere Ende liegt unter dem heutigen GRV-Satz.

## Belastbarkeit

Das Modell wurde ueber 100 Jahre, 220 Parameterkonfigurationen und mehr als 10.000 stochastische Simulationspfade getestet:

| Szenario | Ergebnis |
|----------|----------|
| Standardvolatilitaet (8%) | 91–97% der Pfade bestehen den Garantietest |
| Markteinbruch mit anschliessender Erholung | Bestanden |
| Anhaltende Niedrigrendite (0% real, 10 Jahre) | Bestanden |
| Null Prozent Rendite ueber 100 Jahre | Bestanden — erfordert staatliche Stuetzung (gedeckelt auf 10% der Systemassets) |
| 5 adversariale Stresstests | 4 von 5 bei >90% Erfolgsrate; der fuenfte (gleichzeitiger Ausfall mehrerer Annahmen) trifft jedes kapitalgedeckte System |

Die stochastische Simulation zeigt, dass das System unter realistischen Bedingungen robust ist — aber nicht risikolos. Insbesondere die Aufbauphase (erste 10–15 Jahre) ist gegenueber Marktvolatilitaet empfindlicher als der Langfristbetrieb.

## Was sich fuer verschiedene Gruppen aendert

| Gruppe | Beitragsentwicklung | Rentenentwicklung |
|--------|--------------------|--------------------|
| Geringverdiener (Pflege, Handwerk) | Sinkt | Steigt deutlich (Garantie 85%) |
| Mittleres Einkommen | Sinkt | Steigt moderat (Garantie 60%) |
| Hohes Einkommen | Sinkt um bis zu 34% | Kein eigener Rentenanspruch; Infrastruktur-Zertifikate |
| Arbeitgeber | Entlastung durch niedrigeren Gesamtbeitrag | — |

## Grenzen

- Das Modell setzt stabile institutionelle Rahmenbedingungen voraus.
- Die Garantien werden durch den Kapitalstock und einen staatlichen Backstop gedeckt — bei dauerhaft negativen Realrenditen waere eine oeffentliche Stuetzung noetig.
- Die konkreten Ersatzraten sind Modellergebnisse unter bestimmten Annahmen, keine politischen Zusagen.
- Ob und wie ein solches System politisch eingefuehrt werden kann, ist eine offene Frage, die das Modell nicht beantwortet.

---

Die vollstaendige technische Dokumentation findet sich in [CONFIG_F.md](../CONFIG_F.md). Das ausfuehrliche Paper in `paper/`.
