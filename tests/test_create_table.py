import unittest

from enzyme.table import define_table, get_table, create_table, column


define_table(
    'users',
    column.primary_id(),
    column.string('username', unique=True),
    column.integer('age'),
    column.meta_times()
)


class MockDb:
    def __init__(self):
        self.__last_sql = ''

    def execute(self, sql, params=None):
        self.__last_sql = sql

    def last_sql(self):
        return self.__last_sql


class CreateTableTestCase(unittest.TestCase):
    def testCreateTable(self):
        conn = MockDb()
        create_table(conn, get_table('users'))
        self.assertEqual(
            (
                'CREATE TABLE IF NOT EXISTS `users`('
                '`id` INT NOT NULL AUTO_INCREMENT,'
                '`username` VARCHAR(100) NOT NULL,'
                '`age` INT NOT NULL,'
                '`created_at` DATETIME NOT NULL,'
                '`updated_at` DATETIME NOT NULL,'
                '`deleted_at` DATETIME,'
                'PRIMARY KEY(`id`),'
                'UNIQUE KEY(`username`)'
                ')ENGINE=InnoDB DEFAULT CHARSET=utf8'
            ),
            conn.last_sql()
        )
