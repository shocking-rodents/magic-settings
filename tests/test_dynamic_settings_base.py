# -*- coding: utf-8 -*-
import asyncio
from functools import partial

import pytest

from magic_settings import BaseDynamicSettings, Property, Undefined

# use a dict as a source for derived class

source = {
    'PARAM_LIST': ['a', 'bb', 'ccc'],
    'PARAM_INT': 42
}


class BaseDynamicSettingsDict(BaseDynamicSettings):
    async def update_settings_from_source(self):
        super().update_config(**source)

    async def update_config(self, **kwargs):
        source.update(kwargs)
        return super().update_config(**kwargs)


class DynSettings(BaseDynamicSettingsDict):
    PARAM_LIST = Property(types=list, converts=[partial(str.split, sep=',')])
    PARAM_INT = Property(types=int, converts=[int])


@pytest.fixture
async def dyn_settings(event_loop):
    yield DynSettings(event_loop, 1)


# tests

@pytest.mark.asyncio
async def test_update_from_source(dyn_settings):
    await dyn_settings.update_settings_from_source()
    assert dyn_settings.PARAM_LIST == ['a', 'bb', 'ccc']
    assert dyn_settings.PARAM_INT == 42


@pytest.mark.asyncio
async def test_loop(dyn_settings):
    assert isinstance(dyn_settings.PARAM_LIST, Undefined)
    with pytest.raises(ValueError):
        dyn_settings.post_validate()

    await dyn_settings.start_update()
    await asyncio.sleep(1)

    assert dyn_settings.PARAM_LIST == ['a', 'bb', 'ccc']
    assert dyn_settings.PARAM_INT == 42

    await dyn_settings.stop_update()


@pytest.mark.asyncio
async def test_update_source(dyn_settings):
    await dyn_settings.update_settings_from_source()
    assert dyn_settings.PARAM_LIST == ['a', 'bb', 'ccc']
    assert dyn_settings.PARAM_INT == 42

    d = await dyn_settings.update_config(**{'PARAM_LIST': '1,2,3'})

    assert source['PARAM_LIST'] == '1,2,3'

    await dyn_settings.update_settings_from_source()
    assert dyn_settings.PARAM_LIST == ['1', '2', '3']
    assert d.PARAM_LIST == dyn_settings.PARAM_LIST

    source['PARAM_LIST'] = ['a', 'bb', 'ccc']


@pytest.mark.asyncio
async def test_cancelled_from_task(dyn_settings, event_loop):
    async def outer_task():
        await dyn_settings.start_update()
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await dyn_settings.stop_update()
            raise

    task = event_loop.create_task(outer_task())
    await asyncio.sleep(1)
    assert not dyn_settings.task.cancelled()
    assert not task.cancelled()

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert dyn_settings.task.cancelled()
    assert task.cancelled()


@pytest.mark.asyncio
async def test_loop_exception(dyn_settings):
    source_backup = dict(source)
    source['PARAM_LIST'] = 42
    with pytest.raises(ValueError):
        await dyn_settings.update_settings_from_source()
    await dyn_settings.start_update()
    await asyncio.sleep(1)

    source.update(source_backup)
    assert not dyn_settings.task.done()

    await asyncio.sleep(1)
    assert dyn_settings.PARAM_LIST == ['a', 'bb', 'ccc']
    await dyn_settings.stop_update()


@pytest.mark.asyncio
async def test_loop_exception_fail(dyn_settings):
    source_backup = dict(source)
    source['PARAM_LIST'] = 42
    dyn_settings.task_retries_number = 2
    dyn_settings.task_retry_delay = 0.2
    await dyn_settings.start_update()
    await asyncio.sleep(1)

    assert dyn_settings.task.done()
    source.update(source_backup)
