# определения и вызов модулей
import pandas as pd
from get_api_kladr import FoundColumn, KladrHouse


if __name__ == "__main__":
    # загрузка файлов для тестовой работы
    df = pd.read_csv('data.csv',
                     encoding='cp1251', sep=';', decimal='.', dtype='object')  # type: pd.DataFrame

    d = FoundColumn(city='Бердск', street='')

    fc = KladrHouse(df, con='test')
    fc.get_kladr(FoundColumn(city='Бердск', street='Мира'), True)

    f = fc.con
    print(d)