import datetime
import sqlite3
import pandas as pd
import requests
import json
from os.path import dirname, abspath

import matplotlib.pyplot as plt
import numpy as np

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app.models import *

currency_columns = {
    'date': 0,
    'BYR': 1,
    'USD': 2,
    'EUR': 3,
    'KZT': 4,
    'UAH': 5,
    'AZN': 6,
    'KGS': 7,
    'UZS': 8,
    'GEL': 9
}

def index(request):
    return render(request, 'index.html')

def demand_by_count(request):
    conn = sqlite3.connect('db.sqlite3')
    query = """SELECT substr(published_at, 1, 4) AS 'Год',
                COUNT(published_at) AS 'Количество'
                FROM vacancies
                GROUP BY `Год`;"""
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()

    for stat in data:
        cursor.execute(f"""UPDATE demand_stats SET total_count = {stat[1]} WHERE year = {stat[0]}""")
        conn.commit()

    conn.close()
    return HttpResponse(status=200)

def demand_by_average(request):
    conn = sqlite3.connect('db.sqlite3')
    query = """SELECT substr(published_at, 1, 7) AS 'Год',
                AVG(CASE
                    WHEN (salary_to IS NULL AND salary_from IS NULL )
                        THEN 0
                    WHEN (salary_to IS NULL)
                        THEN ROUND(salary_from, 2)
                    WHEN (salary_from IS NULL)
                        THEN ROUND(salary_to, 2)
                    ELSE
                        ROUND((salary_to + salary_from) / 2, 2)
                    END) AS 'Средняя з/п',
                salary_currency AS 'Валюта',
                COUNT()
                FROM vacancies
                WHERE `Валюта` IS NOT NULL
                GROUP BY `Год`, `Валюта`;"""
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    total_year = {}
    count_year = {}
    for vac in data:
        sql_query = f"""SELECT * FROM currencies WHERE date = '{vac[0]}'"""
        cursor.execute(sql_query)
        if vac[2] == 'RUR':
            currency = 1
        else:
            cur_data = cursor.fetchall()[0]
            currency = cur_data[currency_columns[vac[2]]]


        if(currency == float('nan') or currency is None):
            continue

        year = vac[0][:4]
        if year not in total_year.keys():
            total_year[year] = vac[1] * currency
            count_year[year] = 1
        else:
            total_year[year] += vac[1] * currency
            count_year[year] += 1

    for year in total_year.keys():
        cursor.execute(f"""UPDATE demand_stats SET total_average = {round(total_year[year] / count_year[year], 2)} WHERE year = {year}""")
        conn.commit()

    conn.close()
    return HttpResponse(status=200)


def demand_by_count_prof(request):
    conn = sqlite3.connect('db.sqlite3')
    query = """SELECT substr(published_at, 1, 4) AS 'Год',
                COUNT(published_at) AS 'Количество'
                FROM vacancies
                WHERE instr(name, 'fullstack') OR
                      instr(name, 'фулстак') OR
                      instr(name, 'фуллтак') OR
                      instr(name, 'фуллстэк') OR
                      instr(name, 'фулстэк') OR
                      instr(name, 'full stack')
                GROUP BY `Год`;"""
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()

    for stat in data:
        cursor.execute(f"""UPDATE demand_stats SET prof_count = {stat[1]} WHERE year = {stat[0]}""")
        conn.commit()

    conn.close()
    return HttpResponse(status=200)


