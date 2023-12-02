import datetime as dt
import logging
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

from src.utils import logging_function

logging_function("CW")
logger = logging.getLogger("CW.reports")


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
            return df_report

        return inner

    return wrapper


@printing("report.xlsx")
def get_expenses_by_category(
        df: pd.DataFrame, category: str, end_date_str: Optional[str] = None
) -> pd.DataFrame:
    """Фильтрует DataFrame в соответствии с датой и интересуемой категорией
    :param df: исходный DataFrame
    :param category: интересуемая категория
    :param end_date: по какую дату в формате "%Y.%m.%d", по умолчанию вычисляется текущая
    :return DataFrame объект отфильтрованный по дате (три месяца до указанной) и указанной категории
    """

    if end_date_str:
        try:
            end_date = dt.datetime.strptime(end_date_str, "%Y.%m.%d").date()
        except ValueError as err:
            logger.error(err)
            print("Неверно указана дата")
            end_date = dt.datetime.now().date()
    else:
        end_date = dt.datetime.now().date()

    start_date = end_date - dt.timedelta(days=90)
    df["Дата операции"] = df["Дата операции"].map(
        lambda p: dt.datetime.strptime(p, "%d.%m.%Y %H:%M:%S").date()
    )
    df_by_date = df[(df["Дата операции"] <= end_date) & (df["Дата операции"] >= start_date)]
    df_by_date_and_category = df_by_date[df_by_date["Категория"] == category]
    logger.info(f"Получены данные по категории {category}")
    return df_by_date_and_category
