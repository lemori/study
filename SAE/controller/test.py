#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
from config.setting import render
import util

session = web.ctx.session

class Test:
    def POST(self):
        """Test for web."""
        i = web.input()
        choice = i.get('choice', None)
        item = i.get('item', None)
        if choice == '1':
            return render.index(util.list_categories())
        elif choice == '2':
            if item == '':
                return render.index('请输入商品名称')
            else:
                return render.index(util.search_for_goods(item))
        else:
            return render.index('请选择一个选项')

