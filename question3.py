import requests
import pandas as pd
from xml.dom import minidom
import pdb



def get_transactions(identifier: str) -> pd.DataFrame:
    pdb.set_trace()
    data = requests.get("https://sdw-wsrest.ecb.europa.eu/service/data/BP6/{}".format(identifier))
    with open("for_question3.xml", 'wb') as f:
        f.write(data.content)
    df1 = pd.DataFrame(columns=["IDENTIFIER", "TIME_PERIOD", "OBS_VALUE"])
    doc = minidom.parse("for_question3.xml")
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


def get_formula_data(formula: str) -> pd.DataFrame:
    if "+" in formula:
        df1 = get_transactions(formula.split("=")[1].split("+")[0].strip())
        df2 = get_transactions(formula.split("=")[1].split("+")[1].strip())
        df1 = df1.merge(df2, on="TIME_PERIOD")
        df1['OBS_VALUE_y'].fillna(0, inplace=True)
        df1['OBS_VALUE_x'].fillna(0, inplace=True)
        df1['OBS_VALUE'] = df1['OBS_VALUE_y'] + df1['OBS_VALUE_x']
        df1.drop(columns=['OBS_VALUE_y','OBS_VALUE_x'],inplace=True)
        df1 = df1[['TIME_PERIOD', 'IDENTIFIER_x', 'IDENTIFIER_y', 'OBS_VALUE']]
        df1.to_csv('aggregation.csv')
        return df1
    if "-" in formula:
        df1 = get_transactions(formula.split("=")[1].split("-")[0].strip())
        df2 = get_transactions(formula.split("=")[1].split("-")[1].strip())
        df1 = df1.merge(df2, on="TIME_PERIOD")
        df1['OBS_VALUE_y'].fillna(0, inplace=True)
        df1['OBS_VALUE_x'].fillna(0, inplace=True)
        df1['OBS_VALUE'] = df1['OBS_VALUE_x'] - df1['OBS_VALUE_y']
        df1['OBS_VALUE'] = abs(df1['OBS_VALUE'])
        df1.drop(columns=['OBS_VALUE_y', 'OBS_VALUE_x'], inplace=True)
        df1 = df1[['TIME_PERIOD', 'IDENTIFIER_x', 'IDENTIFIER_y', 'OBS_VALUE']]
        df1.to_csv('aggregation.csv')
        return df1


def compute_aggregates(formula: str) -> pd.DataFrame:
    df1 = get_formula_data(formula)
    column_name = formula.split("=")[0].strip()
    df2 = pd.DataFrame(columns=['TIME_PERIOD', column_name])
    df2[['TIME_PERIOD', column_name]] = df1[['TIME_PERIOD', 'OBS_VALUE']]
    return df2


print(compute_aggregates("Q.N.I8.W1.S1.S1.T.A.FA.D.F._Z.EUR._T._X.N = Q.N.I8.W1.S1P.S1.T.A.FA.D.F._Z.EUR._T._X.N + Q.N.I8.W1.S1Q.S1.T.A.FA.D.F._Z.EUR._T._X.N"))
