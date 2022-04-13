import json
from datetime import datetime

from flask import Flask, request, jsonify, make_response, send_from_directory
import dataUtils.dataFunction as dataProcess
from dataUtils import FN
from dataUtils.const import const
import time
import os
from flask_sqlalchemy import SQLAlchemy
import pymysql
import ast
import uuid
from sqlUtils.sqlPreprocess import upload_data, handle_data, storage_data, confirm_data, confirm_all_data, \
    standard_name_data, add_standard_name

pymysql.install_as_MySQLdb()


# 配置跨域
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.after_request(after_request)
uid = ''
task_uuid = ''

#两个文件常量
CHINESE='chinese1.xlsx'
ENGLISH='english1.xlsx'
# 数据库配置
class Config(object):
    """配置参数"""
    # 设置连接数据库的URL
    user = 'root'
    password = '1000'  # 远程数据库密码
    # password = '123456'
    database = 'arx'
    # 远程数据库连接
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@81.69.35.249:3306/%s' % (user, password, database)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@c_mysql:3306/%s' % (user, password, database)
    # 设置sqlalchemy自动更跟踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 查询时会显示原始SQL语句
    # app.config['SQLALCHEMY_ECHO'] = True

    # 禁止自动提交数据处理
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False


# 读取配置
app.config.from_object(Config)

# 创建数据库sqlalchemy工具对象
db = SQLAlchemy(app)


class User(db.Model):
    # 定义表名
    __tablename__ = 'b_pretreatment'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version_uuid = db.Column(db.String(36), nullable=False)
    attribute_name = db.Column(db.String(255), unique=True)
    attribute_type = db.Column(db.String(100))


class Version(db.Model):
    # 定义表名
    __tablename__ = 'b_version_storage'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version_uuid = db.Column(db.String(36), nullable=False)
    task_uuid = db.Column(db.String(36), nullable=False)


class Information(db.Model):
    # 定义表名
    __tablename__ = 'b_content_storage'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version_uuid = db.Column(db.String(36), nullable=False)
    name = db.Column(db.String(36), nullable=False)
    dataLevel = db.Column(db.String(36), nullable=False)
    I = db.Column(db.String(36), nullable=False)
    QI = db.Column(db.String(36), nullable=False)
    sensitive = db.Column(db.String(36), nullable=False)
    level = db.Column(db.String(36), nullable=False)
    rate = db.Column(db.String(36), nullable=False)
    confirm = db.Column(db.String(36), nullable=False)
    standard_name=db.Column(db.String(36))

class StandardData(db.Model):
    # 定义表名
    __tablename__ = 'b_standard_file'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    standard_name  = db.Column(db.String(36), nullable=False)
    standard_c = db.Column(db.String(36), nullable=False)
    standard_e = db.Column(db.String(36), nullable=False)

# 获取所有标准
@app.route('/data/getstandard', methods=['GET'])
def data_getstandard():
    return_dict = {'code': '1', 'msg': '获取数据成功'}
    ret = db.session.execute(
        "select standard_name from b_standard_file"
    )
    payload = []
    for result in ret:
        content = {'standard_name': result[0]}
        payload.append(content)
        content = {}
    if not payload:
        return_dict['code'] = '0'
        return_dict['msg'] = '没有标准'
        return_dict['data'] = False
        return jsonify(return_dict)
    return_dict['data'] = payload
    return jsonify(return_dict)
#添加标准
@app.route('/data/add_standard',methods=['POST'])
def add_standard():
    return_dict = {'code': '1', 'msg': '成功传入文件'}
    name = request.form.get("standard_name")
    file1 = request.files.get('standard_chinese')
    file2 = request.files.get('standard_english')
    if name is None:
        return_dict['code'] = '0'
        return_dict['msg'] = '传入名称错误'
        return jsonify(return_dict)
    if file1 is None or file2 is None:
        return_dict['code'] = '0'
        return_dict['msg'] = '传入的不是文件'
        return jsonify(return_dict)
    number = db.session.execute(
        "select count(id) from b_standard_file"
    )
    num = '';
    for nums in number:
        num = nums[0] + 1
    num=str(num)
    #传入数据库的标准名
    s1="chinese" + num + ".xlsx"
    s2="english" + num + ".xlsx"
    #添加到数据库中
    condition=add_standard_name(db, StandardData, name, s1, s2)
    if not condition:
        return_dict['code'] = '0'
        return_dict['msg'] = '数据名重复,请更换'
        return jsonify(return_dict)
    file1.save("./dictionary/"+"chinese"+num+".xlsx")
    file2.save("./dictionary/" + "english" + num + ".xlsx")
    return jsonify(return_dict)
#传入所需标准的名字
@app.route('/data/standard_name',methods=['GET'])
def standard_name():
    version_uuid = request.args.get("version_uuid")
    return_dict = {'code': '1', 'msg': '成功选择标准'}
    name=request.args.get("standard_name")
    payload=standard_name_data(db,name,Information,version_uuid)
    if not payload:
        return_dict['code'] = '0'
        return_dict['msg'] = '传入standard_name错误'
        return_dict['data'] = False
        return jsonify(return_dict)
    global CHINESE,ENGLISH
    CHINESE=payload[2].strip()
    ENGLISH=payload[3].strip()
    print(CHINESE)
    print(ENGLISH)
    return jsonify(return_dict)
#只确认其中一个数据的接口
@app.route('/data/updateconfirm', methods=['GET'])
def updateconfirm():
    return_dict = {'code': '1', 'msg': '成功确认数据'}
    data = []
    data.append(request.args.get("version_uuid"))
    data.append(request.args.get("attribute_name"))
    response = confirm_data(db,Information, data)
    if response == True:
        return jsonify(return_dict)
    else:
        return_dict['code'] = '0'
        return_dict['msg'] = '确认数据失败,未找到该条数据'
        return jsonify(return_dict)

