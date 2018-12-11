# Magic-settings

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
***ValueError***: Если тип modules ___не___ ```list``` или ```NoneType```. Если тип элемента в ***modules*** ___не___ ```ModuleType```.

Загрузка настроек
-----
Загрузку настроек можно инициировать в любом месте проекта.
```python
from where_your_settings import settings

settings.init()
```
При повторном вызове снова пройдет по конфигурационным файлам и обновит их.

Приоритизация настроек
---
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

***Примеры***:
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
---
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

Динамические настройки
---

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