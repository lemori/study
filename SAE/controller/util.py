#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import collections
import cStringIO
import re

DB_VALUE = {
    'id':'序号', 'name':'名称', 'passwd':'密码', 'password':'密码', 'mobile':'手机号',
    'account':'账户', 'email':'电子邮箱', 'Fovor':'收藏', 'History':'历史记录',
    'regdate':'注册日期', 'lastactive':'最后活跃日期', 'isvalid':'是否有效',
    'bindto':'绑定的账号', 'privilege':'等级', 'balance':'余额', 'bonus':'积分',
    'cash':'现金', 'creditcard':'信用卡', 'debitcard':'借记卡', 'address':'收货地址',
    'brief':'描述', 'ontime':'上架时间', 'atime':'添加时间', 'price':'价格',
    'discount':'折扣', 'insale':'是否在售', 'picurl':'图片链接', 'weburl':'详情链接',
    'Category':'商品类别列表', 'Goods':'商品列表', 'uid':'用户ID', 'tid':'ID号',
    'gid':'商品ID', 'ftype':'品类'
}

MESSAGE_TYPE = {
    'text':'文字', 'image':'图片', 'voice':'语音', 'video':'视频', 'music':'音乐', 'news':'图文'
}

MESSAGE = {
    'load_session_failed': '很抱歉，出现未知错误，请重试',
    'no_more_choices': '当前无其他选项，您可回复【00】回到主菜单',
    'invalid_request': '您输入的查询无效，回复【?】查看帮助',
    'user_register': '请输入用户名和密码，用空格隔开',
    'user_login': '请输入用户名(或手机号、邮箱)和密码，用空格隔开',
    'user_logout': '您已成功退出！回复【8】重新登录。',
    'invalid_login_info': '用户名或密码错误。回复【01】查看常见疑问',
    'user_existed': '该用户名已被注册，请换一个名称。',
    'login_succeed': '注册成功！您的用户名是：$NAME',
    'invalid_index': '序号应当是数字，请重新选择',
    'view_category': '回复序号查看相应商品类别',
    'view_category_detail': '回复【05】收藏\n回复其它序号查看其他商品类别',
    'search_goods': '查询商品，请输入商品名称，如“手机”。',
    'list_goods': '输入序号查看相应商品详细\n若继续查询请输入名称',
    'view_goods_detail': '回复【05】收藏\n回复【09】购买',
    'invalid_goods_choice': '无效的选项。\n回复【05】收藏\n回复【09】购买\n回复【00】回到主菜单'
}

# Language Uitl
def encode_simple(s):
    """Encoding string value in utf-8 format."""
    if isinstance(s, unicode):
        return s.encode("utf-8")
    elif isinstance(s, str):
        return unicode(s, "utf-8")
    else:
        return s

def encode(obj):
    """Encoding any object in utf-8 format as a string."""
    if isinstance(obj, unicode):
        out = cStringIO.StringIO()
        for c in obj:
            if ord(c)<32 or c in u'"\\':
                out.write('\\x%.2x' % ord(c))
            else:
                out.write(c.encode("utf-8"))
        return out.getvalue()
    elif isinstance(obj, str):
        out = cStringIO.StringIO()
        for c in obj:
            if ord(c)<32 or c in '"\\':
                out.write('\\x%.2x' % ord(c))
            else:
                out.write(c)
        return out.getvalue()
    else:
        return str(obj)

# Other common utils
def isint(value):
    try:
        value = int(value)
    except ValueError:
        return False
    else:
        return True

def isascii(string):
    try:
        string.encode('ascii')
    except:
        return False
    else:
        return True

def istimeout(atime, timeout=3600):
    """atime:check point.
    timeout:a datetime, or seconds before now. by default 3600s."""
    if isinstance(timeout, datetime.datetime):
        return atime < timeout
    if not isinstance(timeout, int):
        timeout = 3600
    timeout = datetime.timedelta(0, timeout, 0)
    last_allowed_time = datetime.datetime.now() - timeout
    return atime < last_allowed_time

def isemail(s):
    p = re.compile(r'^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$')
    return p.match(s) != None

def check_raw_input(request):
    """Check if original request valid. Return audited request"""
    s = request.strip()
    return s

def check_user_info(info):
    """Returns user name and """
    s = info.split()
    if len(s) == 1:
        return MESSAGE['user_login']
    user, pwd = s[0], s[1]
    if (not 2 <= len(user) <= 36) or (not 6 <= len(pwd) <= 16):
        return MESSAGE['invalid_login_info']
    if len(user) < 6 and isascii(user):
        return MESSAGE['invalid_login_info']
    u = {'name':'', 'pwd':'', 'mobile':'', 'email':''}
    if len(user) == 11 and isint(user):
        u['name'] = u['mobile'] = user
    elif isemail(user):
        u['name'] = u['email'] = user
    else:
        u['name'] = user
    u['pwd'] = pwd
    return u

def check_update_info(info, ignore=['id']):
    """Info:a dict containing information to update.
    ignore:a list to be ignored.Default is id."""
    if not isinstance(info, dict):
        return 'Wrong user information when update user'
    if ignore:
        for item in ignore:
            del info[item]
    #Only items that listed in DB_VALUE can be updated.
    for i in info.items():
        if i not in DB_VALUE:
            del info[i]
    #OK, even it is empty
    return info

def output(obj):
    """Output obj in Chinese by a better format"""
    out = ''
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, (list, dict, collections.OrderedDict)):
                out += output(item) + '\n' + '--------' + '\n'
            elif item in DB_VALUE:
                out += encode(DB_VALUE[item]) + '\n'
            else:
                out += encode(item) + '\n'
    elif isinstance(obj, (dict, collections.OrderedDict)):
        for item, value in obj.items():
            if isinstance(value, (list, dict, collections.OrderedDict)):
                out += encode(item) + ': ' + output(value) + '\n' + '--------' + '\n'
            elif item in DB_VALUE:
                out += encode(DB_VALUE[item]) + ': ' + encode(value) + '\n'
            else:
                out += encode(item) + ': ' + encode(value) + '\n'
    else:
        out = encode(str(obj)) + '\n'
    #OK
    return out[0:-1]

