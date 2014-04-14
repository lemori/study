#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column,ForeignKey,create_engine
from sqlalchemy.dialects.mysql import CHAR,DECIMAL,INTEGER,SMALLINT,TIMESTAMP,TINYINT,VARCHAR,TEXT
from sqlalchemy.sql.expression import text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WebpySession(Base):
    """This session only works for PC request."""
    __tablename__ = 'session'
    __table_args__ = {
        'mysql_engine':'MyISAM',
        'mysql_charset':'utf8'
    }
    session_id = Column(CHAR(128), nullable=False, primary_key=True)
    atime = Column(TIMESTAMP, nullable=False, server_default = text("CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP"))
    data = Column(TEXT, nullable=True)

#User defined tables BEGIN
class WxSession(Base):
    """This session only works for PC request."""
    __tablename__ = 'wx_session'
    __table_args__ = {
        'mysql_engine':'MyISAM',
        'mysql_charset':'utf8'
    }
    wx_session_id = Column(INTEGER(11), primary_key = True)
    wx_id = Column(CHAR(28), nullable = False, unique = True, index=True)
    user = Column(VARCHAR(28), default = '')
    nowstep = Column(VARCHAR(20), default = '')
    prestep = Column(VARCHAR(20), default = '')
    privilege = Column(TINYINT(4), default = '')
    loggedin = Column(TINYINT(4), default = 0)
    atime = Column(TIMESTAMP, nullable=False, server_default = text("CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP"))  

class User(Base):
    __tablename__ = 'User'
    __table_args__ = {
        'mysql_engine':'MyISAM',
        'mysql_charset':'utf8'
    }
    #column
    id = Column(INTEGER(11), primary_key = True)
    name = Column(VARCHAR(36), nullable = False, unique = True, index = True)
    passwd = Column(VARCHAR(16), nullable = False)
    mobile = Column(CHAR(11), unique = True, index = True)
    email = Column(VARCHAR(36), unique = True)
    regdate = Column(TIMESTAMP, server_default = text("CURRENT_TIMESTAMP"))
    lastactive = Column(TIMESTAMP)
    isvalid = Column(TINYINT(4), default = 1)
    bindto = Column(VARCHAR(30))
    privilege = Column(TINYINT(4), default = 0)
    perserved1 = Column(VARCHAR(45))
    perserved2 = Column(VARCHAR(45))

class Acct(Base):
    __tablename__ = 'Acct'
    __table_args__ = {
        'mysql_engine':'MyISAM',
        'mysql_charset':'utf8'
    }
    #column
    id = Column(INTEGER(11), primary_key = True)
    uid = Column(INTEGER(11), ForeignKey('User.id', ondelete='CASCADE', onupdate='CASCADE'), unique = True)
    balance = Column(DECIMAL(10,2), nullable = False, default = 0.00)
    bonus = Column(INTEGER(10), nullable = False, default = 0)
    creditcard = Column(VARCHAR(30))
    debitcard = Column(VARCHAR(30))
    address = Column(VARCHAR(254))
    rank = Column(TINYINT(4), default = 1)
    perserved1 = Column(VARCHAR(45))
    perserved2 = Column(VARCHAR(45))

class Category(Base):
    __tablename__ = 'Category'
    __table_args__ = {
        'mysql_engine':'MyISAM',
        'mysql_charset':'utf8'
    }
    #column
    id = Column(INTEGER(11), primary_key = True)
    name = Column(VARCHAR(16), nullable = False, unique = True, index = True)
    brief = Column(VARCHAR(30))
    rank = Column(TINYINT(4), default = 1)
    perserved1 = Column(VARCHAR(45))
    perserved2 = Column(VARCHAR(45))

class Goods(Base):
    __tablename__ = 'Goods'
    __table_args__ = {
        'mysql_engine':'MyISAM',
        'mysql_charset':'utf8'
    }
    #column
    id = Column(INTEGER(11), primary_key = True)
    cid = Column(INTEGER(11), ForeignKey('Category.id', ondelete='SET NULL', onupdate='CASCADE'), nullable = True)
    name = Column(VARCHAR(30), nullable = False, index = True)
    brief = Column(VARCHAR(127))
    price = Column(DECIMAL(8,2), default = 0.00)
    discount = Column(TINYINT(4), default = 100)
    picurl = Column(VARCHAR(255))
    weburl = Column(VARCHAR(127))
    ontime = Column(TIMESTAMP, server_default = text("CURRENT_TIMESTAMP"))
    insale = Column(TINYINT(4), default = 1)
    rank = Column(TINYINT(4), default = 1)
    perserved1 = Column(VARCHAR(45))
    perserved2 = Column(VARCHAR(45))

class Favor(Base):
    __tablename__ = 'Favor'
    __table_args__ = {
        'mysql_engine':'MyISAM',
        'mysql_charset':'utf8'
    }
    #column
    id = Column(INTEGER(11), primary_key = True)
    uid = Column(INTEGER(11), ForeignKey('User.id', ondelete='CASCADE', onupdate='CASCADE'), nullable = False)
    ftype = Column(CHAR(1), nullable = False)
    tid = Column(INTEGER(11), nullable = True)
    atime = Column(TIMESTAMP, nullable=False, server_default = text("CURRENT_TIMESTAMP"))
    perserved = Column(VARCHAR(45))

class History(Base):
    __tablename__ = 'History'
    __table_args__ = {
        'mysql_engine':'MyISAM',
        'mysql_charset':'utf8'
    }
    #column
    id = Column(INTEGER(11), primary_key = True)
    uid = Column(INTEGER(11), ForeignKey('User.id', ondelete='CASCADE', onupdate='CASCADE'), nullable = False)
    gid = Column(INTEGER(11), ForeignKey('Goods.id', ondelete='SET NULL', onupdate='CASCADE'), nullable = True)
    cash = Column(DECIMAL(8,2), nullable = True)
    bonus = Column(INTEGER(10), nullable = True)
    atime = Column(TIMESTAMP, nullable=False, server_default = text("CURRENT_TIMESTAMP"))
    perserved = Column(VARCHAR(45))

#User defined tables END

metadata = Base.metadata

if __name__ =='__main__':
    from setting import open_engine, close_engine
    mysql_engine = open_engine()
    metadata.create_all(mysql_engine)
    close_engine(mysql_engine)

