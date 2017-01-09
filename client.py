import pymysql


def get_mysql_conn(host, user, password, db, charset='utf8', timeout=5):
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db,
            charset=charset,
            connect_timeout=timeout,
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print e
        raise Exception('Fail on connecting to mysql! ' + e.message)


if __name__ == '__main__':
    pass