def demand_by_average_prof(request):
    conn = sqlite3.connect('db.sqlite3')
    query = """SELECT substr(published_at, 1, 7) AS 'Год',
                AVG(CASE
                    WHEN (salary_to IS NULL AND salary_from IS NULL )
                        THEN 0
                    WHEN (salary_to IS NULL)
                        THEN ROUND(salary_from, 2)
                    WHEN (salary_from IS NULL)
                        THEN ROUND(salary_to, 2)
                    ELSE
                        ROUND((salary_to + salary_from) / 2, 2)
                    END) AS 'Средняя з/п',
                salary_currency AS 'Валюта'
                FROM vacancies
                WHERE `Валюта` IS NOT NULL AND(
                      instr(name, 'fullstack') OR
                      instr(name, 'фулстак') OR
                      instr(name, 'фуллтак') OR
                      instr(name, 'фуллстэк') OR
                      instr(name, 'фулстэк') OR
                      instr(name, 'full stack'))
                GROUP BY `Год`, `Валюта`;"""
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    total_year = {}
    count_year = {}
    for vac in data:
        sql_query = f"""SELECT * FROM currencies WHERE date = '{vac[0]}'"""
        cursor.execute(sql_query)
        if vac[2] == 'RUR':
            currency = 1
        else:
            cur_data = cursor.fetchall()[0]
            currency = cur_data[currency_columns[vac[2]]]

        if(currency == float('nan') or currency is None):
            continue

        year = vac[0][:4]
        if year not in total_year.keys():
            total_year[year] = vac[1] * currency
            count_year[year] = 1
        else:
            total_year[year] += vac[1] * currency
            count_year[year] += 1

    for year in total_year.keys():
        cursor.execute(f"""UPDATE demand_stats SET prof_average = {round(total_year[year] / count_year[year], 2)} WHERE year = {year}""")
        conn.commit()

    conn.close()
    return HttpResponse(status=200)

def update_geo_total_avg(request):
    conn = sqlite3.connect('db.sqlite3')
    query = """SELECT area_name AS 'Город',
                    ROUND(AVG(CASE
                            WHEN (salary_to IS NULL AND salary_from IS NULL )
                                THEN 0
                            WHEN (salary_to IS NULL)
                                THEN ROUND(salary_from, 2)
                            WHEN (salary_from IS NULL)
                                THEN ROUND(salary_to, 2)
                            ELSE
                                ROUND((salary_to + salary_from) / 2, 2)
                            END), 2) AS 'Уровень зарплат по городам',
                    substr(published_at, 1, 7) AS 'Дата',
                    salary_currency AS 'Валюта',
                    SUM(CASE WHEN salary_to IS NULL AND salary_from IS NULL THEN 0 ELSE 1 END) AS 'Количество'
                    FROM vacancies
                    WHERE `Валюта` IS NOT NULL
                    GROUP BY `Город`, `Дата`, `Валюта`;"""
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()

    total_area = {}
    count_curr_area = {}
    count_area = {}
    total_count = 0
    for vac in data:
        sql_query = f"""SELECT * FROM currencies WHERE date = '{vac[2]}'"""
        cursor.execute(sql_query)
        if vac[3] == 'RUR':
            currency = 1
        else:
            cur_data = cursor.fetchall()[0]
            currency = cur_data[currency_columns[vac[3]]]

        if (currency == float('nan') or currency is None):
            continue

        area = vac[0]
        if area not in total_area.keys():
            total_area[area] = vac[1] * currency
            count_curr_area[area] = 1
            count_area[area] = vac[4]
        else:
            total_area[area] += vac[1] * currency
            count_curr_area[area] += 1
            count_area[area] += vac[4]

        total_count += vac[4]

    cursor.execute("""DELETE FROM geography_total_average""")
    conn.commit()

    for area in total_area.keys():
        if (count_area[area] / total_count >= 0.01):
            cursor.execute(
                f"""INSERT INTO geography_total_average VALUES ('{area}', {round(total_area[area] / count_curr_area[area], 2)})""")
            conn.commit()

    conn.close()

    return HttpResponse(status=200)

def update_geo_total_count(request):
    conn = sqlite3.connect('db.sqlite3')
    query = """SELECT area_name AS 'Город',
                ROUND(cast(COUNT(*) as float) / cast((SELECT COUNT (*) from vacancies) as float) * 100.0, 2) as 'Доля вакансий'
                FROM vacancies
                GROUP BY area_name
                HAVING COUNT(*) >= (SELECT COUNT(*) * 0.01 FROM vacancies)
                ORDER BY `Доля вакансий` DESC
                LIMIT 10;"""
    df = pd.read_sql(query, conn)
    df.to_sql('geography_total_count', conn, if_exists='replace', index=False)

    return HttpResponse(status=200)

