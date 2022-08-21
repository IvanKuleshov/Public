# второе тестирование гит
# тестирование гит
# определения и вызов модулей
import pandas as pd
import sqlite3
from get_api_kladr import AddressColumn, IdColumns, KladrHouse

if __name__ == "__main__":
    con = sqlite3.connect("kladrDB.db")

    # загрузка файлов для тестовой работы
    df = pd.read_csv('data.csv',
                     encoding='cp1251', sep=';', decimal='.', dtype='object')  # type: pd.DataFrame

    ac = AddressColumn(city='CITY', street='STREET', type_street='TYPE_S', num_house='BUILDING', num_flat='FLAT')
    place_kladr = KladrHouse(df, con=con, address_columns=ac, is_auto_col=False)

    ic = IdColumns('кря')
    d = place_kladr.get_kladr(ic, is_auto_id=False)

    sql = '''SELECT * FROM norm_replace'''

    #df = pd.read_sql_query(sql=sql, con=con)

#re.sub('!Я улицо', 'Хуюлица', str, flags=re.I) # str - должна быть строка
#df.STREET.replace(r'(?i)Геодезческая|Геодезическая', '!Я улицо', inplace=True, regex=True)