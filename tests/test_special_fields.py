# -*- coding: utf-8 -*-
import os

from magic_settings.special_property import BoolProperty, FloatProperty, IntProperty, StringListProperty, StringProperty
from magic_settings.utils import BaseSettings

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(TEST_DIR, 'files', 'special_properties.env')


class TestSettings(BaseSettings):
    INTEGER_PROPERTY = IntProperty()
    FIRST_STRING_PROPERTY = StringProperty()
    SECOND_STRING_PROPERTY = StringProperty()
    BOOL_TRUE_PROPERTY = BoolProperty()
    BOOL_FALSE_PROPERTY = BoolProperty()
    FIRST_FLOAT_PROPERTY = FloatProperty()
    SECOND_FLOAT_PROPERTY = FloatProperty()
    DELIMETED_BY_COMMA_LIST_PROPERTY = StringListProperty()
    DELIMITED_BY_COLON_LIST_PROPERTY = StringListProperty(delimiter=':')
    MISSING_INTEGER_PROPERTY = IntProperty(default=8)
    MISSING_STRING_PROPERTY = StringProperty(default='Test string')
    MISSING_BOOL_PROPERTY = BoolProperty(default=True)
    MISSING_STRING_LIST_PROPERTY = StringListProperty(default=['test', 'test'])


def test_init_settings():
    settings = TestSettings(dotenv_path=DOTENV_PATH)
    settings.init()

    assert settings.INTEGER_PROPERTY == 5
    assert settings.FIRST_STRING_PROPERTY == '1'
    assert settings.SECOND_STRING_PROPERTY == 'value'
    assert settings.BOOL_TRUE_PROPERTY is True
    assert settings.BOOL_FALSE_PROPERTY is False
    assert settings.FIRST_FLOAT_PROPERTY == 5.0
    assert settings.SECOND_FLOAT_PROPERTY == 5.5
    assert settings.DELIMETED_BY_COMMA_LIST_PROPERTY == ['one', 'two', 'three']
    assert settings.DELIMITED_BY_COLON_LIST_PROPERTY == ['four', 'five', 'six']
    assert settings.MISSING_INTEGER_PROPERTY == 8
    assert settings.MISSING_STRING_PROPERTY == 'Test string'
    assert settings.MISSING_BOOL_PROPERTY is True
    assert settings.MISSING_STRING_LIST_PROPERTY == ['test', 'test']
