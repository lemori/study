#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
from sqlalchemy import func, or_, not_

from config.setting import open_session, close_session
from config.model import User, Acct, Favor, History, Category, Goods
#import util

__all__ = ["valid_login", "check_exist_user", "add_account", "add_favor", "add_history", "add_category", "add_goods", "add_user", "delete", "update", "pin", "buy"]

tables = {
    'user'      : User,
    'account'   : Acct,
    'favor'     : Favor,
    'history'   : History,
    'category'  : Category,
    'goods'     : Goods
}

def add_account(uid, balance=0.00, bonus=0, addr=''):
    """Add a new account with user id, balance and bounus.
    Once created successfully, return the account id."""
    session = open_session()
    try:
        a = Acct(uid=uid, balance=balance, bonus=bonus, address=addr)
        session.add(a)
        session.commit()
        return a.id
    except Exception, ex:
        session.rollback()
        print ex
        return False
    finally:
        close_session(session)

def add_favor(uid, favor_type, target_id):
    """Add a new favor with user, category and goods ids.
    Once created successfully, return the favor id."""
    session = open_session()
    try:
        f = Favor(uid=int(uid), ftype=favor_type, tid=int(target_id))
        session.add(f)
        session.commit()
        return f.id
    except Exception, ex:
        session.rollback()
        print ex
        return False
    finally:
        close_session(session)

def add_history(uid, goods_id, cash=0.00, bonus=0):
    """Add a new history with user id, goods id, cash and bonus.
    Once created successfully, return the history id."""
    session = open_session()
    try:
        h = History(uid=int(uid), gid=int(goods_id), cash=cash, bonus=bonus)
        session.add(h)
        session.commit()
        return h.id
    except Exception, ex:
        session.rollback()
        print ex
        return False
    finally:
        close_session(session)

def add_category(name, brief='', rank=1):
    """Add a new category with name, brief, rank.
    Once created successfully, return the category id and name."""
    session = open_session()
    try:
        c = Category(name=name, brief=brief, rank=rank)
        session.add(c)
        session.commit()
        return {'id':c.id, 'name':c.name}
    except Exception, ex:
        session.rollback()
        print ex
        return False
    finally:
        close_session(session)

def add_goods(category_id, name, brief='', price=0.00, pic_url='', web_url='', rank=1):
    """Add a new goods with category_id, name, brief, etc.
    Once created successfully, return the goods id and name."""
    session = open_session()
    try:
        g = Goods(cid=int(category_id), name=name, brief=brief, price=float(price), picurl=pic_url, weburl=web_url, rank=rank)
        session.add(g)
        session.commit()
        return {'id':g.id, 'name':g.name}
    except Exception, ex:
        session.rollback()
        print ex
        return False
    finally:
        close_session(session)

def check_exist_user(session, u_account):
    """u_account can be name/mobile/email.
    Returns count if found any, otherwise, 0."""
    query_str = ''
    if u_account['name']:
        query_str += 'name="' + u_account['name'] + '" or '
    if u_account['mobile']:
        query_str += 'mobile="' + u_account['mobile'] + '" or '
    if u_account['email']:
        query_str += 'email="' + u_account['email'] + '" or '
    if not query_str:
        #Error user info, return 1 is safe
        return 1
    return session.query(func.count(User.id)).filter(query_str[0:-4]).scalar()

def add_user(name, pwd, mobile='', email='', bindto=None, privilege=0):
    """Add a new user with name, password, mobile, email.
    Once created successfully, return the user id, name and privilege."""
    session = open_session()
    try:
        #If existed, it will raise error
        user = User(name=name, passwd=pwd, mobile=mobile, email=email, lastactive=func.current_timestamp(), bindto=bindto, privilege=privilege)
        session.add(user)
        session.flush()
        #Add an account to this user
        a = Acct(uid=user.id)
        session.add(a)
        session.commit()
        return {'id':user.id, 'name':user.name, 'privilege':user.privilege}
    except Exception, ex:
        session.rollback()
        print ex
        return False
    finally:
        close_session(session)

def _clean_user_info(session, user):
    """Clean user info manually as MyISAM doesn't support foreign key."""
    #Acct
    a = session.query(Acct).filter(Acct.uid == user.id).one()
    session.delete(a)
    #Favor
    for f in session.query(Favor).filter(Favor.uid == user.id).all():
        session.delete(f)
    #History
    for h in session.query(History).filter(History.uid == user.id).all():
        session.delete(h)
    #Critic user attributes but remain user name, mobile, email for recall
    user.preserved1 = user.mobile + '#' + user.email
    r = str(random.uniform(0.2, 1.0))
    user.email, user.mobile, user.isvalid, user.bindto = None, r[2:13], 0, None
    session.merge(user)

def _del_user(session, user_list):
    """Delete user by user list"""
    import random
    if not isinstance(user_list, list):
        ulist = [user_list]
    count = 0
    for uid in ulist:
        user = session.query(User).get(int(uid))
        if user != None:
            _clean_user_info(session, user)
            count += 1
            print '**User "' + str(uid) + '" has been deleted.'
    return count

