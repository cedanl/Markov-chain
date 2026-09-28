# Modellen

## Model 1: Stationary Markov Chain

* Historische overgangskansen worden verondersteld constant te blijven over de tijd.
* Eenvoudig en transparant basismodel.
* Geschikt wanneer er geen duidelijke veranderingen of trends zichtbaar zijn in de doorstroompatronen.

## Model 2: Non-Stationary Markov Chain + Lineaire Regressie

* Overgangskansen worden voorspeld op basis van een lineaire trend in historische data.
* Houdt rekening met geleidelijke veranderingen door de tijd.
* Geschikt wanneer doorstroom-, uitstroom- of instroompercentages een duidelijke stijgende of dalende trend vertonen.

## Model 3: Non-Stationary Markov Chain + Exponential Smoothing

* Recente jaren krijgen meer gewicht dan oudere observaties.
* Reageert sneller op nieuwe ontwikkelingen en veranderingen in patronen.
* Geschikt wanneer recente ontwikkelingen relevanter zijn dan historische trends op lange termijn.

# Lokaal draaien

Vereist: [uv](https://docs.astral.sh/uv/).

```bash
uv sync && uv run python main.py
```

Het script draait standaard op `synthetisch.csv`. Die dataset bevat per student per studiejaar: `id`, `Studiejaar`, `niveau`, `instroom`, `doorstroom`, `uitstroom` en `jaar_nummer`. Instroom, doorstroom en uitstroom zijn al bepaald, dus de stap `prepare_student_data` wordt overgeslagen.

De synthetische data loopt van 2015 t/m 2023. Het model traint op 2016 t/m 2021, test op 2022 en 2023 en voorspelt 2024. Pas de jaren aan in `main.py`.

## Draaien op een bronexport

Zet in `main.py` `DATA_BRON = "bronexport"` en `BRONEXPORT_PAD` naar de export van de instelling. Pas ook de jaren aan. `prepare_student_data` bepaalt dan zelf instroom, doorstroom en uitstroom.

De export is een CSV met één regel per inschrijving per studiejaar. Deze kolommen zijn nodig; andere kolommen worden genegeerd:

| Kolom | Inhoud |
|---|---|
| `Studiejaar` | Studiejaar, bijvoorbeeld `2022-2023`. Alleen de eerste vier tekens worden gebruikt. |
| `Deelnemernummer` | Studentnummer |
| `Volgnummer` | Volgnummer van de inschrijving |
| `begindatum` | Begindatum inschrijving (`JJJJ-MM-DD`) |
| `einddatum` | Einddatum inschrijving (`JJJJ-MM-DD`), leeg als de inschrijving loopt |
| `crebo` | Crebocode. Regels met `99999` vallen weg. |
| `niveau` | `Niveau1` t/m `Niveau4` |
| `Cluster` | Cluster. Regels met `Cluster Techniek` vallen weg. |

Een student telt mee in een studiejaar als de inschrijving loopt op 1 oktober. `voorbeeld_bronexport.csv` is een klein nepbestand in dit formaat.

Tests draaien: `uv run pytest`.
