#coding: UTF-8
import os

import sae
import web

from weixinInterface import WeixinInterface

urls = (
  '/', "hello",
  '/weixin', 'WeixinInterface'
)

class Hello:
	def GET(self):
		#print "你好"
		app_root = os.path.dirname(__file__)
        templates_root = os.path.join(app_root, 'templates')
        render = web.template.render(templates_root)
		return render.hello("你好")

app = web.application(urls, globals()).wsgifunc()

application = sae.create_wsgi_app(app)
