from .db_tool import DbTool
from .migration_tool import MigrationTool


class Installer:
    """
    Главный класс скрипта, в нем определяются все основные шаги скрипта
    """
    @staticmethod
    def drop_and_create_dbs():
        with DbTool() as connection:
            connection.drop_project_databases()
            connection.create_project_databases()

    @staticmethod
    def delete_and_update_migrations():
        mt = MigrationTool()
        mt.delete_migration_files()
        mt.makemigrations_and_migrate()
