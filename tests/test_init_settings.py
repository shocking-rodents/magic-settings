# -*- coding: utf-8 -*-
import os
from json import loads

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


@pytest.mark.parametrize('modules, prefix, dotenv_path, override_env, yaml_settings_path, use_env', [
    ([base, local], 'ENV', DOTENV_PATH, True, YAML_SETTINGS_PATH, True),
    ([base, local], 'ENV', DOTENV_PATH, True, None, True),
    (None, 'ENV', DOTENV_PATH, True, None, True),
    ([base, local], None, None, False, None, True),
    ([base, None], None, None, False, None, True),
    ([base, local], 'ENV', DOTENV_PATH, True, None, False),
])
def test_settings_dict(modules, prefix, dotenv_path, override_env, yaml_settings_path, use_env):
    """ Тест функции получения словаря настроек """
    settings = TestSettings(
        modules=modules, prefix=prefix,
        dotenv_path=dotenv_path, override_env=override_env,
        yaml_settings_path=yaml_settings_path, use_env=use_env
    )
    settings.init()

    settings_dict = settings.to_dict()

    modules_names = [source['address']['name'] for source in settings_dict['sources']
                     if source['source_type'] == 'module']
    if modules is not None:
        for module_name in modules:
            if module_name is not None:
                assert module_name.__name__ in modules_names

    source_types = [source['source_type'] for source in settings_dict['sources']]

    if dotenv_path and use_env:
        assert 'dotenv' in source_types

    if yaml_settings_path:
        assert 'yaml' in source_types

    property_names = settings_dict['properties'].keys()
    for prop in property_names:
        assert getattr(settings, prop) == settings_dict['properties'][prop]


@pytest.mark.parametrize('modules, prefix, dotenv_path, override_env, yaml_settings_path, use_env', [
    ([base, local], 'ENV', DOTENV_PATH, True, YAML_SETTINGS_PATH, True),
    ([base, local], 'ENV', DOTENV_PATH, True, None, True),
    (None, 'ENV', DOTENV_PATH, True, None, True),
    ([base, local], None, None, False, None, True),
    ([base, None], None, None, False, None, True),
    ([base, local], 'ENV', DOTENV_PATH, True, None, False),
])
def test_settings_json(modules, prefix, dotenv_path, override_env, yaml_settings_path, use_env):
    """ Тест функции получения json настроек """
    settings = TestSettings(
        modules=modules, prefix=prefix,
        dotenv_path=dotenv_path, override_env=override_env,
        yaml_settings_path=yaml_settings_path, use_env=use_env
    )
    settings.init()

    json_dict = loads(settings.to_json())
    settings_dict = settings.to_dict()
    assert json_dict == settings_dict


def test_settings_dict_format():
    modules = [base, local]
    prefix = 'ENV'
    dotenv_path = DOTENV_PATH
    override_env = True
    yaml_settings_path = YAML_SETTINGS_PATH
    use_env = True
    settings = TestSettings(
        modules=modules, prefix=prefix,
        dotenv_path=dotenv_path, override_env=override_env,
        yaml_settings_path=yaml_settings_path, use_env=use_env
    )
    settings.init()
    settings_dict = settings.to_dict()
    assert settings_dict == {
        'properties': {
            'PREFIX': 'YAML_ENV',
            'TEST_PROP': 'YAML_PROPERTY',
            'USE_YAML': True,
        },
        'sources': [
            {
                'source_type': 'module',
                'address': {
                    'name': 'tests.files.base'
                }
            }, {
                'source_type': 'module',
                'address': {
                    'name': 'tests.files.local'
                }
            }, {
                'source_type': 'dotenv',
                'address': {
                    'dotenv_path': DOTENV_PATH,
                    'override': True
                }
            }, {
                'source_type': 'yaml',
                'address': {
                    'yaml_settings_path': YAML_SETTINGS_PATH
                }
            }
        ]
    }
