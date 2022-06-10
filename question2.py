import requests
import pandas as pd
from xml.dom import minidom


def get_transactions(identifier: str) -> pd.DataFrame:
    data = requests.get("https://sdw-wsrest.ecb.europa.eu/service/data/BSI/{}".format(identifier))
    with open("for_question2.xml", 'wb') as f:
        f.write(data.content)
    df1 = pd.DataFrame(columns=["IDENTIFIER", "TIME_PERIOD", "OBS_VALUE"])
    doc = minidom.parse("for_question2.xml")
    outer_layer = doc.getElementsByTagName("generic:Obs")
    counter = 0
    for i in outer_layer:
        inner_lyr_period = i.getElementsByTagName("generic:ObsDimension")[0]
        inner_layer_exrt = i.getElementsByTagName("generic:ObsValue")[0]
        time_period = inner_lyr_period.getAttribute("value")
        rate = float(inner_layer_exrt.getAttribute("value"))
        df1.loc[counter] = [identifier, time_period, rate]
        counter += 1
    return df1


def get_symmetric_identifier(identifier: str,swap_components: dict) -> str:
    list_of_comp = identifier.split(".")
    for key, value in swap_components.items():
        temp = list_of_comp[key]
        list_of_comp[key] = list_of_comp[value]
        list_of_comp[value] = temp
    s = "."
    return s.join(list_of_comp)


def get_asymmetries(identifier: str, swap_components: dict) -> pd.DataFrame:
    df1 = get_transactions(identifier)
    new_identifier = get_symmetric_identifier(identifier, swap_components)
    df2 = get_transactions(new_identifier.strip())
    df1 = df1.merge(df2, how="inner", on="TIME_PERIOD")
    df1.info()
    df1.rename(columns={'IDENTIFIER_x': 'PROVIDED_ID', 'TIME_PERIOD': 'TIME_PERIOD', 'OBS_VALUE_x': 'OBS_VALUE_X', 'IDENTIFIER_y': 'SYMMETRIC_ID', 'OBS_VALUE_y': 'OBS_VALUE_Y'}, inplace=True)
    df1['DELTA'] = abs(df1['OBS_VALUE_X']-df1['OBS_VALUE_Y'])
    df1.dropna(how='any')
    df1.drop(columns=['OBS_VALUE_X', 'OBS_VALUE_Y'], inplace=True)
    df1 = df1[['TIME_PERIOD', 'PROVIDED_ID', 'SYMMETRIC_ID', 'DELTA']]
    df1.to_csv("df1.csv")
    return df1


print(get_asymmetries("Q.HR.N.A.A20.A.1.AT.2000.Z01.E", {1: 7}))
