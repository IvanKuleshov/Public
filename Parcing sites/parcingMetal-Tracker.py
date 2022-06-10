# -*- coding: utf-8 -*-
# python 3.7
# pip install beautifulsoup4
# pip install lxml

import pandas as pd
from bs4 import BeautifulSoup
import json
import os


#  Возвращает текст html-страницы по ссылке
def site(page: str) -> str:
    import requests
    try:
        r = requests.get(page)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    return r.text


def Get_Groups_Metal_Tracker(page: str) -> pd.DataFrame:
    soup = BeautifulSoup(page, 'lxml')

    tracks = soup.find(class_='new_trackers')
    groups = tracks.findAll('center')
    infos = tracks.findAll(class_='update')

    data = []
    for group, info in zip(groups, infos):
        row = {'Год': '-', 'Стиль': '-', 'Формат': '-', 'Страна': '-', 'Добавлено': '-', 'Размер': '-',
               'Группа': group.find('h3').text,
               'Ссылка': 'https://www.metal-tracker.com' + group.find('a').get('href')}

        info = info.find(class_='basic_data').findAll('li')
        for inf in info:
            s = inf.text.split(':')
            if s[0] in ['Год', 'Стиль', 'Формат', 'Страна', 'Добавлено', 'Размер']:
                row[s[0]] = s[1].strip()

        data.append(row)

    return pd.DataFrame(data)



# ----Metal-Tracker ------
# Перебираем страницы
page = site('https://www.metal-tracker.com/')
# из очередной страницы вытаскиваем информацию

data = Get_Groups_Metal_Tracker(page)

dirname = os.path.dirname(__file__) + '/'

# Сбрасываем скачанные данные в файл
data.to_excel(dirname + 'metal-tracker.xlsx', 'data')

import subprocess

subprocess.Popen(dirname + 'metal-tracker.xlsx', shell=True)
