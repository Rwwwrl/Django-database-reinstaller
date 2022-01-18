import os

from django.core.management.base import BaseCommand

from ...installer_tool import Installer
from ... import print_service as p


class Command(BaseCommand):
    help = 'Переустановка баз данных, создание и примение миграций'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--postgres', action='store_true')
        parser.add_argument('-m', '--migrations', action='store_true')


    def handle(self, *args, **options):
        p.info('Начало скрипта')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
        if options['postgres']:
            Installer.drop_and_create_dbs()
        if options['migrations']:
            Installer.delete_and_update_migrations() 
        p.success('СКРИПТ УСПЕШНО ВЫПОЛНЕН')

 