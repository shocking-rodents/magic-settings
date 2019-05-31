# Magic-settings

## Installation

```bash
$ pip install magic-settings
```

Using settings from `yaml` file

```bash
$ pip install magic-settings[yaml]
```

## Initialization

### Project settings class declaration
```python
from magic_settings import BaseSettings, Property

class MySettings(BaseSettings):
    VERSION = Property(types=str)
    PROJECT_DIR = Property(types=str)
```
Class ```Property``` is a descriptor with following parameters:
- ***types*** - Type of ```value``` or a tuple of possible ```types```. It is a ```ValueError``` if ```value``` is not one of the ```types```.
- ***validators*** - List of ```callable``` objects each of which is successively applied to ```value```.  Raises ```ValueError``` if ```value``` does not pass at least one of the validations.
- ***choices*** - List of any objects. If ```value``` is not in ```choices``` - raises ```ValueError```. When using this parameter, parameters  ```types``` and ```validators``` are ignored.
- ***default*** - Sets the default value of ```Property```.
- ***converts*** - List of ```callable``` objects. It is a chain of transformations that are successively applied to the ```value``` and overwrite it each time. It applies to ```value``` only if ```value``` is a string. Raises ```ValueError``` if ```value``` at least one of the transformations failed to apply.

### Settings configuration
Settings configuration occurs at the stage of creating a Settings object.

```python
from my_project import my_module, my_awesome_module
from my_config import MySettings

settings = MySettings(
    modules=[my_module, my_awesome_module],
    prefix='MY_PROJECT_ENV_SETTINGS',
    dotenv_path='/path/to/my/env',
    override_env=True,
    yaml_settings_path='/path/to/my/yaml/settings.yaml',
    use_env=True
)
```

### Parameters
- ***modules***: List of python files to import with variables. Default - ```None```. 
- ***prefix***: The prefix with which the environment variables are taken. Default - ```None```.

    _settings.py_
    ```python
    class MySettings(BaseSettings):
        PSYDUCK = Property(types=str)
    ```
    _.env_
    ```dotenv
    MYPROJECT_PSYDUCK=Owowowow
    ```
    _some_other_place.py_
    ```python
    settings = MySettings(prefix='MYPROJECT')
    ```
    or\
    _some_other_place.py_
    ```python
    settings = MySettings(prefix='MYPROJECT_')
    ```
    
- ***dotenv_path***: Path to env-file. Default - ```None```. Using for exporting variables from env-file to environment. If ```dotenv_path``` is ```None``` -  walking up the directory tree looking for the specified file - called ```.env``` by default.
- ***override_env***: ```True``` - override existing system environment variables, ```False``` - do not override. Default - ```False```. 
- ***yaml_settings_path***: Path to yaml config file. Default - ```None```.
- ***use_env***: ```True``` - use environment variables. Default - ```True```.

### Exceptions
***ValueError***: If ***modules*** type is not ```list``` or ```NoneType``` and if type of element in ***modules*** is not ```ModuleType```.

Settings loading
----------------
Loading settings can be initiated anywhere in the project.
```python
from where_your_settings import settings

settings.init()
```
If called again, it goes through the configuration files and update properties.

Settings priority
-----------------
In case of intersection of settings the following priority will be applied:
_my_module_ -> _my_awesome_module_ -> _.env_ -> _settings.yaml_
```python
class MySettings(BaseSettings):
    PSYDUCK = Property(types=str)
```
_my_module.py_
```python
PSYDUCK = 'one'
```
_my_awesome_module.py_
```python
PSYDUCK = 'two'
```
_.env_
```dotenv
MYPROJECTPREFIX_PSYDUCK=env
```
_setting.yaml_
```yaml
PSYDUCK: yaml
```

Examples:
--------
```python
settings = MySettings(modules=[my_module])
# PSYDUCK = 'one'
```
```python
settings = MySettings(modules=[my_module, my_awesome_module])
# PSYDUCK = 'two'
```

