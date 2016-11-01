import itertools
from collections import OrderedDict

from .column import ColumnDefiner


def define_table(table_name, *columns):
    table_data = dict(
        name=table_name,
        columns=list(),
        indexes=list(),
    )

    for column in columns:
        column(table_data)

    table = Table(table_data)
    return table


class Table:
    __tables = OrderedDict()

    def __init__(self, data):
        self.__data = data

        self.add_table(self)

    @property
    def name(self):
        return self.__data['name']

    @property
    def engine(self):
        return self.__data.get('engine', 'InnoDB')

    @property
    def charset(self):
        return self.__data.get('charset', 'utf8')

    def itercolumns(self):
        return iter(self.__data['columns'])

    def create_sql(self, force=False):
        sql = (
            'CREATE TABLE {force} `{table_name}`('
            '{define}'
            ')ENGINE={engine} DEFAULT CHARSET={charset}'
        ).format(
            force='' if force else 'IF NOT EXISTS',
            table_name=self.name,
            define=','.join(
                itertools.chain(
                    self._create_columns_sql(),
                    self._create_index_sql()
                )
            ),
            engine=self.engine,
            charset=self.charset
        )

        return sql

    def _create_columns_sql(self):
        for column in self.__data['columns']:
            sql = '`{name}` {type}'.format(
                name=column['name'],
                type=column['column_type'].name,
            )

            if 'type_desc' in column:
                sql += '(%s)' % column['type_desc']

            if not column.get('null'):
                sql += ' NOT NULL'

            if column.get('auto_increment'):
                sql += ' AUTO_INCREMENT'

            yield sql

    def _create_index_sql(self):
        for index in self.__data['indexes']:
            yield '{index_type} KEY(`{columns}`)'.format(
                index_type=index['index_type'].name,
                columns=','.join(index['columns']),
            )

    @classmethod
    def get_table(cls, name):
        return cls.__tables[name]

    @classmethod
    def add_table(cls, table):
        if table.name in cls.__tables:
            raise ValueError('%s already in tables' % table.name)

        cls.__tables[table.name] = table

    @classmethod
    def clear(cls):
        cls.__tables.clear()


def get_table(name):
    return Table.get_table(name)


def clear_table():
    return Table.clear()


def create_table(conn, table):
    sql = table.create_sql()
    conn.execute(sql)


column = ColumnDefiner()
