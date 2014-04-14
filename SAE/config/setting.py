#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import web
#import sae

web.config.debug = False

db_conf = {
    'db':'',        # 数据库名
    'user':'',       # 用户名
    'password':'',     # 密码
    'host':'',     # 主库域名（可读写）
    'port':'',          # 端口，类型为，请根据框架要求自行转换为int
    'slave':''              # 从库域名（只读）
}

db = web.database(dbn='mysql', port=int(db_conf['port']), host=db_conf['host'], db=db_conf['db'], user=db_conf['user'], pw=db_conf['password'])

render = web.template.render('templates/', cache=False)

config = web.storage(
    email='',
    site_name = 'Test',
    site_desc = '',
    static = '/static',
)

web.template.Template.globals['config'] = config
web.template.Template.globals['render'] = render

def default_session():
    """session will be .update'd() with returned dict"""
    return {'user':'', 'loggedin':0, 'privilege':0, 'nowstep':'', 'prestep':''}

#For User sql operations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__DB_CONNECT_STRING = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (
    db_conf['user'],db_conf['password'],db_conf['host'],db_conf['port'],db_conf['db'])
__engine = create_engine(__DB_CONNECT_STRING, pool_recycle=20, echo=True)
DB_Session = sessionmaker(bind=__engine)

def open_engine():
    eg = create_engine(__DB_CONNECT_STRING, pool_recycle=20, echo=True)
    print "New engine created"
    return eg

def close_engine(eg):
    eg.drop()
    print "An engine dropped"

def open_session():
    #open a session
    dbs = DB_Session()
    print "Connected to MySql"
    return dbs

def close_session(dbs):
    #close a session
    dbs.close()
    print "Connection closed"

