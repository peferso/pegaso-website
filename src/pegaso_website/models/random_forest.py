import pandas as pd
import os
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import requests
import urllib
import pymysql
import numpy as np

def random_forest(params):

    brd = params["brand"]
    kms = params["kilometers"]
    pwr = params["power"]
    dor = params["doors"]
    yyr = params["age"]

    API_ENDPOINT = os.environ['RF_API_ENDPOINT']

    response_API = requests.get('http://' +
                                API_ENDPOINT +
                                '/predict_rf/' +
                                str(brd) + '/' +
                                str(kms) + '/' +
                                str(pwr) + '/' +
                                str(dor) + '/' +
                                str(yyr)
                                )

    price = round(float(response_API.text), 2)

    prices = []
    for i in range(yyr, yyr + 11):
        kms_f = int(kms) + int(kms)/max(yyr, 1) * yyr
        yyr_f = i
        response_API = requests.get('http://' +
                                    API_ENDPOINT +
                                    '/predict_rf/' +
                                    str(brd) + '/' +
                                    str(int(kms_f)) + '/' +
                                    str(pwr) + '/' +
                                    str(dor) + '/' +
                                    str(yyr_f)
                                    )
        prices.append(round(float(response_API.text), 2))

    years = [y for y in range(yyr, yyr + 11)]

    forecast = get_plot_forecast(years, prices)

    data = fetch_data_for_distr(brd)

    distr = get_plot_distr(data, price, brd)

    return price, prices, forecast, distr

def fetch_data_for_distr(brand):
    connection = pymysql.connect(host=os.environ['DBHOST'],
                                 user=os.environ['DBUSER'],
                                 passwd=os.environ['DBPASS'],
                                 db="pegaso_db",
                                 charset='utf8')
    con_cursor = connection.cursor()
    con_cursor.execute("select price_c from raw_data where brand='" + str(brand) + "';")
    output = con_cursor.fetchall()
    data = []
    for i in output:
        data.append(i[0])
    data = np.array(data)
    return data

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64decode(image_png)
    graph = graph.decode('utf8')
    buffer.close()
    return graph

def get_plot_forecast(x, y):
    '''
    #graph = get_graph()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64decode(image_png)
    graph = graph.decode('utf8')
    buffer.close()
    '''
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 10))
    plt.title('Price forecast at constant km/year rate')
    plt.plot(x, y)
    plt.xlabel('Age (years)')
    plt.ylabel('Price (Euros)')
    plt.tight_layout()
    fig = plt.gcf()
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    graph = urllib.parse.quote(string)
    return graph

def get_plot_distr(data, price, brand):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 10))
    plt.tight_layout()
    fig, axs = plt.subplots(1, 1, figsize=(10, 10), tight_layout=True)
    axs.hist(data, bins=10, edgecolor='k', alpha=0.65)
    plt.title('Price distribution for brand ' + str(brand))
    plt.axvline(price, color='k', linestyle='dashed', linewidth=1)
    plt.xlabel('Price (Euros)')
    plt.ylabel('Frequency')
    fig = plt.gcf()
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    graph = urllib.parse.quote(string)
    return graph