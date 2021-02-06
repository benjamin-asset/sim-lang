import os
from urllib.parse import urlparse
import pymysql.cursors


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


def query(sql):
    connection = get_connection()
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows
    finally:
        connection.close()
