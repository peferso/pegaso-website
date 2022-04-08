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
    kms_f = 0.0
    for i in range(0, yyr + 11):
        if kms == 0:
            kms_f = kms_f + 20000 / max(yyr, 1)
        else:
            kms_f = kms_f + int(kms) / max(yyr, 1)
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

    years = [y for y in range(0, yyr + 11)]

    forecast = get_plot_forecast(years, prices, yyr, price)

    data_prices = fetch_data_for_distr(brd)

    data_colplt_prc, data_colplt_kms, data_colplt_pwr, data_colplt_yrs = fetch_data_for_colplt(brd)

    distr = get_plot_distr(data_prices, 'price (Euros)', 'Frequency', 'Distribution for brand ',  price, brd)

    xl = 'kilometers'
    yl = 'price (Euros)'
    zl = 'power (CV)'
    title = 'Price vs Km distribution for brand ' + str(brd).capitalize()
    x = data_colplt_kms
    y = data_colplt_prc
    z = data_colplt_pwr
    colplt1 = get_plot_colmap(x, y, z, xl, yl, zl, np.amin(x), np.amax(x), np.amin(y), np.amax(y), title, kms, price)

    xl = 'years'
    yl = 'kilometers'
    zl = 'price (Euros)'
    x = data_colplt_yrs
    y = data_colplt_kms
    z = data_colplt_prc
    title = 'Kilometers vs years for brand ' + str(brd).capitalize()
    colplt2 = get_plot_colmap(x, y, z, xl, yl, zl, np.amin(x), np.amax(x), np.amin(y), np.amax(y), title, yyr, kms)

    data_colplt_prc, data_colplt_kms, data_colplt_pwr, data_colplt_yrs, data_colplt_brd = fetch_data_for_colplt_full()

    xl = 'kilometers'
    yl = 'price (Euros)'
    zl = 'years'
    x = data_colplt_kms
    y = data_colplt_prc
    z = data_colplt_yrs
    c = data_colplt_brd
    title = 'Price distribution among brands'
    colplt3 = get_plot_colmap_categories(x, y, z, c, xl, yl, zl, 0.0, 300000.0, 0.0, 200000.0, title, kms, price)

    mae, mape, pred_devaluations, prices_dev, power_dev, years_dev = build_devaluation_pred_data_set(brd)

    distr_dev = get_plot_distr(pred_devaluations, 'price devaluation (Euros)', 'Frequency', 'Distribution for brand ',
                               int(predict(brd, 1, pwr, dor, 0, 'predict_rf') - price), brd)

    xl = 'price (Euros)'
    yl = 'estimated price 0km (Euros)'
    zl = 'power'
    x = prices_dev
    y = pred_devaluations + prices_dev
    z = power_dev
    title = 'predicted price-km0 vs price ' + str(brd).capitalize()
    sctplt_dev = get_plot_colmap(x, y, z, xl, yl, zl, np.amin(x), np.amax(x), np.amin(y), np.amax(y), title, yyr, kms)

    return [price, mae, mape], prices, forecast, distr, colplt1, colplt2, colplt3, distr_dev, sctplt_dev

def get_query_data(query):
    connection = pymysql.connect(host=os.environ['DBHOST'],
                                 user=os.environ['DBUSER'],
                                 passwd=os.environ['DBPASS'],
                                 db="pegaso_db",
                                 charset='utf8')
    con_cursor = connection.cursor()
    con_cursor.execute(query)
    output = con_cursor.fetchall()
    return output

def predict(brd, kms, pwr, dor, yyr, model):
    API_ENDPOINT = os.environ['RF_API_ENDPOINT']
    response_API = requests.get('http://' +
                                API_ENDPOINT +
                                '/' + str(model) + '/' +
                                str(brd) + '/' +
                                str(kms) + '/' +
                                str(pwr) + '/' +
                                str(dor) + '/' +
                                str(yyr)
                                )
    price = round(float(response_API.text), 2)
    return price

