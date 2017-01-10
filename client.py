# coding=utf8
from functools import wraps
import pymysql


def get_mysql_conn(host, user, password, db, charset='utf8', timeout=5):
    try:
        return MysqlConnection(host, user, password, db, charset, timeout).conn
        # conn = pymysql.connect(
        #     host=host,
        #     user=user,
        #     password=password,
        #     db=db,
        #     charset=charset,
        #     connect_timeout=timeout,
        #     cursorclass=pymysql.cursors.DictCursor
        # )
        # return conn
    except Exception as e:
        print e
        raise Exception('Fail on connecting to mysql! ' + e.message)


def singleton(cls):
    """单例模式装饰器"""
    _instances = {}

    @wraps(cls)
    def _wrapper(*args, **kwargs):
        """"""
        key = '<{}_{}_{}>'.format(cls.__name__, args, kwargs)
        if key not in _instances:
            _instances[key] = cls(*args, **kwargs)
        return _instances[key]
    return _wrapper
    # instance = cls(*args, **kwargs)
    # instance.__call__ = lambda: instance
    # return instance


@singleton
class MysqlConnection(object):
    """Mysql连接对象"""

    def __init__(self, host, user, password, db, charset='utf8', timeout=5):
        self._conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db,
            charset=charset,
            connect_timeout=timeout,
            cursorclass=pymysql.cursors.DictCursor
        )

    @property
    def conn(self):
        return self._conn


class ConnectionPool(object):
    """"""


if __name__ == '__main__':
    # print get_mysql_conn('10.17.35.80', 'root', 'horuseye', 'horuseye8888')
    # print MysqlConnection('10.17.35.80', 'root', 'horuseye', 'horuseye8888').conn

    mc1 = MysqlConnection('10.17.35.80', 'root', 'horuseye', 'horuseye8888')
    mc2 = MysqlConnection('10.17.35.80', 'root', 'horuseye', 'horuseye')
    mc3 = MysqlConnection('10.17.35.80', 'root', 'horuseye', 'horuseye')
    print id(mc1), id(mc2), id(mc3)
    print id(mc1.conn), id(mc2.conn), id(mc3.conn)

    print id(get_mysql_conn('10.17.35.80', 'root', 'horuseye', 'horuseye8888'))
    print id(get_mysql_conn('10.17.35.80', 'root', 'horuseye', 'horuseye'))
    print id(get_mysql_conn('10.17.35.80', 'root', 'horuseye', 'horuseye'))