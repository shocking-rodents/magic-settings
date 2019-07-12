# -*- coding: utf-8 -*-
from functools import partial

from .utils import Property


class StringProperty(Property):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, types=str)


class IntProperty(Property):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, types=int, converts=[int])


class FloatProperty(Property):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, types=float, converts=[float])


class BoolProperty(Property):
    @staticmethod
    def convert_bool_value_by_string(value: str):
        """
        Returns 0 if value equals 'false', returns 1 if value equals 'true' (case-insensitive).
        In other values, just returns init value
        """
        if value.lower() == 'false':
            return 0
        if value.lower() == 'true':
            return 1
        return value

    def __init__(self, **kwargs):
        super().__init__(**kwargs, types=bool, converts=[self.convert_bool_value_by_string, int, bool])


class StringListProperty(Property):
    @staticmethod
    def split_list(raw, delimiter):
        return list(filter(None, raw.split(sep=delimiter)))

    def __init__(self, delimiter=',', **kwargs):
        super().__init__(**kwargs, types=list, converts=[partial(self.split_list, delimiter=delimiter)])


class HostListProperty(Property):
    @staticmethod
    def split_hosts(hosts):
        """Parse comma-separated host-port pairs. """
        return [(host.split(':')[0], int(host.split(':')[1])) for host in hosts.split(',') if host != '']

    def __init__(self, **kwargs):
        super().__init__(**kwargs, types=list, converts=[self.split_hosts])
