#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import func, or_, not_

from config.setting import open_session, close_session
from config.model import WxSession as WX
import util
import util_query as uquery
from util_db import add_user, pin, buy, valid_login

__wx_items_list = ['wx_session_id', 'wx_id', 'user', 'nowstep', 'prestep', 'loggedin', 'privilege']

def menu(user=None, ignore_welcome=False):
    """返回给用户的操作指南（文字版）"""
    head = '回复【1】查看商品类别\n回复【2】查找商品\n'
    foot = '回复【?】查看可选操作\n回复【00】回到主菜单\n回复【01】查看常见疑问'
    dh = ''
    if user:
        if not ignore_welcome:
            dh += '欢迎回来，' + user + '！\n'
        dh += head
        dh += '回复【4】查看账户信息\n'
        dh += '回复【5】查看收藏\n'
        dh += '回复【6】查看购物历史\n'
        dh += '回复【9】退出\n'
    else:
        if not ignore_welcome:
            dh += '欢迎来到VS简单分享！\n'
        dh += head
        dh += '回复【7】用户注册\n'
        dh += '回复【8】登录\n'
    dh += foot
    return dh

def help_info():
    q = '常见疑问：\n'
    q += '1、用户注册需提交用户名和密码，用户名可以是手机号、邮箱或其它形式\n'
    q += '2、用户登录可使用用户名/手机号/邮箱+密码\n'
    q += '3、用户名长度需在6-36之间；如果包含中文，长度最少为2\n'
    q += '4、密码长度需在6-16之间\n'
    q += '5、回复【?】则显示当前可用的选项\n'
    q += '6、回复【00】将退出当前所有操作并回到主菜单'
    return q

def common_reply(req, status):
    if status['loggedin'] == 1:
        user = util.encode(status['user'].split('#')[0])
    else:
        user = ''
    if req == '00':
        update_status(status, {'nowstep': '', 'prestep': ''})
        return menu(user)
    if req == '01' or req == 'help':
        return help_info()
    #显示当前可用操作
    s = status['nowstep'].split('#')[0]
    if not s:
        return menu(user)
    if s in util.MESSAGE:
        return util.MESSAGE[s]
    return menu(user, True)

def update_status(status, new_status=None):
    """"""
    session = open_session()
    try:
        w = session.query(WX).get(int(status['wx_session_id']))
        if new_status != None:
            status.update(new_status)
        for item in __wx_items_list[2:]:
            setattr(w, item, status[item])
        session.merge(w)
        session.commit()
    except Exception, ex:
        print ex
    finally:
        close_session(session)

def _copy_status(wx_session):
    status = {}
    for item in __wx_items_list:
        status[item] = getattr(wx_session, item)
    return status

def get_wx_status(wxid):
    """"""
    session = open_session()
    try:
        w = session.query(WX).filter(WX.wx_id == wxid).first()
        if w == None:
            w = WX(wx_id=wxid)
            session.add(w)
            session.commit()
        elif w.loggedin == 1 and util.istimeout(w.atime):
            #Expired
            w.nowstep = w.prestep = ''
            w.loggedin = w.privilege = 0
            session.merge(w)
            session.commit()
        return _copy_status(w)
    except Exception, ex:
        print ex
        return False
    finally:
        close_session(session)

def do_after(status, action):
    """"""
    if action == 'logged_in':
        pass
    user = status['user'].split('#')[0]
    return common_reply('?', status)

def _user_login(status, request):
    uinfo = util.check_user_info(request)
    if isinstance(uinfo, str):
        return uinfo
    r = valid_login(uinfo)
    if isinstance(r, str):
        return r
    #Logged in successfully
    status.update({'user':r['name']+'#'+str(r['id']), 'privilege':r['privilege'], 'nowstep':status['prestep'], 'prestep':'', 'loggedin':1})
    update_status(status)
    return do_after(status, 'logged_in')

def _user_register(status, request):
    uinfo = util.check_user_info(request)
    if isinstance(uinfo, str):
        return uinfo
    e = uquery.user_existed(uinfo)
    if e:
        return e
    r = add_user(uinfo['name'], uinfo['pwd'], uinfo['mobile'], uinfo['email'])
    update_status(status, {'user':r['name']+'#'+str(r['id']), 'nowstep':status['prestep'], 'prestep':'', 'loggedin':1, 'privilege':r['privilege']})
    return util.MESSAGE['login_succeed'].replace('$NAME', util.encode(r['name']))

