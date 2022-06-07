import pandas as pd
import sqlite3
from typing import NamedTuple
from sklearn.linear_model import LinearRegression


# from typing_extensions import TypedDict # Из-за того, что питон 3.7, в старших версиях используется typing
# from dataclasses import dataclass


# - работа с интерфейсом
# - работа с БД
# модуль для нормализации адреса

class FoundColumn(NamedTuple):
    city: str
    street: str
    district: str = None
    type_street: str = None
    num_house: str = None
    block_house: str = None
    num_flat: str = None
    name_work: str = None


class KladrHouse:

    def __init__(self, df: pd.DataFrame, con: sqlite3.Connection):
        self.df = df.copy()
        self.con = con  # connect to BD
        #self.found_columns = None  # Возможно, здесь будет проблема, проверить при тестировании

    #  Используя переданные или определенные поля, определяем КЛАДР
    def get_kladr(self, found_columns: FoundColumn, is_auto: bool = True) -> FoundColumn:
        #  Если заказано автоматическое определение - вызываем функцию
        if is_auto:
            self.found_columns = self.get_auto_search_columns()
            print(f'Найденные колонки: {found_columns}')
        else:
            self.found_columns = found_columns

        #  Заменяем опечатки
        self.replace_typos()

        #  Записываем таблицу data в базу данных
        self.df.to_sql('data', self.con, if_exists='replace', index=False)

        return found_columns

    #  Попытка автоматического поиска названий колонок
    def get_auto_search_columns(self) -> FoundColumn:
        findC = FoundColumn(city='г. Новосибирск', street='Комсомольская')
        df = self.df
        return findC

    #  Производит поиск-замену по таблице typos (поле из DF, что заменить, на что заменить)
    def replace_typos(self):
        #  Мапим наш датафрейм полями Found, Вытаскиваем из базы опечатки в датафрейм, заменяем опечатки
        new_columns = {v: k
                       for k, v
                       in self.found_columns._asdict().items()
                       if v in self.df.columns}
        self.df.rename(columns=new_columns, inplace=True)

        #  Вытаскиваем из БД таблицу typos, перебираем в цикле опечатки и применяем их к DF
        df_typos = pd.read_sql_query(sql='SELECT * FROM typos', con=self.con)  # type: pd.DataFrame
        for _, typo in df_typos.iterrows():
            pole = typo['pole']

            if pole in self.df.columns:
                self.df[pole].replace(
                    r'(?i)' + typo['old_word'],
                    typo['new_word'],
                    inplace=True, regex=True
                )
        pass
