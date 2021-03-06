#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
from flask import Blueprint, request
import jimit as ji

from models import RoleAppMapping
from models import UidOpenidMapping
from models import Utils, Rules, App


__author__ = 'James Iter'
__date__ = '2016/11/5'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2016 by James Iter.'


blueprint = Blueprint(
    'app',
    __name__,
    url_prefix='/api/app'
)

blueprints = Blueprint(
    'apps',
    __name__,
    url_prefix='/api/apps'
)


@Utils.dumps2response
@Utils.superuser
def r_create():

    app = App()

    args_rules = [
        Rules.APP_NAME.value,
        Rules.APP_HOME_PAGE.value,
        Rules.APP_REMARK.value
    ]

    app.id = ji.Common.generate_random_code(length=16, letter_form='mix', numeral=True)
    app.secret = ji.Common.generate_random_code(length=32, letter_form='mix', numeral=True)
    app.name = request.json.get('name', '')
    app.home_page = request.json.get('home_page', '')
    app.remark = request.json.get('remark', '')

    try:
        ji.Check.previewing(args_rules, app.__dict__)
        app.create()
        app.get()
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = app.__dict__
        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
@Utils.superuser
def r_delete(_id):
    app = App()

    args_rules = [
        Rules.APP_ID.value
    ]
    app.id = _id

    try:
        ji.Check.previewing(args_rules, app.__dict__)
        if app.exist():
            app.delete()
            # 删除依赖于该AppKey的openid
            UidOpenidMapping.delete_by_filter('appid:in:' + _id)
            # 删除依赖于该AppKey的role映射
            RoleAppMapping.delete_by_filter('appid:in:' + _id)
        else:
            ret = dict()
            ret['state'] = ji.Common.exchange_state(40401)
            return ret

    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
@Utils.superuser
def r_update(_id):

    args_rules = [
        Rules.APP_ID.value
    ]

    if 'name' in request.json:
        args_rules.append(
            Rules.APP_NAME.value
        )

    if 'home_page' in request.json:
        args_rules.append(
            Rules.APP_HOME_PAGE.value
        )

    if 'remark' in request.json:
        args_rules.append(
            Rules.APP_REMARK.value
        )

    if args_rules.__len__() < 2:
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        return ret

    request.json['id'] = _id

    try:
        ji.Check.previewing(args_rules, request.json)
        app = App()
        app.id = request.json['id']
        app.get()

        if request.json.get('secret', False):
            app.secret = ji.Common.generate_random_code(length=32, letter_form='mix', numeral=True)

        app.name = request.json.get('name', app.name)
        app.home_page = request.json.get('home_page', app.home_page)
        app.remark = request.json.get('remark', app.remark)

        app.update()
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
@Utils.superuser
def r_get_by_filter():
    page = str(request.args.get('page', 1))
    page_size = str(request.args.get('page_size', 50))

    args_rules = [
        Rules.PAGE.value,
        Rules.PAGE_SIZE.value
    ]

    try:
        ji.Check.previewing(args_rules, {'page': page, 'page_size': page_size})
    except ji.PreviewingError, e:
        return json.loads(e.message)

    page = int(page)
    page_size = int(page_size)

    # 把page和page_size换算成offset和limit
    offset = (page - 1) * page_size
    # offset, limit将覆盖page及page_size的影响
    offset = str(request.args.get('offset', offset))
    limit = str(request.args.get('limit', page_size))

    order_by = request.args.get('order_by', 'id')
    order = request.args.get('order', 'asc')
    filter_str = request.args.get('filter', '')

    args_rules = [
        Rules.OFFSET.value,
        Rules.LIMIT.value,
        Rules.ORDER_BY.value,
        Rules.ORDER.value
    ]

    try:
        ji.Check.previewing(args_rules, {'offset': offset, 'limit': limit, 'order_by': order_by, 'order': order})
        offset = int(offset)
        limit = int(limit)
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()
        ret['paging'] = {'total': 0, 'offset': offset, 'limit': limit, 'page': page, 'page_size': page_size,
                         'next': '', 'prev': '', 'first': '', 'last': ''}

        ret['data'], ret['paging']['total'] = App.get_by_filter(offset=offset, limit=limit, order_by=order_by,
                                                                order=order, filter_str=filter_str)

        host_url = request.host_url.rstrip('/')
        other_str = '&filter=' + filter_str + '&order=' + order + '&order_by=' + order_by
        last_pagination = (ret['paging']['total'] + page_size - 1) / page_size

        if page <= 1:
            ret['paging']['prev'] = host_url + blueprint.url_prefix + '?page=1&page_size=' + page_size.__str__() + \
                                    other_str
        else:
            ret['paging']['prev'] = host_url + blueprint.url_prefix + '?page=' + str(page-1) + '&page_size=' + \
                                    page_size.__str__() + other_str

        if page >= last_pagination:
            ret['paging']['next'] = host_url + blueprint.url_prefix + '?page=' + last_pagination.__str__() + \
                                    '&page_size=' + page_size.__str__() + other_str
        else:
            ret['paging']['next'] = host_url + blueprint.url_prefix + '?page=' + str(page+1) + '&page_size=' + \
                                    page_size.__str__() + other_str

        ret['paging']['first'] = host_url + blueprint.url_prefix + '?page=1&page_size=' + \
            page_size.__str__() + other_str
        ret['paging']['last'] = \
            host_url + blueprint.url_prefix + '?page=' + last_pagination.__str__() + '&page_size=' + \
            page_size.__str__() + other_str

        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)


