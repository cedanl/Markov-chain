

import pandas as pd

from data_preparation import prepare_student_data
from markov_preparation import prepare_markov_data
from markov_model import run_model


# --------------------------------------------------
# DATA INLADEN
# --------------------------------------------------

student_data = pd.read_csv(
    r"C:\Users\HMUSS\OneDrive - Albeda\Bureaublad\Npulse\Dataset28052026.csv"
)

crebo_data = pd.read_excel(
    r"C:\Users\HMUSS\OneDrive - Albeda\Bureaublad\Npulse\crebokoppeltabel.xlsx"
)


# --------------------------------------------------
# DATA VOORBEREIDEN
# --------------------------------------------------

clean_data = prepare_student_data(
    student_data,
    crebo_data
)


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

TRAIN_JAREN = range(2018, 2024)
TEST_JAREN = [2024, 2025]
PROGNOSE_JAREN = [2026]

INSTROOM_AANNAME_JAAR = 2025

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