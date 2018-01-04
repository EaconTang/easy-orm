# coding=utf-8
from functools import wraps
import logging
import time


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


def retry_onFalse(times=-1, interval=10):
    """
    失败重试机制，作为装饰器使用
    默认重试次数是无限次，默认重试间隔为10秒
    重试的条件是方法返回值为False
    """
    return _retry_onFalse({'times': times, 'interval': interval})


def _retry_onFalse(params):
    def _retry(func):
        @wraps(func)
        def __retry(*args, **kwargs):
            time_count_start = params['times']
            while params['times'] != 0:
                res = func(*args, **kwargs)
                if not res:
                    params['times'] -= 1
                    time.sleep(params['interval'])
                    logging.debug('Retry(times: {0}) function: {1}, args: {2}, kwargs: {3}'.format(
                        time_count_start - params['times'], func.func_name, args, kwargs
                    ))
                else:
                    return True
            return False

        return __retry

    return _retry


def retry_onException(times, interval, exceptions=None):
    """
    重试的条件是发生异常
    """
    return _retry_onException({'times': times, 'interval': interval})


def _retry_onException(params):
    """"""
    raise NotImplementedError


def lock_with(_lock):
    """锁装饰器"""
    def _locked(func):
        @wraps(func)
        def __locked(*args, **kwargs):
            with _lock:
                return func(*args, **kwargs)

        return __locked

    return _locked