def build_devaluation_pred_data_set(brd):
    output = get_query_data("select rd.price_c, pp.price_pred, pp.price_pred_if_new, pp.batch_ts, rd.power, rd.kilometers " +
                            "from                                   " +
                            "    raw_data rd,                       " +
                            "    predicted_prices_random_forest pp " +
                            "where                                  " +
                            "    rd.id=pp.id                       " +
                            "and                                    " +
                            "    rd.brand='" + str(brd) + "';       ")
    predictions = []
    values = []
    pred_devaluations = []
    power = []
    kilometers = []

    for i in output:
        prc = i[0]
        pred_prc = i[1]
        prc_new = i[2]
        power.append(i[4])
        kilometers.append(i[5])
        predictions.append(float(pred_prc))
        values.append(float(prc))
        pred_devaluations.append(int(prc_new - prc))
    predictions = np.array(predictions)
    values = np.array(values)
    pred_devaluations = np.array(pred_devaluations)
    power = np.array(power)
    kilometers= np.array(kilometers)
    mae = round(np.mean(abs(predictions - values)), 2)
    mape = round(np.mean(abs((predictions - values)/values * 100.0)), 2)
    return mae, mape, pred_devaluations, values, power, kilometers


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

def fetch_data_for_colplt(brand):
    connection = pymysql.connect(host=os.environ['DBHOST'],
                                 user=os.environ['DBUSER'],
                                 passwd=os.environ['DBPASS'],
                                 db="pegaso_db",
                                 charset='utf8')
    con_cursor = connection.cursor()
    con_cursor.execute( "select price_c, kilometers, power, year, batch_ts " +
                        "from                       " +
                        "    raw_data               " +
                        "where                      " +
                        "    power is not null      " +
                        "and                        " +
                        "    kilometers is not null " +
                        "and                        " +
                        "    year is not null       " +
                        "and                        " +
                        "    brand='" + str(brand) + "';")
    output = con_cursor.fetchall()
    data_colplt_prc = []
    data_colplt_kms = []
    data_colplt_pwr = []
    data_colplt_yyr = []
    for i in output:
        data_colplt_prc.append(i[0])
        data_colplt_kms.append(i[1])
        data_colplt_pwr.append(i[2])
        data_colplt_yyr.append( ( int(str(i[4]).split('-')[0]) - int(i[3]) ) )
    data_colplt_prc = np.array(data_colplt_prc)
    data_colplt_kms = np.array(data_colplt_kms)
    data_colplt_pwr = np.array(data_colplt_pwr)
    data_colplt_yyr = np.array(data_colplt_yyr)
    return data_colplt_prc, data_colplt_kms, data_colplt_pwr, data_colplt_yyr


def fetch_data_for_colplt_full():
    connection = pymysql.connect(host=os.environ['DBHOST'],
                                 user=os.environ['DBUSER'],
                                 passwd=os.environ['DBPASS'],
                                 db="pegaso_db",
                                 charset='utf8')
    con_cursor = connection.cursor()
    con_cursor.execute("select price_c, kilometers, power, year, batch_ts, brand " +
                       "from                       " +
                       "    raw_data               " +
                       "where                      " +
                       "    power is not null      " +
                       "and                        " +
                       "    kilometers is not null " +
                       "and                        " +
                       "    year is not null       " +
                       "and                        " +
                       "    brand in (             " +
                       "         select brand from brands_count where num_cars>1000 order by num_cars desc" +
                       "              );           ")
    output = con_cursor.fetchall()
    data_colplt_prc = []
    data_colplt_kms = []
    data_colplt_pwr = []
    data_colplt_yyr = []
    data_colplt_brd = []
    for i in output:
        data_colplt_prc.append(i[0])
        data_colplt_kms.append(i[1])
        data_colplt_pwr.append(i[2])
        data_colplt_yyr.append((int(str(i[4]).split('-')[0]) - int(i[3])))
        data_colplt_brd.append(str(i[5]))
    data_colplt_prc = np.array(data_colplt_prc)
    data_colplt_kms = np.array(data_colplt_kms)
    data_colplt_pwr = np.array(data_colplt_pwr)
    data_colplt_yyr = np.array(data_colplt_yyr)
    data_colplt_brd = np.array(data_colplt_brd)
    return data_colplt_prc, data_colplt_kms, data_colplt_pwr, data_colplt_yyr, data_colplt_brd


