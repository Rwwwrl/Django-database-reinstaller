class SingletoneBaseClass(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        cls.key = cls._get_key(*args, **kwargs)
        if not cls._already_created():
            new_instance = super().__call__(*args, **kwargs)
            cls._instances[cls.key] = new_instance
        return cls._instances[cls.key]

    def _get_key(self, **kwargs):
        '''
        возвращаем ключ, по которому мы можем идентифицировать инстанс
        в словаре _instances
        '''
        raise NotImplementedError

    def _already_created(self):
        '''
        метод, в котором мы описываем логику проверки вхождения
        self в self._instances
        '''
        raise NotImplementedError


class ClassicSingletone(SingletoneBaseClass):
    def _get_key(self):
        return self

    def _already_created(self):
        return self.key in self._instances


class DbToolSingletone(ClassicSingletone):
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.is_initialized = True
        return instance

    def _get_key(self, **kwargs):
        return kwargs.get('db_name')