def update_geo_prof_avg(request):
    conn = sqlite3.connect('db.sqlite3')
    query = """SELECT area_name AS 'Город',
                ROUND(AVG(CASE
                        WHEN (salary_to IS NULL AND salary_from IS NULL )
                            THEN 0
                        WHEN (salary_to IS NULL)
                            THEN ROUND(salary_from, 2)
                        WHEN (salary_from IS NULL)
                            THEN ROUND(salary_to, 2)
                        ELSE
                            ROUND((salary_to + salary_from) / 2, 2)
                        END), 2) AS 'Уровень зарплат по городам',
                substr(published_at, 1, 7) AS 'Дата',
                salary_currency AS 'Валюта',
                COUNT(published_at) AS 'Количество'
                FROM vacancies
                WHERE `Валюта` IS NOT NULL AND (
                      instr(name, 'fullstack') OR
                      instr(name, 'фулстак') OR
                      instr(name, 'фуллтак') OR
                      instr(name, 'фуллстэк') OR
                      instr(name, 'фулстэк') OR
                      instr(name, 'full stack')
                        )
                GROUP BY `Город`, `Дата`, `Валюта`;"""
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()

    total_area = {}
    count_curr_area = {}
    count_area = {}
    total_count = 0
    for vac in data:
        sql_query = f"""SELECT * FROM currencies WHERE date = '{vac[2]}'"""
        cursor.execute(sql_query)
        if vac[3] == 'RUR':
            currency = 1
        else:
            cur_data = cursor.fetchall()[0]
            currency = cur_data[currency_columns[vac[3]]]

        if (currency == float('nan') or currency is None):
            continue

        area = vac[0]
        if area not in total_area.keys():
            total_area[area] = vac[1] * currency
            count_curr_area[area] = 1
            count_area[area] = vac[4]
        else:
            total_area[area] += vac[1] * currency
            count_curr_area[area] += 1
            count_area[area] += vac[4]

        total_count += vac[4]

    cursor.execute("""DELETE FROM geography_prof_average""")
    conn.commit()

    for area in total_area.keys():
        if (count_area[area] / total_count >= 0.01):
            cursor.execute(f"""INSERT INTO geography_prof_average VALUES ('{area}', {round(total_area[area] / count_curr_area[area], 2)})""")
            conn.commit()

    conn.close()

    return HttpResponse(status=200)

def update_geo_prof_count(request):
    conn = sqlite3.connect('db.sqlite3')
    query = """SELECT area_name AS 'Город',
                ROUND(cast(COUNT(*) as float) / cast((SELECT COUNT (*) from vacancies WHERE(instr(name, 'fullstack') OR
                      instr(name, 'фулстак') OR
                      instr(name, 'фуллтак') OR
                      instr(name, 'фуллстэк') OR
                      instr(name, 'фулстэк') OR
                      instr(name, 'full stack'))) as float) * 100.0, 2) as 'Доля вакансий'
                FROM vacancies
                WHERE(instr(name, 'fullstack') OR
                      instr(name, 'фулстак') OR
                      instr(name, 'фуллтак') OR
                      instr(name, 'фуллстэк') OR
                      instr(name, 'фулстэк') OR
                      instr(name, 'full stack'))
                GROUP BY area_name
                HAVING COUNT(*) >= (SELECT COUNT(*) * 0.01 FROM vacancies WHERE(instr(name, 'fullstack') OR
                      instr(name, 'фулстак') OR
                      instr(name, 'фуллтак') OR
                      instr(name, 'фуллстэк') OR
                      instr(name, 'фулстэк') OR
                      instr(name, 'full stack')))
                ORDER BY `Доля вакансий` DESC
                LIMIT 10;"""
    df = pd.read_sql(query, conn)
    df.to_sql('geography_prof_count', conn, if_exists='replace', index=False)

    return HttpResponse(status=200)

