# -*- coding: utf-8 -*-
import contextlib
import logging
import os
import types
import warnings
from json import dumps
from typing import Any, Callable, Dict, List, Tuple, Type, Union

from dotenv import load_dotenv

try:
    import yaml
except ImportError:
    yaml = None

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
        :param use_env: True if use environment variables else False
        :raises ValueError: if modules type is not list or NoneType
                or if item in modules type is not ModuleType
        """
        if not isinstance(modules, (list, NoneType)):
            raise ValueError('modules type is not list or NoneType')

        self.modules = modules or list()

        for module in self.modules:
            if not isinstance(module, (types.ModuleType, NoneType)):
                raise ValueError(f'{module} type is not ModuleType or NoneType')

        self.yaml_settings_path = yaml_settings_path

        if self.yaml_settings_path and not yaml:
            raise ValueError('To use yaml_settings_path you need install PyYaml library.'
                             'Use magic-settings[yaml] to install it.')

        self.dotenv_path = dotenv_path
        self.override_env = override_env
        self.prefix = prefix if isinstance(prefix, str) else ''

        self.use_env = use_env

    @property
    def _use_yaml_settings(self):
        return isinstance(self.yaml_settings_path, str)

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
            self._validate_types(_property)
            self._validate_choices(_property)
            self._validate_default(_property)

    def post_validate(self):
        for _property in self.properties:
            value = getattr(self, _property.name)
            if isinstance(value, Undefined):
                raise ValueError(f'Undefined value of required {_property.name} property, '
                                 f'you must specify it in your config source.')

    @staticmethod
    def _validate_types(_property):
        if _property.types is None:
            raise ValueError(f'Types should be specified on {_property.name} property')

    @staticmethod
    def _validate_choices(_property):
        for choice in _property.choices:
            if _property.types and not isinstance(choice, _property.types):
                raise ValueError(f'Choices values of {_property.name} property '
                                 f'should be any of {_property.types} types')

            if _property.validators and not all([validator(choice) for validator in _property.validators]):
                raise ValueError(f'Choices values of {_property.name} property falls validation')

    @staticmethod
    def _validate_default(_property):
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
            self.update_config(**_get_config_dict_from_module(module))

        if self.use_env:
            if self.dotenv_path:
                load_dotenv(dotenv_path=self.dotenv_path, override=self.override_env)
            self.update_config(**_get_config_dict_from_env(prefix=self.prefix))

        if self._use_yaml_settings:
            self.update_config(**_get_config_dict_from_yaml(self.yaml_settings_path))

        self.post_validate()

    def to_dict(self):
        """ Dict representation """
        sources = []

        for module in self.modules:
            if module is not None:
                sources.append({
                    'source_type': 'module',
                    'address': {
                        'name': module.__name__,
                    },
                })

        if self.use_env:
            sources.append({
                'source_type': 'dotenv',
                'address': {
                    'dotenv_path': self.dotenv_path,
                    'override': self.override_env,
                },
            })

        if self._use_yaml_settings:
            sources.append({
                'source_type': 'yaml',
                'address': {
                    'yaml_settings_path': self.yaml_settings_path,
                }
            })

        result_dict = {
            'properties': {prop.name: getattr(self, prop.name) for prop in self.properties},
            'sources': sources,
        }
        return result_dict

    def to_json(self):
        """ Json representation """
        return dumps(self.to_dict(), ensure_ascii=False)

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


def _get_config_dict_from_module(module):
    return {var: getattr(module, var) for var in filter(str.isupper, dir(module))}


def _get_config_dict_from_env(prefix: str = '', environ: Dict = None):
    """Creates dictionary using environment variables with prefix
    :param prefix: prefix variable searching by
    :param environ: dictionary, by default os.environ
    :return: dictionary with environment variable without prefix
    """
    prefix = f'{prefix}_' if prefix and not prefix.endswith('_') else prefix

    environ = os.environ if environ is None else environ
    if not prefix:
        return environ

    result = {}
    for key, value in environ.items():
        if key.startswith(prefix) and key != prefix:
            key_without_prefix = key[len(prefix):]
            result[key_without_prefix] = value
    return result


def _validate_yaml_dict(yaml_dict):
    """Validate dict parsed from yaml configuration file
    :param yaml_dict: dict parsed from yaml configuration file
    :raises TypeError: if configuration file has several levels of nesting or param is not dict
    """
    if not isinstance(yaml_dict, dict):
        raise TypeError(f'configuration file has several levels of nesting.')
    for key, value in yaml_dict.items():
        if not isinstance(key, str) or isinstance(value, dict):
            raise TypeError(f'configuration file has several levels of nesting.')


def _get_config_dict_from_yaml(path: str):
    """Get and validate dict from yaml file
    :param path: path to yaml configuration file
    :return: dict parsed from yaml configuration file or empty dict if exception
    """
    try:
        with open(path) as file:
            result = yaml.load(file, Loader=yaml.SafeLoader) or {}
            _validate_yaml_dict(result)
    except (IOError, TypeError, ValueError) as e:
        logger.error(f'Cannot read YAML config: {e}')
        result = {}
    return result
