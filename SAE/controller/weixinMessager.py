#!/usr/bin/env python
# -*- coding: utf-8 -*-
import lxml
import time
from lxml import etree

from config.setting import render
from util import MESSAGE_TYPE, MESSAGE
from util_wx import check_text_action

def reply_text(fromUser, toUser, content):
    return render.reply_text(fromUser, toUser, int(time.time()), content)

def reply_image(fromUser, toUser, content):
    fromUser = xml.find("FromUserName").text
    toUser = xml.find("ToUserName").text
    msg = '图片：http://cn.bing.com/images/'
    return render.reply_text(fromUser,toUser,int(time.time()),msg)

def reply_voice(fromUser, toUser, content):
    fromUser = xml.find("FromUserName").text
    toUser = xml.find("ToUserName").text
    msg = '语音：http://cn.bing.com/search?q=语音'
    return render.reply_text(fromUser,toUser,int(time.time()),msg)

def reply_video(fromUser, toUser, content):
    fromUser = xml.find("FromUserName").text
    toUser = xml.find("ToUserName").text
    msg = '视频：http://cn.bing.com/video/'
    return render.reply_text(fromUser,toUser,int(time.time()),msg)

def reply_music(fromUser, toUser, content):
    fromUser = xml.find("FromUserName").text
    toUser = xml.find("ToUserName").text
    msg = '音乐：http://cn.bing.com/music/'
    return render.reply_text(fromUser,toUser,int(time.time()),msg)

def reply_news(fromUser, toUser, content):
    t = int(time.time())
    title = content['title']
    desc = content['description']
    pic = content['pic']
    url = content['url']
    return render.reply_news(fromUser,toUser,t, title, desc, pic, url)

def reply_custom(fromUser, toUser, content):
    #调用客服消息接口
    return ''

#按内容发送被动响应消息
_reply_msg = {
    "text": reply_text,
    "image": reply_image,
    "voice": reply_voice,
    "video": reply_video,
    "music": reply_music,
    "news": reply_news,
    "custom": reply_custom
}

def check_wxid(wxid):
    if len(wxid) > 28:
        wxid = wxid[-28:]
    return wxid

class Messager():
    def __init__(self, xml):
        self.xml = etree.fromstring(xml) #进行XML解析
        self.fromUser = self.xml.find("FromUserName").text
        self.toUser = self.xml.find("ToUserName").text
        self.msgType = self.xml.find("MsgType").text
        self.wxid = check_wxid(self.fromUser)

    def reply(self):
        if self.msgType != 'text':
            #不能及时处理非文本消息，但至少可以向用户表明我们已经收到了
            msg = '您向我们发送了一份' + MESSAGE_TYPE[self.msgType] + '。我们正在处理中。您可以继续操作:)'
            return reply_text(self.fromUser, self.toUser, msg)
        content = self.xml.find("Content").text
        msg = check_text_action(self.wxid, content)
        if isinstance(msg, str):
            if msg in MESSAGE:
                msg = MESSAGE[msg]
            return reply_text(self.fromUser, self.toUser, msg)
        return _reply_msg.get(msg['type'])(self.fromUser, self.toUser, msg['content'])

