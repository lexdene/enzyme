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

        model = self()
        model.load_data(result)
        return model


class Model(metaclass=MetaModel):
    def __init__(self, **kwargs):
        self.__loaded_data = {}
        self.__setted_data = kwargs

    def load_data(self, data):
        self.__loaded_data = data

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
