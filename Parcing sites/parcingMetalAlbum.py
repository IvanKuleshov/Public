# -*- coding: utf-8 -*-
# python 3.7.9
# pip install beautifulsoup4
# pip install lxml
"""
    Синтаксис разбора:
    есть тег: <div class='user_name' href='http://site.ru'>Город:</div>
    soup.find('div') - найдет содержимое тега
    soup.find('div', class_='user_name') - найдет href и город. class пишется с префиксом '_'
        более правильный синтаксис: soup.find('div', {'class', 'user_name'})
    soup.find('div', class_='user_name').get('href') - найдет содержимое ссылки, http://site.ru
    soup.find('div', class_='user_name').text - найдет строку "Город:"
"""

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


def get_parcing_html_text(page: str) -> str:
    try:
        headers = {"User-Agent":
                       "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"}

        r = requests.get(page, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    return r.text


def Get_Groups_Darkalbum(page: str, stop_link: str) -> Tuple[pd.DataFrame, bool]:
    soup = BeautifulSoup(page, 'lxml')

    tracks = soup.find(class_='floats clearfix')
    groups = tracks.findAll(class_='short-tablet clearfix')

    data = []
    for group in groups:
        row = {'Тип': '-', 'Год выхода': '-', 'Регион': '-', 'Жанры': '-', 'Продолжительность': '-', 'Лейбл': '-',
               'Группа': '-', 'Альбом': '-',
               'Ссылка': group.find('a').get('href')}

        #  Проверяем на то, что достигнута ссылка прошлого раза
        if row['Ссылка'] == stop_link:
            return pd.DataFrame(data), True

        #  Читаем характеристики альбома: Тип, год выхода и т.д.
        info = group.find(class_='sh-list').findAll('li')
        for inf in info:
            s = inf.text.split(':', 1)
            if s[0] in row.keys():
                row[s[0].strip()] = s[1].strip()

        #  Проходим на карточку группы и читам название альбома и группы из соответствующих полей
        soup = BeautifulSoup(get_parcing_html_text(row['Ссылка']), 'lxml')
        row['Альбом'] = soup.find('span', {'itemprop': 'inAlbum'}).text
        row['Группа'] = soup.find('span', {'itemprop': 'byArtist'}).text

        data.append(row)

    return pd.DataFrame(data), False


dirname = os.path.dirname(__file__) + '/'

# ---- Darkalbum.ru
try:
    with open(dirname + 'parcing_option.json', 'r') as f:
        options = json.load(f)

except (FileNotFoundError, json.decoder.JSONDecodeError) as err:
    options = {"link": ""}

group_data = pd.DataFrame.from_dict({})

# Перебираем страницы
for i in range(50):
    page = get_parcing_html_text('https://darkalbum.ru/albums/page/' + str(i + 1) + '/')  # очередная страница
    sleep(1)
    data, status = Get_Groups_Darkalbum(page, options['link'])  # получаем информацию по альбомам на странице
    group_data = group_data.append(data)  # добавляем очередную страницу

    if status:  # выход, если пусто
        break

# ссылку на последний скачанный альбом добавляем в опции
try:
    with open(dirname + 'parcing_option.json', 'w') as f:
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
    group_data_old = pd.read_excel(dirname + 'metal-albums.xlsx', 'data')
except FileNotFoundError:
    group_data_old = pd.DataFrame([])

writer = pd.ExcelWriter(dirname + 'metal-albums.xlsx')

#  Сохраняем для вывода в нужной последовательности
col_order = ['Группа', 'Альбом', 'Год выхода', 'Жанры',
             'Тип', 'Продолжительность', 'Регион', 'Лейбл', 'Рейтинг', 'Ссылка']
group_data = group_data[col_order]

group_data.to_excel(writer, 'new', index=False)
group_data = group_data.append(group_data_old)
group_data.to_excel(writer, 'data', index=False)
writer.save()

subprocess.Popen(dirname + 'metal-albums.xlsx', shell=True)
