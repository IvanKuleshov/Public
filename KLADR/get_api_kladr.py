import pandas as pd
import sqlite3
from typing import NamedTuple
from sklearn.linear_model import LinearRegression


# from typing_extensions import TypedDict # Из-за того, что питон 3.7, в старших версиях используется typing
# from dataclasses import dataclass


# - работа с интерфейсом
# - работа с БД
# модуль для нормализации адреса
class IdColumns(NamedTuple):
    id_kladr: str = None
    id_house: str = None
    id_flat: str = None
    id_work: str = None


class AddressColumn(NamedTuple):
    city: str
    street: str
    district: str = None
    type_street: str = None
    num_house: str = None
    block_house: str = None
    num_flat: str = None
    name_work: str = None


class KladrHouse:

    def __init__(self, df: pd.DataFrame, con: sqlite3.Connection,
                 address_columns: AddressColumn, is_auto_col: bool = False):

        self.df = df
        self.con = con  # connect to BD
        self.address_columns = address_columns  # Маркированные столбцы адреса
        self.id_columns = IdColumns()  # Маркированные столбцы id-шников
        self.is_auto_col = is_auto_col

        #  Преобразуем в нижний регистр, для всевозможных сравнений по данным в дальнейшем
        self.df_lower = self.df.applymap(lambda x: str(x).lower() if type(x)==str else x)

    #  Используя переданные или определенные поля, определяем КЛАДР
    def get_kladr(self, id_columns: IdColumns, is_auto_id: bool = False,
                  is_kladr: bool = False, is_house: bool = True, is_flat: bool = False, is_work: bool = False,
                  over_address: bool = True, over_id: bool = False) -> pd.DataFrame:

        #  Если заказано автоматическое определение адресных полей - вызываем функцию
        if self.is_auto_col:
            self.address_columns = self.get_auto_search_columns()
            print(f'Найденные колонки: {self.address_columns}')

        #  Если заказано автоматическое определение полей id - вызываем функцию
        if is_auto_id:
            self.id_columns = self.get_auto_search_id()
            print(f'Найденные id: {self.id_columns}')

        #  Заменяем опечатки
        self.replace_typos()

        #  Восстанавливаем поля id по образцам замен в БД
        self.id_from_history(id_columns.id_kladr, over_id)

        #  Записываем таблицу data в базу данных
        self.df.to_sql('data', self.con, if_exists='replace', index=False)

        return self.df_lower

    #  Попытка автоматического поиска названий колонок
    def get_auto_search_columns(self) -> AddressColumn:
        findC = AddressColumn(city='г. Новосибирск', street='Комсомольская')

        return findC

    #  Попытка автоматического поиска названий колонок идешников
    def get_auto_search_id(self) -> IdColumns:
        findId = IdColumns(id_kladr='id_kladr', id_house='id_house')

        return findId

    #  Производит поиск-замену по таблице typos (поле из DF, что заменить, на что заменить)
    def replace_typos(self):
        #  Мапим наш датафрейм полями Found, Вытаскиваем из базы опечатки в датафрейм, заменяем опечатки
        #  upd.: 07/06/2022 - данная конструкция была для того, чтобы все запросы к data делать через sql
        #  но решено отказаться в пользу pandas, поэтому закоменчено
        #  new_columns = {v: k
        #               for k, v
        #               in self.address_columns._asdict().items()
        #               if v in self.df.columns}
        #  self.df.rename(columns=new_columns, inplace=True)

        #  Вытаскиваем из БД таблицу typos, перебираем в цикле опечатки и применяем их к DF
        df_typos = pd.read_sql_query(sql='SELECT * FROM typos', con=self.con)  # type: pd.DataFrame
        for _, typo in df_typos.iterrows():
            #  переделал строку. см upd
            #  pole = typo['pole']
            pole = self.address_columns._asdict()[typo['pole']]

            if pole in self.df.columns:
                self.df[pole].replace(
                    r'(?i)' + typo['old_word'],
                    typo['new_word'],
                    inplace=True, regex=True
                )
        pass

    #  Производим восстановление кода КЛАДР из столбцов адреса по ранее определенным шаблонам, сохраненных в БД
    def id_from_history(self, id_kladr: str = 'id_kladr', over_id: bool = False):
        #  Если ид не существует в ДФ, то создать поле id_kladr
        pole = id_kladr
        if id_kladr not in self.df_lower.columns:
            pole = 'id_kladr'

            if pole not in self.df_lower.columns:
                self.df_lower[pole] = None

        #  Если запрещено переписывать ИД КЛАДР, то выбираем только строки с пустым КЛАДР
        work_df = self.df_lower if over_id else self.df_lower[self.df_lower[pole].isna()]
        #  Делаем индекс отдельным столбцом, т.к. merge не сохраняет индекс, а нам нужен Update по нему
        work_df.reset_index(inplace=True)

        #  merge сначала по связке district-city-street, если district не пустое; затем по city-street
        df_for_merge = pd.read_sql_query(sql=f'''   SELECT 
                                                        district, city, street, kladr as {pole}
                                                    FROM full_replace''',
                                         con=self.con)
        #  переводим в нижний регистр, т.к. LOWER для русских строк в SQLITE не работает
        df_for_merge = df_for_merge.applymap(lambda x: str(x).lower() if type(x) == str else x)

        mask = df_for_merge['district'].isna()  #  выбираем строки с пустым районом

        work_df_merge1 = pd.merge(work_df, df_for_merge[mask],
                                  how='inner',
                                  left_on=[self.address_columns.city,
                                           self.address_columns.street],
                                  right_on= ['city', 'street'],
                                  suffixes=('_', None))

        work_df_merge2 = pd.merge(work_df, df_for_merge[~mask],
                                  how='inner',
                                  left_on=[self.address_columns.district,
                                           self.address_columns.city,
                                           self.address_columns.street],
                                  right_on=['district', 'city', 'street'],
                                  suffixes=('_', None))

        #  Собираем датафреймы воедино
        self.df_lower.update(work_df_merge1.set_index('index')[pole])
        self.df_lower.update(work_df_merge2.set_index('index')[pole])

        pass

    '''
    Функция нормализации
    
    1. Собираем из Дата все Район-Город-Улица без повторов.
    2. Для каждой строки делаем нормировку адреса
    3. Переносим нормировку в Дата
    4. По нормированным колонкам восстанавливаем КЛАДР, при этом
    5. если есть Район - восстанавливаем КЛАДР без пометки [использовать ту же функцию - подумать как преобразовать]
    6. Если Района нет, то восстанавливаем КЛАДР с пометкой дубля (если Город-Улица не уникальны)
    7. Для всех строк с пометкой, если есть на доме Номер дома, то пытаться восстановить КЛАДР из другой таблицы похожей на хистори
    8. Если номера дома нет, то КЛАДР убрать
    
    9. Далее по номеру КЛАДРА и остальным сущностям восстанавливаем остальные ИД - отдельная функция
    
    восстановление кладр, можно сделать одной функцией только с передаваемым параметром, определяющим сценарий:
    1) сверка по район-город-улица + город-улица -> КЛАДР
    2) сверка по район-город-улица +... но имена другие -> КЛАДР
    3) сверка по другим город-улица -> КЛАДР, пометка
    4) сверка по номеру дома + город-улица -> КЛАДР
    '''