import os
from urllib.parse import urlparse
import pymysql.cursors
from enum import Enum


class Isolation(Enum):
    READ_COMMITTED = "READ COMMITTED"
    READ_UNCOMMITTED = "READ UNCOMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"


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
            cursor.execute(f"SET SESSION TRANSACTION ISOLATION LEVEL {isolation_level.value}")

        cursor.execute(sql)
        rows = cursor.fetchall()

        if isolation_level is not None:
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        return rows
    finally:
        connection.close()
