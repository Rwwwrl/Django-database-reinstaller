import os
from sys import platform

from . import print_service as p


class FileTool:


    def __new__(cls, apps_list):
        cls.apps_list = apps_list
        cls.python_command = 'sudo python3' if platform == 'linux' else 'python'
        return super().__new__(cls)

    @classmethod
    def delete_migration_files(cls):
        '''
        удалить файлы миграций из папок приложений 
        '''
        root_project_path = os.getcwd()
        for app in cls.apps_list:
            migration_folder_path = os.path.join(root_project_path, app, 'migrations')
            for file in os.listdir(migration_folder_path):
                if not file == '__init__.py':
                    file_path = os.path.join(migration_folder_path, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        p.info('Были удалены файлы миграции')
    
    @classmethod
    def makemigrations_and_migrate(cls):
        cls.__run_python_command('makemigrations')
        cls.__run_python_command('migrate')

    @classmethod
    def __run_python_command(cls, python_command):
        command = cls.python_command + ' manage.py ' + python_command
        result = os.system(cls.python_command + ' manage.py ' + python_command)
        if result:
            p.info(command + ' успешно проведена')
        else:
            p.error(command + ' проведена с ошибкой')