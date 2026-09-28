import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing


# ============================================================
# STATUSSEN
# ============================================================

STATUSSEN = [
    'Niveau1_jaar_1_nieuw',
    'Niveau1_jaar_1',
    'Niveau1_jaar_2',
    'Niveau1_jaar_>2',

    'Niveau2_jaar_1_nieuw',
    'Niveau2_jaar_1',
    'Niveau2_jaar_2',
    'Niveau2_jaar_>2',

    'Niveau3_jaar_1_nieuw',
    'Niveau3_jaar_1',
    'Niveau3_jaar_2',
    'Niveau3_jaar_3',
    'Niveau3_jaar_>3',

    'Niveau4_jaar_1_nieuw',
    'Niveau4_jaar_1',
    'Niveau4_jaar_2',
    'Niveau4_jaar_3',
    'Niveau4_jaar_4',
    'Niveau4_jaar_5',
    'Niveau4_jaar_>5',

    'uitstroom'
]


NIEUWE_STATUSSEN = [
    'Niveau1_jaar_1_nieuw',
    'Niveau2_jaar_1_nieuw',
    'Niveau3_jaar_1_nieuw',
    'Niveau4_jaar_1_nieuw'
]


# ============================================================
# INPUT CONTROLEREN
# ============================================================

def controleer_data(df):

    verplichte_kolommen = {
        'studiejaar',
        'markov_status',
        'volgende_markov_status'
    }

    ontbrekend = verplichte_kolommen - set(df.columns)

    if ontbrekend:
        raise ValueError(
            f"Ontbrekende kolommen: {ontbrekend}"
        )


# ============================================================
# OVERGANGSMATRICES PER JAAR
# ============================================================

def maak_jaar_matrices(df, jaren):

    matrices = {}

    for jaar in jaren:

        jaar_data = df[
            df['studiejaar'] == jaar
        ]

        aantallen = pd.crosstab(
            jaar_data['markov_status'],
            jaar_data['volgende_markov_status']
        )

        aantallen = aantallen.reindex(
            index=STATUSSEN,
            columns=STATUSSEN,
            fill_value=0
        )

        matrix = aantallen.div(
            aantallen.sum(axis=1),
            axis=0
        ).fillna(0)

        # Uitstroom is absorberend
        matrix.loc['uitstroom', :] = 0
        matrix.loc['uitstroom', 'uitstroom'] = 1

        matrices[jaar] = matrix

    return matrices


# ============================================================
# STATIONAIR MODEL
# ============================================================

def maak_stationaire_matrix(matrices):

    if not matrices:
        raise ValueError(
            "Geen overgangsmatrices beschikbaar."
        )

    matrix = sum(
        matrices.values()
    ) / len(matrices)

    matrix.loc['uitstroom', :] = 0
    matrix.loc['uitstroom', 'uitstroom'] = 1

    matrix = matrix.div(
        matrix.sum(axis=1),
        axis=0
    ).fillna(0)

    return matrix


# ============================================================
# REGRESSIE EN EXPONENTIAL SMOOTHING
# ============================================================

def voorspel_overgangskansen(matrices):

    jaren = sorted(matrices)

    regressie = {}
    smoothing = {}

    for huidige_status in STATUSSEN:

        if huidige_status == 'uitstroom':
            continue

        for volgende_status in STATUSSEN:

            overgang = (
                huidige_status,
                volgende_status
            )

            kansen = np.array([
                matrices[jaar].loc[
                    huidige_status,
                    volgende_status
                ]
                for jaar in jaren
            ])

            # Te weinig informatie
            if len(kansen) < 3 or kansen.sum() <= 0.01:

                regressie[overgang] = 0
                smoothing[overgang] = 0

                continue

            x = np.arange(
                len(kansen)
            ).reshape(-1, 1)

            # ----------------------------
            # Lineaire regressie
            # ----------------------------

            try:

                model = LinearRegression()

                model.fit(
                    x,
                    kansen
                )

                regressie[overgang] = model.predict(
                    [[len(kansen)]]
                )[0]

            except Exception:

                regressie[overgang] = 0

            # ----------------------------
            # Exponential smoothing
            # ----------------------------

            try:

                trend = (
                    'mul'
                    if np.all(kansen > 0)
                    else 'add'
                )

                model = ExponentialSmoothing(
                    kansen,
                    trend=trend
                ).fit(
                    optimized=True
                )

                smoothing[overgang] = (
                    model.forecast(1)[0]
                )

            except Exception:

                smoothing[overgang] = 0

    return regressie, smoothing


# ============================================================
# VOORSPELDE OVERGANGSMATRIX
# ============================================================

def maak_matrix(voorspelde_kansen):

    matrix = pd.DataFrame(
        0.0,
        index=STATUSSEN,
        columns=STATUSSEN
    )

    for overgang, kans in voorspelde_kansen.items():

        huidige_status, volgende_status = overgang

        matrix.loc[
            huidige_status,
            volgende_status
        ] = max(0, kans)

    # Uitstroom absorberend
    matrix.loc['uitstroom', :] = 0
    matrix.loc['uitstroom', 'uitstroom'] = 1

    # Rijen optellen tot 1
    matrix = matrix.div(
        matrix.sum(axis=1),
        axis=0
    ).fillna(0)

    return matrix


# ============================================================
# ALLE MODELLEN MAKEN
# ============================================================

