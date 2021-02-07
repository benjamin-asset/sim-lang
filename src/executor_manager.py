from connection_manager import query
from executor import execute_ticker
from stock_type import StockType
from compiler import Compiler
from datetime import date
import pandas as pd
from language_utils import import_class


compiler = Compiler()


Indicator = import_class('utils', 'Indicator')
Function = import_class('utils', 'function', 'Function')


def __fun(code, df):
    exec(compile(code, '', mode='exec'))
    return df


def execute(source_code, stock_type: StockType, from_date: date):
    compile_result = compiler.compile(source_code)
    sql = "select * from data_candleday where date >= '2021-01-01';"
    rows = query(sql)

    total_df = pd.DataFrame(rows)
    print('\n'.join(map(lambda x: x.code, compile_result)))

    for result in compile_result:
        # TODO: is_rank 값 잘 들어가는지 계속 확인하고, 검증할것
        if result.is_rank:
            y = total_df.groupby('date').apply(lambda df: __fun(result.code, df)).reset_index(drop=True)
        else:
            y = total_df.groupby('ticker_id').apply(lambda df: __fun(result.code, df)).reset_index(drop=True)

        different_columns = total_df.columns.symmetric_difference(y.columns)
        for column in different_columns:
            total_df.insert(0, column, y[column])

    return total_df[Compiler.RESULT_COLUMN]


if __name__ == '__main__':
    execute(
        """
        rank(rank(sma(close, 3))) < 0.5
        """,
        0,
        date(2020, 12, 1)
    )
