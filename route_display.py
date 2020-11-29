import folium
from typing import List, Tuple
import json
import pandas as pd
import numpy as np
from IPython.display import display
import pandas as pd
import time
from datetime import datetime
from route import max, routes, country_capital_pos, ports_pos, provinces_table, cities_table,point_latlong
def ColorPicker(Number):
    #LevelList=[100,1000,5000,10000,100000]
    #ColorLevel=['#fee5d9','#fcbba1','#fc9272','#fb6a4a','#de2d26','#a50f15']
    LevelList = [1, 100, 1000, 5000, 10000]
    #ColorLevel = ['#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#800026']
    #ColorLevel = ['#fff5f0', '#fcbba1', '#fc9272', '#fb6a4a', '#ef3b2c', '#cb181d', '#a50f15', '#67000d']
    ColorLevel = ['#fff5f0', '#fcbba1', '#ef3b2c', '#a50f15', '#67000d''#000000']
    j=len(LevelList)
    for i in range(len(LevelList)):
        if Number<LevelList[i]:
            return ColorLevel[i]
    return ColorLevel[j]
def print_trace(m,route: List[List[float]]):
    """
    Save the map with route locally.
    :param Location: list of latitude and longtitude of all locations on the route.
                   List[float] : the length is 2, while the first element is latitude
                                                and the second element is longtitude.
    """
    Location=[]
    number=len(route)
    for region in route:
        Location.append([point_latlong[region][1],point_latlong[region][0]])
    i=0
    for region in route:
        latitude=point_latlong[region][1]
        longtitude=point_latlong[region][0]
        if i==0:
            folium.Marker(
                [latitude,longtitude], tooltip='运输起点：'+region,
            icon=folium.Icon(color='green',icon='star', prefix='fa')).add_to(m)
        elif i==number-1:
            folium.Marker(
                [latitude,longtitude], tooltip='运输终点：'+region,icon=folium.Icon(color='red',icon='star', prefix='fa')).add_to(m)
        else:
            folium.Marker([latitude,longtitude], tooltip=region).add_to(m)
        i+=1
    # m = folium.Map(zoom_start=10)
    # for latitude, longtitude in Location:
    #     folium.Marker(
    #         [latitude, longtitude], popup='<i>Latitude:</i>'+str(latitude)+'<br><i>Longtitude:</i>'+str(longtitude)
    #     ).add_to(m)
    route = folium.PolyLine(
        Location,  # 要连接的坐标点
        weight=4,  # 线的大小
        color='orange',  # 线的颜色
        opacity=0.5,  # 线的透明度
    ).add_to(m)
    # m.save('route_display.html')
    return m

def CovidMap(DisplayDay):
    # 从WHO网站爬取数据
    #with requests.get("https://dashboards-dev.sprinklr.com/data/9043/global-covid19-who-gis.json") as r:
    #    covid19_json=r.content
    #   time.sleep(0.5)
    #covid19_json = requests.get("https://dashboards-dev.sprinklr.com/data/9043/global-covid19-who-gis.json").content
    with open('global-covid19-who-gis.json','r',encoding='utf-8-sig') as f:
       covid19_json = json.load(f)
    # 查到的数据格式为
    # 'day', 'Country', 'Region', 'Deaths', 'Cumulative Deaths', 'Confirmed', 'Cumulative Confirmed'
    colname = pd.DataFrame(covid19_json['dimensions'])["name"].append(pd.DataFrame(covid19_json['metrics'])["name"]).to_list()
    covid19_dataframe = pd.DataFrame(covid19_json["rows"],columns=colname)
    # 数据处理

    df_abb = pd.read_csv("country_codes.csv",header = None)
    dic_abb = {df_abb.iloc[i,1]:df_abb.iloc[i,2] for i in range(np.shape(df_abb)[0])}
    covid19_dataframe['fullname'] = covid19_dataframe['Country'].map(dic_abb)
    # 简化数据，只需要最新的日期的确诊数据和累积确诊数据
    covid19_dataframe['Day']=covid19_dataframe.apply(lambda x:(datetime.fromtimestamp(x['day']/1000)),axis=1)
    covid19_dataframe['Date']=covid19_dataframe.apply(lambda  x:x['Day'].strftime('%Y-%m-%d'),axis=1)
    covid19_dataframe=covid19_dataframe[covid19_dataframe['Date']==DisplayDay]
    covid19_dataframe=covid19_dataframe.reset_index()
    covid19_dataframe = covid19_dataframe[["Country","fullname","Cumulative Confirmed","Confirmed"]]
    #print('covid:',covid19_dataframe)
    ConfirmDict = {key: value for key, value in zip(covid19_dataframe['fullname'], covid19_dataframe['Confirmed'])}
    CumulativeConfirmDict = {key: value for key, value in zip(covid19_dataframe['fullname'], covid19_dataframe['Cumulative Confirmed'])}

    m1 = folium.Map(tiles='Mapbox Bright')
    with open('CountryBorder.json', 'r', encoding='utf-8-sig') as f:
         CountryBorder= json.load(f)
    for country_dic in CountryBorder['features']:
        name = country_dic["properties"]["ISO3"]
        if name not in ConfirmDict:
            country_dic["properties"]["POP2005"] = 0
        else:
            country_dic["properties"]["POP2005"] = int(ConfirmDict[name])

    folium.GeoJson(CountryBorder,
                   style_function=lambda x: {'fillColor': ColorPicker(x['properties']['POP2005']),
                                             'weight': 0.2, 'fillOpacity': 10},
                   tooltip=folium.GeoJsonTooltip(fields=('NAME', 'POP2005',),
                                                 aliases=('Country', 'Confirmed')),
                   smooth_factor=2.0).add_to(m1)
    # m1.save('confirmed.html')
    # 添加疫情数据到地图

    return m1


def MapAndRoute(RouteInfo):
    route=RouteInfo[1]#['布鲁塞尔', '热那亚', '亚历山大', '亚丁', '新加坡', '广州港', '澳门', '秦皇岛']
    querytime=RouteInfo[2]
    #querytime=time.strptime(querytime,'%Y-%m-%d %H:%M:%S')
    #print(querytime)
    querydate=querytime[0:10]
    #print(querydate)
    confirmed=CovidMap(querydate)
    confirmed=print_trace(confirmed,route)
    #confirmed.save('route_display_2.html')
    return confirmed

#以下的代码是建立城市名到经纬度的转换。
# routeInfo=('Fruit and fruit product', ['卡萨布兰卡', '达喀尔', '开普敦', '达累斯萨拉姆', '新加坡', '广州港', '兰州'], '2020-03-14 05:26:20', 0)
# print(datetime.fromtimestamp(1606576631517/1000))
# MapAndRoute(routeInfo)