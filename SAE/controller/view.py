#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
from config.setting import render
import util
import util_db as udb
import util_query as uquery

session = web.ctx.session

def user_login(name, pwd):
    r = uquery.check_valid_login(pwd, name)
    if r != False:
        session.user = r['name']
        session.loggedin = True
        session.laststep = 'loggedin'
        session.privilege = r['privilege']
        return True
    else:
        return False

class Index:
    def GET(self):
        print session.loggedin
        if session.loggedin == True:
            msg = session.user
        else:
            msg = 'Guest'
        return render.index(msg)

class Login:
    def GET(self):
        print session.loggedin
        if session.loggedin == True:
            return render.index(session.user)
        else:
            return render.login('')

class Logout:
    def GET(self):
        session.user = ''
        session.loggedin = False
        session.privilege = 0
        raise web.seeother('/')

class LoginCheck:
    def POST(self):
        """Deal with user login action."""
        #获取表单信息
        print '>LoginCheck<', web.input()
        i = web.input()
        user =i.get('username',None)
        pwd=i.get('userpwd',None)
        print user,pwd
        if user != None and pwd != None:
            if user_login(name=user, pwd=pwd):
                session.loggedin = True
                session.user = user
                return render.index('welcome back(' + session.user + ")")
            else:
                return render.login('Wrong username or password!')
        else:
            #raise web.seeother('/login')
            return render.login('Username and password can not be empty!')

