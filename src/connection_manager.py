import os
from urllib.parse import urlparse
import pymysql.cursors
from enum import Enum


class Isolation(Enum):
    READ_COMMITTED = "READ COMMITTED"
    READ_UNCOMMITTED = "READ UNCOMMITTED"


def get_connection():
    database_url = os.getenv('DATABASE_URL')
    result = urlparse(database_url)

    return pymysql.connect(
        host=result.hostname,
        port=result.port,
        user=result.username,
        password=result.password,
        db=result.path[1:] if result.path else '',
        charset='utf8'
    )


def query(sql: str, isolation_level=None):
    connection = get_connection()
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        if isolation_level is not None:
            isolation(cursor, isolation_level, lambda x: cursor.execute(sql))
        else:
            cursor.execute(sql)
        return cursor.fetchall()
    finally:
        connection.close()


def isolation(cursor, isolation_level, function):
    cursor.execute(f"SET SESSION TRANSACTION ISOLATION LEVEL {isolation_level.value}")
    function()
    cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ")
