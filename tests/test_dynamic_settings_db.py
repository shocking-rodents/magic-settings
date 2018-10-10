import asyncio
from functools import partial

import peewee
import peewee_async
import pytest

from magic_settings import BaseDynamicSettingsDB, Property, Undefined

db_settings = {
    "database": "xe",
    "host": "localhost",
    "port": 1521,
    "username": "system",
    "password": "oracle",
    "autocommit": True
}


class SettingsTest(peewee.Model):
    key = peewee.CharField(max_length=100, unique=True)
    value = peewee.TextField(null=True)
    active = peewee.BooleanField(default=True)


class SettingsTestDifferentFields(peewee.Model):
    key2 = peewee.CharField(max_length=100, unique=True)
    value2 = peewee.TextField(null=True)
    active2 = peewee.BooleanField(default=True)


class DynSettings(BaseDynamicSettingsDB):
    PARAM_LIST = Property(types=list, converts=[partial(str.split, sep=',')])
    PARAM_INT = Property(types=int, converts=[int])


@pytest.fixture
async def db(event_loop):
    database = peewee_async.PooledOracleDatabase(**db_settings)
    SettingsTest._meta.database = database
    SettingsTest.create_table(True)
    db = peewee_async.Manager(database, loop=event_loop)
    database.set_allow_sync(False)
    await db.create(SettingsTest, key='PARAM_LIST', value='a,bb,ccc')
    await db.create(SettingsTest, key='PARAM_INT', value=42)

    yield db

    await db.close()
    database.set_allow_sync(True)
    SettingsTest.drop_table(True)


@pytest.fixture
async def db2(event_loop):
    database = peewee_async.PooledOracleDatabase(**db_settings)
    SettingsTestDifferentFields._meta.database = database
    SettingsTestDifferentFields.create_table(True)
    db = peewee_async.Manager(database, loop=event_loop)
    database.set_allow_sync(False)
    await db.create(SettingsTestDifferentFields, key2='PARAM_LIST', value2='a,bb,ccc')
    await db.create(SettingsTestDifferentFields, key2='PARAM_INT', value2=42)

    yield db

    await db.close()
    database.set_allow_sync(True)
    SettingsTestDifferentFields.drop_table(True)


@pytest.fixture
async def dyn_settings(db, event_loop):
    dyn_settings = DynSettings(
        event_loop,
        5,
        db,
        SettingsTest,
    )
    yield dyn_settings


# tests

@pytest.mark.asyncio
async def test_update_loop(dyn_settings):
    assert isinstance(dyn_settings.PARAM_LIST, Undefined)
    with pytest.raises(ValueError):
        dyn_settings.post_validate()

    await dyn_settings.start_update()
    await asyncio.sleep(1)

    dyn_settings.post_validate()
    assert isinstance(dyn_settings.PARAM_LIST, list)
    assert dyn_settings.PARAM_LIST == ['a', 'bb', 'ccc']
    assert dyn_settings.PARAM_INT == 42

    await dyn_settings.stop_update()


@pytest.mark.asyncio
async def test_change_param(dyn_settings, db):
    await dyn_settings.update_settings_from_source()
    assert dyn_settings.PARAM_LIST == ['a', 'bb', 'ccc']
    assert dyn_settings.PARAM_INT == 42

    v1 = await db.get(SettingsTest, key='PARAM_LIST')
    v1.value = '1,2,3'
    await db.update(v1)
    v2 = await db.get(SettingsTest, key='PARAM_INT')
    v2.value = 999
    await db.update(v2)

    await dyn_settings.update_settings_from_source()

    assert dyn_settings.PARAM_LIST == ['1', '2', '3']
    assert dyn_settings.PARAM_INT == 999


@pytest.mark.asyncio
async def test_unusual_field_names(db2):
    dyn_settings = DynSettings(
        None,
        2,
        db2,
        SettingsTestDifferentFields,
        key_field='key2',
        value_field='value2',
        active_field='active2'
    )
    await dyn_settings.update_settings_from_source()
    assert dyn_settings.PARAM_LIST == ['a', 'bb', 'ccc']
    assert dyn_settings.PARAM_INT == 42


@pytest.mark.asyncio
async def test_active(dyn_settings, db):
    await dyn_settings.update_settings_from_source()
    assert dyn_settings.PARAM_LIST == ['a', 'bb', 'ccc']
    assert dyn_settings.PARAM_INT == 42

    p1 = await db.get(SettingsTest, key='PARAM_LIST')
    p1.value = '1,2,3'
    p1.active = False
    await db.update(p1)
    p2 = await db.get(SettingsTest, key='PARAM_INT')
    p2.value = 999
    await db.update(p2)

    await dyn_settings.update_settings_from_source()

    assert dyn_settings.PARAM_LIST == ['a', 'bb', 'ccc']
    assert dyn_settings.PARAM_INT == 999


@pytest.mark.asyncio
async def test_udpate_config(dyn_settings, db):
    await dyn_settings.update_settings_from_source()
    assert dyn_settings.PARAM_LIST == ['a', 'bb', 'ccc']
    assert dyn_settings.PARAM_INT == 42

    d = await dyn_settings.update_config(**{'PARAM_LIST': '1,2,3'})

    p = await db.get(SettingsTest, key='PARAM_LIST')
    assert p.value == '1,2,3'

    await dyn_settings.update_settings_from_source()
    assert dyn_settings.PARAM_LIST == ['1', '2', '3']
    assert d.PARAM_LIST == dyn_settings.PARAM_LIST


@pytest.mark.asyncio
async def test_udpate_config_invalid(dyn_settings, db):
    await dyn_settings.update_settings_from_source()
    with pytest.raises(ValueError):
        await dyn_settings.update_config(**{'PARAM_LIST': [1, 2, 3]})
