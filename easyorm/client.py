# coding=utf8
from functools import wraps
import pymysql


def get_mysql_conn(host, user, password, db, charset='utf8', timeout=5):
    try:
        return MysqlConnection(host, user, password, db, charset, timeout).conn
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


@singleton
class MysqlConnection(object):
    """Mysql连接对象"""

    def __init__(self, host, user, password, db, charset='utf8', timeout=5, auto_commit=False):
        self._host = host
        self._user = user
        self._password = password
        self._db = db
        self._charset = charset
        self._connect_timeout = timeout
        self._auto_commit = auto_commit
        self._conn = None

    @property
    def conn(self):
        self._conn = pymysql.connect(
            host=self._host,
            user=self._user,
            password=self._password,
            db=self._db,
            charset=self._charset,
            connect_timeout=self._connect_timeout,
            cursorclass=pymysql.cursors.DictCursor
        )
        if self._auto_commit:
            self._conn.autocommit(True)
        return self._conn

    def set_auto_commit(self, flag=True):
        self._auto_commit = flag


class ConnectionPool(object):
    """"""


if __name__ == '__main__':
    # print get_mysql_conn('10.17.35.80', 'root', 'horuseye', 'horuseye8888')
    # print MysqlConnection('10.17.35.80', 'root', 'horuseye', 'horuseye8888').conn

    # mc1 = MysqlConnection('10.17.35.80', 'root', 'horuseye', 'horuseye8888')
    # mc2 = MysqlConnection('10.17.35.80', 'root', 'horuseye', 'horuseye')
    # mc3 = MysqlConnection('10.17.35.80', 'root', 'horuseye', 'horuseye')
    # print id(mc1), id(mc2), id(mc3)
    # print id(mc1.conn), id(mc2.conn), id(mc3.conn)
    #
    # print id(get_mysql_conn('10.17.35.80', 'root', 'horuseye', 'horuseye8888'))
    # print id(get_mysql_conn('10.17.35.80', 'root', 'horuseye', 'horuseye'))
    # print id(get_mysql_conn('10.17.35.80', 'root', 'horuseye', 'horuseye'))

    import time
    from easyorm.executor import TableExecutor

    rows = ((str(i), i) for i in xrange(1000))
    conn = get_mysql_conn('10.17.35.80', 'root', 'horuseye', 'horuseye_tangyk')

    t1 = time.time()

    # tsd_test = TableExecutor(conn, 'tsd_test')
    # for name, age in rows:
    #     tsd_test.insert(name=name, age=age).commit()

    with conn.cursor() as c:
        c.executemany('Insert Into tsd_test VALUES (%s, %s)', rows)
    conn.commit()
    print time.time() - t1