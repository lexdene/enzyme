from enum import Enum


class ColumnTypes(Enum):
    INT = 1
    BOOLEAN = 2
    VARCHAR = 3
    DATETIME = 4
    TIME = 5
    ENUM = 6


class IndexTypes(Enum):
    PRIMARY = 1
    UNIQUE = 2


class ColumnDefiner:
    def __getattr__(self, key):
        # fail early
        func = getattr(_builder, key)

        def define_function(*argv, **kwargs):
            def build_function(table_data):
                return func(table_data, *argv, **kwargs)

            return build_function

        return define_function


class ColumnBuilder:
    def primary_id(self, table_data):
        self.integer(table_data, 'id', null=False, auto_increment=True)
        self.add_index(table_data, ['id'], IndexTypes.PRIMARY)

    def meta_times(self, table_data):
        self.datetime(table_data, 'created_at', null=False)
        self.datetime(table_data, 'updated_at', null=False)
        self.datetime(table_data, 'deleted_at', null=True)

    def integer(self, table_data, name, **kwargs):
        table_data['columns'].append(dict(
            name=name,
            column_type=ColumnTypes.INT,
            **kwargs
        ))

    def string(self, table_data, name, length=100, unique=False, **kwargs):
        table_data['columns'].append(dict(
            name=name,
            column_type=ColumnTypes.VARCHAR,
            type_desc=length,
            **kwargs
        ))

        if unique:
            self.add_index(table_data, [name], IndexTypes.UNIQUE)

    def datetime(self, table_data, name, **kwargs):
        table_data['columns'].append(dict(
            name=name,
            column_type=ColumnTypes.DATETIME,
            **kwargs
        ))

    def add_index(self, table_data, columns, index_type):
        table_data['indexes'].append(dict(
            columns=columns,
            index_type=index_type
        ))


_builder = ColumnBuilder()
