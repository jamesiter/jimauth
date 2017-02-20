#!/usr/bin/env python
# -*- coding: utf-8 -*-


import mysql.connector
import mysql.connector.pooling
from mysql.connector import errorcode
import time

from initialize import app, logger


__author__ = 'James Iter'
__date__ = '16/6/8'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2016 by James Iter.'


class Database(object):

    cnxpool = None

    def __init__(self):
        pass

    @classmethod
    def init_conn(cls):
        try:
            cls.cnxpool = mysql.connector.pooling.MySQLConnectionPool(
                host=app.config["db_host"],
                user=app.config["db_user"],
                password=app.config["db_password"],
                port=app.config["db_port"],
                database=app.config["db_name"],
                raise_on_warnings=app.config["debug"],
                pool_size=app.config["db_pool_size"],
                charset=app.config["db_charset"]
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                e_msg = u'用户名或密码错误'
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                e_msg = u'数据库不存在'
            else:
                e_msg = err.msg

            print(e_msg)
            exit(err.errno)

    @classmethod
    def keepalived(cls):
        def ping(label='', _cnxpool=None):
            if _cnxpool is None:
                logger.critical(''.join(['cnxpool must not None by ', label]))
                return

            try:
                _cnx = _cnxpool.get_connection()
                _cnx.ping(attempts=1, delay=0)
            except mysql.connector.errors.InterfaceError as err:
                logger.critical(err.msg)
            except mysql.connector.Error as err:
                logger.error(err)
            else:
                _cnx.close()

        while True:
            time.sleep(5)
            ping(label='', _cnxpool=cls.cnxpool)
