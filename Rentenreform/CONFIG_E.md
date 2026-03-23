# Config E — Erweiterte Konfiguration

## Zusammenfassung

Config E erweitert Config D um vier strukturelle Module:

| Modul | Datei | Kernparameter |
|-------|-------|---------------|
| Tontine-Longevity | `model.py` | `tontine_enabled=True`, `cap_multiple=3.0` |
| Symmetrische Reserve | `model.py` | `reserve_rule_enabled=True`, triggers 1%/3% |
| Monte Carlo | `monte_carlo.py` | N=10.000, vol=8%, log-normal + regime |
| Generationen-Anleihe | `transition.py` | 100-Jahr Bond, Target2-Swap |

**Optimaler Beitragssatz:** `tau_high = 13.00%` (+0.75pp vs Config D)
Effektiver Gesamtbeitragssatz: ~13.4% (vs GRV 18.6%)

## Kernergebnisse

### Deterministische Szenarien (100% Pass bei tau_high=12.75%)

| Szenario | Low | Mid | LP/capita |
|----------|-----|-----|-----------|
| base 1.7% | 85.0% | 73.1% | EUR 30.000 |
| realistic 2.5% | 90.3% | 97.8% | EUR 30.000 |
| low 1.0% | 85.0% | 60.0% | EUR 30.000 |
| hard 0.5% | 85.0% | 60.0% | EUR 30.000 |
| flat 0.0% | 85.0% | 60.0% | EUR 29.864 |

### Monte Carlo (10.000 Pfade, tau_high=12.75%)

| Volatilitaet | Pass-Rate | Low P5 | Mid P5 | Pool-Depletion |
|-------------|-----------|--------|--------|----------------|
| 5% | 100.0% | 85.0% | 60.0% | 3.0% |
| 8% | 94.0% | 70.4% | 53.4% | 14.0% |
| 10% | 88.5% | 56.5% | 44.9% | 25.0% |
| 15% | 67.1% | 34.4% | 27.1% | 51.3% |

**Regime-Switching** (Bull 6%/Bear -2%, Markov): 80.8% Pass bei 8% vol.

### Kritische Schwelle

**Portfolio-Volatilitaet <= 8% erforderlich fuer >=94% Pass-Rate.**
Implikation: Anlagemandat muss ausgewogene Allokation vorschreiben
(~40-60% Aktien, 40-60% Anleihen/Immobilien).

Bei 5% Volatilitaet: 100% Pass-Rate (rein konservative Allokation).

### Fundamentale Grenze kapitalgedeckter Systeme

Auch bei tau_high=20% erreicht das System unter Regime-Switching nur
~90% Pass-Rate. Die verbleibenden ~5-10% sind Pfade mit anhaltend
negativen Realrenditen (>5 Jahre Bear-Markt), die kein kapitalgedecktes
System ueberstehen kann. Moegliche Ergaenzungen:
- Lifecycle-Investing (altersabhaengige Risikoreduktion)
- Dynamische Garantieanpassung bei Extremszenarien
- Hybridkomponente mit teilweisem Umlageverfahren

## Modul-Details

### 1. Tontine-Longevity-Pool

**Mechanismus:** Statt statischem Floor (EUR 10.000/Jahr) werden
Longevity-Pool-Mittel pro Kopf unter den Ueberlebenden verteilt.
Nachhaltigkeits-Constraint: Bonus nur wenn Pool > kumulierter
Floor-Bedarf aller verbleibenden Longevity-Rentner.

**Formel:**
```
if pool > total_remaining_floor_need:
    bonus = (pool - floor_need) / n_survivors / avg_remaining_years
    payout = min(floor + bonus, floor * cap_multiple)
else:
    payout = floor  (Fallback)
```

**Backstop:** Staat garantiert nur den Floor (EUR 10.000), nicht
den Tontine-Aufschlag. Aufschlag ist "best effort" aus Pool-Mitteln.

