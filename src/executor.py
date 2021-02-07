import ast

import pandas as pd
import pymysql.cursors
from dotenv import load_dotenv
from language_utils import import_class
from connection_manager import query, Isolation
from datetime import date
from stock_type import StockType
from compiler import Compiler


load_dotenv()

Indicator = import_class('utils', 'Indicator')
Function = import_class('utils', 'function', 'Function')


compiler = Compiler()


def __execute_term(code, df):
    exec(compile(code, '', mode='exec'))
    return df


def execute_term(source_code: str, stock_type: StockType, from_date: date, to_date: date):
    compile_result = compiler.compile(source_code)

    sql = """
    select td.date, dc.ticker_id, dc.close from data_iskoreatradingday td
    left join data_candleday dc on td.date = dc.date
    where td.is_tradable = 1
    and td.date between '{}' and '{}';
    """.format(from_date, to_date)
    rows = query(sql, Isolation.REPEATABLE_READ)

    total_df = pd.DataFrame(rows)
    for item in compile_result.item_list:
        # TODO: is_rank 값 잘 들어가는지 계속 확인하고, 검증할것
        if item.is_rank:
            y = total_df.groupby('date').apply(lambda df: __execute_term(item.code, df)).reset_index(drop=True)
        else:
            y = total_df.groupby('ticker_id').apply(lambda df: __execute_term(item.code, df)).reset_index(drop=True)

        different_columns = total_df.columns.symmetric_difference(y.columns)
        for column in different_columns:
            total_df.insert(0, column, y[column])

    return total_df


def by_apply(df, function):
    df.apply(function)


def by_pd_vector(df, function):
    df['custom'] = function()


# https://aldente0630.github.io/data-science/2018/08/05/a-beginners-guide-to-optimizing-pandas-code-for-speed.html
def by_np_vector(df, function):
    df['custom'] = function()


if __name__ == '__main__':
    execute_ticker("1 + 2", 1, date(2021, 1, 1), date(2022, 1, 1))
