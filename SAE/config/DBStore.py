#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import web

from model import sql_session

class SQLAStore(web.session.Store):
    def __init__(self, table):
        self.table = table

    def __contains__(self, key):
        return bool(sql_session.execute(self.table.select(self.table.c.session_id==key)).fetchone())

    def __getitem__(self, key):
        s = sql_session.execute(self.table.select(self.table.c.session_id==key)).fetchone()
        if s is None:
            raise KeyError
        else:
            sql_session.execute(self.table.update().values(atime=datetime.datetime.now()).where(self.table.c.session_id==key))
            return self.decode(s[self.table.c.data])

    def __setitem__(self, key, value):
        pickled = self.encode(value)
        if key in self:
            sql_session.execute(self.table.update().values(data=pickled).where(self.table.c.session_id==key))
        else:
            sql_session.execute(self.table.insert().values(session_id=key, data=pickled))
        sql_session.commit()

    def __delitem__(self, key):
        sql_session.execute(self.table.delete(self.table.c.session_id==key))

    def cleanup(self, timeout):
        timeout = datetime.timedelta(timeout/(24.0*60*60))
        last_allowed_time = datetime.datetime.now() - timeout
        sql_session.execute(self.table.delete(self.table.c.atime<last_allowed_time))

