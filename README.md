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
