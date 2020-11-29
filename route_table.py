#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   routes_table.py
@Time    :   2020/11/28 21:20:38
@Author  :   SHILIU
@Version :   1.0
'''

# here put the import lib
from route import max, routes, point_latlong
from sqlalchemy import create_engine
import psycopg2
import pandas as pd

# route路线处理
routes_dict = []
for info in routes:
    routes_dict.append({'food_name':info[0], 'route':info[1], 'time':info[2], 'is_safe':info[3], 'food_url':info[4], 'describe':info[5] })
routes_df = pd.DataFrame(routes_dict)

# 导入数据库
engine = create_engine('postgresql://postgres:shiliu@127.0.0.1:5432/postgres')
routes_df.to_sql('route', engine, index = False, if_exists='replace')
print("Table created successfully........")
