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

    python_command = "sudo python3" if platform == "linux" else "python"

    @classmethod
    def delete_migration_files(cls) -> None:
        """
        удалить файлы миграций из папок приложений
        """
        user_defined_apps = AppTool.get_user_defined_apps()
        for app in user_defined_apps:
            migration_folder_path = os.path.join(settings.BASE_DIR, app, "migrations")
            for file in os.listdir(migration_folder_path):
                if not file == "__init__.py":
                    file_path = os.path.join(migration_folder_path, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            p.info(f"Были удалены миграции для приложения '{app}'")

    @classmethod
    def makemigrations_and_migrate(cls):
        cls.__run_python_command("makemigrations")
        cls.__run_python_command("migrate")

    @classmethod
    def __run_python_command(cls, python_command) -> None:
        """
        запуска питоновской джанго комманды
        """
        command = cls.python_command + " manage.py " + python_command
        result_status = os.system(command)
        if not result_status:
            p.info(command + " успешно проведена")
        else:
            p.error(command + " проведена с ошибкой")
