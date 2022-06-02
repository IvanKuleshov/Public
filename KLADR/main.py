# определения и вызов модулей
import pandas as pd
from get_api_kladr import get_kladr


if __name__ == "__main__":
    # загрузка файлов для тестовой работы
    df = pd.read_csv('data.csv',
                     encoding='cp1251', sep=';', decimal='.', dtype='object')  # type: pd.DataFrame

    fc = get_kladr(df)
