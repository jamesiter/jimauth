#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, request, g, make_response
from flask import session
import jimit as ji

from models import App
from models import RoleAppMapping
from models import Utils, Rules, User


__author__ = 'James Iter'
__date__ = '16/6/8'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2016 by James Iter.'


blueprint = Blueprint(
    'user',
    __name__,
    url_prefix='/api/user'
)


@Utils.dumps2response
def r_sign_up():

    user = User()

    args_rules = [
        Rules.LOGIN_NAME.value,
        Rules.PASSWORD.value
    ]
    user.login_name = request.json.get('login_name')
    user.password = request.json.get('password')

    try:
        ji.Check.previewing(args_rules, user.__dict__)
        user.password = ji.Security.ji_pbkdf2(user.password)
        user.create()
        user.get_by('login_name')
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = user.__dict__
        del ret['data']['password']
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_sign_up_by_mobile_phone():

    user = User()

    args_rules = [
        Rules.MOBILE_PHONE.value,
        Rules.PASSWORD.value
    ]
    user.mobile_phone = request.json.get('mobile_phone')
    user.password = request.json.get('password')
    user.login_name = ji.Common.generate_random_code(length=10, letter_form='lower')

    try:
        ji.Check.previewing(args_rules, user.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if user.exist_by('mobile_phone'):
            ret['state'] = ji.Common.exchange_state(40901)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', user.mobile_phone])
            return ret

        user.password = ji.Security.ji_pbkdf2(user.password)
        user.create()
        user.get_by('login_name')
        ret['data'] = user.__dict__
        del ret['data']['password']
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_sign_up_by_email():

    user = User()

    args_rules = [
        Rules.EMAIL.value,
        Rules.PASSWORD.value
    ]
    user.email = request.json.get('email')
    user.password = request.json.get('password')
    user.login_name = ji.Common.generate_random_code(length=10, letter_form='lower')

    try:
        ji.Check.previewing(args_rules, user.__dict__)

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)

        if user.exist_by('email'):
            ret['state'] = ji.Common.exchange_state(40901)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], ': ', user.email])
            return ret

        user.password = ji.Security.ji_pbkdf2(user.password)
        user.create()
        user.get_by('login_name')
        ret['data'] = user.__dict__
        del ret['data']['password']
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_sign_in():

    user = User()

    args_rules = [
        Rules.LOGIN_NAME.value,
        Rules.PASSWORD.value
    ]
    user.login_name = request.json.get('login_name')
    user.password = request.json.get('password')

    try:
        ji.Check.previewing(args_rules, user.__dict__)
        plain_password = user.password
        user.get_by('login_name')

        if not ji.Security.ji_pbkdf2_check(password=plain_password, password_hash=user.password):
            ret = dict()
            ret['state'] = ji.Common.exchange_state(40101)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], u': 鉴权失败'])
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        token = Utils.generate_token(user.id)
        session['token'] = token
        rep = make_response()
        rep.data = json.dumps({'state': ji.Common.exchange_state(20000), 'manager': user.manager}, ensure_ascii=False)
        return rep

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_sign_in_by_mobile_phone():

    user = User()

    args_rules = [
        Rules.MOBILE_PHONE.value,
        Rules.PASSWORD.value
    ]
    user.mobile_phone = request.json.get('mobile_phone')
    user.password = request.json.get('password')

    try:
        ji.Check.previewing(args_rules, user.__dict__)
        plain_password = user.password
        user.get_by('mobile_phone')

        if not ji.Security.ji_pbkdf2_check(password=plain_password, password_hash=user.password):
            ret = dict()
            ret['state'] = ji.Common.exchange_state(40101)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], u': 鉴权失败'])
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        token = Utils.generate_token(user.id)
        session['token'] = token
        rep = make_response()
        rep.data = json.dumps({'state': ji.Common.exchange_state(20000), 'manager': user.manager}, ensure_ascii=False)
        return rep

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_sign_in_by_email():

    user = User()

    args_rules = [
        Rules.EMAIL.value,
        Rules.PASSWORD.value
    ]
    user.email = request.json.get('email')
    user.password = request.json.get('password')

    try:
        ji.Check.previewing(args_rules, user.__dict__)
        plain_password = user.password
        user.get_by('email')

        if not ji.Security.ji_pbkdf2_check(password=plain_password, password_hash=user.password):
            ret = dict()
            ret['state'] = ji.Common.exchange_state(40101)
            ret['state']['sub']['zh-cn'] = ''.join([ret['state']['sub']['zh-cn'], u': 鉴权失败'])
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

        token = Utils.generate_token(user.id)
        session['token'] = token
        rep = make_response()
        rep.data = json.dumps({'state': ji.Common.exchange_state(20000), 'manager': user.manager}, ensure_ascii=False)
        return rep

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_sign_out():
    for key in session.keys():
        session.pop(key=key)


@Utils.dumps2response
def r_get():
    user = User()

    args_rules = [
        Rules.UID.value
    ]
    user.id = g.token.get('uid', 0).__str__()

    try:
        ji.Check.previewing(args_rules, user.__dict__)
        user.id = long(user.id)
        user.get()
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = user.__dict__
        del ret['data']['password']
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_change_password():

    user = User()

    args_rules = [
        Rules.UID.value
    ]
    user.id = g.token.get('uid', 0).__str__()

    try:
        ji.Check.previewing(args_rules, user.__dict__)
        user.get()
    except ji.PreviewingError, e:
        return json.loads(e.message)

    args_rules = [
        Rules.PASSWORD.value
    ]
    user.password = request.json.get('password')

    try:
        ji.Check.previewing(args_rules, user.__dict__)
        user.password = ji.Security.ji_pbkdf2(user.password)
        user.update()
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_auth():
    user = User()

    args_rules = [
        Rules.UID.value
    ]
    user.id = g.token.get('uid', 0).__str__()

    try:
        ji.Check.previewing(args_rules, user.__dict__)
        user.id = long(user.id)
        user.get()
        if not user.enabled:
            ret = dict()
            ret['state'] = ji.Common.exchange_state(40301)
            raise ji.PreviewingError(json.dumps(ret, ensure_ascii=False))

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
def r_app_list():
    order_by = request.args.get('order_by', 'create_time')
    order = request.args.get('order', 'asc')
    app_map_by_id = dict()
    user = User()

    args_rules = [
        Rules.UID.value
    ]
    user.id = g.token.get('uid', 0).__str__()

    try:
        ji.Check.previewing(args_rules, user.__dict__)

        user.get()

        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()

        app_data, app_total = App.get_all(order_by=order_by, order=order)

        for app in app_data:
            del app['secret']
            app_map_by_id[app['id']] = app

        role_app_mapping_data, role_app_mapping_total = RoleAppMapping.get_all(order_by='role_id', order='asc')

        for role_app_mapping in role_app_mapping_data:
            if role_app_mapping['role_id'] == user.role_id:
                ret['data'].append(app_map_by_id[role_app_mapping['appid']])

        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)

