## ORM简易实现

一个简易可用的Mysql表的增删改查执行器，屏蔽SQL语法复杂度
  
    基本用法:
    
        >>> conn = get_mysql_conn(host, port, user, password, db, charset, timeout, auto_commit，**kwargs)
        >>> t1 = TableExecutor(conn, 'table_1')

        # 查询, result属性返回结果集，statement属性查看SQL语句
        >>> t1.query('id', 'name').where(role='admin').result
        [{"id": 1, "name": "eacon"}, {"id": 2, "name": "tyk"}]

        >>> t1.query('id', 'name').where(role='admin').statement
        SELECT id, name FROM table_1 WHERE role="admin"

        # 插入、更新、删除，commit()方法返回执行结果，statement属性查看SQL语句
        >>> t1.insert(name='eacon', id=3).commit()
        True

        >>> t1.update(role='user').where(name='eacon).statement
        UPDATE table_1 SET role="user" WHERE name="eacon"

        >>> t1.delete().where(id=4).commit()
        False

        # 修改数据表名或连接对象
        >>> te.table = 'table-name'
        >>> te.conn = MysqlConnection
        
    
   自带实现线程安全的连接池：
   
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