import os
from sys import platform

from django.conf import settings

from . import print_tool as p
from .app_tool import AppTool


def get_python_command():
    '''
    Функция для получения команды "python" с учетом платформы и
    наличия виртуального окружения
    '''
    python_env_path = os.environ.get('VIRTUAL_ENV', None)
    if platform in ('linux', 'darwin'):
        python_command = 'python3'
        if python_env_path:
            python_command = f'{python_env_path}/bin/python3'
    else:
        python_command = 'python'
        if python_env_path:
            python_command = f'{python_env_path}\\Scripts\\python'
    return python_command


class MigrationTool:
    """
    класс для работы с миграциями:
    - удаление файлов старых миграций,
    - создание и применение новых
    """
    def __new__(cls):
        cls._user_defined_apps = AppTool.get_user_defined_apps()
        cls._available_django_apps = list(
            filter(lambda app: not AppTool._is_app_in_ignore(app), cls._user_defined_apps),
        )
        return super().__new__(cls)

    @property
    def user_defined_apps(self):
        return self._user_defined_apps

    @property
    def available_django_apps(self):
        return self._available_django_apps

    @classmethod
    def delete_migration_files(cls) -> None:
        """
        удалить файлы миграций из папок приложений для каждого доступного приложения
        """
        for app in cls._available_django_apps:
            migration_folder_path = os.path.join(settings.BASE_DIR, app, "migrations")
            for file in os.listdir(migration_folder_path):
                if not file == "__init__.py":
                    file_path = os.path.join(migration_folder_path, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        if cls._available_django_apps:
            p.info(f"Были удалены миграции из этих приложений: {cls._available_django_apps}")
        else:
            p.info("Не было удалено файлов миграции ни из одного приложения")

    @classmethod
    def makemigrations_and_migrate(cls):
        for app in cls._available_django_apps:
            cls._run_python_command(f"makemigrations {app}")
            cls._run_python_command(f"migrate {app}")
        if not cls._available_django_apps:
            p.info("Не были создано и выполнено ни одной миграции")

    @staticmethod
    def _run_python_command(python_command: str) -> None:
        """
        запуск питоновской джанго комманды
        """
        command = get_python_command() + " manage.py " + python_command
        result_status = os.system(command)
        if not result_status:
            p.info(command + " успешно проведена")
        else:
            p.error(command + " проведена с ошибкой")
