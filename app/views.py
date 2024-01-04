import sqlite3
import pandas as pd

from django.http import HttpResponse
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

