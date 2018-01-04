# coding=utf-8
import time

from easysql.fields import *


class TableExecutor(object):
    """
    一个简易可用的Mysql表的增删改查执行器，屏蔽SQL语法复杂度
    Usage:
        >>> conn = get_mysql_conn()
        >>> t1 = TableExecutor(conn, 'table_1')

        # 查询, result属性返回结果集，statement属性查看SQL语句
        >>> t1.query('id', 'name').where(role='admin').result
        [{"id": 1, "name": "eacon"}, {"id": 2, "name": "tyk"}]

        >>> t1.query('id', 'name').where(role='admin').statement
        SELECT id, name FROM table_1 WHERE role="admin"

        # 插入、更新、删除，commit()方法返回执行结果，statement属性查看SQL语句
        >>> t1.insert(name='eacon', id=3).commit()
        True

        >>> t1.update(role='user').where(name='eacon').statement
        UPDATE table_1 SET role="user" WHERE name="eacon"

        >>> t1.delete().where(id=4).commit()
        False

        # 修改数据表名或连接对象
        >>> te.table = 'table-name'
        >>> te.conn = MysqlConnection
    """

    def __init__(self, conn=None, table=None):
        self._conn = conn
        self._table = table
        self._sql = ''

    def check(self):
        if self._table is None or self._conn is None or self._sql == '':
            raise Exception('Invalid!')

    @property
    def table(self):
        return self._table

    @table.setter
    def table(self, _table):
        self._table = _table

    @property
    def conn(self):
        return self._conn

    @conn.setter
    def conn(self, _conn):
        self._conn = _conn

    @property
    def statement(self):
        """仅返回SQL语句"""
        return self._sql

    def _execute_one(self):
        # ToDo
        self.check()
        with self._conn.cursor() as _cursor:
            _cursor.execute(self._sql)

    def _execute_many(self, *values):
        # ToDo
        self.check()
        with self._conn.cursor() as _cursor:
            _cursor.executemany()

    @property
    def result(self):
        """SELECT的查询结果集"""
        self.check()
        try:
            with self._conn.cursor() as _cursor:
                _cursor.execute(self._sql)
                res = _cursor.fetchall()
        except:
            res = []
        return res

    def result_next(self):
        # ToDo
        raise NotImplementedError

    def result_many(self, size):
        # ToDo
        raise NotImplementedError

    def commit(self):
        """提交UPDATE/INSERT的操作"""
        self.check()
        try:
            with self._conn.cursor() as _cursor:
                _cursor.execute(self._sql)
            self._conn.commit()
            SUCCESS = True
        except Exception as e:
            SUCCESS = False
        return SUCCESS

    def query(self, *args):
        """TableExecutor.query(col1, col2).where(cond1='...', cond2=...)"""
        self.clear()
        if args:
            self._sql += """SELECT {0} FROM {1}""".format(', '.join(args), self._table)
        else:
            self._sql += """SELECT * FROM {0}""".format(self._table)
        return self

    def insert(self, **kwargs):
        """TableExecutor.insert(col1='..', col2='..').where(cond1='...', cond2=...)"""
        self.clear()
        if kwargs:
            keys = kwargs.keys()
            values = [self.value_str(kwargs.get(key)) for key in keys]
            self._sql += """INSERT INTO {0} ({1}) VALUES ({2})""".format(
                self._table,
                ', '.join(keys),
                ', '.join(values)
            )
        else:
            raise Exception('Kwargs should not be bull!')
        return self

    def insert_many(self, **kwargs):
        """
        TableExecutor.insert_many(col1=(*list), col2=(*list))
        :param kwargs:
        :return:
        """

    def update(self, **kwargs):
        """TableExecutor.update(col1='..', col2='..').where(cond1='...', cond2=...)"""
        self.clear()
        if kwargs:
            kv_list = ['{0}={1}'.format(k, self.value_str(v)) for k, v in kwargs.iteritems()]
            self._sql += """UPDATE {0} SET {1}""".format(
                self._table,
                ', '.join(kv_list)
            )
        else:
            raise Exception('Kwargs should not be null!')
        return self

    def delete(self):
        """TableExecutor.delete().where(cond1=, cond2=...)"""
        self.clear()
        self._sql = """DELETE FROM {0}""".format(self._table)
        return self

    def _where(self, and_or, **kwargs):
        # ToDo:需要支持like子句
        """
        :param and_or:
        :param kwargs:
        :return:
        """
        if kwargs:
            self._sql += """ WHERE {0}""".format(
                ' {} '.format(and_or).join(
                    ['{0}{1}{2}'.format(k, self.cmp_str(v), self.value_str(v)) for k, v in kwargs.iteritems()])
            )
        return self

    def where_and(self, **kwargs):
        """条件查询，AND查询"""
        return self._where('AND', **kwargs)

    def where_or(self, **kwargs):
        """条件查询，OR查询"""
        return self._where('OR', **kwargs)

    def where(self, **kwargs):
        """条件查询，默认AND查询"""
        return self.where_and(**kwargs)

    def sortby(self, *args, **kwargs):
        """排序字段"""
        if args:
            self._sql += """ ORDER BY {}""".format(
                ', '.join(args)
            )
            if kwargs:
                desc = kwargs.get('desc', False)
                if desc:
                    self._sql += ' DESC'
        return self

    def groupby(self, *args):
        """分组字段"""
        if args:
            self._sql += """ GROUP BY {}""".format(
                ', '.join(args)
            )
        return self

    def cmp_str(self, v):
        """
        WHERE子句中的字段kv比较符，=, <, >, IS, REGEXP...
        :param self:
        :return:
        """
        if isinstance(v, (IsNull, NotNUll)):
            return " IS "
        elif isinstance(v, Regexp):
            return " REGEXP "
        else:
            return "="

    def value_str(self, _val):
        """
        在INSERT、UPDATE语句中：
            如果值是整形，只需转换为字符串返回；
            如果值是字符串，需要加单/双引号；
            如果值是自定义的Timestamp类型，需要转换为时间格式并且加引号
        :param _val:
        :return:
        """
        if isinstance(_val, (int, float, long)):
            return str(_val)
        if isinstance(_val, basestring):
            return '"{0}"'.format(self.escape_sql(_val))
        if isinstance(_val, Timestamp):
            return '"{0}"'.format(_val.datetime_str)
        if isinstance(_val, Regexp):
            return '"{0}"'.format(_val.expression)
        if isinstance(_val, IsNull):
            return 'NULL'
        if isinstance(_val, NotNUll):
            return 'NOT NULL'
        else:
            return str(_val)

    def escape_sql(self, text):
        """对于字符串的值，如果里面有单/双引号，需要转义"""
        return str(text).replace('"', '\\"').replace("'", "\\'")

    def clear(self):
        """clear sql statement"""
        self._sql = ''


class MultiTableExecutor(object):
    """
    多表查询
    构造每个表的sql语句字典，进行组合？
    """

    # ToDo

    def __init__(self, conn=None, tables=None):
        self._conn = conn
        self._tables = tables
        self._sql = ''


if __name__ == '__main__':
    from easysql.client import get_mysql_conn

    conn = get_mysql_conn('10.17.35.80', 'root', 'horuseye', 'horuseye8888')
    te = TableExecutor(conn, 'tsd_alert')

    print te.query('alert_id', 'alert_metric').sortby('id', 'name', desc=True).groupby('name').statement

    print te.insert(alert_metric='eacon', alert_id=604, alert_info='!!!').statement

    print te.update(alert_metric='tyk').where(alert_id='604', alert_name=NotNUll(), alertInfo=IsNull()).statement

    print te.delete().where(alert_id=Regexp('^a\d{2}')).statement
