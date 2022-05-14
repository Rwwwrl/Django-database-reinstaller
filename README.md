# Скрипт для:

- Переустановки бд, задействованных в джанго-проекте.
- Удаления всех старых файлов миграций, создания и применения новых для всех приложений в джанго-проекте.

## Установка

1. Установить пакет:

   - `pip install django-reinstallation-app`

   - Или, находясь внутри _database_installer:_ `pip install dist/django_reinstallation_app-X.tar.gz`

2. Добавить _django_reinstallation_app_ в _settings.INSTALLED_APPS_:

```python
INSTALLED_APPS = (
    ...
    'django_reinstallation_app',
    ...
)
```

## Настройка

1. Скрипт по умолчанию берет все бд и их настройки (_name, user, host ..._) из **_settings.DATABASES_**. БД должна быть **_postgres_**.
   Заигнорить бд, для которой переустановку делать не надо можно, указав в _settings.py_

```python
DATABASES_TO_IGNORE = ['*']  # Заигнорить все бд, которые есть в проекте
DATABASES_TO_IGNORE = ['some_db']  # Заигнорить бд some_db (some_db - имя бд в postgres)
```

2. Скрипт по умолчанию удаляет старые миграции, создает новые и применяет их для всех приложений, созданных пользователем в _settings.INSTALLED_APPS_  
   Заигнорить приложение, для которого не нужно этого делать можно, указав в _settings.py_

```python
DJANGO_APPS_TO_IGNORE = ['*']  # Заигнорить все приложения, которые есть в проекте
DJANGO_APPS_TO_IGNORE = ['app']  # Заигнорить приложение app
```

## Запуск

Запуск скрипта реализован как джанго-комманда `python manage.py install -p -m`

**_-p_** - переустановка БД

**_-m_** - удаление старых миграция, создание и примение новых