**Ergebnis:** Per-capita steigt von EUR 10.000 auf EUR 30.000 (=3x Cap)
bei positiven Renditen. Bei 0% Rendite: EUR 29.864 (knapp unter Cap).

### 2. Symmetrische Reserve-Regel

**Mechanismus:** Antizyklischer Puffer fuer den Garantie-Pool:
- r > 3% (Trigger High): Ueberschuss-Wachstum → Reserve (30% Skim)
- r < 1% (Trigger Low): Reserve → Pool (30% Inject)
- Reserve verdient 0.5% Realrendite (sicherer Zins)

**Wirkung:** Glaettet Pool-Volatilitaet, reduziert Sequenzrisiko.
Peak Reserve (Median): EUR 203 Mrd. Sichtbar vor allem in MC-Laeufen
mit stochastischen Renditen.

### 3. Monte Carlo Simulation

**Architektur:**
- Log-normal Renditen: E[r] kalibriert auf Ziel, vol einstellbar
- Regime-Switching: 2-Zustand Markov (Bull/Bear) mit Transitionen
- Parallelisierung: multiprocessing.Pool ueber alle CPU-Kerne
- Performance: 10.000 Pfade in 4.2s (16 Kerne, Ryzen 5700X3D)

**Aufruf:**
```bash
python src/monte_carlo.py --config params/config_e.yaml \
    --tau_high 0.1275 --n_paths 10000 --volatility 0.08 \
    --json out/mc_config_e_10k.json

# Mit Regime-Switching:
python src/monte_carlo.py --config params/config_e.yaml \
    --tau_high 0.1275 --n_paths 1000 --regime \
    --json out/mc_config_e_regime.json
```

### 4. Generationen-Anleihe (Uebergangsfinanzierung)

**Problem:** 47-Jahre Uebergangsperiode von GRV zu RSSP erzeugt
Finanzierungsluecke (alte GRV-Ansprueche + neue RSSP-Aufbau).

**Loesung:** 100-jaehrige Staatsanleihe + Target2-Equity-Swap.

| Parameter | Basis | Optimistisch |
|-----------|-------|-------------|
| Realzins | 2.0% | 1.0% |
| Target2-Swap | 0 | EUR 500 Mrd |
| Peak Bond | EUR 25.2 Bio | EUR 8.6 Bio |
| Tilgung | nie | Jahr 116 |

**Detailergebnis:** Bei 1% Realzins + EUR 500 Mrd Target2-Mobilisierung
wird die Anleihe in Jahr 116 vollstaendig getilgt. Gesamtzinskosten:
EUR 4.7 Bio. Bedingung: Freigewordener Bundeszuschuss (bis EUR 100 Mrd/yr)
wird vollstaendig zur Tilgung eingesetzt.

## Kostenuebersicht

| Konfiguration | tau_high | Eff. Gesamtbeitrag | Delta zu GRV |
|---------------|----------|-------------------|--------------|
| Config D | 12.25% | ~12.6% | -6.0 pp |
| Config E | 13.00% | ~13.4% | -5.2 pp |
| GRV (aktuell) | — | 18.6% | Referenz |

**Kosten der Config-E-Erweiterungen:** +0.75 pp Solidarbeitrag (High).
Dafuer: 3x Longevity-Payout, Reserve-Puffer, stochastische Absicherung.

## Dateien

```
params/config_e.yaml       Config E Parameter
src/model.py               Hauptmodell (erweitert um Tontine + Reserve)
src/monte_carlo.py         Monte Carlo Wrapper (multiprocessing)
src/transition.py          Generationen-Anleihe Rechner
out/mc_config_e_10k.json   MC Ergebnis (10k Pfade, 8% vol)
out/mc_config_e_vol15.json MC Ergebnis (1k Pfade, 15% vol)
out/mc_config_e_regime.json MC Ergebnis (1k Pfade, Regime-Switching)
out/transition_base.json   Uebergangsrechnung (Basis)
out/transition_optimistic.json Uebergangsrechnung (Optimistisch)
```
