#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   route.py
@Time    :   2020/11/27 11:06:13
@Author  :   SHILIU
@Version ：  2.0
'''

# here put the import lib
import json as js
from random import choice, random, uniform
import os
import csv
import datetime
import requests

# Todos
'''
1.国外的城市目前全用的是各国首都，可以换成其它城市
2.国内港口的物品不可能运到港澳台
3.港口会优先配送物品到离它进的城市，不可能南辕北辙
4.最后生成的城市要根据省会位置来确定，现在不是
'''

class SaveJson(object):
    '''将字典存为json'''
    def save_file(self, path, item):
        # 先将字典对象转化为可写入文本的字符串
        item = js.dumps(item, ensure_ascii=False)
        try:
            if not os.path.exists(path):
                with open(path, "w", encoding='utf-8') as f:
                    f.write(item + ",\n")
                    # print("^_^ write success")
            else:
                with open(path, "a", encoding='utf-8') as f:
                    f.write(item + ",\n")
                    # print("^_^ write success")
        except Exception as e:
            print("write error==>", e)

# 读入一个存放每个国家名称及其首都的表格1，经度在前，纬度在后
# 来源 https://www.cnblogs.com/leo-lpf/p/9700337.html
json_path1 = 'country.json'
json_file1 = open(json_path1, encoding='UTF-8')
country_pos = js.load(json_file1)

# 读入一个存放有每个国家中英文名称及其首都名称的表格2
# 这个表格中国家的数量比上面一个要少
# 来源 https://github.com/yyc2686/CapitalSpider Target文件夹
def csv2dict(in_file,key,value):
    '''
        csv文件转字典
        输入: csv文件路径
        输出: 以国家中文名为键，以(国家英文名，首都)为值的字典
    '''
    new_dict = {}
    with open(in_file, 'rt') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # new_dict[row[key]] = (row[value[0]], row[value[1]], row[value[2]])
            new_dict[row[key]] = (row[value[i]] for i in range(len(value)))
            new_dict[row[key]] = tuple(new_dict[row[key]])
    return new_dict
csv_file1 = 'country_info_with_capital_revised.csv'
key = 'Label'
value = ('Name', 'Capital', 'Continent')
country_capital_nopos = csv2dict(csv_file1, key, value)

# 遍历表2的键，获取对应首都的经纬度
country_capital_pos = {}
for country in country_capital_nopos:
    if country in country_pos:
        country_capital_pos[country_capital_nopos[country][1]] = (country, country_capital_nopos[country][0], country_pos[country], country_capital_nopos[country][2])
cities_foreign = list(country_capital_pos.keys())

# 主要的海港
# 来源 http://www.lenglian.org.cn/news/2018/26690.html
ports_pos = {'大连港':[121.62, 38.92],
         '天津港':[117.2, 39.13],
         '青岛港':[120.33, 36.07],
         '上海港':[121.48, 31.22],
         '宁波港':[121.56, 29.86],
         '厦门港':[118.1, 24.46],
         '广州港':[113.23, 23.16],
         '连云港':[119.16, 34.59],
         '珠海港':[113.52, 22.3]}
ports = list(ports_pos.keys())

# 中国省会
# 来源 https://github.com/yyc2686/CapitalSpider Target文件夹
def posstr2posnum(posstr):
    '''
        输入：形如'[116.46, 39.92]'的字符串
        输出: 形如[116.46, 39.92]的列表
    '''
    posstr = posstr[1:-1]
    return [float(posstr.split(',')[0]), float(posstr.split(',')[1])]

def simple_province(province_value):
    '''
        把省份后面的市、自治区、省删掉，同时把经纬度字符串换成二元数值列表
        输入：provinces_table表中键对应的值，形如('北京市', '[116.46, 39.92]')
        输出：('北京', [116.46, 39.92])
    '''
    province = province_value[0]
    latlong = province_value[1]
    province_dict = {'内蒙古自治区': '内蒙古',
                     '广西壮族自治区': '广西',
                     '西藏自治区': '西藏',
                     '新疆维吾尔自治区': '新疆',
                     '宁夏回族自治区': '宁夏',
                     '香港特别行政区': '香港',
                     '澳门特别行政区': '澳门'}
    if '市' in province or '省' in province:
        province = province[0:-1]
    else:
        province = province_dict[province]
    latlong = posstr2posnum(latlong)
    return (province, latlong)

csv_file2 = 'china_provinces.csv'
key = 'Label'
value = ('City', 'latlong')
provinces_table = csv2dict(csv_file2, key, value)
for provincial_capital in provinces_table:
    provinces_table[provincial_capital] = simple_province(provinces_table[provincial_capital])
provinces_capitals = list(provinces_table.keys())

# 所在城市
# 来源 https://github.com/yyc2686/CapitalSpider Target文件夹
csv_file3 = 'china_digital_index.csv'
key = 'Label'
value = ('Province', 'latlong')
cities_table = csv2dict(csv_file3, key, value)
f = lambda value: (value[0], posstr2posnum(value[1]))
for city in cities_table:
    cities_table[city] = f(cities_table[city])
cities = list(cities_table.keys())

def randomtimes(start, end, n, frmt="%Y-%m-%d %H:%M:%S"):
    '''
        输入：起始时间点，结束时间点，以及输入的时间格式
        输出: n个在指定时间段内的随机时间点
    '''
    stime = datetime.datetime.strptime(start, frmt)
    etime = datetime.datetime.strptime(end, frmt)
    time_datetime = [random() * (etime - stime) + stime for _ in range(n)]
    time_str = [t.strftime(frmt) for t in time_datetime]
    if len(time_str) == 1:
        return time_str[0]
    else:
        return time_str

def random_pick(some_list, probabilities):
    '''
        以指定的概率获取元素，以一个列表为基准概率，从一个列表中随机获取元素
        输入：可供选取的元素列表及其对应的概率
        输入：选中的数字
    '''
    x = uniform(0,1)
    cumulative_probability = 0.0
    for item, item_probability in zip(some_list, probabilities):
        cumulative_probability += item_probability
        if x < cumulative_probability:
            break
    return item 


# 不同州的航线
shipping_lines = {
    '大洋洲': {
        '珀斯': ['珀斯', '悉尼', '香港', '广州港'],
        '悉尼': ['悉尼', '香港', '广州港'],
        '惠灵顿': ['惠灵顿', '悉尼', '香港', '广州港']},
    '南美洲': {
        '科隆': ['科隆', '檀香山', '横滨', '上海港'],
        '利马': ['利马', '科隆', '檀香山', '横滨', '上海港'],
        '瓦尔帕莱素': ['瓦尔帕莱素', '惠灵顿', '悉尼', '香港', '广州港'],
        '布谊诺斯艾利斯': ['布谊诺斯艾利斯', '惠灵顿', '悉尼', '香港', '广州港'],
        '里约热内卢': ['里约热内卢', '布谊诺斯艾利斯', '惠灵顿', '悉尼', '香港', '广州港']},
    '北美洲': {
        '温哥华': ['温哥华', '上海港'],
        '旧金山': ['旧金山', '横滨', '上海港']},
    '非洲': {
        '巴士拉': ['巴士拉', '亚丁', '新加坡', '广州港'],
        '亚丁': ['亚丁', '新加坡', '广州港'],
        '蒙巴萨': ['蒙巴萨', '新加坡', '广州港'],
        '达累斯萨拉姆': ['达累斯萨拉姆', '新加坡', '广州港'],
        '开普敦': ['开普敦', '达累斯萨拉姆', '新加坡', '广州港'],
        '达喀尔': ['达喀尔', '开普敦', '达累斯萨拉姆', '新加坡', '广州港'],
        '卡萨布兰卡': ['卡萨布兰卡', '达喀尔', '开普敦', '达累斯萨拉姆', '新加坡', '广州港']
    },
    '欧洲': {
        '斯德哥尔摩': ['斯德哥尔摩', '伦敦', '达喀尔', '开普敦', '达累斯萨拉姆', '新加坡', '广州港'],
        '哥本哈根': ['哥本哈根', '达喀尔', '开普敦', '达累斯萨拉姆', '新加坡', '广州港'],
        '安特卫普': ['安特卫普', '达喀尔', '开普敦', '达累斯萨拉姆', '新加坡', '广州港'],
        '鹿特丹': ['鹿特丹', '达喀尔', '开普敦', '达累斯萨拉姆', '新加坡', '广州港'],
        '汉堡': ['汉堡', '达喀尔', '开普敦', '达累斯萨拉姆', '新加坡', '广州港'],
        '马赛': ['马赛', '亚历山大', '亚丁', '新加坡', '广州港'],
        '热那亚': ['热那亚', '亚历山大', '亚丁', '新加坡', '广州港'],
        '康斯坦察': ['康斯坦察', '亚历山大', '亚丁', '新加坡', '广州港'],
        '亚历山大': ['亚历山大', '亚丁', '新加坡', '广州港']
    }
}
# 第一次采用百度地图api查各大港口的经纬度，找到之后存成json，后续不需要百度地图api了
# ports_all = []
# for cont in shipping_lines:
#     for ports_in_cont in shipping_lines[cont]:
#         ports_all.extend(shipping_lines[cont][ports_in_cont])
# ports_all = set(ports_all)
# api_prefix = "http://api.map.baidu.com/geocoding/v3/?address="
# api_suffix = "&output=json&ak=jULEhaxesjcESQVKTxUWh6szmnFqIlSA"
# # address = '亚历山大'
# ports_foreign_pos = {}
# for address in ports_all:
#     url_map = api_prefix + address + api_suffix
#     latlong_resp = requests.get(url_map)
#     latlong_json = latlong_resp.json()
#     if latlong_json['status'] == 0:
#         latlong_value = [latlong_json['result']['location']['lng'], latlong_json['result']['location']['lat']]
#         ports_foreign_pos[address] = latlong_value
#     else:
#         print(address)
# # 保存各港口经纬度
# path_ports_foreign = 'ports_foreign_pos.json'
# s = SaveJson()
# s.save_file(path_ports_foreign, ports_foreign_pos)
json_path2 = 'ports_foreign_pos.json'
json_file2 = open(json_path2, encoding='UTF-8')
ports_foreign_pos = js.load(json_file2)

foods = ['Meat and meat product',
         'Fish and fish product',
         'Fruit and fruit product',
         'Vegetables',
         'Milk and milk product',
         'Mixed',
         'Fresh cut salads',
         'Other']
# 生成的虚拟运送路线数目
max = 10
# 0表示检测没问题，1表示检测有问题
results = [0, 1]
probs = [0.95, 0.05]
# 随机组合，生成运送路线
routes = []
for i in range(max):
    food = choice(foods)
    foreign = choice(cities_foreign) #国外的某个城市
    cont = country_capital_pos[foreign][3]
    if cont == '亚洲':
        # 亚洲的话，就考虑四个城市
        port = choice(ports)
        provinces_capital = choice(provinces_capitals)
        city = choice(cities)
        route = [foreign, port, provinces_capital, city]
    else:
        # 其它洲，就考虑海运路线
        route_tochina = choice(list(shipping_lines[cont].values()))
        provinces_capital = choice(provinces_capitals)
        city = choice(cities)
        route = [foreign]
        route.extend(route_tochina)
        route.extend([provinces_capital, city])
    time = randomtimes('2020-11-01 07:00:00','2020-11-17 09:00:00',1)
    result_check = random_pick(results, probs)
    routes.append((food, route, time, result_check))

# 国外城市foreign的经纬度保存在字典country_capital_pos对应的键值对中
# 港口port的经纬度保存在字典ports_pos对应的键值对中
# 国内省会城市provinces_capital的经纬度保存在provinces_table对应的键值对中
# 国内城市city的经纬度保存在字典cities_table对应的键值对中
# print('fighting')

# 新增经纬度合并
point_latlong = {}
for key in country_capital_pos:
    point_latlong[key] = country_capital_pos[key][2]
for key in ports_pos:
    point_latlong[key] = ports_pos[key]
for key in provinces_table:
    point_latlong[key] = provinces_table[key][1]
for key in cities_table:
    point_latlong[key] = cities_table[key][1]
for key in cities_table:
    point_latlong[key] = ports_foreign_pos[key]
for i in range(len(routes)):
    print(routes[i])
