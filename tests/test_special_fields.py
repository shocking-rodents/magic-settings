# -*- coding: utf-8 -*-
import os

import pytest

from magic_settings.special_property import (BoolProperty, FloatProperty, HostListProperty, IntProperty,
                                             StringListProperty, StringProperty)
from magic_settings.utils import BaseSettings

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(TEST_DIR, 'files', 'special_properties.env')


class TestSettings(BaseSettings):
    DELIMITED_BY_COLON_LIST_PROPERTY = StringListProperty(delimiter=':')
    MISSING_INTEGER_PROPERTY = IntProperty(default=8)
    MISSING_STRING_PROPERTY = StringProperty(default='Test string')
    MISSING_BOOL_PROPERTY = BoolProperty(default=True)
    MISSING_STRING_LIST_PROPERTY = StringListProperty(default=['test', 'test'])
    MISSING_MULTI_HOST_PROPERTY = HostListProperty(default=[['localhost', 1234]])


def test_property_params():
    settings = TestSettings(dotenv_path=DOTENV_PATH)
    settings.init()

    assert settings.DELIMITED_BY_COLON_LIST_PROPERTY == ['four', 'five', 'six']
    assert settings.MISSING_INTEGER_PROPERTY == 8
    assert settings.MISSING_STRING_PROPERTY == 'Test string'
    assert settings.MISSING_BOOL_PROPERTY is True
    assert settings.MISSING_STRING_LIST_PROPERTY == ['test', 'test']
    assert settings.MISSING_MULTI_HOST_PROPERTY == [['localhost', 1234]]


@pytest.mark.parametrize('property_class, env_value, python_value', [
    (IntProperty, '1', 1),
    (IntProperty, '0', 0),
    (IntProperty, '-5', -5),
    (IntProperty, '1000000000000', 1000000000000),
    (FloatProperty, '5.0', 5.0),
    (FloatProperty, '5.', 5.0),
    (FloatProperty, '5', 5.0),
    (FloatProperty, '1e3', 1000.0),
    (FloatProperty, '-0.5', -0.5),
    (FloatProperty, '-.5', -0.5),
    (BoolProperty, 'true', True),
    (BoolProperty, 'false', False),
    (BoolProperty, 'True', True),
    (BoolProperty, 'fAlSe', False),
    (BoolProperty, '1', True),
    (BoolProperty, '0', False),
    (StringProperty, 'Test string + юникод', 'Test string + юникод'),
    (StringProperty, '', ''),
    (StringProperty, '1', '1'),
    (StringListProperty, '', []),
    (StringListProperty, ',', []),
    (StringListProperty, 'one,', ['one']),
    (StringListProperty, 'one,two,three', ['one', 'two', 'three']),
    (StringListProperty, 'test string ,more test', ['test string ', 'more test']),
    (StringListProperty, '1,2,', ['1', '2']),
    (HostListProperty, '', []),
    (HostListProperty, 'localhost:8080,', [['localhost', 8080]]),
    (HostListProperty, '192.168.20.1:80,www.yandex.ru:1234,localhost:8888',
     [['192.168.20.1', 80], ['www.yandex.ru', 1234], ['localhost', 8888]]),
])
def test_custom_property_values(property_class, env_value, python_value):
    os.environ['PROPERTY'] = env_value

    class TestSettings(BaseSettings):
        PROPERTY = property_class()

    settings = TestSettings()
    settings.init()

    assert settings.PROPERTY == python_value
