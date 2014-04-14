#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import web
import time
import os
#import urllib2,json

import weixinMessager as M

class WeixinInterface:
    def __init__(self):
        pass
    
    def GET(self):
        #获取输入参数
        data = web.input()
        signature = data.signature
        timestamp = data.timestamp
        nonce = data.nonce
        echostr = data.echostr
        #微信的token
        token = ""
        #字典序排序
        list = [token,timestamp,nonce]
        list.sort()
        sha1 = hashlib.sha1()
        map(sha1.update,list)
        #sha1加密算法
        hashcode = sha1.hexdigest()
        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            #check the user status
            view_session(self)
            check_user_status(self, fromUser)
            return echostr
            
    def POST(self):
        #str_xml = web.data().decode('utf-8') #获得post来的数据
        #msgtype = raw_input('Enter message type : ')
        #if not msgtype:
        #    msgtype = "text"
        msgtype = 'text'
        msg = raw_input('Enter a message : ')
        if not msg:
            msg = '0'
        info = {'time':int(time.time()), 'type': msgtype, 'content': msg}
        str_xml = "WXMSG_XML" % (info['time'],info['type'],info['content'])
        #print str_xml
        return replyMsg.reply(str_xml)

