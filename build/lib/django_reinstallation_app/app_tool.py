import os
from pathlib import Path
from typing import List

from django.apps import apps
from django.conf import settings


class AppTool:
    '''
    Класс, в котором сосредоточена логика работы с джанго приложениями
    '''
    @classmethod
    def get_user_defined_apps(cls) -> List[str]:
        """
        получить все django-приложения, определенные пользователем
        """
        installed_apps = apps.get_app_configs()
        user_defined_apps = []
        for app in installed_apps:
            app_folder = settings.BASE_DIR / app.name
            if cls._is_django_app(app_folder):
                user_defined_apps.append(app.name)
        return user_defined_apps

    @staticmethod
    def _is_django_app(folder_path: Path) -> bool:
        """
        проверить, является ли эта папка django-приложением ( = есть ли у него файл apps)
        """
        apps_file_path = os.path.join(folder_path, "apps.py")
        return os.path.exists(apps_file_path) and os.path.isfile(apps_file_path)

    @staticmethod
    def _is_app_in_ignore(app_name: str) -> bool:
        """
        проверить, есть ли приложение в списке игнора для сброса и применения новых миграций
        ( в settings.DJANGO_APPS_TO_IGNORE )
        """
        django_apps_to_ignore = getattr(settings, "DJANGO_APPS_TO_IGNORE", [])
        return django_apps_to_ignore == ["*"] or app_name in django_apps_to_ignore
