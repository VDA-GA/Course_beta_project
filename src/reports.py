import datetime as dt
from typing import Any, Optional, Callable
from functools import wraps
from src.views import load_data_from_xlsx

import pandas as pd


def printing(filename: str) -> Any:
    """
    Записывает данные отчета в excel файл
    :param filename: название файла отчета
    """

    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            df_report = func(*args, **kwargs)
            df_report.to_excel(filename, index=False)
            return None

        return inner

    return wrapper


@printing('report.xlsx')
def get_expenses_by_category(df: pd.DataFrame, category: str, end_date: Optional[str] = None) -> pd.DataFrame:
    """Фильтрует DataFrame в соответствии с датой и интересуемой категорией
        :param df: исходный DataFrame
        :param category: интересуемая категория
        :param end_date: по какую дату, по умолчанию вычисляется текущая
        :return DataFrame объект отфильтрованный по дате (три месяца до указанной) и указанной категории"""

    if end_date:
        end_date = dt.datetime.strptime(end_date, "%Y.%m.%d").date()
    else:
        end_date = dt.datetime.now().date()

    start_date = end_date - dt.timedelta(days=90)
    df['Дата операции'] = df['Дата операции'].map(
        lambda p: dt.datetime.strptime(p, "%d.%m.%Y %H:%M:%S").date())
    df_by_date = df[(df['Дата операции'] <= end_date) & (df['Дата операции'] >= start_date)]
    df_by_date_and_category = df_by_date[df_by_date['Категория'] == category]
    return df_by_date_and_category


df = load_data_from_xlsx('data/operations.xls')
res = get_expenses_by_category(df, 'Наличные')
