import json
import pandas as pd
from pathlib import Path


def get_user_settings(file_user_settings: str) -> dict:
    """Получает данные пользователя из user_settings
        :param file_user_settings: json-файл пользовательских настроек
        :return список словарей стоимости акций"""

    path_to_project = Path(Path.cwd()).parent
    abs_path = Path(path_to_project, file_user_settings)
    with open(abs_path) as f:
        user_settings = json.load(f)
    return user_settings


def load_data_from_xlsx(filename: str) -> pd.DataFrame:
    """Загружает данные из excell-файла
            :param filename: путь к файлу .xlsl или .xls
            :return объект DataFrame"""
    path_to_project = Path(Path.cwd()).parent
    abs_path = Path(path_to_project, filename)
    df_data = pd.read_excel(abs_path)
    return df_data


def list_from_df(df_data: pd.DataFrame) -> list[dict]:
    """Создает список словарей из DataFrame объекта в виде
    {'category': Название категории, 'amount': сумма транзакции}}
        :param df_data: DataFrame объект
        :return список словарей транзакций"""
    list_of_dict = []
    for i in range(0, len(df_data)):
        list_of_dict.append({'category': df_data.index[i], 'amount': round(df_data.iloc[i], 2)})
    return list_of_dict
