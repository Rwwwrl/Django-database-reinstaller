import os

from services.db_tool import DbTool
from services.file_tool import FileTool
from services import print_service as p


class Installer:

    @staticmethod
    def drop_and_create_dbs():
        with DbTool(db_name='postgres') as postgres_db_instance:
            postgres_db_instance.drop_project_databases()
            postgres_db_instance.create_project_databases()

    @staticmethod
    def delete_and_update_migrations():
        f = FileTool(['app']) 
        f.delete_migration_files()
        f.makemigrations_and_migrate() 


if __name__ == '__main__':
    p.info('НАЧАЛО СКРИПТА')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
    Installer.drop_and_create_dbs()
    Installer.delete_and_update_migrations() 
    p.success('СКРИПТ УСПЕШНО ВЫПОЛНЕН')

