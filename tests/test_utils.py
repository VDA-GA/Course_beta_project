import pandas as pd
import pytest

from src.utils import get_user_settings, list_from_df, load_data_from_xlsx


@pytest.mark.parametrize(
    "arg, expected_result",
    [
        ("user_currencies", ["USD", "EUR"]),
        ("user_stocks", ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]),
    ],
)
def test_get_user_settings(arg, expected_result):
    assert get_user_settings("user_settings.json")[arg] == expected_result


@pytest.fixture
def df():
    return pd.read_excel("test1.xlsx")


def test_load_data_from_xlsx_1():
    assert load_data_from_xlsx("tests/test1.xlsx").shape == (10, 15)


def test_list_from_df(df):
    new_df = df.groupby("Категория")["Сумма операции с округлением"].sum()
    assert len(list_from_df(new_df)) == 5
