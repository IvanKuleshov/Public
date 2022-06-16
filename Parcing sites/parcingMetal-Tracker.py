# -*- coding: utf-8 -*-
# python 3.7.9
# pip install beautifulsoup4
# pip install lxml

import pandas as pd
from bs4 import BeautifulSoup
import requests
from time import sleep  # для выставления задержки перед запросом, можно убрать
from typing import Tuple  # для type hinting у функции Get_Groups_Darkalbum, можно убрать и удалить -> у функции
import json
import os
import subprocess
import tkinter as tk
from tkinter import messagebox


def get_parcing_html_text(page: str, data: dict) -> str:
    try:
        headers = {"User-Agent":
                       "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"}

        r = requests.post(url=page, data=data, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    return r.text


def Get_Groups_Metal_Tracker(page: str, stop_link: str) -> Tuple[pd.DataFrame, bool]:
    soup = BeautifulSoup(page, 'lxml')

    groups = soup.findAll('center')
    infos = soup.findAll(class_='update')

    data = []
    for group, info in zip(groups, infos):
        row = {'Год': '-', 'Стиль': '-', 'Формат': '-', 'Страна': '-', 'Добавлено': '-', 'Размер': '-',
               'Группа': '-', 'Альбом': '-',
               'Ссылка': 'https://www.metal-tracker.com' + group.find('a').get('href')}

        s = group.find('h3').text.split(' - ', 1)
        row['Группа'], row['Альбом'] = s[0], s[1]

        #  Проверяем на то, что достигнута ссылка прошлого раза
        if row['Ссылка'] == stop_link:
            return pd.DataFrame(data), True

        info = info.find(class_='basic_data').findAll('li')
        for inf in info:
            s = inf.text.split(':')
            if s[0] in ['Год', 'Стиль', 'Формат', 'Страна', 'Добавлено', 'Размер']:
                row[s[0]] = s[1].strip()

        data.append(row)

    return pd.DataFrame(data), False


dirname = os.path.dirname(__file__) + '/'

# ---- https://www.metal-tracker.com
try:
    with open(dirname + 'parcing_option_mt.json', 'r') as f:
        options = json.load(f)

except (FileNotFoundError, json.decoder.JSONDecodeError) as err:
    options = {"link": ""}

group_data = pd.DataFrame.from_dict({})

# Перебираем страницы
for i in range(100):
    page = get_parcing_html_text('https://www.metal-tracker.com/site/getupdates.html',
                                 data={'page': i})  # очередная страница
    sleep(2)
    data, status = Get_Groups_Metal_Tracker(page, options['link'])  # получаем информацию по альбомам на странице
    group_data = group_data.append(data)  # добавляем очередную страницу

    if status:  # выход, если пусто
        break

# ссылку на последний скачанный альбом добавляем в опции
try:
    with open(dirname + 'parcing_option_mt.json', 'w') as f:
        options['link'] = group_data.iloc[0]['Ссылка']
        json.dump(options, f)
except Exception as err:
    pass

#  Определяем, не вышли ли обновления наших любимых групп
if not group_data.empty:
    favorite_bands = pd.read_excel('favorite_bands.xlsx')
    group_data = group_data.merge(favorite_bands, how='left', on='Группа')
    favorite_bands = group_data.query('Рейтинг.notnull()')

    #  Если среди новых альбомов есть мои любимые группы - вывести messageBox об этом
    if not favorite_bands.empty:
        root = tk.Tk()
        tk.messagebox.showinfo('Новые альбомы любимых групп',
                               favorite_bands[['Группа', 'Альбом', 'Рейтинг']].to_string(index=False))
        root.withdraw()

# Сбрасываем скачанные данные в файл
try:
    group_data_old = pd.read_excel(dirname + 'metal-tracker.xlsx', 'data')
except FileNotFoundError:
    group_data_old = pd.DataFrame([])

writer = pd.ExcelWriter(dirname + 'metal-tracker.xlsx')

#  Сохраняем для вывода в нужной последовательности
col_order = ['Группа', 'Альбом', 'Год', 'Стиль',
             'Формат', 'Размер', 'Страна', 'Добавлено', 'Рейтинг', 'Ссылка']
group_data = group_data[col_order]

group_data.to_excel(writer, 'new', index=False)
group_data = group_data.append(group_data_old)
group_data.to_excel(writer, 'data', index=False)
writer.save()

subprocess.Popen(dirname + 'metal-tracker.xlsx', shell=True)
