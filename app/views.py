import datetime
import sqlite3
import pandas as pd
import requests

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

def hello(request):
    return render(request, 'hello.html', {'hello': 'hello'})

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
    query = """SELECT key_skills FROM vacancies WHERE key_skills IS NOT NULL"""
    cursor = conn.cursor()
    cursor.execute(query)
    vacancy_skills = cursor.fetchall()
    skills_count = {}
    for skills in vacancy_skills:
        separated_skills = skills[0].split('\n')
        for skill in separated_skills:
            if skill in skills_count:
                skills_count[skill] += 1
            else:
                skills_count[skill] = 1

    sorted_skills = sorted(skills_count.items(), key=lambda item: item[1], reverse=True)

    cursor.execute("""DELETE FROM skills_total;""")

    for index, skill in enumerate(sorted_skills):
        cursor.execute(f"""INSERT INTO skills_total VALUES ('{skill[0]}', {skill[1]});""")
        conn.commit()
        if index == 19:
            break

    conn.close()

    return HttpResponse(status=200)

def update_prof_key_skills(request):
    conn = sqlite3.connect('db.sqlite3')
    query = """SELECT key_skills FROM vacancies WHERE key_skills IS NOT NULL AND 
                (instr(name, 'fullstack') OR
                instr(name, 'фулстак') OR
                instr(name, 'фуллтак') OR
                instr(name, 'фуллстэк') OR
                instr(name, 'фулстэк') OR
                instr(name, 'full stack'))"""

    cursor = conn.cursor()
    cursor.execute(query)
    vacancy_skills = cursor.fetchall()
    skills_count = {}
    for skills in vacancy_skills:
        separated_skills = skills[0].split('\n')
        for skill in separated_skills:
            if skill in skills_count:
                skills_count[skill] += 1
            else:
                skills_count[skill] = 1

    sorted_skills = sorted(skills_count.items(), key=lambda item: item[1], reverse=True)

    cursor.execute("""DELETE FROM skills_prof;""")

    for index, skill in enumerate(sorted_skills):
        cursor.execute(f"""INSERT INTO skills_prof VALUES ('{skill[0]}', {skill[1]});""")
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
