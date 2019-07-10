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
    def __init__(self, **kwargs):
        super().__init__(**kwargs, types=bool, converts=[int, bool])


class StringListProperty(Property):
    def __init__(self, delimiter=',', **kwargs):
        super().__init__(**kwargs, types=list, converts=[partial(str.split, sep=delimiter)])
