from .singletone import DbToolSingletone


class DbToolInitializer(DbToolSingletone):

    def __init__(cls, *args, **kwargs):
        cls._databases_used_in_project = cls._get_used_databases_in_project()
        cls._available_databases = list(
            filter(
                lambda db: not cls._is_this_db_in_ignore(db.db_postgres_name),
                cls._databases_used_in_project,
            ),
        )
        cls._default_connection_data = cls.get_default_connection_config()
        return super().__init__(*args, **kwargs)
