# -*- coding: utf-8 -*-
import asyncio
import time

import pytest
from magic_settings.utils import BaseSettings, Property


@pytest.fixture
def settings():
    class Settings(BaseSettings):
        FOO = Property(types=str, default='BAR')
        BAR = Property(types=str, default='FOO')
    settings = Settings()
    return settings


def test_temp_property(settings):
    """Test attributes are setted out on settings for the duration of the context manager"""
    with settings.temp_set_attributes(FOO='TEMP_FOO', BAR='TEMP_BAR'):
        assert settings.FOO == 'TEMP_FOO'
        assert settings.BAR == 'TEMP_BAR'
    assert settings.FOO == 'BAR'
    assert settings.BAR == 'FOO'


def test_temp_bad_property(settings):
    """Test context manager raises AttributeError if kwargs have nonexistent attribute name"""
    with pytest.raises(AttributeError, match=r'does`t have such attribute'):
        with settings.temp_set_attributes(FOO='TEMP_FOO', BAR='TEMP_BAR', BAD_ATTR='BAD_ATTR'):
            pass


@pytest.mark.asyncio
async def test_coro(event_loop, settings):
    """Test context manager can handle async code inside"""
    with settings.temp_set_attributes(FOO='TEMP_FOO', BAR='TEMP_BAR'):
        before = time.monotonic()
        # Do some async stuff
        await asyncio.sleep(0.1, loop=event_loop)
        after = time.monotonic()
        assert after - before >= 0.1

        assert settings.FOO == 'TEMP_FOO'
        assert settings.BAR == 'TEMP_BAR'

    assert settings.FOO == 'BAR'
    assert settings.BAR == 'FOO'
