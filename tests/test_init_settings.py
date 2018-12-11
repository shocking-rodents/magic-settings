# -*- coding: utf-8 -*-
import os

import pytest
from magic_settings.utils import BaseSettings, Property

from tests.files import base, local

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(TEST_DIR, 'files', '.env')
YAML_SETTINGS_PATH = os.path.join(TEST_DIR, 'files', 'settings.yaml')


class TestSettings(BaseSettings):
    USE_YAML = Property(types=bool, converts=[bool], default=False)
    TEST_PROP = Property(types=str)
    PREFIX = Property(types=str)


@pytest.mark.parametrize('modules, prefix, dotenv_path, override_env, yaml_settings_path, use_env, expected', [
    ([base, local], 'ENV', DOTENV_PATH, True, YAML_SETTINGS_PATH, True, [True, 'YAML_ENV', 'YAML_PROPERTY']),
    ([base, local], 'ENV', DOTENV_PATH, True, None, True, [True, 'ENV_ENV', 'ENV_PROPERTY']),
    (None, 'ENV', DOTENV_PATH, True, None, True, [True, 'ENV_ENV', 'ENV_PROPERTY']),
    ([base, local], None, None, False, None, True, [False, 'BASE_ENV', 'BASE_PROPERTY']),
    ([base, None], None, None, False, None, True, [False, 'BASE_ENV', 'BASE_PROPERTY']),
    ([base, local], 'ENV', DOTENV_PATH, True, None, False, [False, 'BASE_ENV', 'BASE_PROPERTY']),
])
def test_init_settings(modules, prefix, dotenv_path, override_env, yaml_settings_path, use_env, expected):
    settings = TestSettings(
        modules=modules, prefix=prefix,
        dotenv_path=dotenv_path, override_env=override_env,
        yaml_settings_path=yaml_settings_path, use_env=use_env
    )
    settings.init()

    assert [settings.USE_YAML, settings.PREFIX, settings.TEST_PROP] == expected


def test_init_with_bad_module():
    """Test init with bad parameters"""
    with pytest.raises(ValueError, message='Expecting ValueError'):
        TestSettings(modules=[base, local, 'not_module'])


def test_undefined_property():
    settings_path = os.path.join(TEST_DIR, 'files', 'incomplete_settings.yaml')
    settings = TestSettings(yaml_settings_path=settings_path)
    with pytest.raises(ValueError) as error:
        settings.post_validate()
    expected = 'Undefined value of required PREFIX property, you must specify it in your config source.'
    assert str(error.value) == expected
