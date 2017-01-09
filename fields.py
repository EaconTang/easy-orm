# coding=utf8
"""
自定义的数据类型，对应Myslq字段类型
"""


class Timestamp(object):
    """
    时间戳数据类型
    更新数据时，Mysql的TIMESTAMP字段，可以通过这个对象来赋予时间戳
    Usage:
        TableExecutor().insert(id=2, current_time=Timestamp(1489239340))
    """

    def __init__(self, _timestamp):
        self._timestamp = _timestamp

    @property
    def value(self):
        return str(self._timestamp)

    @value.setter
    def value(self, _new_value):
        self._timestamp = _new_value

    @property
    def datetime_str(self):
        time_struct = time.localtime(int(self._timestamp))
        return '{0:0>2d}-{1:0>2d}-{2:0>2d} {3:0>2d}:{4:0>2d}:{5:0>2d}'.format(
            time_struct.tm_year, time_struct.tm_mon, time_struct.tm_mday,
            time_struct.tm_hour, time_struct.tm_min, time_struct.tm_sec
        )

    def __str__(self):
        return '<Timestamp: {0}|{1}>'.format(self._timestamp, self.datetime_str)
