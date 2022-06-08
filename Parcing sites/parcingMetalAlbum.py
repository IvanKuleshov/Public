# pip install beautifulsoup4
# pip install lxml

import pandas as pd
from bs4 import BeautifulSoup
import json
import os


def site(page: str):
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


def Get_Groups_Darkalbum(page: str, stop_link: str):
    soup = BeautifulSoup(page, 'lxml')

    tracks = soup.find(class_='floats clearfix')
    groups = tracks.findAll(class_='short-tablet clearfix')

    data = []
    for group in groups:
        row = {'Тип': '-', 'Год выхода': '-', 'Регион': '-', 'Жанры': '-', 'Продолжительность': '-', 'Лейбл': '-',
               'Группа': group.find('a').text,
               'Ссылка': group.find('a').get('href')}

        # Проверяем на то, что достигнута ссылка прошлого раза
        if row['Ссылка'] == stop_link:
            return pd.DataFrame(data), True

        info = group.find(class_='sh-list').findAll('li')
        for inf in info:
            s = inf.text.split(':', 1)
            if s[0] in row.keys():
                row[s[0].strip()] = s[1].strip()

        data.append(row)

    return pd.DataFrame(data), False


# ----Metal-Tracker ------
# Перебираем страницы
# page = site('https://www.metal-tracker.com/')
# из очередной страницы вытаскиваем информацию
# data = Get_Groups_Metal_Tracker(page)

dirname = os.path.dirname(__file__) + '/'

# ---- Darkalbum.ru
with open(dirname + 'parcing_option.json', 'r') as f:
    try:
        options = json.load(f)
    except:
        options = {"link": ""}

group_data = pd.DataFrame.from_dict({})

# Перебираем страницы
for i in range(55):
    page = site('https://darkalbum.ru/albums/page/' + str(i + 1) + '/')  # очередная страница
    data, status = Get_Groups_Darkalbum(page, options['link'])  # получаем информацию по альбомам на странице
    group_data = group_data.append(data)  # добавляем очередную страницу

    if status:  # выход, если пусто
        break

# ссылку на последний скачанный альбом добавляем в опции
with open(dirname + 'parcing_option.json', 'w') as f:
    try:
        options['link'] = group_data.iloc[0]['Ссылка']
    except:
        pass
    json.dump(options, f)

# Сбрасываем скачанные данные в файл
group_data_old = pd.read_excel(dirname + 'metal-albums.xlsx', 'data')

writer = pd.ExcelWriter(dirname + 'metal-albums.xlsx')

group_data.to_excel(writer, 'new', index=False)
group_data = group_data.append(group_data_old)
group_data.to_excel(writer, 'data', index=False)
writer.save()

import subprocess

subprocess.Popen(dirname + 'metal-albums.xlsx', shell=True)