def delete(del_list):
    """Delete a set of records.
    del_list: a dict like{'user':id} or {'user':[id1, id2]}."""
    if not isinstance(del_list, dict):
        return '待删除列表格式不正确。'
    #check if delete user record
    if table_type == 'user':
        return del_user(uid=key)
    session = open_session()
    try:
        count, msg = 0, ''
        for item, value in del_list.items():
            if item in tables:
                if item == 'user':
                    #Special for user records
                    count += _del_user(session, value)
                elif isinstance(value, list):
                    for i in value:
                        record = session.query(tables[item]).get(int(i))
                        if record:
                            session.delete(record)
                            count += 1
                            print '**Record from ' + tables[item] + ' by ' + str(i) + ' deleted.'
                else:
                    record = session.query(tables[item]).get(int(value))
                    if record:
                        session.delete(record)
                        count += 1
                        print '**Record from ' + tables[item] + ' by ' + str(value) + ' deleted.'
        if count:
            session.commit()
        else:
            msg = '没啥可删除的'
        return {'count':count, 'msg':msg}
    except Exception, ex:
        session.rollback()
        print ex
        return {'count':0, 'msg':'删除时出现错误，已撤销。'}
    finally:
        close_session(session)

def _update_by_type(session, table_type, info):
    """Update a record. Return if succeeded."""
    record = session.query(tables[table_type]).get(int(info['id']))
    if record == None:
        #'**Record from ' + table_type + ' by ' + str(key) + ' not found'
        return False
    count = 0
    for item, value in info.items():
        if hasattr(record, item):
            setattr(record, item, value)
            count += 1
    print '**Record from ' + table_type + ' by ' + str(key) + ' updated'
    if count:
        if table_type == 'user':
            setattr(record, 'lastactive', func.current_timestamp())
        session.merge(record)
        return True
    else:
        return False

def update(info):
    """Update records from a collection and returns {count, msg}.
    info: a dict like {'type':'user', 'id':uid, 'item':value} or {'user':{}, 'account':{}}"""
    #update common records
    session = open_session()
    try:
        count, msg = 0, ''
        if 'type' in info:
            #A single records
            if not info['type'] in tables:
                return {'count':0, 'msg':'不能识别的记录: ' + info['type'] + '！'}
            if not 'id' in info:
                return {'count':0, 'msg':'无效的记录！'}
            info = util.check_update_info(info, [])
            #Remind that no column named 'type'
            if _update_by_type(session, info['type'], info):
                count = 1
        else:
            #A set of records
            for item, value in info.items():
                if item in tables and isinstance(value, dict) and 'id' in value:
                    value = util.check_update_info(value, [])
                    if _update_by_type(session, item, value):
                        count += 1
        if count:
            session.commit()
        else:
            msg = '没什么可更新的。'
        return {'count':count, 'msg':msg}
    except Exception, ex:
        session.rollback()
        print ex
        return {'count':0, 'msg':'更新时出现错误，已撤销。'}
    finally:
        close_session(session)

def pin(uid, ftype, tid):
    if ftype == 'goods':
        ftype = 'G'
    elif ftype == 'category':
        ftype = 'C'
    else:
        return '无效的收藏类别：' + ptype
    session = open_session()
    try:
        q = 'uid=' + str(uid) + ' and ftype="' + ftype + '" and tid=' + str(tid)
        f = session.query(Favor).filter(q).first()
        if f:
            return '您已经收藏过该商品。'
        else:
            f = Favor(uid=int(uid), ftype=ftype, tid=int(tid))
            session.add(f)
            session.commit()
            return '您已成功收藏该商品。'
    except Exception, ex:
        session.rollback()
        print ex
        return '收藏时出现错误，请重试。'
    finally:
        close_session(session)
        
def buy(uid, gid):
    session = open_session()
    try:
        u = session.query(User).get(int(uid))
        if not u:
            return '无效的用户：' + str(uid)
        g = session.query(Goods).get(int(gid))
        if not g:
            return '无效的商品：' + str(gid)
        a = session.query(Acct).filter(Acct.uid == u.id).one()
        price = g.price * g.discount / 100
        bonus = int(math.ceil(g.price * 2))
        cash = 0.00
        if a.bonus > bonus:
            a.bonus = a.bonus - bonus
        elif a.balance > price:
            a.balance = a.balance - price
            bonus, cash = 0, price
        else:
            return '余额及积分不足，请先充值。'
        h = History(uid=int(uid), gid=int(gid), cash=cash, bonus=bonus)
        session.add(h)
        session.merge(a)
        session.commit()
        return '您已购买该商品，剩余余额' + str(a.balance) + '元，积分' + str(a.bonus) + '个。'
    except Exception, ex:
        session.rollback()
        print ex
        return '购买时出现错误，请重试。'
    finally:
        close_session(session)

def valid_login(u_account):
    """Check if current login pass is acceptable.
    User can login by name, mobile or email.
    Returns a dict {id, name, privilege} if valid."""
    query_str = ''
    if u_account['name']:
        query_str = 'name="' + u_account['name'] + '"'
    elif u_account['mobile']:
        query_str = 'mobile="' + u_account['mobile'] + '"'
    elif u_account['email']:
        query_str = 'email="' + u_account['email'] + '"'
    if not query_str or not u_account['pwd']:
        #Error user info, return 1 is safe
        return '无效的用户名和密码格式'
    query_str += ' and passwd="' + u_account['pwd'] + '"'
    session = open_session()
    try:
        u = session.query(User).filter(query_str).first()
        if u == None:
            return '用户名或密码错误。'
        u.lastactive = func.current_timestamp()
        session.merge(u)
        session.commit()
        return {'id': u.id, 'name': u.name, 'privilege': u.privilege}
    except Exception, ex:
        print ex
        return '出错了，请重试。'
    finally:
        close_session(session)

