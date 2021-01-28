import os

from urllib.parse import urlparse
import pandas as pd
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()


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


def execute(source_code, field_list, start_date, end_date, function):
    connection = get_connection()
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # DB 쿼리
        sql = "select * from account_user;"
        cursor.execute(sql)
        rows = cursor.fetchall()
        print(rows)
        df = pd.DataFrame(rows)

        # pandas loop
        # for loop 시간 비교
        # apply 시간 비교
        function(df, source_code)

        # 실행

        # 값 누적 후 리턴
    finally:
        connection.close()


def by_apply(df, function):
    df.apply(function)


def by_pd_vector(df, function):
    df['custom'] = function()


# https://aldente0630.github.io/data-science/2018/08/05/a-beginners-guide-to-optimizing-pandas-code-for-speed.html
def by_np_vector(df, function):
    df['custom'] = function()


if __name__ == '__main__':
    execute("1 + 2", 1, 2, 3)
