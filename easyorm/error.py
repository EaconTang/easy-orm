class EasyORMError(Exception):
    """"""


class ConnectionFail(EasyORMError):
    """"""


class NetworkFail(EasyORMError):
    """"""


class DBError(EasyORMError):
    """"""


class MysqlPingFail(DBError):
    """"""


class ThreadUnregisterdError(DBError):
    """"""
