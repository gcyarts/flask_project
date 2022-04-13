# -*- coding: utf-8 -*-
# 定义一个常量类实现常量的功能
#
# 该类定义了一个方法__setattr()__,和一个异常ConstError, ConstError类继承
# 自类TypeError. 通过调用类自带的字典__dict__, 判断定义的常量是否包含在字典
# 中。如果字典中包含此变量，将抛出异常，否则，给新创建的常量赋值。
class _const:
    class ConstError(TypeError): pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't rebind const (%s)" % name)
        self.__dict__[name] = value


const = _const()

# 生成文件名
const.TARGET = './target/target.csv'


# 常量
const.NUMBER = "^[0-9]*$"  # 数字
const.EANDN = "^[A-Za-z0-9]+"  # 大写小写英文字母+数字
const.CHINESE = "^[\u4e00-\u9fa5]{0,}"  # 汉字的判断
const.ENGLISH = "^[A-Za-z]+$"  # 大写小写英文字母

# 正则表达式(数字、英文)
const.PHONE1 = '^(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$'
const.PHONE2 = '^(\(\d{3,4}-)|\d{3.4}-)?\d{7,8}$'
const.PHONE3 = '\d{3}-\d{8}|\d{4}-\d{7}'
const.EMAIL = '^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$'
const.DOMAIN = '[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(/.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+/.?'
const.ID = '/(^\d{15})|(\d17([0−9]|X))/'
const.QQNUMBER = '[1-9][0-9]{4,}'
const.DATE = '^\d{4}-\d{1,2}-\d{1,2}'

# 通过正则表达式一一对应
mapsNE = {
    const.PHONE1: '手机号',
    const.EMAIL: '邮箱',
    const.DOMAIN: '域名',
    const.ID: '身份证号',
    const.DATE: '日期',
    const.PHONE3: '联系电话',
}  # 在通过中文字符名的匹配 进行找到等级