def maak_modellen(df, train_jaren):

    jaar_matrices = maak_jaar_matrices(
        df,
        train_jaren
    )

    regressie, smoothing = (
        voorspel_overgangskansen(
            jaar_matrices
        )
    )

    modellen = {
        'regressie': maak_matrix(
            regressie
        ),

        'exponential_smoothing': maak_matrix(
            smoothing
        ),

        'stationair': maak_stationaire_matrix(
            jaar_matrices
        )
    }

    return modellen


# ============================================================
# STARTVECTOR
# ============================================================

def maak_startvector(df, jaar):

    vector = (
        df.loc[
            df['studiejaar'] == jaar,
            'markov_status'
        ]
        .value_counts()
        .reindex(
            STATUSSEN,
            fill_value=0
        )
        .astype(float)
    )

    # Uitstroom hoort niet bij actieve studenten
    vector.loc['uitstroom'] = 0

    return vector


# ============================================================
# INSTROOMVECTOR
# ============================================================

def maak_instroomvector(df, jaar):

    instroom = df.loc[
        (df['studiejaar'] == jaar)
        & df['markov_status'].isin(
            NIEUWE_STATUSSEN
        ),
        'markov_status'
    ]

    vector = (
        instroom
        .value_counts()
        .reindex(
            STATUSSEN,
            fill_value=0
        )
        .astype(float)
    )

    return vector


# ============================================================
# ÉÉN JAAR VOORSPELLEN
# ============================================================

def voorspel_jaar(
    startvector,
    matrix,
    instroomvector
):

    startvector = startvector.copy()

    startvector.loc['uitstroom'] = 0

    # Markov-berekening
    voorspelling = (
        startvector.values
        @ matrix.values
    )

    voorspelling = pd.Series(
        voorspelling,
        index=STATUSSEN
    )

    # Nieuwe instroom apart toevoegen
    voorspelling.loc[NIEUWE_STATUSSEN] = (
        instroomvector.loc[NIEUWE_STATUSSEN]
    )

    return voorspelling


# ============================================================
# ECHTE AANTALLEN
# ============================================================

def echte_aantallen(df, jaar):

    jaar_data = df[
        df['studiejaar'] == jaar
    ]

    aantallen = (
        jaar_data['markov_status']
        .value_counts()
        .reindex(
            STATUSSEN,
            fill_value=0
        )
        .astype(float)
    )

    # Uitstroom komt uit de volgende Markov-status
    aantallen.loc['uitstroom'] = (
        jaar_data[
            'volgende_markov_status'
        ]
        .eq('uitstroom')
        .sum()
    )

    return aantallen


# ============================================================
# FOUTMARGE
# ============================================================

def bereken_fout(
    df,
    voorspelling,
    jaar
):

    echt = echte_aantallen(
        df,
        jaar
    )

    resultaat = pd.DataFrame({
        'echt': echt,
        'voorspeld': voorspelling
    })

    resultaat['verschil'] = (
        resultaat['voorspeld']
        - resultaat['echt']
    )

    resultaat['absolute_fout'] = (
        resultaat['verschil'].abs()
    )

    resultaat['foutpercentage'] = (
        resultaat['verschil']
        / resultaat['echt'].replace(
            0,
            np.nan
        )
        * 100
    )

    return resultaat.round(2)


# ============================================================
# COMPLETE MODEL
# ============================================================

def run_model(
    df,
    train_jaren,
    test_jaren,
    prognose_jaren,
    instroom_aanname_jaar,
    modellen=None
):

    controleer_data(df)

    if modellen is None:

        modellen = [
            'regressie',
            'exponential_smoothing',
            'stationair'
        ]

    startjaar = max(train_jaren)

    # Overgangsmatrices maken. Het startjaar zelf niet meenemen:
    # de matrix van dat jaar bevat de overgang naar het eerste
    # testjaar, en die moet het model juist voorspellen.
    model_matrices = maak_modellen(
        df,
        [jaar for jaar in train_jaren if jaar < startjaar]
    )

    voorspel_jaren = (
        list(test_jaren)
        + list(prognose_jaren)
    )

    beschikbare_jaren = set(
        df['studiejaar'].unique()
    )

    voorspellingen = {}
    foutmarges = {}

    # --------------------------------------------------------
    # Per model voorspellen
    # --------------------------------------------------------

    for modelnaam in modellen:

        matrix = model_matrices[
            modelnaam
        ]

        vorige_vector = maak_startvector(
            df,
            startjaar
        )

        voorspellingen[modelnaam] = {}
        foutmarges[modelnaam] = {}

        # ----------------------------------------------------
        # Jaar voor jaar voorspellen
        # ----------------------------------------------------

        for jaar in voorspel_jaren:

            # Werkelijke instroom gebruiken
            # wanneer deze beschikbaar is
            if (
                jaar in beschikbare_jaren
                and jaar not in prognose_jaren
            ):

                instroom_jaar = jaar

            else:

                instroom_jaar = (
                    instroom_aanname_jaar
                )

            instroomvector = maak_instroomvector(
                df,
                instroom_jaar
            )

            voorspelling = voorspel_jaar(
                vorige_vector,
                matrix,
                instroomvector
            )

            voorspellingen[
                modelnaam
            ][jaar] = voorspelling

            # Foutmarge alleen voor testjaren
            if jaar in test_jaren:

                foutmarges[
                    modelnaam
                ][jaar] = bereken_fout(
                    df,
                    voorspelling,
                    jaar
                )

            # Voorspelling wordt start voor volgend jaar
            vorige_vector = voorspelling

    return (
        voorspellingen,
        foutmarges,
        model_matrices
    )