#确认全部数据的接口
@app.route('/data/confirmall', methods=['GET'])
def confirmall():
    data = []
    data.append(request.args.get("version_uuid"))
    return_dict = {'code': '1', 'msg': '成功确认数据'}
    confirm_all_data(db, Information, data)
    return jsonify(return_dict)
# 返回当前版本号的所有数据
@app.route('/data/getall', methods=['GET'])
def data_getall():
    version_uuid = request.args.get("version_uuid")
    # 定义一个返回的样式
    return_dict = {'code': '1', 'msg': '获取数据成功'}
    if version_uuid is None:
        return_dict['code'] = '0'
        return_dict['msg'] = '获取数据失败'
        return_dict['data'] = False
        return jsonify(return_dict)
    ret = db.session.execute(
        "select * from b_content_storage where version_uuid =" + "\"" + version_uuid + "\"  ORDER BY FIELD(level,'未识别','疑似正确','正确') ASC"
    )
    payload = []
    rate =''
    standard_name_s=''
    i = 1
    # for result1 in ret:
    #     if result1[10] is not None:
    #         standard_name_s=result1[10]
    #         break
    for result in ret:
        rate = result[8]
        if result[10] is not None:
            standard_name_s=result[10]
        content = {'id': i, 'name': result[2], 'dataLevel': result[3], 'I': result[4], 'QI': result[5],
                   'sensitive': result[6], 'level': result[7],'confirm': result[9]}
        payload.append(content)
        i = i + 1
        content = {}
    # 检验是否有数据
    if not payload:
        return_dict['code'] = '0'
        return_dict['msg'] = '传入version_uuid错误'
        return_dict['data'] = False
        return jsonify(return_dict)
    return_dict['data'] = {'standard_name':standard_name_s,'rate':rate,'result':payload}
    return jsonify(return_dict)


# 更新数据
@app.route('/data/upload', methods=['GET'])
def data_upload():
    return_dict = {'code': '1', 'msg': '修改数据成功'}
    data = []
    data.append(request.args.get("version_uuid"))
    data.append(request.args.get("task_uuid"))
    data.append(request.args.get("attribute_name"))
    data.append(request.args.get("I"))
    data.append(request.args.get("QI"))
    data.append(request.args.get("sensitive"))
    print(data)
    response = upload_data(db, User, Information, data)
    if response == True:
        return jsonify(return_dict)
    else:
        return_dict['code'] = '0'
        return_dict['msg'] = '修改数据失败,可能为传入version_uuid错误'
        return jsonify(return_dict)

# 获取当前任务下所有的uid
@app.route('/data/getuid', methods=['GET'])
def data_getuid():
    task_uuid=request.args.get("task_uuid")
    return_dict = {'code': '1', 'msg': '获取数据成功'}
    ret = db.session.execute(
        "select version_uuid from b_version_storage where task_uuid =" + "\"" + task_uuid + "\""
    )
    payload = []
    for result in ret:
        content = {'version_uuid': result[0]}
        payload.append(content)
        content = {}
    if not payload:
        return_dict['code'] = '0'
        return_dict['msg'] = '传入task_uuid错误'
        return_dict['data'] = False
        return jsonify(return_dict)
    return_dict['data'] = payload
    return jsonify(return_dict)


# 对数据进行处理并存入数据库
@app.route('/data/preprocess', methods=['POST'])
def data_preprocess():
    #选择所对应的标准  默认为第一种金融标准
    FN.CHINESEDATA='./dictionary/'+CHINESE
    FN.ENGLISHDATA='./dictionary/'+ENGLISH
    # 返回的json值
    return_dict = {'code': '1', 'msg': '获取数据成功'}
    # 获取路径
    url = request.host_url
    # 获取参数
    global uid, task_uuid
    task_uuid = request.form.get("task_uuid")
    rate = request.form.get("rate")
    # 从数据库中读取原数据
    ret = db.session.execute(
        "select * from b_input_file where task_uuid =" + "\"" + task_uuid + "\""
    )
    payload1 = []
    for result in ret:
        #把数据类型还原成本身
        list = ast.literal_eval(result[2])
        payload1.append(list)

    if not payload1:
        return_dict['code'] = '0'
        return_dict['msg'] = '传入task_uuid错误'
        return_dict['data'] = False
        return jsonify(return_dict)

    # 判断传入的task_uuid 没问题时生成uid
    number = db.session.execute(
        "select count(name) from b_content_storage"
    )
    num= '';
    for nums in number:
        num =nums[0]+1
    uid = "version" + str(num)
    #将任务uid 和我生成的uid存储到b_version_storage中
    storage_data(db, Version, uid, task_uuid)


    #对数据进行预处理(关键步骤)  返回一个文件
    data_result= dataProcess.read_csv(payload1, float(rate))
    # # 以时间戳命名文件 文件重命名
    # ts = time.time()
    # global file_name
    # file_name = "./target/" + str(ts) + '.csv'
    # os.rename("./target/target.csv", file_name)

    # 将数据传入数据库 并返回前端所需要的形式
    payload = handle_data(db, User, Information,data_result, uid, rate)
    if payload is None:
        return_dict['code'] = '0'
        return_dict['msg'] = '获取数据失败'
        return_dict['data'] = False
        return jsonify(return_dict)
    return_dict['data'] = {'version_uuid':uid,'result':payload}
    # 返回的参数
    return jsonify(return_dict)


if __name__ == '__main__':
    app.run()
