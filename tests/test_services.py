import pandas as pd
import pytest

from src.services import dict_of_transaction_from_df, invest_copilka


@pytest.fixture
def df():
    return pd.read_excel("test1.xlsx")


def test_dict_of_transaction_from_df(df):
    assert dict_of_transaction_from_df(df)[0]["date_transaction"] == "2021-12-31"
    assert dict_of_transaction_from_df(df)[0]["amount"] == 160.89
    assert len(dict_of_transaction_from_df(df)) == 7


@pytest.fixture
def list_transactions():
    data_frame = pd.read_excel("test1.xlsx")
    return dict_of_transaction_from_df(data_frame)


def test_invest_copilka(list_transactions):
    assert invest_copilka("2021-12", list_transactions, 50) == 256.55
