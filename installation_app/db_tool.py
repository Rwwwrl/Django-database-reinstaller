import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED
from collections import namedtuple
from typing import List

from . import print_tool as p

from django.conf import settings

# db_django_name - значение db в словаре settings.DATABASES (пример "default"),
# db_postgres_name - значение db['NAME'] в словаре settings.DATABASES (пример "test"),
DB_SETTING_DATA = namedtuple("DB_SETTING_DATA", ["db_django_name", "db_postgres_name"])


class DbTool:
    """
    Класс для работы с базой данных, синглтон
    """

    db_connections = []

    def __new__(cls, db_name, *args, **kwargs):
        for db_connection in cls.db_connections:
            if db_connection.connect_data["database"] == db_name:
                return db_connection
        new_db_connection_instance = super().__new__(cls)
        cls.db_connections.append(new_db_connection_instance)
        cls.databases_in_project = cls.__get_used_databases_in_project()
        return new_db_connection_instance

    def __init__(
        self,
        db_name,
        db_user: str = "postgres",
        db_host: str = "localhost",
        db_port: str = "5432",
        password: str = None,
    ) -> None:
        connect_data = self.__get_bd_info_by_django_settings(db_name)
        if connect_data:
            self.connect_data = connect_data
        else:
            self.connect_data = {
                "database": db_name,
                "user": db_user,
                "host": db_host,
                "port": db_port,
                "password": password,
            }

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

    def exec_request(self, sql_string: str, is_isolate_required: bool = False) -> None:
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

        p.success(sql_string)
        cursor.close()

    def check_is_user_connected_to_free_db(func):
        """
        для удаления и создания БД мы должны быть подключены в бд "postgres"
        иначе будет ошибка
        """

        def inner(self_instance, *args, **kwargs):
            if self_instance.connect_data["database"] in self_instance.databases_in_project:
                p.error("Вы пытаетесь удалить или создать бд подключившись к одной из этих баз данных")
                raise SystemError
            return func(self_instance, *args, **kwargs)

        return inner

    @staticmethod
    def __get_used_databases_in_project() -> List[tuple[str, str]]:
        """
        получить спосок используемых бд в проекте
        """
        database_dict = settings.DATABASES
        databases_in_project = []
        for db in database_dict:
            # Мы работаем только с постгресом
            if database_dict[db]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
                db_data = DB_SETTING_DATA(db, database_dict[db]["NAME"])
                databases_in_project.append(db_data)
        return databases_in_project

    def __get_bd_info_by_django_settings(self, db_name: str) -> None:
        """
        получить все настройки для бд из файла settings, чтобы не дублировать их
        """
        for db in self.databases_in_project:
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
            f"Не было найдено настроек для бд '{db_name}' в settings.DATABASES, будут использованы настройки, которые вы передали в экземляр"
        )

    @staticmethod
    def is_this_db_in_ignore(db_name: str) -> bool:
        databases_to_ignore = getattr(settings, "DATABASES_TO_IGNORE", [])
        return databases_to_ignore == ["*"] or db_name in databases_to_ignore

    @check_is_user_connected_to_free_db
    def drop_project_databases(self) -> None:
        """
        удалить все базы данных, которые есть в проекте
        """
        sql_string = "DROP DATABASE IF EXISTS {};"
        bd_that_were_deleted = []
        for db in self.databases_in_project:
            if not self.is_this_db_in_ignore(db.db_postgres_name):
                bd_that_were_deleted.append(db.db_postgres_name)
                self.exec_request(sql_string.format(db.db_postgres_name), is_isolate_required=True)
        if bd_that_were_deleted:
            p.info(f"БЫЛИ УДАЛЕНЫ БД: {bd_that_were_deleted}")
        else:
            p.info("НЕ БЫЛО УДАЛЕНО НИ ОДНОЙ БД")

    @check_is_user_connected_to_free_db
    def create_project_databases(self) -> None:
        """
        создать пустые базы данных? которые есть в проекте
        """
        sql_string = "CREATE DATABASE {};"
        bd_that_were_created = []
        for db in self.databases_in_project:
            if not self.is_this_db_in_ignore(db.db_postgres_name):
                bd_that_were_created.append(db.db_postgres_name)
                self.exec_request(sql_string.format(db.db_postgres_name), is_isolate_required=True)
        if bd_that_were_created:
            p.info(f"БЫЛИ СОЗДАНЫ ЭТИ БД: {bd_that_were_created}")
        else:
            p.info("НЕ БЫЛО СОЗДАНО НИ ОДНОЙ БД")
