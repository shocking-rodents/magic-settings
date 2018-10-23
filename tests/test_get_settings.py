# -*- coding: utf-8 -*-
import os

import pytest

from magic_settings.utils import BaseSettings, Property
from tests.files import base, local


TEST_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope='module')
def settings():
    """Fixture settings"""
    class TestSettings(BaseSettings):
        USE_YAML = Property(types=bool)
        TEST_PROP = Property(types=str)
        PREFIX = Property(types=str)

    settings = TestSettings()
    return settings


def test_get_settings_with_params(settings):
    """Test get_settings with all parameters"""
    dotenv_path = os.path.join(TEST_DIR, 'files', '.env')
    yaml_settings_path = os.path.join(TEST_DIR, 'files', 'settings.yaml')
    settings.get_settings(
        prefix='ENV',
        dotenv_path=dotenv_path,
        override_env=True,
        yaml_settings_path=yaml_settings_path,
        use_yaml_settings=True,
        base=base,
        local=local,
    )
    assert settings.USE_YAML is True
    assert settings.PREFIX == 'YAML_ENV'
    assert settings.TEST_PROP == 'YAML_PROPERTY'


def test_get_settings_without_params(settings):
    """Test get_settings without parameters"""
    settings.get_settings(base=base, local=local)
    assert settings.USE_YAML is True
    assert settings.PREFIX == 'BASE_ENV'
    assert settings.TEST_PROP == 'BASE_PROPERTY'