def update_total_key_skills(request):
    conn = sqlite3.connect('db.sqlite3')
    query = """SELECT key_skills, substr(published_at, 1, 4) FROM vacancies WHERE key_skills IS NOT NULL"""
    cursor = conn.cursor()
    cursor.execute(query)
    vacancy_skills = cursor.fetchall()
    skills_date = {}

    for skills in vacancy_skills:
        separated_skills = skills[0].split('\n')
        if skills[1] not in skills_date:
            skills_date[skills[1]] = {}
        for skill in separated_skills:
            if skill in skills_date[skills[1]]:
                skills_date[skills[1]][skill] += 1
            else:
                skills_date[skills[1]][skill] = 1

    for key, value in skills_date.items():
        skills_date[key] = json.dumps({item[0]: item[1] for index, item in
                                       enumerate(list(sorted(value.items(), key=lambda x: x[1], reverse=True))) if
                                       index < 20})

    sorted_skills = sorted(skills_date.items(), key=lambda item: item[0])

    cursor.execute("""DELETE FROM skills_total;""")

    for index, skill in enumerate(sorted_skills):
        cursor.execute(f"""INSERT INTO skills_total VALUES ({skill[0]}, '{skill[1]}');""")
        conn.commit()
        if index == 19:
            break

    conn.close()

    return HttpResponse(status=200)

def update_prof_key_skills(request):
    conn = sqlite3.connect('db.sqlite3')
    query = """SELECT key_skills, substr(published_at, 1, 4) FROM vacancies WHERE key_skills IS NOT NULL AND 
                (instr(name, 'fullstack') OR
                instr(name, 'фулстак') OR
                instr(name, 'фуллтак') OR
                instr(name, 'фуллстэк') OR
                instr(name, 'фулстэк') OR
                instr(name, 'full stack'))"""
    cursor = conn.cursor()
    cursor.execute(query)
    vacancy_skills = cursor.fetchall()
    skills_date = {}

    for skills in vacancy_skills:
        separated_skills = skills[0].split('\n')
        if skills[1] not in skills_date:
            skills_date[skills[1]] = {}
        for skill in separated_skills:
            if skill in skills_date[skills[1]]:
                skills_date[skills[1]][skill] += 1
            else:
                skills_date[skills[1]][skill] = 1

    for key, value in skills_date.items():
        skills_date[key] = json.dumps({item[0]: item[1] for index, item in enumerate(list(sorted(value.items(), key=lambda x: x[1], reverse=True))) if index < 20})

    sorted_skills = sorted(skills_date.items(), key=lambda item: item[0])

    cursor.execute("""DELETE FROM skills_prof;""")

    for index, skill in enumerate(sorted_skills):
        cursor.execute(f"""INSERT INTO skills_prof VALUES ({skill[0]}, '{skill[1]}');""")
        conn.commit()
        if index == 19:
            break

    conn.close()

    return HttpResponse(status=200)


def clean_vacancy(vacancy):
    vacancy['area'] = vacancy['area']['name'] if vacancy['area'].__contains__('name') else 'Нет данных'
    if vacancy['salary']['from'] != None and vacancy['salary']['to'] != None and vacancy['salary']['from'] != \
                                                                                 vacancy['salary']['to']:
        vacancy[
            'salary'] = f"от {'{0:,}'.format(vacancy['salary']['from']).replace(',', ' ')} до {'{0:,}'.format(vacancy['salary']['to']).replace(',', ' ')} {vacancy['salary']['currency']}"
    elif vacancy['salary']['from'] != None:
        vacancy[
            'salary'] = f"{'{0:,}'.format(vacancy['salary']['from']).replace(',', ' ')} {vacancy['salary']['currency']}"
    elif vacancy['salary']['to'] != None:
        vacancy[
            'salary'] = f"{'{0:,}'.format(vacancy['salary']['to']).replace(',', ' ')} {vacancy['salary']['currency']}"
    else:
        vacancy['salary'] = 'Нет данных'
    vacancy['key_skills'] = ', '.join(map(lambda x: x['name'], vacancy['key_skills']))
    return vacancy


def get_vacancies(request):
    try:
        data = []
        info = requests.get('https://api.hh.ru/vacancies?text=%22fullstack%22&specialization=1&per_page=100').json()
        for row in info['items']:
            if any(x in row['name'].lower() for x in ['fullstack', 'фулстак', 'фуллтак', 'фуллстэк', 'фулстэк', 'full stack']) and not row['salary'] is None:
                data.append({'id': row['id'], 'published_at': row['published_at']})
        data = sorted(data, key=lambda x: x['published_at'])
        vacancies = {}
        for index, vacancy in enumerate(data[len(data) - 10:]):
            vacancies[index] = clean_vacancy(requests.get(f'https://api.hh.ru/vacancies/{vacancy["id"]}').json())
        return JsonResponse(vacancies)
    except Exception as e:
        print(e)
        print(datetime.datetime.now())
        return HttpResponse(status=500)

