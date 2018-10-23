# -*- coding: utf-8 -*-
import asyncio
import logging
from abc import ABC, abstractmethod

from magic_settings import BaseSettings

logger = logging.getLogger(__name__)


class BaseDynamicSettings(BaseSettings, ABC):
    def __init__(self, loop, update_period, task_retries_number=3, task_retry_delay=1):
        self.loop = loop
        self.update_period = update_period
        self.task = None

        self.task_retries_number = task_retries_number
        self.task_retry_delay = task_retry_delay

    @abstractmethod
    async def update_settings_from_source(self):
        """Updating active settings from source"""
        pass

    async def periodic(self):
        """Updating settings task"""
        for _ in range(self.task_retries_number):
            try:
                while True:
                    await self.update_settings_from_source()
                    await asyncio.sleep(self.update_period)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception('Updating settings task')
            await asyncio.sleep(self.task_retry_delay)

    async def start_update(self):
        """Start updating task"""
        self.task = self.loop.create_task(self.periodic())

    async def stop_update(self):
        """Stop updating task"""
        self.task.cancel()
        try:
            await self.task
        except asyncio.CancelledError:
            pass
