import pandas as pd
import time
import logging

from dotenv import load_dotenv
from language.language_utils import import_module
from rdb.connection_manager import query, Isolation
from datetime import date
from language.compiler import Compiler
from rdb import sql_builder

from utils.executor import Executor
from utils.generator import Generator
from utils.parameter import Market

load_dotenv()

indicator = import_module('utils', 'indicator')
function = import_module('utils', 'function')
language = import_module('language', 'language_definition')

TAG = '[CalculateUnit]'


class CalculateUnit:
    def __init__(self):
        self.compiler = Compiler()

    def _calculate(self, code, df):
        exec(compile(code, '', mode='exec'))
        return df

    def calculate(self, source_code: str, priority_code: str, buy_price_code: str, sell_price_code: str,
                  market: Market, from_date: date, to_date: date):
        logging.debug(f'{TAG} Start calculate start_date = {from_date}, end_date = {to_date}')
        compile_result = self.compiler.compile(source_code, priority_code, buy_price_code, sell_price_code)

        sql = sql_builder.build(compile_result.fields, from_date, to_date)
        rows = query(sql, Isolation.READ_COMMITTED)

        # executor = Executor("")
        # generator = Generator(executor)

        if len(rows) == 0:
            return None

        now = time.time()
        total_df = pd.DataFrame(rows)

        for item in compile_result.item_list:
            # TODO: is_rank 값 잘 들어가는지 계속 확인하고, 검증할것
            # 랭크 함수는 날짜 단위로 동작
            if item.is_rank:
                y = total_df.groupby('date', as_index=False).apply(lambda df: self._calculate(item.code, df))
            else:   # 랭크 함수 이외의 함수는 종목 단위로 동작
                y = total_df.groupby('ticker_id', as_index=False).apply(lambda df: self._calculate(item.code, df))

            different_columns = total_df.columns.symmetric_difference(y.columns)
            for column in different_columns:
                total_df.insert(0, column, y[column])

        logging.debug('{} execute time : {:0.3f}s'.format(TAG, time.time() - now))
        return total_df
