import pandas as pd
import pytest

from src.reports import get_expenses_by_category, printing


@pytest.fixture
def df():
    return pd.read_excel("test2.xlsx")


def test_get_expenses_by_category(df):
    data = get_expenses_by_category(df, "Супермаркеты", "2021.12.31")
    assert data.shape == (4, 15)


def test_printing():
    @printing("test.xlsx")
    def get_data_frame():
        return pd.read_excel("test2.xlsx")

    get_data_frame()

    test_data = pd.read_excel("test.xlsx")

    assert test_data.shape == (23, 15)
