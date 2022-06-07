# определения и вызов модулей
import pandas as pd
import sqlite3
from get_api_kladr import FoundColumn, KladrHouse

if __name__ == "__main__":
    con = sqlite3.connect("kladrDB.db")

    # загрузка файлов для тестовой работы
    df = pd.read_csv('data.csv',
                     encoding='cp1251', sep=';', decimal='.', dtype='object')  # type: pd.DataFrame

    fc = FoundColumn(city='CITY', street='STREET', type_street='TYPE_S', num_house='BUILDING', num_flat='FLAT')

    place_kladr = KladrHouse(df, con=con)

    d = place_kladr.get_kladr(fc, False)

    sql = '''SELECT * FROM norm_replace'''

    #df = pd.read_sql_query(sql=sql, con=con)

#re.sub('!Я улицо', 'Хуюлица', str, flags=re.I) # str - должна быть строка
#df.STREET.replace(r'(?i)Геодезческая|Геодезическая', '!Я улицо', inplace=True, regex=True)