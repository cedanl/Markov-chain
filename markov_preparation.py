import numpy as np


def prepare_markov_data(df):
    """
    Bereidt de statussen voor die later
    gebruikt worden in de Markov Chain.
    """

    df = df.copy()

    # Sorteren
    df = (
        df
        .sort_values(['student_id', 'studiejaar'])
        .drop_duplicates(
            subset=['student_id', 'studiejaar'],
            keep='last'
        )
    )

    # Vorig niveau
    df['vorig_niveau'] = (
        df.groupby('student_id')['niveau']
        .shift(1)
    )

    # Nieuw traject bij instroom of verandering van niveau
    df['nieuw_traject'] = (
        df['instroom'].eq(1) |
        (
            df['vorig_niveau'].notna() &
            df['niveau'].ne(df['vorig_niveau'])
        )
    )

    # Trajectnummer
    df['traject_id'] = (
        df.groupby('student_id')['nieuw_traject']
        .cumsum()
    )

    # Jaar binnen traject
    df['jaar_in_traject'] = (
        df
        .groupby(['student_id', 'traject_id'])
        .cumcount()
        .add(1)
    )

    # Volgende observatie
    df['volgend_trajectjaar'] = (
        df.groupby('student_id')['jaar_in_traject']
        .shift(-1)
    )

    df['volgend_niveau'] = (
        df.groupby('student_id')['niveau']
        .shift(-1)
    )

    # Huidige status
    df['status'] = np.select(
        [
            df['jaar_in_traject'].eq(1),
            df['jaar_in_traject'].eq(2),
            df['jaar_in_traject'].eq(3),
            df['jaar_in_traject'].eq(4),
            df['jaar_in_traject'].eq(5),
            df['jaar_in_traject'].gt(5)
        ],
        [
            'jaar_1',
            'jaar_2',
            'jaar_3',
            'jaar_4',
            'jaar_5',
            'jaar_>5'
        ],
        default='onbekend'
    )

    # Volgende status
    next_status = np.array([
        'uitstroom',
        None,
        'jaar_1',
        'jaar_1',
        'jaar_2',
        'jaar_3',
        'jaar_4',
        'jaar_5',
        'jaar_>5'
    ], dtype=object)

    df['volgende_status'] = np.select(
        [
            df['uitstroom'].eq(1),

            df['volgend_niveau'].isna(),

            df['volgend_niveau'].ne(df['niveau']),

            df['volgend_trajectjaar'].eq(1),
            df['volgend_trajectjaar'].eq(2),
            df['volgend_trajectjaar'].eq(3),
            df['volgend_trajectjaar'].eq(4),
            df['volgend_trajectjaar'].eq(5),
            df['volgend_trajectjaar'].gt(5)
        ],
        next_status,
        default='onbekend'
    )

    # Markov-status
    df['markov_status'] = (
        df['niveau'].astype(str)
        + '_'
        + df['status']
    )

    # Nieuwe instroom herkenbaar maken
    df.loc[
        df['instroom'].eq(1),
        'markov_status'
    ] += '_nieuw'

    # Volgende Markov-status
    df['volgende_markov_status'] = np.where(
        df['volgende_status'].isna() |
        df['volgende_status'].eq('uitstroom'),

        df['volgende_status'],

        df['volgend_niveau'].astype(str)
        + '_'
        + df['volgende_status'].astype(str)
    )

    # Lange trajecten samenvoegen
    jaar_grenzen = {
        'Niveau1': 2,
        'Niveau2': 2,
        'Niveau3': 3
    }

    for niveau, grens in jaar_grenzen.items():

        # Huidige status
        huidig = (
            df['niveau'].eq(niveau) &
            df['jaar_in_traject'].gt(grens)
        )

        df.loc[
            huidig,
            'markov_status'
        ] = f'{niveau}_jaar_>{grens}'

        # Volgende status
        volgend = (
            df['volgend_niveau'].eq(niveau) &
            df['volgend_trajectjaar'].gt(grens)
        )

        df.loc[
            volgend,
            'volgende_markov_status'
        ] = f'{niveau}_jaar_>{grens}'

    return df