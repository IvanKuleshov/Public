import pandas as pd
from typing import Optional
from typing_extensions import TypedDict # Из-за того, что питон 3.7, в старших версиях используется typing


# - работа с интерфейсом
# - работа с БД
# модуль для нормализации адреса

class FoundColumn(TypedDict):
    district: Optional[str]
    city: str


# Вызов функйции, автоопределения колонок - возвращает dict. где название параметра - название колонки из Датафрейм
def get_auto_search_columns(df: pd.DataFrame) -> FoundColumn:
    findC = FoundColumn(district=None, city='г. Новосибирск')
    print(findC)
    return findC


def get_kladr(df: pd.DataFrame) -> FoundColumn:
    fc = get_auto_search_columns(df)

    return fc
