from xml.dom import minidom
import requests
import pandas as pd
from pandas import DataFrame


def get_exchange_rate(source: str, target: str = "EUR") -> pd.DataFrame:
    file = requests.get("https://sdw-wsrest.ecb.europa.eu/service/data/EXR/M.{}.{}.SP00.A?".format(source, target))
    with open("currency_ex_rate.xml", 'wb') as f:
        f.write(file.content)
    doc = minidom.parse("currency_ex_rate.xml")
    outer_layer = doc.getElementsByTagName("generic:Obs")
    df1 = pd.DataFrame(columns=["Time_Period", "Obs_Value"])
    counter = 0
    for i in outer_layer:
        inner_layer_perd = i.getElementsByTagName("generic:ObsDimension")[0]
        inner_layer_exrt = i.getElementsByTagName("generic:ObsValue")[0]
        time_period = inner_layer_perd.getAttribute("value")
        rate = float(inner_layer_exrt.getAttribute("value"))
        df1.loc[counter] = [time_period, rate]
        counter += 1

    return df1


def get_raw_data(identifier: str) -> pd.DataFrame:
    file = requests.get("https://sdw-wsrest.ecb.europa.eu/service/data/BP6/{}?".format(identifier))
    with open("currency_ex_rate_custom.xml", 'wb') as f:
        f.write(file.content)
    doc = minidom.parse("currency_ex_rate_custom.xml")
    outer_layer = doc.getElementsByTagName("generic:Obs")
    df2 = pd.DataFrame(columns=["Time_Period", "Obs_Value"])
    counter = 0
    for i in outer_layer:
        inner_layer_perd = i.getElementsByTagName("generic:ObsDimension")[0]
        inner_layer_exrt = i.getElementsByTagName("generic:ObsValue")[0]
        time_period = inner_layer_perd.getAttribute("value")
        rate = float(inner_layer_exrt.getAttribute("value"))
        df2.loc[counter] = [time_period, rate]
        counter += 1

    return df2


def get_data(identifier: str, target_currency: str = None) -> pd.DataFrame:
    df11 = get_exchange_rate(target_currency)
    df22 = get_raw_data(identifier)
    df3: DataFrame = pd.DataFrame(columns=['Time_Period', 'OBS_VALUE'])
    df12 = df11.merge(df22, how='left', left_on='Time_Period', right_on='Time_Period')
    print(df12)
    df3['Time_Period'] = df12['Time_Period']
    df3['OBS_VALUE'] = df12['Obs_Value_x']*df12['Obs_Value_y']
    return df3


print(get_data("M.N.I8.W1.S1.S1.T.N.FA.F.F7.T.EUR._T.T.N", "GBP"))
