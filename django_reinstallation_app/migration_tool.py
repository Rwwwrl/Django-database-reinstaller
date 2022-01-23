import os
from sys import platform

from django.conf import settings

from . import print_tool as p
from .app_tool import AppTool


class MigrationTool:
    """
    класс для работы с миграциями:
    - удаление файлов старых миграций,
    - создание и применение новых
    """

    def __new__(cls):
        cls.__python_command = "sudo python3" if platform == "linux" else "python"
        cls.__user_defined_apps = AppTool.get_user_defined_apps()
        cls.__available_django_apps = list(filter(lambda app: not cls.is_app_in_ignore(app), cls.__user_defined_apps))
        return super().__new__(cls)

    @property
    def user_defined_apps(self):
        return self.__user_defined_apps

    @property
    def available_django_apps(self):
        return self.__available_django_apps

    @property
    def python_command(self):
        return self.__python_command

    @classmethod
    def delete_migration_files(cls) -> None:
        """
        удалить файлы миграций из папок приложений
        """
        for app in cls.__available_django_apps:
            migration_folder_path = os.path.join(settings.BASE_DIR, app, "migrations")
            for file in os.listdir(migration_folder_path):
                if not file == "__init__.py":
                    file_path = os.path.join(migration_folder_path, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        if cls.__available_django_apps:
            p.info(f"Были удалены миграции из этих приложений: {cls.__available_django_apps}")
        else:
            p.info("Не было удалено файлов миграции ни из одного приложения")

    @classmethod
    def makemigrations_and_migrate(cls):
        for app in cls.__available_django_apps:
            cls.__run_python_command(f"makemigrations {app}")
            cls.__run_python_command(f"migrate {app}")
        if not cls.__available_django_apps:
            p.info("Не были создано и выполнено ни одной миграции")

    @staticmethod
    def is_app_in_ignore(app_name) -> bool:
        """
        проверить, есть ли этот приложение в списке игнора для сброса и применения новых миграций
        ( в settings.DJANGO_APPS_TO_IGNORE )
        """
        django_apps_to_ignore = getattr(settings, "DJANGO_APPS_TO_IGNORE", [])
        return django_apps_to_ignore == ["*"] or app_name in django_apps_to_ignore

    @classmethod
    def __run_python_command(cls, python_command) -> None:
        """
        запуска питоновской джанго комманды
        """
        command = cls.__python_command + " manage.py " + python_command
        result_status = os.system(command)
        if not result_status:
            p.info(command + " успешно проведена")
        else:
            p.error(command + " проведена с ошибкой")
