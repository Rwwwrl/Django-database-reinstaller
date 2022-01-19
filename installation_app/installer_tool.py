from .db_tool import DbTool
from .migration_tool import MigrationTool


class Installer:
    """
    Главный класс скрипта, в нем вызывается все шаги скрипта
    """

    @staticmethod
    def drop_and_create_dbs():
        with DbTool(db_name="postgres") as postgres_db_instance:
            postgres_db_instance.drop_project_databases()
            postgres_db_instance.create_project_databases()

    @staticmethod
    def delete_and_update_migrations():
        mt = MigrationTool()
        mt.delete_migration_files()
        mt.makemigrations_and_migrate()