def _list_categories(status):
    update_status(status, {'nowstep': 'view_category', 'prestep': status['nowstep']})
    clist = uquery.list_categories()
    if isinstance(clist, str):
        return clist
    return util.output(clist) + '\n------\n' + util.MESSAGE['view_category']

def _view_category(status, request):
    if not util.isint(request):
        return 'invalid_index'
    clist = uquery.view_category(request)
    if isinstance(clist, str):
        return clist
    update_status(status, {'nowstep': 'view_category_detail#'+request, 'prestep': status['nowstep']})
    return util.output(clist) + '\n------\n' + util.MESSAGE['view_category_detail']

def _view_category_detail(status, request):
    if not util.isint(request):
        return 'invalid_index'
    if request == '05':
        #收藏
        if status['loggedin'] != 1:
            update_status(status, {'nowstep': 'user_login', 'prestep': status['nowstep']})
            return 'user_login'
        uid, cid = status['user'].split('#')[1], status['nowstep'].split('#')[1]
        return pin(uid, 'category', cid)
    else:
        return _view_category(status, request)

def _search_goods(status, request):
    glist = uquery.search_goods(request, 3)
    if isinstance(glist, str):
        return glist
    update_status(status, {'nowstep': 'list_goods', 'prestep': status['nowstep']})
    return util.output(glist) + '\n------\n' + util.MESSAGE['list_goods']

def _list_goods(status, request):
    if util.isint(request):
        glist = uquery.wx_goods_detail(request)
        if isinstance(glist, str):
            return glist
        update_status(status, {'nowstep': 'view_goods_detail#'+request, 'prestep': status['nowstep']})
        return {'type':'news', 'content':glist}
    else:
        return _search_goods(status, request)

def _view_goods_detail(status, request):
    if request in ['05', '09']:
        if status['loggedin'] != 1:
            update_status(status, {'nowstep': 'user_login', 'prestep': status['nowstep']})
            return 'user_login'
        uid, gid = status['user'].split('#')[1], status['nowstep'].split('#')[1]
        if request == '05':
            #收藏
            return pin(uid, 'goods', gid)
        else:
            #购买
            return buy(uid, gid)
    else:
        return 'invalid_goods_choice'

_action_map = {
    'user_login': _user_login,
    'user_register': _user_register,
    'view_category': _view_category,
    'view_category_detail': _view_category_detail,
    'search_goods': _search_goods,
    'list_goods': _list_goods,
    'view_goods_detail': _view_goods_detail
}

def check_text_action(wxid, request):
    """与用户的互动"""
    request = util.check_raw_input(request)
    status = get_wx_status(wxid)
    if not status:
        return util.MESSAGE['load_session_failed']
    #Global request
    if request in ['00', '01', '?', 'help', util.encode_simple('？')]:
        return common_reply(request, status)
    #Sub menu request
    if status['nowstep']:
        action = status['nowstep'].split('#')[0]
        if action in _action_map:
            return _action_map.get(action)(status, request)
    #Main menu request
    user, loggedin = None, status['loggedin']
    if loggedin == 1:
        user = status['user'].split('#')[1]
    if request == '1':#查看商品类别
        msg = _list_categories(status)
    elif request == '2':#查找商品
        update_status(status, {'nowstep': 'search_goods', 'prestep': ''})
        msg = 'search_goods'
    elif request == '4' and user:#查看账户信息
        msg = util.output(uquery.wx_account_info(user))
    elif request == '5' and user:#查看收藏
        msg = util.output(uquery.wx_favor_info(user))
    elif request == '6' and user:#查看购物历史
        msg = util.output(uquery.wx_history_info(user))
    elif request == '7' and not user:#注册
        update_status(status, {'nowstep': 'user_register', 'prestep': ''})
        msg = 'user_register'
    elif request == '8' and not user:#登录
        update_status(status, {'nowstep': 'user_login', 'prestep': ''})
        msg = 'user_login'
    elif request == '9' and loggedin:#退出
        update_status(status, {'user':'', 'nowstep':'', 'prestep':'', 'loggedin':0, 'privilege':0})
        msg = 'user_logout'
    else:#默认输出欢迎页面
        msg = 'invalid_request'
    #ok, return the message
    return msg

