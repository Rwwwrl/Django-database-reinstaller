from services.db_tool import DbTool

import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
# django.setup()

class Installer:

    @staticmethod
    def drop_and_create_dbs():
        with DbTool(db_name='postgres') as postgres_db_instance:
            postgres_db_instance.drop_project_databases()
            postgres_db_instance.create_project_databases()


if __name__ == '__main__':
    Installer.drop_and_create_dbs()
    