@Utils.dumps2response
@Utils.superuser
def r_content_search():
    page = str(request.args.get('page', 1))
    page_size = str(request.args.get('page_size', 50))

    args_rules = [
        Rules.PAGE.value,
        Rules.PAGE_SIZE.value
    ]

    try:
        ji.Check.previewing(args_rules, {'page': page, 'page_size': page_size})
    except ji.PreviewingError, e:
        return json.loads(e.message)

    page = int(page)
    page_size = int(page_size)

    # 把page和page_size换算成offset和limit
    offset = (page - 1) * page_size
    # offset, limit将覆盖page及page_size的影响
    offset = str(request.args.get('offset', offset))
    limit = str(request.args.get('limit', page_size))

    order_by = request.args.get('order_by', 'id')
    order = request.args.get('order', 'asc')
    keyword = request.args.get('keyword', '')

    args_rules = [
        Rules.OFFSET.value,
        Rules.LIMIT.value,
        Rules.ORDER_BY.value,
        Rules.ORDER.value,
        Rules.KEYWORD.value
    ]

    try:
        ji.Check.previewing(args_rules, {'offset': offset, 'limit': limit, 'order_by': order_by, 'order': order,
                                         'keyword': keyword})
        offset = int(offset)
        limit = int(limit)
        ret = dict()
        ret['state'] = ji.Common.exchange_state(20000)
        ret['data'] = list()
        ret['paging'] = {'total': 0, 'offset': offset, 'limit': limit, 'page': page, 'page_size': page_size}

        ret['data'], ret['paging']['total'] = App.content_search(offset=offset, limit=limit, order_by=order_by,
                                                                 order=order, keyword=keyword)

        host_url = request.host_url.rstrip('/')
        other_str = '&keyword=' + keyword + '&order=' + order + '&order_by=' + order_by
        last_pagination = (ret['paging']['total'] + page_size - 1) / page_size

        if page <= 1:
            ret['paging']['prev'] = host_url + blueprints.url_prefix + '/_search?page=1&page_size=' + \
                                    page_size.__str__() + other_str
        else:
            ret['paging']['prev'] = host_url + blueprints.url_prefix + '/_search?page=' + str(page-1) + \
                                    '&page_size=' + page_size.__str__() + other_str

        if page >= last_pagination:
            ret['paging']['next'] = host_url + blueprints.url_prefix + '/_search?page=' + last_pagination.__str__() + \
                                    '&page_size=' + page_size.__str__() + other_str
        else:
            ret['paging']['next'] = host_url + blueprints.url_prefix + '/_search?page=' + str(page+1) + \
                                    '&page_size=' + page_size.__str__() + other_str

        ret['paging']['first'] = host_url + blueprints.url_prefix + '/_search?page=1&page_size=' + \
            page_size.__str__() + other_str
        ret['paging']['last'] = \
            host_url + blueprints.url_prefix + '/_search?page=' + last_pagination.__str__() + '&page_size=' + \
            page_size.__str__() + other_str

        return ret
    except ji.PreviewingError, e:
        return json.loads(e.message)

