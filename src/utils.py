import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd


def logging_function(name_module: str) -> None:
    """Функция инициализирующая логгер
    :param name_module: имя регистратора"""
    logger = logging.getLogger(name_module)
    logger.setLevel(logging.DEBUG)
    handler1 = logging.FileHandler(filename="log.txt", encoding="utf-8")
    handler1.setFormatter(
        logging.Formatter(
            "%(asctime)s %(name)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    handler1.setLevel(logging.DEBUG)
    logger.addHandler(handler1)
    logger.debug("Логер инициализирован")


logging_function("CW")
logger = logging.getLogger("CW.utils")


def get_user_settings(file_user_settings: str) -> Any:
    """Получает данные пользователя из user_settings
    :param file_user_settings: json-файл пользовательских настроек
    :return список словарей стоимости акций"""

    path_to_project = Path(Path.cwd()).parent
    abs_path = Path(path_to_project, file_user_settings)
    try:
        with open(abs_path) as f:
            user_settings = json.load(f)
        logging.info("Пользовательские настройки успешно получены")
    except FileNotFoundError as err:
        logger.error(err)
        print("Файл не найден")
    except json.JSONDecodeError as err:
        logger.error(err)
        print("JSON-файл имеет неправильный формат ")
    return user_settings


def load_data_from_xlsx(filename: str) -> Any:
    """Загружает данные из excell-файла
    :param filename: путь к файлу .xlsl или .xls
    :return объект DataFrame"""
    path_to_project = Path(Path.cwd()).parent
    abs_path = Path(path_to_project, filename)
    try:
        df_data = pd.read_excel(abs_path)
        logger.debug(
            f"Получены данные из Excel. Размер полученного DataFrame = {df_data.shape}"
        )
        return df_data
    except FileNotFoundError as err:
        logger.error(err)
        print("Файл не найден")


def list_from_df(df_data: pd.DataFrame | pd.Series) -> list[dict]:
    """Создает список словарей из DataFrame объекта в виде
    {'category': Название категории, 'amount': сумма транзакции}}
        :param df_data: DataFrame объект
        :return список словарей транзакций"""
    list_of_dict = []
    for i in range(0, len(df_data)):
        list_of_dict.append(
            {"category": df_data.index[i], "amount": round(df_data.iloc[i], 2)}
        )
    logger.debug(f"Получен список транзакций содержащий {len(list_of_dict)} элементов")
    return list_of_dict
