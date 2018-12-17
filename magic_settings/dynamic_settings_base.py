# -*- coding: utf-8 -*-
import asyncio
import logging
from abc import ABC, abstractmethod

from magic_settings import BaseSettings

logger = logging.getLogger(__name__)


class DynamicSettingsSourceError(Exception):
    """ Source for dynamic settings is unavailable """
    pass


class BaseDynamicSettings(BaseSettings, ABC):
    def __init__(self, loop, update_period, task_retries_number=3):
        self.loop = loop
        self.update_period = update_period
        self.task = None

        self.task_retries_number = task_retries_number

    @abstractmethod
    async def update_settings_from_source(self):
        """Updating active settings from source"""
        pass

    async def _periodic(self):
        """Updating settings task"""
        retries_left = self.task_retries_number
        while retries_left >= 0:
            try:
                await self.update_settings_from_source()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception(
                    f'An error have occured while updating settings from source. Retries left: {retries_left}')
                retries_left -= 1
            else:
                retries_left = self.task_retries_number
            await asyncio.sleep(self.update_period)

    async def start_update(self):
        """Start updating task"""
        self.task = self.loop.create_task(self._periodic())

    async def stop_update(self):
        """Stop updating task"""
        self.task.cancel()
        try:
            await self.task
        except asyncio.CancelledError:
            pass
