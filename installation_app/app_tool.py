import os

from django.apps import apps
from django.conf import settings


class AppTool:
    @classmethod
    def get_user_defined_apps(cls):
        """
        получить все django-приложения, определенные пользователем
        """
        installed_apps = apps.get_app_configs()
        user_defined_apps = []
        for app in installed_apps:
            app_folder = settings.BASE_DIR / app.name
            if cls.__is_django_app(app_folder):
                user_defined_apps.append(app.name)
        return user_defined_apps

    @staticmethod
    def __is_django_app(folder_path):
        """
        проверить, является ли эта папка django-приложением ( = есть ли у него файл apps)
        """
        apps_file_path = os.path.join(folder_path, "apps.py")
        result = os.path.exists(apps_file_path) and os.path.isfile(apps_file_path)
        return os.path.exists(apps_file_path) and os.path.isfile(apps_file_path)
