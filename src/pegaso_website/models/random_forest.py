import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import matplotlib.pyplot as plt
import base64
from io import BytesIO


def random_forest(params):

    brd = params["brand"]
    kms = params["kilometers"]
    pwr = params["power"]
    dor = params["doors"]
    yyr = params["years"]

    features_labels = ['kilometers', 'power', 'doors', 'years', 'brand_AUDI', 'brand_BMW', 'brand_CITROEN', 'brand_FIAT', 'brand_FORD',
     'brand_HYUNDAI', 'brand_JAGUAR', 'brand_KIA', 'brand_LANDROVER', 'brand_MAZDA', 'brand_MERCEDES', 'brand_MINI',
     'brand_NISSAN', 'brand_OPEL', 'brand_PEUGEOT', 'brand_PORSCHE', 'brand_RENAULT', 'brand_SEAT', 'brand_SKODA',
     'brand_SMART', 'brand_TOYOTA', 'brand_VOLKSWAGEN', 'brand_VOLVO']

    values = []

    for col in features_labels:
        if col.split('_')[0] == 'brand' and col.split('_')[1] == params['brand']:
            values.append(1)
        elif col.split('_')[0] == 'brand' and col.split('_')[1] != params['brand']:
            values.append(0)
        else:
            values.append(params[col])

    X = np.array(values)
    X = X.reshape(1, -1)
    rf = joblib.load("pegaso_website/models/rf_2022-02-12_22-41-03312819.joblib")

    price = rf.predict(X)
    price = round(price[0], 2)

    params_2 = params
    rows = []
    for years in range(yyr, yyr + 11):
        values = []
        params_2["years"] = years
        params_2["kilometers"] = int(params_2["kilometers"]) + int(params["kilometers"])/(max(int(params["years"]), 1))
        for col in features_labels:
            if col.split('_')[0] == 'brand' and col.split('_')[1] == params_2['brand']:
                values.append(1)
            elif col.split('_')[0] == 'brand' and col.split('_')[1] != params_2['brand']:
                values.append(0)
            else:
                values.append(params_2[col])
        rows.append(values)

    X = np.array(rows)

    prices = rf.predict(X)

    years = [y for y in range(yyr, yyr + 11)]
    chart = get_plot(years, prices)

    return price, chart

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64decode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(x,y):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 6))
    plt.title('Future price estimation in the following years at a similar km per year rate')
    plt.plot(x, y)
    plt.xlabel('Year')
    plt.ylabel('Price in Euros')
    plt.tight_layout()
    graph = get_graph()
    return graph
