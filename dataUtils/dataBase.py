import pandas as pd
import difflib
import re

from dataUtils import FN
from dataUtils.const import const
import numpy as np


def check_format(xlsxname, name,rate=0.6):
    __validate_ = rate  # 判断相似程度
    df = pd.read_excel(xlsxname)
    column_num = 0
    data = [False,-1,-1,-1]
    for i in df.head():
        validate = difflib.SequenceMatcher(None, i, name).quick_ratio()
        if validate==1 :
            data = df.iloc[:, column_num].values
            data = np.append(data, '正确')
            break
        if validate >= __validate_:
            print(i)
            print('-------------------------------')
            data = df.iloc[:, column_num].values
            break
        column_num += 1
    return data


def match_format(data, maps, rate):
    name = -1
    datas=[False,-1,-1,-1]
    for key in maps:
        if re.search(key, data) is not None:
            print(key)
            name = maps[key]
            break
    if name == -1:
        return datas
    return check_format(FN.CHINESEDATA, name, rate)


