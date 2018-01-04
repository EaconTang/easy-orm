# coding=utf8
import logging
import threading
from queue import Queue

import pymysql

from easyorm.utils import *


@singleton
class MysqlConnection(object):
    """创建一个Mysql连接对象，基于PyMysql封装"""

    def __init__(self, host, port, user, password, db, charset='utf8', timeout=5, auto_commit=False):
        self._host = host
        self._port = port
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
            port=self._port,
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


def get_mysql_conn(host, port, user, password, db, charset='utf8', timeout=5, auto_commit=False):
    try:
        return MysqlConnection(host, port, user, password, db, charset, timeout, auto_commit).conn
    except Exception as e:
        raise Exception('Fail on connecting to mysql! ' + e.message)


MYSQL_CONNECTION_POOL = 10
MYSQL_POOL_NAME = 'mysql-pool'


@singleton
def connection_pool(host, port, user, password, db, charset='utf8', timeout=5, auto_commit=False,
                    pool_size=MYSQL_CONNECTION_POOL, pool_name=MYSQL_POOL_NAME):
    """创建连接池，多线程公用
    """
    pool = Queue(maxsize=pool_size)
    for _ in range(pool_size):
        try:
            _conn = get_mysql_conn(host, port, user, password, db, charset, timeout, auto_commit)
        except Exception as e:
            logging.error('Fail on create mysql connection! ' + e.message)
        else:
            pool.put(_conn)
    if pool.qsize() > 0:
        logging.debug('Connected to mysql: {0}:{1}, use database: {2}'.format(host, port, db))
        logging.debug('Mysql connection pool started! Size: {0}, name: {1}'.format(pool.qsize(), pool_name))
        return True, pool
    else:
        logging.error('Fail to build connection pool!')
        return False, pool


class ConnectionPool(object):
    """
    包含上下文的使用方式，自动从池中取出和放回，并检测连接有效性（失效则自动恢复）
    """
    def __init__(self, pool):
        self.pool = pool

    def reconnect(self):
        """重建mysql连接"""
        return new_connection()

    def check_conn(self, conn):
        """检查连接是否有效"""
        try:
            ping_result = conn.ping()
            if isinstance(ping_result, pymysql.connections.OKPacketWrapper):
                return True
            else:
                raise Exception("Fail to ping mysql server...")
        except Exception as e:
            logging.error('Mysql connection(id: {0}) is not OK, will reconnect... {1}'.format(id(self.conn), e))
            return False

    def __enter__(self):
        """取出之前确保连接有效性"""
        self.conn = self.pool.get()
        if not self.check_conn(self.conn):
            try:
                self.conn.close()
            except:
                pass
            self.conn = self.reconnect()
        logging.debug('Got mysql connection, pool size now: {0}'.format(self.pool.qsize()))
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.put(self.conn)
        logging.debug('Putback mysql connection, pool size now: {0}'.format(self.pool.qsize()))


class ThreadSafeConnectionPool(ConnectionPool):
    """线程安全的连接池，每个线程使用同一个连接
    >>> flag_success, origin_pool = connection_pool(**kwargs)
    >>> if flag_success:
    >>>     pool = ThreadSafeConnectionPool(origin_pool)
    >>> pool.register_me()      # 线程注册(可选，通过上下文进入时会自动注册）
    >>> with pool as conn:
    >>>     conn.cursor()       # 返回当前线程专属的连接
    >>>
    """
    def __init__(self, *args, **kwargs):
        super(ThreadSafeConnectionPool, self).__init__(*args, **kwargs)
        self._registerd = {}

    def register_me(self):
        """注册一个连接拥有者，默认是当前线程id"""
        _id = threading.current_thread().ident
        if _id in self._registerd:
            logging.warning('Thread({0}) is already registerd!'.format(_id))
            return
        if self.pool.empty():
            raise Exception('Not enough connections for register {0}'.format(_id))
        else:
            self._registerd[_id] = self.pool.get()
            logging.debug('OK! Thread({0}) is registerd in mysql connection pool!'.format(_id))

    def __enter__(self):
        _id = threading.current_thread().ident
        if _id not in self._registerd:
            self.register_me()
        _conn = self._registerd[_id]
        if self.check_conn(_conn):
            return _conn
        else:
            try:
                _conn.close()
            except:
                pass
            new_conn = self.reconnect()
            self._registerd[_id] = new_conn
            logging.debug('Thread({0}) reconnect mysql ok! New connection(id: {1}).'.format(_id, id(new_conn)))
            return new_conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


if __name__ == '__main__':
    pass

