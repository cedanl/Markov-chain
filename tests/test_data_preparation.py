from pathlib import Path

import pandas as pd

from data_preparation import prepare_student_data
from markov_preparation import prepare_markov_data

BRONEXPORT_PAD = Path(__file__).parent.parent / "voorbeeld_bronexport.csv"


def test_prepare_student_data_bepaalt_stromen():
    df = prepare_student_data(pd.read_csv(BRONEXPORT_PAD))

    resultaat = {
        (rij.student_id, rij.studiejaar): (rij.instroom, rij.doorstroom, rij.uitstroom)
        for rij in df.itertuples()
    }

    assert resultaat == {
        # Drie jaar achter elkaar, daarna uitgeschreven
        (100001, 2020): (1, 0, 0),
        (100001, 2021): (0, 1, 0),
        (100001, 2022): (0, 1, 1),
        # Jaar weg geweest: telt als uitstroom en opnieuw instroom
        (100002, 2019): (1, 0, 1),
        (100002, 2021): (1, 0, 0),
        (100002, 2022): (0, 1, 0),
        # Wissel van niveau 2 naar niveau 3
        (100006, 2020): (1, 0, 0),
        (100006, 2021): (0, 1, 1),
    }


def test_prepare_student_data_filtert_records():
    df = prepare_student_data(pd.read_csv(BRONEXPORT_PAD))

    # 100003: Cluster Techniek, 100004: crebo 99999,
    # 100005: niet ingeschreven op 1 oktober
    assert not df["student_id"].isin([100003, 100004, 100005]).any()


def test_uitvoer_past_op_prepare_markov_data():
    df = prepare_markov_data(prepare_student_data(pd.read_csv(BRONEXPORT_PAD)))

    assert not df["markov_status"].str.contains("onbekend").any()
