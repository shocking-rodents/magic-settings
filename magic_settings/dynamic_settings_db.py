import logging

from peewee import DatabaseError

from magic_settings import BaseDynamicSettings

logger = logging.getLogger(__name__)


class BaseDynamicSettingsDB(BaseDynamicSettings):
    def __init__(self, loop, update_period, db, db_model,
                 task_retries_number=3, task_retry_delay=1,
                 key_field='key', value_field='value', active_field='active'):
        super().__init__(loop, update_period, task_retries_number, task_retry_delay)

        self.db = db
        self.db_model = db_model
        self.key_field = key_field
        self.value_field = value_field
        self.active_field = active_field

    async def update_config(self, **kwargs):
        """Update config in DB"""
        for k, v in kwargs.items():
            if not isinstance(v, str):
                raise ValueError(f'Value of {k} property should be str for dynamic properties')
            prop = next(p for p in self.properties if p.name == k)
            for method in prop.converts:
                try:
                    method(v)
                except Exception as e:
                    raise ValueError(f'Failed to convert property {k} with error: {e}')
            item = await self.db.get(self.db_model, **{self.key_field: k})
            setattr(item, self.value_field, v)
            await self.db.update(item)

        return super().update_config(**kwargs)

    async def update_settings_from_source(self):
        """Updating active settings from DB"""
        try:
            keys = [p.name for p in self.properties]
            items = await self.db.execute(
                self.db_model.select().where(
                    (getattr(self.db_model, self.key_field) << keys) &
                    (getattr(self.db_model, self.active_field) == True)
                ))
            self.pre_validate()
            super().update_config(**{getattr(item, self.key_field): getattr(item, self.value_field) for item in items})
            self.post_validate()
        except DatabaseError:
            logger.exception('Error while updating settings from DB')
