from pathlib import Path

import pandas as pd

from data_preparation import load_synthetic_data, prepare_student_data
from markov_model import run_model
from markov_preparation import prepare_markov_data

# --------------------------------------------------
# CONFIGURATIE
# --------------------------------------------------

# "synthetisch" of "bronexport"
DATA_BRON = "synthetisch"

SYNTHETISCH_PAD = Path(__file__).parent / "synthetisch.csv"
BRONEXPORT_PAD = Path(__file__).parent / "voorbeeld_bronexport.csv"


# --------------------------------------------------
# DATA INLADEN
# --------------------------------------------------

if DATA_BRON == "bronexport":
    clean_data = prepare_student_data(pd.read_csv(BRONEXPORT_PAD))
else:
    clean_data = load_synthetic_data(SYNTHETISCH_PAD)


# --------------------------------------------------
# MARKOV DATA VOORBEREIDEN
# --------------------------------------------------

markov_data = prepare_markov_data(
    clean_data
)


# Resultaat bekijken
print(markov_data.head())


# --------------------------------------------------
# MARKOV MODEL
# --------------------------------------------------

# De synthetische data loopt van 2015 t/m 2023.
# Pas de jaren aan bij een bronexport.
#
# Het laatste trainjaar is het startjaar: de voorspelling begint
# bij de werkelijke aantallen van dat jaar. De overgangskansen
# komen uit de trainjaren daarvoor (hier 2016 t/m 2020, dus de
# overgangen tot en met 2020 -> 2021). Testjaren zijn jaren met
# bekende uitkomst; die vergelijken we met de voorspelling om de
# foutmarge te bepalen. Prognosejaren liggen in de toekomst.
TRAIN_JAREN = range(2016, 2022)
TEST_JAREN = [2022, 2023]
PROGNOSE_JAREN = [2024]

INSTROOM_AANNAME_JAAR = 2023

MODELLEN = [
    'regressie',
    'exponential_smoothing',
    'stationair'
]


voorspellingen, foutmarges, model_matrices = run_model(
    df=markov_data,
    train_jaren=TRAIN_JAREN,
    test_jaren=TEST_JAREN,
    prognose_jaren=PROGNOSE_JAREN,
    instroom_aanname_jaar=INSTROOM_AANNAME_JAAR,
    modellen=MODELLEN
)


# --------------------------------------------------
# RESULTATEN BEKIJKEN
# --------------------------------------------------

for modelnaam in MODELLEN:

    print("\n" + "=" * 60)
    print(f"MODEL: {modelnaam}")
    print("=" * 60)

    for jaar, voorspelling in voorspellingen[modelnaam].items():

        print(f"\nVoorspelling {jaar}")
        print(voorspelling.round(0))

        if jaar in foutmarges[modelnaam]:

            print(f"\nFoutmarge {jaar}")
            print(foutmarges[modelnaam][jaar])