# -*- coding: utf-8 -*-
import os

import pytest
from dotenv import load_dotenv

from magic_settings.utils import BaseSettings, Property
from tests.files import base, local


TEST_DIR = os.path.dirname(os.path.abspath(__file__))


class TestSettings(BaseSettings):
    USE_YAML = Property(types=bool, converts=[bool], default=False)
    TEST_PROP = Property(types=str)
    PREFIX = Property(types=str)


@pytest.fixture
def settings_with_yaml():
    """Fixture settings with yaml"""
    dotenv_path = os.path.join(TEST_DIR, 'files', '.env')
    yaml_settings_path = os.path.join(TEST_DIR, 'files', 'settings.yaml')
    settings = TestSettings(
        modules=[base, local],
        prefix='ENV',
        dotenv_path=dotenv_path,
        override_env=True,
        yaml_settings_path=yaml_settings_path,
    )

    return settings


@pytest.fixture
def settings_with_env():
    """Fixture settings with env"""
    dotenv_path = os.path.join(TEST_DIR, 'files', '.env')
    settings = TestSettings(modules=[base, local], prefix='ENV', dotenv_path=dotenv_path, override_env=True)
    return settings


@pytest.fixture
def settings_with_prefix():
    """Fixture settings with prefix"""
    dotenv_path = os.path.join(TEST_DIR, 'files', '.env')
    load_dotenv(dotenv_path=dotenv_path, override=True)
    settings = TestSettings(prefix='ENV')
    return settings


@pytest.fixture
def settings_with_modules():
    """Fixture settings with modules"""
    settings = TestSettings(modules=[base, local])
    return settings


def test_init(settings_with_yaml):
    """Test init with yaml"""
    settings_with_yaml.init()
    assert settings_with_yaml.USE_YAML
    assert settings_with_yaml.PREFIX == 'YAML_ENV'
    assert settings_with_yaml.TEST_PROP == 'YAML_PROPERTY'


def test_init_with_env(settings_with_env):
    """Test init with env"""
    settings_with_env.init()
    assert settings_with_env.USE_YAML
    assert settings_with_env.PREFIX == 'ENV_ENV'
    assert settings_with_env.TEST_PROP == 'ENV_PROPERTY'


def test_init_with_prefix(settings_with_prefix):
    """Test init with prefix"""
    settings_with_prefix.init()
    assert settings_with_prefix.USE_YAML
    assert settings_with_prefix.PREFIX == 'ENV_ENV'
    assert settings_with_prefix.TEST_PROP == 'ENV_PROPERTY'


def test_init_with_modules(settings_with_modules):
    """Test init with modules"""
    settings_with_modules.init()
    assert not settings_with_modules.USE_YAML
    assert settings_with_modules.PREFIX == 'BASE_ENV'
    assert settings_with_modules.TEST_PROP == 'BASE_PROPERTY'


def test_init_with_bad_module():
    """Test init with bad parameters"""
    with pytest.raises(ValueError, message='Expecting ValueError'):
        TestSettings(modules=[base, local, 'not_module'])
