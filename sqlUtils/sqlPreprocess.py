import pandas as pd
import time

from sqlalchemy.sql.elements import and_

#存储版本号
def storage_data(db, Version, version_uuid, task_uuid):
    version1 = Version(task_uuid=task_uuid, version_uuid=version_uuid)
    db.session.add(version1)
    db.session.commit()



#处理数据放到数据库里
def handle_data(db, User, Information, data_result, uid, rate):
    # 写sql语句
    payload = []
    # 写成列表形式
    # for result in ret:
    #     content = {'id': result[0], 'name': result[1], 'dataLevel': result[2], 'I': result[3], 'QI': result[4],
    #                'sensitive': result[5], 'level': result[6]}
    #     payload.append(content)
    #     content = {}
    column_num = 0
    for data in data_result:
        information1 = Information(version_uuid=uid, name=data[5], dataLevel=data[0], I=data[1], QI=data[2],
                                   sensitive=data[3], level=data[4], rate=rate, confirm='否')
        db.session.add(information1)
        db.session.commit()
        # content = {'id': column_num, 'name': i, 'dataLevel': data[0], 'I': data[1], 'QI': data[2],
        #            'sensitive': data[3], 'level': data[4]}
        # payload.append(content)
        str1 = "Identifying" if (data[1] == '1') else ""
        str2 = "Quasi-identifying" if (data[2] == '1') else ""
        str3 = "Sensitive" if (data[3] == '1') else "Insensitive"
        strs = '' + str1 + str2 + str3
        d_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        user1 = User(version_uuid=uid, attribute_name=data[5], attribute_type=strs)
        db.session.add(user1)
        db.session.commit()
        column_num += 1

    ret = db.session.execute(
        "select * from b_content_storage where version_uuid =" + "\"" + str(uid) + "\"  ORDER BY FIELD(level,'未识别','疑似正确','正确') ASC"
    )
    payload = []
    i=1
    for result in ret:
        rate = result[8]
        content = {'id': i, 'name': result[2], 'dataLevel': result[3], 'I': result[4], 'QI': result[5],
                   'sensitive': result[6], 'level': result[7], 'confirm': result[9]}
        payload.append(content)
        i = i + 1
        content = {}
    return payload

#更新数据
def upload_data(db, User, Information, data):
    i = 1
    # user = User.query.filter(User.id == i).first()
    # print(user)
    information = Information.query.filter(
        and_(Information.version_uuid == data[0], Information.name == data[2])).first()
    print(information)
    if information is None:
        return False
    information.I = data[3]
    information.QI = data[4]
    information.sensitive = data[5]
    user = User.query.filter(and_(User.version_uuid == data[0], User.attribute_name == data[2])).first()
    # user.attribute_name = rows[1]
    # d_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    str1 = "Identifying" if (data[3] == '1') else ""
    str2 = "Quasi-identifying" if (data[4] == '1') else ""
    str3 = "Sensitive" if (data[5] == '1') else "Insensitive"
    if str1 != '' or str2 != '':
        str = '' + str1 + str2
    else:
        str = '' + str1 + str2 + str3
    # print(str)
    user.attribute_type = str
    db.session.commit()
    return True

#确认单个数据
def confirm_data(db,Information, data):
    i = 1
    # user = User.query.filter(User.id == i).first()
    # print(user)
    information = Information.query.filter(
        and_(Information.version_uuid == data[0], Information.name == data[1])).first()
    print(information)
    if information is None:
        return False
    information.confirm = '是'
    db.session.commit()
    return True

#确认所有数据
def confirm_all_data(db,Information,data):
    i = 1
    # user = User.query.filter(User.id == i).first()
    # print(user)
    Information.query.filter(Information.version_uuid == data[0]).update({'confirm':'是'})
    db.session.commit()
    return True

#获取标准名所对应的数据
def standard_name_data(db,name,Information,version_uuid):
    ret = db.session.execute(
        "select * from b_standard_file where standard_name =" + "\""+name+"\""
    )
    payload = []
    i = 1
    for result in ret:
        payload=result
    if not payload:
        return payload
    else:
        information = Information.query.filter(Information.version_uuid == version_uuid).first()
        information.standard_name = name
        db.session.commit()
        return payload

#添加数据标准
def add_standard_name(db,standardData,name,s1,s2):
    ret = db.session.execute(
        "select * from b_standard_file where standard_name =" + "\"" + name + "\""
    )
    payload = []
    for result in ret:
        payload = result
    if payload:
        return False
    standardData1 = standardData(standard_name=name, standard_c=s1, standard_e=s2)
    db.session.add(standardData1)
    db.session.commit()
    return True



