# -*- coding: utf-8 -*-
import os

import pytest

from magic_settings import BaseSettings, Property, NoneType
from magic_settings.utils import _get_config_dict_from_yaml, _get_config_dict_from_module
from tests.files import base, local, test_module


class TestSettings(BaseSettings):
    PROJECT_DIR = Property(types=str, default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    STR = Property(types=str)
    INT = Property(types=int)
    BOOL = Property(types=bool)
    LIST = Property(types=list)
    NONE = Property(types=(str, NoneType))
    HOST_LIST = Property(types=list)


def test_get_config_dict_from_yaml():
    """Test _get_config_dict_from_yaml method creates the dictionary correctly."""
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_path = os.path.join(project_dir, 'tests', 'files', 'yaml_config_test.yaml')
    config = _get_config_dict_from_yaml(test_path)
    assert config == {'STR': 'bar', 'INT': 123, 'BOOL': True, 'LIST': ['a', 'b', 'c'],
                      'NONE': None, 'HOST_LIST': ['localhost:5672', 'localhost:15672']}


def test_settings_from_yaml():
    """Test _get_config_dict_from_yaml method with update_config method update settings correctly."""
    settings = TestSettings()
    settings.pre_validate()
    settings.update_config(
        **_get_config_dict_from_yaml(os.path.join(settings.PROJECT_DIR, 'tests', 'files', 'yaml_config_test.yaml'))
    )
    settings.post_validate()
    assert settings.STR == 'bar'
    assert settings.INT == 123
    assert settings.BOOL is True
    assert settings.LIST == ['a', 'b', 'c']
    assert settings.NONE is None
    assert settings.HOST_LIST == ['localhost:5672', 'localhost:15672']


@pytest.mark.parametrize('module, expected', (
    (base, {'USE_YAML': False, 'TEST_PROP': 'BASE_PROPERTY', 'PREFIX': 'BASE_ENV'}),
    (local, {}),
    (test_module, {'USE_YAML': False, 'TEST_PROP': 'BASE_PROPERTY', 'PREFIX': 'BASE_ENV', 'PROPERTY': 'property'})
))
def test_get_config_dict_from_module(module, expected):
    """Test _get_config_dict_from_module method creates the dictionary correctly."""
    assert _get_config_dict_from_module(module) == expected
