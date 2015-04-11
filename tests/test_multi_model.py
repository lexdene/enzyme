import unittest

from enzyme.table import define_table, clear_table, column
from enzyme.model import Model, ModelSetBuilder
from enzyme.db import Db


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


class User(Model):
    pass


class MockDb:
    def __init__(self):
        self.__sql_log = []

    def query(self, sql, params=None, **kwargs):
        self.__sql_log.append(sql)

        return [
            {
                'id': 1,
                'username': 'elephant',
                'age': 18,
            },
            {
                'id': 2,
                'username': 'oahcil',
                'age': 13,
            },
        ]

    def execute(self, sql, params=None):
        self.__sql_log.append(sql)

        return None

    def sql_log(self):
        return self.__sql_log


class MultiModelTestCase(unittest.TestCase):
    def testSelectMulti(self):
        conn = MockDb()

        users = ModelSetBuilder(User, conn).select()
        self.assertEqual(2, len(users))

        self.assertEqual(1, users[0].id)
        self.assertEqual(2, users[1].id)

        users = ModelSetBuilder(User, conn).where(id=1).limit(1).select()
        self.assertEqual(2, len(users))

        self.assertEqual(
            [
                (
                    'select\n'
                    '`users`.`id`,\n'
                    '`users`.`username`,\n'
                    '`users`.`age`,\n'
                    '`users`.`created_at`,\n'
                    '`users`.`updated_at`,\n'
                    '`users`.`deleted_at`\n'
                    'from `users` as users'
                ),
                (
                    'select\n'
                    '`users`.`id`,\n'
                    '`users`.`username`,\n'
                    '`users`.`age`,\n'
                    '`users`.`created_at`,\n'
                    '`users`.`updated_at`,\n'
                    '`users`.`deleted_at`\n'
                    'from `users` as users\n'
                    'where id = %(id)s\n'
                    'limit 1'
                ),
            ],
            conn.sql_log()
        )

    def testSelectMultiByModelClass(self):
        conn = MockDb()
        Db.set_singleton(conn)

        users = User.where(id=1).limit(1).select()
        self.assertEqual(2, len(users))

        self.assertEqual(
            [
                (
                    'select\n'
                    '`users`.`id`,\n'
                    '`users`.`username`,\n'
                    '`users`.`age`,\n'
                    '`users`.`created_at`,\n'
                    '`users`.`updated_at`,\n'
                    '`users`.`deleted_at`\n'
                    'from `users` as users\n'
                    'where id = %(id)s\n'
                    'limit 1'
                ),
            ],
            conn.sql_log()
        )
