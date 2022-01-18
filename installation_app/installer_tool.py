from .db_tool import DbTool
from .file_tool import FileTool


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

