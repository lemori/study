#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import collections
import math
from sqlalchemy import func, or_, not_

from config.setting import open_session, close_session
from config.model import WxSession, User, Acct, Favor, History, Category, Goods
from util_db import check_exist_user
import util

_category_list = ['id', 'name', 'brief']
_goods_list = ['id', 'name', 'brief', 'price', 'discount', 'picurl', 'weburl', 'ontime', 'insale']
_user_list = ['name', 'mobile', 'email', 'regdate', 'lastactive', 'bindto', 'privilege']
_account_list = ['balance', 'bonus', 'address']
_favor_list = ['ftype', 'tid', 'atime']
_history_list = ['gid', 'cash', 'bonus', 'atime']

def user_existed(u_account):
    """u_account can be name/mobile/email.
    Returns False if not existed."""
    if not u_account:
        return '无效的查询。'
    session = open_session()
    try:
        if check_exist_user(session, u_account) == 0:
            return False
        else:
            return util.MESSAGE['user_existed']
    except Exception, ex:
        print ex
        return '出错了，请重试。'
    finally:
        close_session(session)
           
def list_categories():
    """List all categories. """
    session = open_session()
    try:
        r_dict = collections.OrderedDict()
        for category in session.query(Category).all():
            r_dict[category.id] = category.name
        return r_dict
    except Exception, ex:
        print ex
        return '出错了，请重试。'
    finally:
        close_session(session)

def view_category(cid):
    session = open_session()
    try:
        category = session.query(Category).get(int(cid))
        if not category:
            return '找不到该目录编号：' + str(cid)
        r_dict = collections.OrderedDict()
        for item in _category_list:
            r_dict[item] = getattr(category, item)
        return r_dict
    except Exception, ex:
        print ex
        return '出错了，请重试。'
    finally:
        close_session(session)

def search_goods(name, limit=10):
    """Search for goods. Returns a list [{...}]"""
    #if name == '':
    #    return 'Search value is empty!'
    session = open_session()
    try:
        q = 'name like "%' + name + '%" and insale=1'
        r_list = []
        for goods in session.query(Goods).filter(q).limit(limit):
            item = collections.OrderedDict()
            item['id'] = goods.id
            item['name'] = goods.name
            r_list.append(item)
        if not r_list:
            return '没有找到相关的商品'
        return r_list
    except Exception, ex:
        print ex
        return '出错了，请重试。'
    finally:
        close_session(session)

def wx_goods_detail(goods_id):
    """Returns the detail as a dict"""
    session = open_session()
    try:
        goods = session.query(Goods).get(int(goods_id))
        if goods == None:
            return '找不到该商品编号：' + str(goods_id)
        r_list = {}
        r_list['title'] = goods.name
        r_list['description'] = goods.brief
        r_list['pic'] = goods.picurl
        r_list['url'] = goods.weburl
        return r_list
    except Exception, ex:
        print ex
        return '出错了，请重试。'
    finally:
        close_session(session)

def wx_account_info(uid):
    """Returns the detail as a dict"""
    session = open_session()
    try:
        u = session.query(User).get(int(uid))
        a = session.query(Acct).filter(Acct.uid == int(uid)).one()
        if not u or not a:
            return '找不到该账户或信息缺失'
        r_list = collections.OrderedDict()
        for item in _user_list:
            r_list[item] = getattr(u, item)
        for item in _account_list:
            r_list[item] = getattr(a, item)
        return r_list
    except Exception, ex:
        print ex
        return '出错了，请重试。'
    finally:
        close_session(session)

def wx_favor_info(uid):
    """Returns the detail as a dict"""
    session = open_session()
    try:
        r_list = collections.OrderedDict()
        for f in session.query(Favor).filter(Favor.uid == int(uid)).all():
            for item in _favor_list:
                r_list[item] = getattr(f, item)
        if not r_list:
            return '您还未有收藏'
        return r_list
    except Exception, ex:
        print ex
        return '出错了，请重试。'
    finally:
        close_session(session)

def wx_history_info(uid):
    """Returns the detail as a dict"""
    session = open_session()
    try:
        r_list = collections.OrderedDict()
        for h in session.query(History).filter(History.uid == int(uid)).all():
            for item in _history_list:
                r_list[item] = getattr(h, item)
        if not r_list:
            return '您还未购买任何商品'
        return r_list
    except Exception, ex:
        print ex
        return '出错了，请重试。'
    finally:
        close_session(session)

