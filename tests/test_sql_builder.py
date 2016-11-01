import unittest

from enzyme import builders
from enzyme.table import clear_table, column, define_table


def setUpModule():
    define_table(
        'users',
        column.primary_id(),
        column.string('username', unique=True),
        column.integer('age'),
        column.meta_times()
    )


def tearDownModule():
    clear_table()


class MockDb:
    def __init__(self):
        self.__sql_log = []

    def query(self, sql, params=None):
        self.__sql_log.append(sql)

    def execute(self, sql, params=None):
        self.__sql_log.append(sql)

    def sql_log(self):
        return self.__sql_log


class SqlBuilderTestCase(unittest.TestCase):
    def testSqlBuilder(self):
        conn = MockDb()
        builder = builders.LinkedBuilder('users', conn)
        builder.select()

        self.assertEqual(
            [
                'select\n'
                '`users`.`id`,\n'
                '`users`.`username`,\n'
                '`users`.`age`,\n'
                '`users`.`created_at`,\n'
                '`users`.`updated_at`,\n'
                '`users`.`deleted_at`\n'
                'from `users` as users',
            ],
            conn.sql_log()
        )
