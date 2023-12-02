import json
import os

import pandas as pd
import pytest

from src.utils import get_user_settings
from src.views import (filter_df_according_to_period, get_analysis_by_date_and_category, get_currencies_rates_list,
                       get_expenses_or_income_transactions, get_stocks_rates_list)


@pytest.fixture
def us():
    res = get_user_settings("user_settings.json")
    return res


def tests_get_currencies_rates_list(us):
    assert len(get_currencies_rates_list(us)) == 2


def tests_get_stocks_rates_list(us):
    assert len(get_stocks_rates_list(us)) == 5


@pytest.fixture
def df():
    return pd.read_excel("test2.xlsx")


@pytest.mark.parametrize(
    "date, period, expected_result",
    [
        ("2021.12.31", "W", 7),
        ("2021.12.31", "M", 11),
        ("2021.12.31", "Y", 19),
        ("2021.12.31", "ALL", 23),
        ("2021.12.31", "D", 23),
    ],
)
def test_filter_df_according_to_period(df, date, period, expected_result):
    res_df = filter_df_according_to_period(df, date, period)
    assert res_df.shape[0] == expected_result


def test_get_expenses_or_income_transactions(df):
    df_ex, df_in = get_expenses_or_income_transactions(df)
    assert (len(df_ex), len(df_in)) == (11, 1)
    assert df_ex.index[0] == "Супермаркеты"
    assert df_in.index[0] == "Пополнения"


def test_get_analysis_by_date_and_category_1():
    filename = "analysis_result.json"
    if os.path.exists(filename):
        os.remove(filename)
    get_analysis_by_date_and_category("2021.12.31", "ALL", "tests/test2.xlsx")
    with open("analysis_result.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["expenses"]["total_amount"] == 7755.66
    assert data["expenses"]["transfers_and_cash"][0]["amount"] == 1600.0
    assert data["income"]["total_amount"] == 15000.0


def test_get_analysis_by_date_and_category_2():
    filename = "analysis_result.json"
    if os.path.exists(filename):
        os.remove(filename)
    get_analysis_by_date_and_category("2021.12.31", "ALL", "tests/test1.xlsx")
    with open("analysis_result.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["expenses"]["total_amount"] == 21793.45
    assert data["expenses"]["transfers_and_cash"][0]["amount"] == 20800
    assert data["income"]["total_amount"] == 5046.00