def update_demand_graphs(request):
    con = sqlite3.connect('db.sqlite3')
    df = pd.read_sql('SELECT * FROM demand_stats', con, index_col=None)

    width = 0.4

    years = [df['year'][i] for i in range(21)]
    total_average = [df['total_average'][i] for i in range(21)]
    prof_average = [df['prof_average'][i] for i in range(21)]
    i = np.arange(len(years))

    plt.figure().set_figwidth(12)
    plt.bar(i + width / 2, total_average, width, label='Все профессии')
    plt.bar(i + width * 1.5, prof_average, width, label='Fullstack-разработчик')
    plt.xticks(i + width, years)
    plt.title('Уровень зарплат по годам')
    plt.legend(fontsize=12)

    parent_dir = dirname(dirname(abspath(__file__)))
    plt.savefig(parent_dir + '/media/demand_average.png')

    return HttpResponse(status=200, content='Graphs updated!')

def update_geo_graphs(request):
    con = sqlite3.connect('db.sqlite3')
    df = pd.read_sql('SELECT * FROM geography_prof_average', con, index_col=None)
    new_df = df.sort_values(['average'], ascending=False)
    area_names = list(new_df['area_name'])
    averages = list(new_df['average'])

    fig, sub = plt.subplots(1, 2)

    fig.set_figwidth(13)
    sub[0].barh(area_names, averages, align='center')
    sub[0].invert_yaxis()
    sub[0].grid(axis='x')
    sub[0].tick_params(axis='x', labelsize=8)
    sub[0].tick_params(axis='y', labelsize=6)
    sub[0].set_title('Уровень зарплат по городам')

    df = pd.read_sql('SELECT * FROM geography_prof_count', con, index_col=None)
    area_names = list(df['area_name'])
    counts = list(df['count'])
    area_names.append('Другие')
    counts.append(100 - sum(counts))

    sub[1].set_prop_cycle(
        color=['#0000FF', '#DC143C', '#A52A2A', '#7FFF00', '#8A2BE2', '#000000', '#D2691E', '#008B8B', '#B8860B',
               '#006400', '#FF8C00', '#8B0000', '#2F4F4F', '#FF1493', '#FFD700', '#00FF00', '#BA55D3', '#FF4500',
               '#800080'])
    sub[1].pie(counts, labels=area_names, textprops={'fontsize': 8}, startangle=120)

    sub[1].set_title('Доля вакансий по городам')

    parent_dir = dirname(dirname(abspath(__file__)))
    plt.savefig(parent_dir + '/media/geo_graphs.png')

    return HttpResponse(status=200, content='Graphs updated!')

def update_skills_graphs(request):
    con = sqlite3.connect('db.sqlite3')
    df = pd.read_sql('SELECT * FROM skills_prof', con, index_col=None)
    years = list(df['date'])
    averages = list(df['stats'])

    fig, sub = plt.subplots(3, 3)
    fig.set_figwidth(15)
    fig.set_figheight(15)
    year_index = 0

    for x in range(3):
        for y in range(3):
            ax = sub[x, y]
            data = json.loads(averages[year_index])
            names = [x for index, x in enumerate(data.keys()) if index < 10]
            counts = [x for index, x in enumerate(data.values()) if index < 10]
            ax.bar(names, counts, width=0.4)
            ax.set_xticks(np.arange(len(names)), names, rotation=50)
            ax.set_title(years[year_index])
            ax.xaxis.labelpad = 20

            year_index += 1

    fig.suptitle('Ключевые навыки для Fullstack-разработчика по годам', fontsize=24)
    fig.tight_layout(pad=1.5)
    parent_dir = dirname(dirname(abspath(__file__)))
    plt.savefig(parent_dir + '/media/skills_graphs.png')

    return HttpResponse(status=200, content='Graphs updated!')