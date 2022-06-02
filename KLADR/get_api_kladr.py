import pandas as pd
from typing import NamedTuple


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

    def __init__(self, df: pd.DataFrame, con: str):
        self.df = df
        self.con = con  # connect to BD

    #  Используя переданные или определенные поля, определяем КЛАДР
    def get_kladr(self, found_columns: FoundColumn, is_auto: bool = True) -> FoundColumn:
        fc = self.get_auto_search_columns(is_auto)

        return fc

    #  Попытка автоматического поиска названий колонок
    def get_auto_search_columns(self, is_auto: bool) -> FoundColumn:
        findC = FoundColumn(city='г. Новосибирск', street='Комсомольская')

        if is_auto:
            print(findC, self.df.head(2))
        return findC