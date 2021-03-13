import pandas as pd
import time
import logging

from dotenv import load_dotenv
from language.language_utils import import_module
from rdb.connection_manager import query, Isolation
from datetime import date
from language.compiler import Compiler
from rdb import sql_builder

from utils.parameter import Market

load_dotenv()

indicator = import_module("utils", "indicator")
function = import_module("utils", "function")
language = import_module("language", "language_definition")


def __calculate(code, df):
    exec(compile(code, "", mode="exec"))
    return df


def calculate(
    source_code: str,
    priority_code: str,
    buy_price_code: str,
    sell_price_code: str,
    market: Market,
    from_date: date,
    to_date: date,
):
    compiler = Compiler()
    compile_result = compiler.compile(source_code, priority_code, buy_price_code, sell_price_code)

    sql = sql_builder.build(compile_result.fields, from_date, to_date)
    rows = query(sql, Isolation.READ_COMMITTED)

    if len(rows) == 0:
        return None

    now = time.time()
    total_df = pd.DataFrame(rows)

    for item in compile_result.item_list:
        # TODO: is_rank 값 잘 들어가는지 계속 확인하고, 검증할것
        # 랭크 함수는 날짜 단위로 동작
        if item.is_rank:
            y = total_df.groupby("date", as_index=False).apply(lambda df: __calculate(item.code, df))
        else:  # 랭크 함수 이외의 함수는 종목 단위로 동작
            y = total_df.groupby("ticker_id", as_index=False).apply(lambda df: __calculate(item.code, df))

        different_columns = total_df.columns.symmetric_difference(y.columns)
        for column in different_columns:
            total_df.insert(0, column, y[column])

    logging.debug("[Profile] execute time : {:0.3f}s".format(time.time() - now))
    return total_df