```python
settings = MySettings(modules=[my_awesome_module, my_module])
# PSYDUCK = 'one'
```
```python
settings = MySettings(modules=[my_module, my_awesome_module], dotenv_path='/path/to/dotenv')
# PSYDUCK = 'env'
```
```python
settings = MySettings(modules=[my_module, my_awesome_module], dotenv_path='/path/to/dotenv', use_env=False)
# PSYDUCK = 'two'
```
```python
settings = MySettings(modules=[my_module, my_awesome_module], dotenv_path='/path/to/dotenv', yaml_settings_path='/path/to/yaml/settings.yaml')
# PSYDUCK = 'yaml'
```

Temporary Property override
---------------------------
_my_module.py_
```python
PIKACHU = 'Psyduck_is_not_fine'
PSYDUCK = 'Owowowow'

```
```python
from my_project import my_module
from my_config import MySettings

class MySettings(BaseSettings):
    PSYDUCK = Property(types=str)
    PIKACHU = Property(types=str)

settings = MySettings(modules=[my_module])
settings.init()

with settings.temp_set_attributes(PSYDUCK='I_am_ok', PIKACHU='Psyduck_is_ok'):
    print(settings.PSYDUCK)
    print(settings.PIKACHU)
    # PSYDUCK='I_am_ok'
    # PIKACHU='Psyduck_is_ok'

print(settings.PSYDUCK)
print(settings.PIKACHU)
# PSYDUCK = 'Owowowow'
# PIKACHU = 'Psyduck_is_not_fine'
```

Method ```temp_set_attributes``` is not thread-safe.

## Settings list
You can use methods `to_dict()`, `to_json()` to get list of settings:
```python
from magic_settings import BaseSettings, Property
class MySettings(BaseSettings):
    PSYDUCK = Property(types=str)
    PIKACHU = Property(types=str)
    
settings = MySettings(dotenv_path='12345.env')
settings.PIKACHU = '3'
settings.PSYDUCK = '12345'
settings.to_dict()
# {
#     'properties': {
#         'PIKACHU': '3',
#         'PSYDUCK': '12345'
#     },
#     'sources': [{
#         'source_type': 'dotenv',
#         'address': {
#             'dotenv_path': '12345.env',
#             'override': False
#         }
#     }]
# }
```

## Validation
It is recommended to use following `BaseSettings` class methods during redefinition `update_settings_from_source` method:
    
1. `pre_validate` - check for the presence of types in` Property`, check for compliance with the type `Property` in possible values ​​of` Property.choices`, check for default values ​​for type matching.
2. `post_validate` - check if each `Property` is assigned a value.
  

Dynamic settings
----------------

### Definition of class working with settings source:
Example with storing settings in dict `source`:
```python
from magic_settings import BaseDynamicSettings, Property

source = {
    'JIGGLYPUFF': 'pink'
}

class BaseDynamicSettingsDict(BaseDynamicSettings):
    async def update_settings_from_source(self):
        super().update_config(**source)

    async def update_config(self, **kwargs):
        source.update(kwargs)
        return super().update_config(**kwargs)
```

### Definition of project`s dynamic settings class
```python
class MyDynamicSettings(BaseDynamicSettingsDict):
    JIGGLYPUFF = Property(types=str)
```

### Initialization of dynamic settings class instance
```python
loop = asyncio.get_event_loop()
dynamic_settings = MyDynamicSettings(loop=loop, update_period=5, task_retries_number=5)
```
- ***update_period***: settings`s update period from source in seconds.
- ***task_retries_number***: the number of attempts to update the settings when an exception occurred before stopping the task.

### Dynamic settings update

#### The only settings update 
```python
await dynamic_settings.update_settings_from_source()
```

#### Running infinity settings update loop:

```python
await dynamic_settings.start_update()
```

#### Stop infinity settings update loop:
```python
await dynamic_settings.stop_update()
```

### Writing settings into the source:
```python
await dynamic_settings.update_config(JIGGLYPUFF='magenta')
```

### Exceptions
- ***magic_settings.DynamicSettingsSourceError*** - this exception should be selected if the settings source in the class inherited from `BaseDynamicSettings` is unavailable.
