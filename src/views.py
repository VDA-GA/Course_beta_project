import datetime as dt
import json
import logging
import os
from typing import List, Any

import pandas as pd
import requests

from src.utils import get_user_settings, list_from_df, load_data_from_xlsx, logging_function

logging_function("CW")
logger = logging.getLogger("CW.views")

PATH_TO_USER_SETTINGS = "user_settings.json"
API_KEY_1: str | None = os.getenv("alphavantageAPI")
DATA = "data/operations.xls"


def get_currencies_rates_list(user_settings: dict) -> List[dict]:
    """Получает котировки валют, указанные в user_settings
    :param user_settings: словарь пользовательских запросов
    :return список словарей котировок"""
    currency_rates = []
    user_currencies = user_settings["user_currencies"]
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        response.raise_for_status()
        currency_rates_data = response.json()
        logger.info("Данные с сайта cbr-xml-daily.ru успешно получены")
        for currency in user_currencies:
            currency_rates.append(
                {currency: currency_rates_data["Valute"][currency]["Value"]}
            )
    except requests.exceptions.RequestException as err:
        logger.error(err)
        print(err)
    return currency_rates


def get_stocks_rates_list(user_settings: dict) -> List[dict]:
    """Получает стоимость акций, указанные в user_settings
    :param user_settings: словарь пользовательских запросов
    :return список словарей стоимости акций"""
    stocks_rates = []
    user_stocks = user_settings["user_stocks"]
    for stock in user_stocks:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY_1}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            logger.info("Данные с сайта alphavantage.co успешно получены")
            data = response.json()
            stocks_rates.append({stock: data["Global Quote"]["05. price"]})
        except requests.exceptions.RequestException as err:
            logger.error(err)
            print(err)
    return stocks_rates


def filter_df_according_to_period(
        df_data: pd.DataFrame, end_date_str: str, time_period: str) -> pd.DataFrame:
    """Фильтрует DataFrame в соответствии с датой и периодом
    :param df_data: исходный DataFrame
    :param end_date_str: по какую дату в формате "%Y.%m.%d"
    :param time_period: интересуемый период
    :return отфильтрованный по дате и периоду DataFrame объект"""
    df_data["Дата операции"] = df_data["Дата операции"].map(
        lambda p: dt.datetime.strptime(p, "%d.%m.%Y %H:%M:%S").date()
    )
    try:
        end_date = dt.datetime.strptime(end_date_str, "%Y.%m.%d").date()
        if time_period == "W":
            start_date = end_date.replace(day=(end_date.day - end_date.weekday()))
        elif time_period == "M":
            start_date = end_date.replace(day=1)
        elif time_period == "Y":
            start_date = end_date.replace(month=1, day=1)
        elif time_period == "ALL":
            start_date = df_data["Дата операции"].min()
        else:
            logger.info("Период задан неверно")
            start_date = df_data["Дата операции"].min()
        return df_data[(df_data["Дата операции"] <= end_date) & (df_data["Дата операции"] >= start_date)]
    except ValueError as err:
        print("Строка должна быть в формате ГГГГ.ММ.ДД")
        logger.error(err)
        return df_data


def get_expenses_or_income_transactions(
        df_data: pd.DataFrame,
) -> tuple[pd.Series[Any], pd.Series[Any]]:
    """Получает кортеж из DataFrame объектов трат и приходов
    :param df_data: исходный DataFrame
    :return кортеж из DataFrame объектов трат и приходов"""
    df_data = df_data[df_data["Статус"] == "OK"]
    df_expenses = df_data[df_data["Сумма платежа"] < 0]
    df_income = df_data[df_data["Сумма платежа"] > 0]
    df_expenses_grouped = df_expenses.groupby("Категория")[
        "Сумма операции с округлением"
    ].sum()
    df_expenses_grouped_sorted = df_expenses_grouped.sort_values(ascending=False)
    df_income_grouped = df_income.groupby("Категория")[
        "Сумма операции с округлением"
    ].sum()
    df_income_grouped_sorted = df_income_grouped.sort_values(ascending=False)
    return df_expenses_grouped_sorted, df_income_grouped_sorted


def get_analysis_by_date_and_category(start_date: str, period: str = "M", filename: str = DATA) -> None:
    """Получает json файл, содержащий транзакции отфильтрованные по категории, дате и периоду
    :param filename: путь к excel файлу с транзакциями
    :param start_date: по какую дату в формате "%Y.%m.%d"
    :param period: интересуемый период"""
    df = load_data_from_xlsx(filename)
    try:
        df_by_date = filter_df_according_to_period(df, start_date, period)
    except ValueError as err:
        logger.error(err, "Введена дата в неверном формате")
        df_by_date = df
    df_expenses, df_income = get_expenses_or_income_transactions(df_by_date)
    list_expenses = list_from_df(df_expenses)
    list_transfers_and_cash = [
        i
        for i in list_expenses
        if i["category"] == "Наличные" or i["category"] == "Переводы"
    ]
    list_main_expenses = [i for i in list_expenses if i not in list_transfers_and_cash]

    if len(list_main_expenses) > 7:
        list_main = list_main_expenses[0:7]
        remains = {
            "category": "Остальное",
            "amount": sum([i["amount"] for i in list_main_expenses[7:]]),
        }
        list_main.append(remains)
    else:
        list_main = list_main_expenses

    list_income = list_from_df(df_income)

    user_settings = get_user_settings(PATH_TO_USER_SETTINGS)

    analysis_result = {
        "expenses": {
            "total_amount": round(sum([i["amount"] for i in list_expenses]), 2),
            "main": list_main,
            "transfers_and_cash": list_transfers_and_cash,
        },
        "income": {
            "total_amount": round(sum([i["amount"] for i in list_income]), 2),
            "main": list_income,
        },
        "currency_rates": get_currencies_rates_list(user_settings),
        "stock_prices": get_stocks_rates_list(user_settings),
    }

    with open("analysis_result.json", "w", encoding="utf-8") as f:
        json.dump(analysis_result, f, ensure_ascii=False)
