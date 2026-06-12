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
