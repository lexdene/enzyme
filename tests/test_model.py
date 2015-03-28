import unittest

from enzyme.table import define_table, clear_table, column
from enzyme.model import Model
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

        return {
            'id': params['id'],
            'username': 'elephant',
            'age': 18,
        }

    def execute(self, sql, params=None):
        self.__sql_log.append(sql)

        return {
            'row_count': 1
        }

    def sql_log(self):
        return self.__sql_log


class ModelTestCase(unittest.TestCase):
    def testGetAndUpdate(self):
        conn = MockDb()
        Db.set_singleton(conn)

        user = User.get(1)
        self.assertEqual(user.age, 18)

        user.age = 19
        self.assertEqual(user.age, 19)

        user.save()
        self.assertEqual(user.age, 19)

        self.assertRaises(ValueError, user.save)

        self.assertEqual(
            [
                'select\n'
                '`users`.`id`,\n'
                '`users`.`username`,\n'
                '`users`.`age`,\n'
                '`users`.`created_at`,\n'
                '`users`.`updated_at`,\n'
                '`users`.`deleted_at`\n'
                'from `users` as users\n'
                'where id = %(id)s\n'
                'limit 1',
                'update users set age=%(age)s\n'
                'where id = %(id)s',
            ],
            conn.sql_log()
        )
