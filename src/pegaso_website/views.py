from django.http import HttpResponse
from django.template import Template, Context
import os
import pymysql
import datetime
import pandas as pd
from django.template import loader
from django.shortcuts import render
from pegaso_website.models.random_forest import random_forest

def build_db_summary_context():
    connection = pymysql.connect(host=os.environ['DBHOST'],
                                 user=os.environ['DBUSER'],
                                 passwd=os.environ['DBPASS'],
                                 db="pegaso_db",
                                 charset='utf8')
    con_cursor = connection.cursor()
    con_cursor.execute('select * from recent_statistics;')
    output = con_cursor.fetchall()[0]
    ctx_vals = []
    ctx_vals.append(output[0])
    ctx_vals.append(round(float(output[1]), 2))
    ctx_vals.append(round(float(output[2]), 2))
    ctx_vals.append(output[3])
    ctx_vals.append(round(float(output[4]), 2))
    ctx_vals.append(round(float(output[5]), 2))
    ctx_vals.append(output[6])
    ctx_vals.append(round(float(output[7]), 2))
    ctx_vals.append(round(float(output[8]), 2))
    con_cursor.execute('select * from batch_dates_variables;')
    output = con_cursor.fetchall()[0]
    ctx_dates = []
    ctx_dates.append(output[0])
    ctx_dates.append(output[1])

    sql_query = pd.read_sql_query('select * from top_ten_most_expensive_current_week;', connection)
    dfex = pd.DataFrame(sql_query,
                        columns=['brand', 'model', 'price_c', 'price_f', 'kilometers', 'year', 'power', 'doors', 'professional_vendor' ])
    dfex = dfex.drop('professional_vendor', axis=1)
    dfex = dfex.drop('doors', axis=1)
    dfex = dfex.rename(
        columns={'brand': 'Brand', 'model': 'Model', 'price_c': 'Price (cash)', 'price_f': 'Price (financed)',
                                'kilometers': 'Kilometers', 'year': 'Year', 'power': 'Power (CV)' }    )

    sql_query = pd.read_sql_query('select * from top_ten_cheapest_current_week;', connection)
    dfch = pd.DataFrame(sql_query,
                        columns=['brand', 'model', 'price_c', 'price_f', 'kilometers', 'year', 'power', 'doors', 'professional_vendor'])
    dfch = dfch.drop('professional_vendor', axis=1)
    dfch = dfch.drop('doors', axis=1)
    dfch = dfch.rename(
        columns={'brand': 'Brand', 'model': 'Model', 'price_c': 'Price (cash)', 'price_f': 'Price (financed)',
                 'kilometers': 'Kilometers', 'year': 'Year', 'power': 'Power (CV)'})

    con_cursor.close()
    return ctx_vals, ctx_dates, dfex, dfch

def get_brands():
    connection = pymysql.connect(host=os.environ['DBHOST'],
                                 user=os.environ['DBUSER'],
                                 passwd=os.environ['DBPASS'],
                                 db="pegaso_db",
                                 charset='utf8')
    sql_query = pd.read_sql_query('select brand from brands_count where num_cars>100;', connection)
    dfex = pd.DataFrame(sql_query, columns=['brand'])
    brands_list = dfex['brand'].tolist()
    brands_list = sorted(brands_list)
    return brands_list

def home_page(request):

    brands_list = get_brands()

    return render(request, 'template_home.html', {'brandsList': brands_list, 'yearsList': range(int(datetime.date.today().strftime("%Y")), 1900, -1)})

def db_summary(request):

    list_of_values, ctx_dates, table_most_exp, table_cheapests = build_db_summary_context()

    return render(request, 'template_database.html', {"list": list_of_values, "last_update_date": ctx_dates, "top_ten_expensive": table_most_exp,  "top_ten_cheapests": table_cheapests})

def training_reports(request):

    return render(request, 'template_training.html')

def about(request):

    return render(request, 'template_about.html')

def results(request):

    input_brand = request.GET['br']
    input_klmts = request.GET['km']
    input_power = request.GET['pw']
    input_doors = request.GET['dr']
    input_yyear = request.GET['yr']

    input_parms = {
        "brand": input_brand,
        "kilometers": input_klmts,
        "power": input_power,
        "doors": input_doors,
        "years": datetime.datetime.now().date().year - int(input_yyear)
        }

    price, chart = random_forest(input_parms)

    return render(request, 'template_results.html', {'ts': datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"), 'inputParms': input_parms, 'pricePred': price, 'chart': chart})
