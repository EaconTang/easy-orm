class EasySQLError(Exception):
    """"""


class ConnectionFail(EasySQLError):
    """"""


class NetworkFail(EasySQLError):
    """"""


class DBError(EasySQLError):
    """"""


class MysqlPingFail(DBError):
    """"""


class ThreadUnregisterdError(DBError):
    """"""
