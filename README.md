# Magic-settings

## Установка

```bash
$ pip install magic-settings
```

Для использования настроек из `yaml` файла

```bash
$ pip install magic-settings[yaml]
```

## Инициализация

### Объявление класса настроек проекта
```python
from magic_settings import BaseSettings, Property

class MySettings(BaseSettings):
    VERSION = Property(types=str)
    PROJECT_DIR = Property(types=str)
```
Класс ```Property``` является дескриптором и содержит следующие параметры:
- ***types*** - Список типов или тип ```значения```. Выбрасывает ```ValueError```, если ```значение``` не является ни одним типом из ```types```.
- ***validators*** - Список из ```callable``` объектов, каждый из которых последовательно применяется к ```значению```.  Выбрасывает ```ValueError```, если ```значение``` не проходит хотя бы одну из валидаций.
- ***choices*** - Список из любых объектов. Если ```значение``` не содержится в ```choices``` - выбрасывает ```ValueError```. При использовании данного параметра игнорируются параметры ```types``` и ```validators```.
- ***default*** - Устанавливает дефолтное значение аттрибута класса ```Property```.
- ***converts*** - Список из ```callable``` объектов. Представляет из себя цепочку преобразований, которые последовательно применяются к ```значению``` и каждый раз перезаписывают его. Применяется к ```значению``` только если оно является строкой. Выбрасывает ```ValueError```, если ```значение``` не проходит хотя бы одно из преобразований.

### Конфигурация настроек
Конфигурация настроек происходит на этапе создания объекта внутри конструктора

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

### Параметры
- ***modules***: Список импортируемых python файлов с переменными. Дефолтное значение ```None```. 
- ***prefix***: Префикс, с которым берутся переменные окружения. Дефолтное значение ```None```.

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
    
- ***dotenv_path***: Путь до env-файла. Дефолтное значение ```None```. Используется для загрузки переменных из env-файла в окружение. Если dotenv_path ```None``` -  то пойдет по дереву каталогов вверх, ища указанный файл - по умолчанию имя файла для поиска - ```.env```.
- ***override_env***: ```True``` - перезаписать значения, которые при загрузке из ```.env``` встречаются с такими же именами в окружении, ```False``` - не перезаписывать. Дефолтное значение - ```False```. 
- ***yaml_settings_path***: Путь до конфигурационного yaml файла. Дефолтное значение ```None```.
- ***use_env***: ```True``` - использовать переменные окружения среды. Дефолтное значение ```True```.

### Исключения
***ValueError***: Если тип modules не ```list``` или ```NoneType```. Если тип элемента в ***modules*** не ```ModuleType```.

Загрузка настроек
-----------------
Загрузку настроек можно инициировать в любом месте проекта.
```python
from where_your_settings import settings

settings.init()
```
При повторном вызове снова пройдет по конфигурационным файлам и обновит их.

Приоритизация настроек
----------------------
В случае, если настройки пересекаются, приоритет будет следующий:
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

Примеры:
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

Временное переопределение Property
----------------------------------
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

Метод ```temp_set_attributes``` не является потокобезопасным.

## Список настроек
Для получения списка настроек можно использовать методы `to_dict()`, `to_json`:
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

## Валидация
При переопределении метода `update_settings_from_source` рекомендуется использовать следующие методы класса `BaseSettings`:

1. `pre_validate` — проверка наличия типов в `Property`, проверка соответствия типу `Property` в возможных значениях `Property.choices`, проверка значения по умолчанию на соответствии типу.

2. `post_validate` — проверка на то, что каждому `Property` присвоено какое-либо значение
  

Динамические настройки
----------------------

### Объявление класса, реализующего работу с источником настроек
На примере хранения настроек в словаре `source`:
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

### Объявление класса динамических настроек проекта

```python
class MyDynamicSettings(BaseDynamicSettingsDict):
    JIGGLYPUFF = Property(types=str)
```

### Инициализация экземпляра динамических настроек
```python
loop = asyncio.get_event_loop()
dynamic_settings = MyDynamicSettings(loop=loop, update_period=5, task_retries_number=5)
```
- ***update_period***: период обновления настроек из источника в секундах
- ***task_retries_number***: количество попыток обновить настройки при возникновении исключения перед остановкой задания

### Обновление динамических настроек

#### Обновление настроек один раз  
```python
await dynamic_settings.update_settings_from_source()
```

#### Запуск бесконечного обновления:

```python
await dynamic_settings.start_update()
```

#### Остановка бесконечного обновления:
```python
await dynamic_settings.stop_update()
```

### Запись настроек в источник
```python
await dynamic_settings.update_config(JIGGLYPUFF='magenta')
```

### Исключения
- ***magic_settings.DynamicSettingsSourceError*** - это исключение следует выбрасывать при недоступности источника настроек в классе, унаследованном от `BaseDynamicSettings`


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
- ***types*** - Type list or type of ```value```. Raises ```ValueError``` if ```value``` is not one of the ```types```.
- ***validators*** - List of ```callable``` objects each of which is consistently applied to ```value```.  Raises ```ValueError``` if ```value``` does not pass at least one of the validations.
- ***choices*** - List of any objects. If ```value``` not contained in ```choices``` - raises ```ValueError```. When using this parameter, parameters  ```types``` and ```validators``` are ignored.
- ***default*** - Sets the default value of the class attribute ```Property```.
- ***converts*** - List of ```callable``` objects. It is a chain of transformations that are consistently applied to the ```value``` and overwrite it each time. It applies to ```value``` only if ```value``` is a string. Raises ```ValueError``` if ```value``` at least one of the transformations failed to apply.

### Settings configuration
Settings configuration occur at the stage of creating an object inside the constructor.

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

Temporary Property redefinition
----------------------------------
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
You can use methods `to_dict()`, `to_json` to get list of settings:
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