def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64decode(image_png)
    graph = graph.decode('utf8')
    buffer.close()
    return graph

def get_plot_forecast(x, y, year, price):
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
    plt.axhline(price, color='k', linestyle='dashed', linewidth=1)
    plt.axvline(year, color='k', linestyle='dashed', linewidth=1)
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

def get_plot_distr(data, xl, yl, title, price, brand):
    plt.close()
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 10))
    plt.tight_layout()
    fig, axs = plt.subplots(1, 1, figsize=(10, 10), tight_layout=True)
    axs.hist(data, bins=10, edgecolor='k', alpha=0.65)
    plt.title(title + str(brand))
    plt.axvline(price, color='k', linestyle='dashed', linewidth=1)
    plt.xlabel(xl)
    plt.ylabel(yl)
    fig = plt.gcf()
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    graph = urllib.parse.quote(string)
    return graph

def get_plot_colmap(x, y, z, xlb, ylb, zlb, x1, x2, y1, y2, title, xp, yp):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 10))
    plt.tight_layout()
    cm = plt.cm.get_cmap('RdYlBu')
    sc = plt.scatter(x, y, c=z, vmin=np.amin(z), vmax=np.amax(z), s=35, cmap=cm)
    plt.colorbar(sc).ax.set_ylabel(zlb, rotation=270, labelpad=+10)
    plt.title(title)
    plt.axhline(float(yp), color='k', linestyle='dashed', linewidth=1)
    plt.axvline(float(xp), color='k', linestyle='dashed', linewidth=1)
    plt.ylabel(ylb)
    plt.xlabel(xlb)
    plt.xlim([x1, x2])
    plt.ylim([y1, y2])
    fig = plt.gcf()
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    graph = urllib.parse.quote(string)
    return graph

def get_plot_colmap_categories(x, y, z, cat, xlb, ylb, zlb, x1, x2, y1, y2, title, xp, yp):
    plt.switch_backend('AGG')
    plt.figure(figsize=(10, 10))
    plt.tight_layout()
    cm = plt.cm.get_cmap('RdYlBu')
    #plt.rcParams.update({'figure.figsize': (10, 10), 'figure.dpi': 100})
    markers_l = ["+", "v", "."]
    i = 0
    for el in np.unique(cat):
        indices = np.where(cat == el)
        xi = x[indices]
        yi = y[indices]
        zi = z[indices]
        #sc = plt.scatter(xi, yi, c=z, vmin=np.amin(z), vmax=np.amax(z), s=35, cmap=cm)
        sc = plt.scatter(xi, yi, c=zi, vmin=np.amin(z), vmax=np.amax(z),  s=35, cmap=cm, marker=markers_l[i], label=str(el))
        i += 1
        if i == 3:
            break
    plt.colorbar(sc).ax.set_ylabel(zlb, rotation=270, labelpad=+10)
    plt.title(title)
    plt.legend(loc='best')
    plt.axhline(float(yp), color='k', linestyle='dashed', linewidth=1)
    plt.axvline(float(xp), color='k', linestyle='dashed', linewidth=1)
    plt.ylabel(ylb)
    plt.xlabel(xlb)
    plt.xlim([x1, x2])
    plt.ylim([y1, y2])
    fig = plt.gcf()
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    graph = urllib.parse.quote(string)
    return graph