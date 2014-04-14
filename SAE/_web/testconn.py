#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sae.const
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_conf = {
    'db':sae.const.MYSQL_DB,      # 数据库名
    'user':sae.const.MYSQL_USER,    # 用户名
    'password':sae.const.MYSQL_PASS,    # 密码
    'host':sae.const.MYSQL_HOST,    # 主库域名（可读写）
    'port':sae.const.MYSQL_PORT,    # 端口，类型为，请根据框架要求自行转换为int
    'slave':sae.const.MYSQL_HOST_S  # 从库域名（只读）
}

def open():
    DB_CONNECT_STRING = 'mysql://%s:%s@%s:%s/%s?charset=utf8&use_unicode=0'%(
        db_conf['user'],db_conf['password'],db_conf['host'],db_conf['port'],db_conf['db'])
    #connect to db
    engine = create_engine(DB_CONNECT_STRING, echo=True)
    DB_Session = sessionmaker(bind=engine)
    session = DB_Session()
    print "Connected to MySql"
    session.execute('show tables')
    print session.execute('show tables').fetchall()
    session.close()
    return "Success"

