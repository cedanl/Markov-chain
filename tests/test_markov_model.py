import pandas as pd

from markov_model import run_model


def test_modellen_leren_niet_van_overgang_naar_testjaar():
    # 2016-2019: iedereen stroomt door. Startjaar 2020: iedereen stroomt uit.
    # Die laatste overgang (2020 -> 2021) is wat getest wordt en mag
    # dus niet in de matrices zitten.
    rijen = [
        {
            "studiejaar": jaar,
            "markov_status": "Niveau4_jaar_1",
            "volgende_markov_status": "uitstroom" if jaar == 2020 else "Niveau4_jaar_2",
        }
        for jaar in range(2016, 2022)
        for _ in range(10)
    ]

    _, _, model_matrices = run_model(
        df=pd.DataFrame(rijen),
        train_jaren=range(2016, 2021),
        test_jaren=[2021],
        prognose_jaren=[],
        instroom_aanname_jaar=2021,
    )

    for matrix in model_matrices.values():
        assert matrix.loc["Niveau4_jaar_1", "uitstroom"] == 0
