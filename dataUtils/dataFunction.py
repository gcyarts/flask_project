import re

from dataUtils import FN
from dataUtils.const import const, mapsNE
import numpy as np
# 读取数据处理数据
from dataUtils.dataBase import check_format, match_format
import time



# state  1:未识别  2:疑似正确  3:正确
def read_csv(results, rate):
    #df2 = pd.read_csv(const.TARGET)
    # df = df.sample(frac=0.3, replace=False, axis=0) #取一部分数据进行抽样检测(正则表达式匹配)
    column_num = 0
    names = []
    data_result=[]
    k = 0
    for result in results:
        names=result
        break

    for i in names:
        s1 = dictionary(str(i), rate)
        data1 = [False, -1, -1, -1]
        data2 = [False, -1, -1, -1]
        if s1[0] != False:
            data1 = s1
        data1=np.array(data1)
        # 准确率达到百分之百 完美匹配
        if data1.size > 4:
            data=data1
            data=data.tolist()
            data.append(i)
            data_result.append(data)
            # df2[str(i)] = data
            # print(type(data))
            # df2.to_csv(const.TARGET, index=False)
            column_num += 1
            continue
        datas =[]
        s=0
        for result in results:
            if s == 0:
                s+=1
                continue
            datas.append(result[column_num])

        s2 = datamatch(datas, rate)

        if s2[0] != False:
            data2 = s2

        if data1[0] == False and data2[0] == False:

            data = [-1, -1, -1, -1, '未识别']  # 未识别
            data.append(i)
        elif data1[0] == False and data2[0] != False:

            data = np.append(data2, '疑似正确')  # 疑似正确
            data = data.tolist()
            data.append(i)
        elif data1[0] != False and data2[0] == False:

            data = np.append(data1, '疑似正确')  # 疑似正确
            data = data.tolist()
            data.append(i)
        else:

            value = True
            for value1, value2 in zip(data1, data2):
                if value1 == value2:
                    continue
                else:
                    value = False
                    data = np.append(data1, '疑似正确')  # 疑似正确
                    data.tolist()
                    data.append(i)
                    break
            if value == True:
                data = np.append(data1, '正确')  # 绝对正确
                data.tolist()
                data.append(i)
        data_result.append(data)
        #print(data_result)
        # df2[str(i)] = data
        # df2.to_csv(const.TARGET, index=False)
        #print(123)
        column_num += 1
    return data_result
# 字段名判断
def dictionary(i, rate):
    data = [False, -1, -1, -1]
    result1 = re.search(const.CHINESE, i)
    result2 = re.search(const.ENGLISH, i)
    if result1 is not None and result1.group() != '':
        result = result1.group()
        return check_format(FN.CHINESEDATA, result, rate)
    elif result2 is not None:
        result = result2.group()
        result = result.lower()
        #print(result)
        return check_format(FN.ENGLISHDATA, result, rate)
    else:
        return data


# 正则表达式匹配
def datamatch(data,rate):
    result = [False, -1, -1, -1]
    for i in data:
        i = str(i)
        if i == 'nan':
            continue
        if re.search(const.EANDN, i) is not None:
            result = match_format(i, mapsNE, rate)
            if result[0] != False:
                break

    return result
