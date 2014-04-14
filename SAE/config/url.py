#!/usr/bin/env python
# -*- coding: utf-8 -*-

pre_fix = 'controller.'

urls = (
    '/',                pre_fix + 'view.Index',
    '/index',           pre_fix + 'view.Index',
    '/login',           pre_fix + 'view.Login',
    '/login_check',     pre_fix + 'view.LoginCheck',
    '/logout',          pre_fix + 'view.Logout',
    '/weixin',          pre_fix + 'WeixinInterface'
)

