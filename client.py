import pymysql


def get_mysql_conn(host, user, password, db, charset):
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db,
            charset=charset,
            # cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        raise Exception('Fail on connecting to mysql! ' + e.message)
