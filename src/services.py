import datetime as dt
import pandas as pd
from typing import List, Dict, Any


def dict_of_transaction_from_df(df: pd.DataFrame) -> list[dict]:
    """Создает список словарей из DataFrame объекта в виде
        {'date_transaction': Дата транзакции, 'amount': сумма транзакции}
            :param df_data: DataFrame объект
            :return список словарей транзакций"""
    dict_of_transaction = []
    df_expenses = df[df['Сумма операции'] < 0]
    df_main = df_expenses[(df_expenses['Категория'] != 'Наличные') & (df_expenses['Категория'] != 'Переводы') & (
            df_expenses['Категория'] != 'Услуги банка')]
    for i in range(0, len(df_main)):
        dict_of_transaction.append(
            {'date_transaction': str(dt.datetime.strptime(df_main.iloc[i, 0], '%d.%m.%Y %H:%M:%S').date()),
             'amount': df_main.iloc[i, 14]})
    return dict_of_transaction


def invest_copilka(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Рассчитывает возможную сумму отложенную на инвестиции при использовании инвесткопилки
            :param month: интересуемый месяц
            :param transactions: список словарей транзакций
            :param limit: комфортный порог округления
            :return возвращает сумму, которую удалось бы отложить в инвесткопилку"""
    filtered_list_transactions = [i for i in transactions if i['date_transaction'][0:7] == month]
    list_of_reb = [i['amount'] % limit for i in filtered_list_transactions if i['amount'] % limit != 0]
    invest = round(sum([limit - l for l in list_of_reb]), 2)
    return invest
