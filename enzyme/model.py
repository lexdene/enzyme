import re

from . import builders, db


def pluralize(word):
    return word + 's'


def _underscore_repl(matchobj):
    if matchobj.start(0) > 0:
        return '_' + matchobj.group(0).lower()
    else:
        return matchobj.group(0).lower()


def underscore(word):
    return re.sub(
        '[A-Z]',
        _underscore_repl,
        word
    )


class MetaModel(type):
    @property
    def table_name(self):
        return pluralize(underscore(self.__name__))

    def get(self, value=None, **kwargs):
        if value is not None:
            kwargs.update(id=value)

        builder = builders.LinkedBuilder(
            self.table_name,
            db.Db.get_singleton()
        )
        result = builder.where(kwargs).find()

        return self.load_data(result)


class Model(metaclass=MetaModel):
    def __init__(self, **kwargs):
        self.__loaded_data = {}
        self.__setted_data = kwargs

    def _load_data(self, data):
        self.__loaded_data = data

    @classmethod
    def load_data(cls, data):
        m = cls()
        m._load_data(data)
        return m

    def __setattr__(self, name, value):
        if name.startswith('_Model__'):
            return super(Model, self).__setattr__(name, value)
        else:
            self.__setted_data[name] = value

    def __getattr__(self, name):
        if name in self.__setted_data:
            return self.__setted_data[name]
        elif name in self.__loaded_data:
            return self.__loaded_data[name]
        else:
            return super(Model, self).__getattr__(name)

    def save(self):
        if self.__setted_data == {}:
            raise ValueError('nothing to save')

        builder = builders.LinkedBuilder(
            self.__class__.table_name,
            db.Db.get_singleton()
        )
        result = builder.where(
            id=self.__loaded_data['id']
        ).update(self.__setted_data)

        if result > 0:
            self.__loaded_data.update(self.__setted_data)
            self.__setted_data = {}

            return True


class ModelSetBuilder:
    def __init__(self, model_class, conn):
        self.__model_class = model_class
        self.__builder = builders.LinkedBuilder(
            model_class.table_name,
            conn
        )

    def select(self):
        result = self.__builder.select()

        return list(
            self.__model_class.load_data(data)
            for data in result
        )

    def __getattr__(self, name):
        if hasattr(self.__builder, name):
            def wrap(*argv, **kwargs):
                func = getattr(self.__builder, name)
                func(*argv, **kwargs)

                return self
            return wrap

        return super(ModelSetBuilder, self).__getattr__(name)
