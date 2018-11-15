# -*- coding: utf-8 -*-
import contextlib
import logging
import os
import types
import warnings
from typing import Any, Dict, List, Type, Callable, Union, Tuple

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

NoneType = type(None)


class Undefined:
    pass


undefined = Undefined()


class BaseSettings:
    """

    class Settings(BaseSettings):
        FOO = Property(types=str, default='foo' converts=[str.lower])

    settings = Settings()
    settings.pre_validate()
    settings.update_config(FOO='bar')
    settings.post_validate()
    """

    def __init__(self, modules=None, prefix=None, dotenv_path=None,
                 override_env=False, yaml_settings_path=None, use_env=True):
        """
        :param modules: list of modules with settings or None
        :param prefix: prefix for env variables
        :param dotenv_path: path to .env file
        :param override_env: override environment variables if True
        :param yaml_settings_path: path to yaml settings
        :raises ValueError: if modules type is not list or NoneType
                or if item in modules type is not ModuleType
        """
        if not isinstance(modules, (list, NoneType)):
            raise ValueError('modules type is not list or NoneType')

        self.modules = modules or list()

        for module in self.modules:
            if not isinstance(module, types.ModuleType):
                raise ValueError(f'{module} type is not ModuleType')

        self.use_yaml_settings = isinstance(yaml_settings_path, str)

        if self.use_yaml_settings:
            self.yaml_settings_path = yaml_settings_path

        self.dotenv_path = dotenv_path
        self.override_env = override_env
        self.prefix = prefix if isinstance(prefix, str) else ''

        self.use_env = use_env

    def update_config(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self

    @property
    def properties(self):
        for name in dir(self.__class__):
            _property = self.__class__.__dict__.get(name)
            if issubclass(_property.__class__, BaseProperty):
                yield _property

    def pre_validate(self):
        for _property in self.properties:
            self.validate_types(_property)
            self.validate_choices(_property)
            self.validate_default(_property)

    def post_validate(self):
        for _property in self.properties:
            value = getattr(self, _property.name)
            if isinstance(value, Undefined):
                raise ValueError(f'Undefined value of {_property.name} property, '
                                 f'you must specify it in settings/local.py')

    @staticmethod
    def validate_types(_property):
        if _property.types is None:
            raise ValueError(f'Types should be specified on {_property.name} property')

    @staticmethod
    def validate_choices(_property):
        for choice in _property.choices:
            if _property.types and not isinstance(choice, _property.types):
                raise ValueError(f'Choices values of {_property.name} property '
                                 f'should be any of {_property.types} types')

            if _property.validators and not all([validator(choice) for validator in _property.validators]):
                raise ValueError(f'Choices values of {_property.name} property falls validation')

    @staticmethod
    def validate_default(_property):
        if isinstance(_property.default, Undefined):
            return None

        # if choices specified, validate default value against choices
        if _property.choices and _property.default not in _property.choices:
            raise ValueError(f'Default value of {_property.name} property '
                             f'should be any of {_property.choices} choices')

        # if choices not specified and types specified, validate default value against types
        if not _property.choices and _property.types and not isinstance(_property.default, _property.types):
            raise ValueError(f'Default value of {_property.name} property '
                             f'should be any of {_property.types} types')

        for validator in _property.validators:
            if not validator(_property.default):
                raise ValueError(f'Default value of {_property.name} property '
                                 f'fall validation on {validator.__name__}')

    def init(self):
        """Initialize settings"""
        self.pre_validate()

        for module in self.modules:
            self.update_config(**get_config_dict_from_module(module))

        if self.use_env:
            if self.dotenv_path:
                load_dotenv(dotenv_path=self.dotenv_path, override=self.override_env)
            self.update_config(**get_config_dict_from_env(prefix=self.prefix))

        if self.use_yaml_settings:
            self.update_config(**get_config_dict_from_yaml(self.yaml_settings_path))

        self.post_validate()

    def get_settings(self):
        """
        Get settings from environments
        :return: configured settings
        """
        warnings.warn('Using get_settings will be removed in 1.0.0 version. Use init instead.', DeprecationWarning)
        self.init()
        return self

    @contextlib.contextmanager
    def temp_set_attributes(self, **kwargs):
        """
        Temporarily set an attributes on settings for the duration of the context manager.
        Not Thread-safe
        :param kwargs: dict: key - attribute name, value - temporary value
        :raises AttributeError: if any key in kwargs doesn't fit to any attribute name in class
        """
        old_values = {}
        for attr, new_value in kwargs.items():
            if hasattr(self, attr):
                old_values[attr] = getattr(self, attr)
                setattr(self, attr, new_value)
            else:
                raise AttributeError(f'{self.__class__} does`t have such attribute')
        yield
        for attr, old_value in old_values.items():
            setattr(self, attr, old_value)


class BaseProperty:
    def __init__(self, types: Union[Tuple[Type, ...], Type] = None, validators: List[Callable] = None,
                 choices: List[Any] = None, default: Any = undefined, converts: List[Callable] = None):

        self.types = types if types is not None else ()
        self.validators = validators if validators is not None else []

        self.choices = choices if choices is not None else []
        self.default = default

        self.converts = converts if converts is not None else []

    def __get__(self, instance, owner):
        if instance is None:
            return self

        value = instance.__dict__.setdefault(self.name, self.default)

        return value

    def __set__(self, instance, value):
        if isinstance(value, str):
            for method in self.converts:
                try:
                    value = method(value)
                except Exception as e:
                    raise ValueError(f'Failed to convert property {self.name} with error: {e}')

        if self.choices:
            if value not in self.choices:
                raise ValueError(f"Value of {self.name} property should be equal to any of {', '.join(self.choices)}")
        else:
            if self.types and not isinstance(value, self.types):
                raise ValueError(f'Value of {self.name} property should be any of {self.types} types')

            for validator in self.validators:
                if not validator(value):
                    # TODO: figure out lambda's source code extraction
                    raise ValueError(f'Property {self.name} falls validation on {validator.__name__}')

        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name

    def __repr__(self):
        return f"Property('{self.name}')"


class ComplexProperty(BaseProperty):
    def __init__(self, keys: Dict = None, sequence: List = None, **kwargs):
        super().__init__(**kwargs)
        self.keys = keys
        self.sequence = sequence

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if all([self.keys, self.sequence]) or not any([self.keys, self.sequence]):
            raise AttributeError(f'At least and only one of `keys` or `sequence` parameter should be specified')

        if self.keys:
            return {key: getattr(instance, _property.name) for key, _property in self.keys.items()}

        if self.sequence:
            return [getattr(instance, _property.name) for _property in self.sequence]

    def __set__(self, instance, value):
        raise AttributeError(f'Direct setting of {self.name} property not allowed')


class TransformsMixin:
    def __init__(self, transforms: List[Callable] = None, **kwargs):
        super().__init__(**kwargs)
        self.transforms = transforms if transforms is not None else []

    def __get__(self, instance, owner):
        value = super().__get__(instance, owner)
        for transform in self.transforms:
            if isinstance(value, List):
                value = transform(*value)
            elif isinstance(value, Dict):
                value = transform(**value)
            else:
                value = transform(value)
        return value


class Property(BaseProperty):
    pass


class TransformsProperty(TransformsMixin, BaseProperty):
    pass


class TransformsComplexProperty(TransformsMixin, ComplexProperty):
    pass


def get_config_dict_from_module(module):
    return {var: getattr(module, var) for var in filter(str.isupper, dir(module))}


def get_config_dict_from_env(prefix: str = None, environ: Dict = None):
    """Creates dictionary using environment variables with prefix
    :param prefix: prefix variable searching by
    :param environ: dictionary, by default os.environ
    :return: dictionary with environment variable without prefix
    """
    prefix = f'{prefix}_' if (prefix is not None) and not prefix.endswith('_') else prefix
    environ = os.environ if environ is None else environ
    keys = list(filter(lambda x: x.startswith(prefix), environ.keys()) if prefix else environ.keys())
    result = {k[len(prefix):]: v for k, v in environ.items() if k in keys}
    return result


def validate_yaml_dict(yaml_dict):
    """Validate dict parsed from yaml configuration file
    :param yaml_dict: dict parsed from yaml configuration file
    :raises TypeError: if configuration file has several levels of nesting or param is not dict
    """
    if not isinstance(yaml_dict, dict):
        raise TypeError(f'configuration file has several levels of nesting.')
    for key, value in yaml_dict.items():
        if not isinstance(key, str) or isinstance(value, dict):
            raise TypeError(f'configuration file has several levels of nesting.')


def get_config_dict_from_yaml(path: str):
    """Get and validate dict from yaml file
    :param path: path to yaml configuration file
    :return: dict parsed from yaml configuration file or empty dict if exception
    """
    try:
        with open(path) as file:
            result = yaml.load(file) or {}
            validate_yaml_dict(result)
    except (IOError, TypeError, ValueError) as e:
        logger.error(f'Cannot read YAML config: {e}')
        result = {}
    return result
