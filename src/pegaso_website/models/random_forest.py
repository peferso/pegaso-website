import pandas as pd
import os
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import requests
import urllib

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

    chart = get_plot(years, prices)

    return price, prices, chart

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64decode(image_png)
    graph = graph.decode('utf8')
    buffer.close()
    return graph

def get_plot(x,y):
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
    plt.figure(figsize=(10, 6))
    plt.title('Future price estimation in the following years at a similar km per year rate')
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
