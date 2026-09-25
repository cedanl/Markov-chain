import pandas as pd


def prepare_student_data(student_data, crebo_data):
    """
    Schoont de studentdata op en bepaalt
    instroom, doorstroom en uitstroom.
    """

    # Kolomnamen studentdata versimpelen
    student_data = student_data.rename(columns={
        'Deelnemernummer': 'student_id',
        'Volgnummer': 'volgnummer',
        'Studiejaar': 'studiejaar',
        'Deelnemer_geslacht': 'geslacht',
        'Leerweg': 'leerweg',
        'College': 'college',
        'Cluster': 'cluster',
    })

    # Ongewenste records verwijderen
    df = df.loc[
        (df['cluster'] != 'Cluster Techniek') &
        (df['crebo'] != 99999)
    ].copy()

    # Alleen benodigde kolommen
    columns = [
        'studiejaar',
        'begindatum',
        'einddatum',
        'student_id',
        'volgnummer',
        'geslacht',
        'leerweg',
        'niveau',
        'college',
        'cluster',
    ]
    df = df[columns].drop_duplicates()

    # Datatypes aanpassen
    df['begindatum'] = pd.to_datetime(df['begindatum'])
    df['einddatum'] = pd.to_datetime(df['einddatum'])

    df['studiejaar'] = ( df['studiejaar'] .str[:4] .astype(int))

    # Bepalen of student ooit geslaagd is
    df['ooit_geslaagd'] = ( df.groupby('student_id')['geslaagd'] .transform('max'))

    # Peildatum: 1 oktober
    df['peildatum'] = pd.to_datetime( df['studiejaar'].astype(str) + '-10-01')

    # Student moet actief zijn op 1 oktober
    df['actief_op_peildatum'] = ( (df['peildatum'] >= df['begindatum']) & (     (df['peildatum'] < df['einddatum']) |     df['einddatum'].isna() ) ).astype(int)

    df = df.loc[ df['actief_op_peildatum'].eq(1)].copy()

    # Eén record per student per studiejaar
    df = (  df  .sort_values(['student_id', 'studiejaar'])  .drop_duplicates(      subset=['student_id', 'studiejaar'],      keep='last'  ))

    # Vorig studiejaar
    df['vorig_jaar'] = (  df.groupby('student_id')['studiejaar']  .shift(1))

    # Verschil met vorig studiejaar
    df['jaar_verschil'] = (  df['studiejaar'] - df['vorig_jaar'])

    # Instroom
    df['instroom'] = ( df['vorig_jaar'].isna() | df['jaar_verschil'].gt(1)).astype(int)

    # Instroomgroep
    df['instroomgroep'] = ( df.groupby('student_id')['instroom'].cumsum())

    # Doorstroom
    df['doorstroom'] = (  df['jaar_verschil'].eq(1) ).astype(int)

    # Volgend studiejaar
    df['volgend_jaar'] = ( df.groupby('student_id')['studiejaar'] .shift(-1) )

    # Mogelijke uitstroom
    mogelijke_uitstroom = (df['volgend_jaar'].isna() | (df['volgend_jaar'] - df['studiejaar']).gt(1))

    # Uitstroom alleen als einddatum bekend is
    df['uitstroom'] = (  mogelijke_uitstroom & df['einddatum'].notna()).astype(int)

    # Dubbele regels samenvoegen
    group_columns = [
        'student_id',
        'volgnummer',
        'studiejaar',
        'niveau',
        'actief_op_peildatum',
        'instroomgroep'
    ]

    df = (
        df
        .groupby(group_columns, as_index=False)[
            ['instroom', 'doorstroom', 'uitstroom']
        ]
        .max()
        .sort_values(['student_id', 'studiejaar'])
    )

    # Jaar binnen instroomgroep
    df['jaar_in_groep'] = (
        df
        .groupby(['student_id', 'instroomgroep'])
        .cumcount()
        .add(1)
    )

    return df