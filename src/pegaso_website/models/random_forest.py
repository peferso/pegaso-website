def random_forest(params):

    brd = params["Brand"]
    kms = params["Kilometers"]
    pwr = params["Power"]
    yyr = params["Year"]

    price = float(pwr)*100000.0 - float(kms)

    return price