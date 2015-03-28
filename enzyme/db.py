class Db:
    _instance = None

    @classmethod
    def set_singleton(cls, instance):
        cls._instance = instance

    @classmethod
    def get_singleton(cls):
        return cls._instance
