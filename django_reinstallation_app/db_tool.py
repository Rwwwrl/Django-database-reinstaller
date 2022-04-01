from collections import namedtuple
from typing import Dict, List, Tuple, Union

from django.conf import settings

import psycopg2
from psycopg2.extensions import (
    ISOLATION_LEVEL_AUTOCOMMIT,
    ISOLATION_LEVEL_READ_COMMITTED,
)

from . import print_tool as p

# db_django_name - значение db в словаре settings.DATABASES (пример "default"),
# db_postgres_name - значение db['NAME'] в словаре settings.DATABASES (пример "test"),
DbSettingData = namedtuple("DbSettingData", ["db_django_name", "db_postgres_name"])


class DbTool:
    """
    Класс для работы с базой данных, синглтон
    """

    db_connections = []

    def __new__(cls, db_name: str = None, *args, **kwargs):
        cls._databases_used_in_project = cls._get_used_databases_in_project()
        cls._available_databases = list(
            filter(
                lambda db: not cls.is_this_db_in_ignore(db.db_postgres_name),
                cls._databases_used_in_project,
            ),
        )

        for db_connection in cls.db_connections:
            if db_connection.connect_data.get("database", None) == db_name:
                return db_connection
        new_db_connection_instance = super().__new__(cls)
        cls.db_connections.append(new_db_connection_instance)
        return new_db_connection_instance

    def __init__(self, db_name: str = None) -> None:
        """
        инициализация данных подключения
        1 - Если передаем db_name, то пытаемся найти настройки бд в settings.DATABASES, если не находим, то
        настройки подключения по умолчанию
        2 - Если мы не передаем db_name, то мы не подключаемся ни к какой бд (нужно для создания/удаления других бд)
        """
        # не нужно опять настраивать инстанс, если мы уже это делали.
        if hasattr(self, 'is_initialized'):
            return
        self.connect_data = self.get_default_connection_config()
        if db_name:
            connect_data = self._get_db_info_by_django_settings(db_name)
            if connect_data:
                self.connect_data = connect_data
                p.info(
                    f"""Были найдены настройки подключений для вашей бд в settings.DATABASE,
                     были использована следующая конфигурация подключения: {self.connect_data}""",
                )
            else:
                self.connect_data.update({"database": db_name})
                p.info(
                    f"""Не было найдено настройки подключений для вашей бд в settings.DATABASE,
                     были использована следующая конфигурация подключения: {self.connect_data}""",
                )
            return
        p.info(
            f"""Вы не подключены ни к какой бд, ваши настройки подкючения: {self.connect_data},
         если вы хотите подключиться к одной из бд, укажите db_name при создание экземляра класса DbTool.""",
        )
        self.is_initialized = True

    @property
    def databases_used_in_project(self):
        return self._databases_used_in_project

    @property
    def available_databases(self):
        return self._available_databases

    def __enter__(self):
        self.__conn = psycopg2.connect(**self.connect_data)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Если во время транзация произошла ошибка - делаем роллбек else коммит
        if exc_type:
            self.__conn.rollback()
        else:
            self.__conn.commit()
        self.__conn.close()

    def _exec_request(self, sql_string: str, is_isolate_required: bool = False) -> None:
        """
        выполнить sql запрос
        """
        cursor = self.__conn.cursor()
        # для "CREATE DATABASE" и "DROP DATABASE" нужно установить в автокоммит
        if is_isolate_required:
            self.__conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        else:
            self.__conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        try:
            cursor.execute(sql_string)
        except psycopg2.Error as e:
            p.error(sql_string)
            raise e

        cursor.close()

    def get_default_connection_config(self) -> Dict[str, str]:
        '''
        получить дефолтные настройки подключение из setttings.DATABASES['default']
        '''
        default_db = settings.DATABASES['default']
        return {
            'user': default_db.get('USER', 'postgres'),
            'host': default_db.get('HOST', 'localhost'),
            'port': default_db.get('PORT', '5432'),
            'password': default_db.get('PASSWORD', None),
        }

    def check_is_user_connected_to_free_db(func):
        """
        Для удаления и создание БД мы не должны быть подключены к одной из этих бд
        """
        def inner(self_instance, *args, **kwargs):
            connected_database = self_instance.connect_data.get("database", None)
            if connected_database and connected_database in self_instance.available_databases:
                p.error("Вы пытаетесь удалить или создать бд подключившись к одной из этих баз данных")
                raise SystemError
            return func(self_instance, *args, **kwargs)

        return inner

    @staticmethod
    def _get_used_databases_in_project() -> List[Tuple[str, str]]:
        """
        получить список используемых бд в проекте
        """
        database_dict = settings.DATABASES
        databases_in_project = []
        for db in database_dict:
            # Мы работаем только с постгресом
            if database_dict[db]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
                db_data = DbSettingData(db, database_dict[db]["NAME"])
                databases_in_project.append(db_data)
        return databases_in_project

    def _get_db_info_by_django_settings(self, db_name: str) -> Union[Dict[str, str], None]:
        """
        получить все настройки для бд из файла settings, чтобы не дублировать их
        """
        for db in self._databases_used_in_project:
            if db.db_postgres_name == db_name:
                p.info("Была найдены настройки бд в джанго проекте, эти настройки и будут использованы для подключения")
                db_config = settings.DATABASE[db.db_django_name]
                return {
                    "database": db_name,
                    "user": db_config.get("USER", "postgres"),
                    "host": db_config.get("HOST", "localhost"),
                    "port": db_config.get("PORT", "5432"),
                    "password": db_config.get("PASSWORD", None),
                }
        p.info(
            f'''Не было найдено настроек для бд '{db_name}' в settings.DATABASES, будут использованы настройки,
             которые вы передали в экземляр''',
        )

    @staticmethod
    def is_this_db_in_ignore(db_name: str) -> bool:
        """
        проверить, находится ли бд с имененем db_name в списке игнора для переустановки
        ( в setttings.DATABASES_TO_IGNORE )
        """
        databases_to_ignore = getattr(settings, "DATABASES_TO_IGNORE", [])
        return databases_to_ignore == ["*"] or db_name in databases_to_ignore

    @check_is_user_connected_to_free_db
    def drop_project_databases(self) -> None:
        """
        удалить все базы данных, которые есть в проекте
        """
        sql_string = "DROP DATABASE IF EXISTS {};"
        droped_databases = []
        for db in self._available_databases:
            try:
                self._exec_request(sql_string.format(db.db_postgres_name), is_isolate_required=True)
            except Exception as e:
                print('Произошла непредвиденная ошибка при удалении БД')
                raise e
            else:
                droped_databases.append(db)
        if droped_databases:
            p.info(f"Были удалены эти БД: {[db.db_postgres_name for db in droped_databases]}")
        else:
            p.info("Не было удалено ни одной БД")

    @check_is_user_connected_to_free_db
    def create_project_databases(self) -> None:
        """
        создать пустые базы данных, которые есть в проекте
        """
        sql_string = "CREATE DATABASE {};"
        created_databases = []
        for db in self._available_databases:
            try:
                self._exec_request(sql_string.format(db.db_postgres_name), is_isolate_required=True)
            except Exception as e:
                print('Произошла непредвиденная ошибка при создании БД')
                raise e
            else:
                created_databases.append(db)
        if created_databases:
            p.info(f"Были созданы эти БД: {[db.db_postgres_name for db in created_databases]}")
        else:
            p.info("Не было создано ни одной БД")
