#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
from config import setting, url

app = web.application(url.urls, globals(), autoreload=True)
db = setting.db
store = web.session.DBStore(db, 'session')
session = web.session.Session(app, store, initializer=setting.default_session)
web.config._session = session

def session_hook():
    web.ctx.session = session
    if not 'user' in session:
        session.user = ''
        session.loggedin = False
        session.privilege = 0
        session.nowstep = ''
        session.prestep = ''

app.add_processor(web.loadhook(session_hook))

#application = sae.create_wsgi_app(app.wsgifunc())

if __name__ == "__main__":
    app.run()
else:
    application = app.wsgifunc()
    
