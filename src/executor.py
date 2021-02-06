import ast

import pandas as pd
import pymysql.cursors
from dotenv import load_dotenv
from language_utils import import_class
from connection_manager import query
from datetime import date


load_dotenv()

Indicator = import_class('utils', 'Indicator')
Function = import_class('utils', 'function', 'Function')


def __execute_ticker(code, df):
    '''
    코드 실행 함수
    :param code: 실행할 소스코드 ast tree
    :param df: 데이터 프레임
    :return:
    '''
    results = dict()
    exec(code)
    return results['result']


def execute_ticker(source_code: str, field_list, from_date: date, to_date: date):
    parse_tree = ast.parse(source_code)
    executable_code = compile(parse_tree, '', 'exec')

    # DB 쿼리
    sql = f"select * from data_candleday " \
          f"where date between '{from_date}' and '{to_date}' " \
          f"order by date;"
    rows = query(sql)
    df = pd.DataFrame(rows)
    grouped = df.groupby('date')
    for key, group in grouped:
        group = group.reset_index(drop=True)
        print(group)

    # pandas loop
    # for loop 시간 비교
    # apply 시간 비교
    # 실행
    return __execute_ticker(executable_code, df)


def by_apply(df, function):
    df.apply(function)


def by_pd_vector(df, function):
    df['custom'] = function()


# https://aldente0630.github.io/data-science/2018/08/05/a-beginners-guide-to-optimizing-pandas-code-for-speed.html
def by_np_vector(df, function):
    df['custom'] = function()


if __name__ == '__main__':
    execute_ticker("1 + 2", 1, date(2021, 1, 1), date(2022, 1, 1))
