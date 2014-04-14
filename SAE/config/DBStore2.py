#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime  
import web, models  
  
class SQLAStore(web.session.Store):  
    def __init__(self, table):  
        self.table = table  
        self.session = models.bindSQL()  
  
    def __contains__(self, key):  
        query = self.session.query(self.table).filter(self.table.session_id==key).first()  
        return bool(query)  
  
    def __getitem__(self, key):  
        s = self.session.query(self.table).filter(self.table.session_id==key).first()  
        if not s:  
            raise KeyError  
        else:  
            s.atime = datetime.datetime.now()  
            self.session.commit()  
            return self.decode(s.data)  
  
    def __setitem__(self, key, value):  
        pickled = self.encode(value)  
        now = datetime.datetime.now()  
        if key in self:  
            query = self.session.query(self.table).filter(self.table.session_id==key).first()  
            query.data = pickled  
            query.atime = now  
        else:  
            query = self.table(session_id=key, data=pickled)  
            self.session.add(query)  
        self.session.commit()  
  
    def __delitem__(self, key):  
        self.session.query(self.table).filter(self.table.session_id==key).delete()  
        self.session.commit()  
  
    def cleanup(self, timeout):  
        timeout = datetime.timedelta(timeout/(24.0*60*60)) #timedelta takes numdays as arg  
        last_allowed_time = datetime.datetime.now() - timeout  
        self.session.query(self.table).filter(self.table.atime < last_allowed_time).delete()  
        self.session.commit()
        
