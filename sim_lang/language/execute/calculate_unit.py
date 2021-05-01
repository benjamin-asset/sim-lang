import pandas as pd
import time
import logging

from dotenv import load_dotenv
from language.language_utils import import_module
from datetime import date
from language.compiler import Compiler

from utils.executor import Executor
from utils.reader import Reader
from utils.parameter import Market, Universe, Field
from decimal import Decimal
import boto3

load_dotenv()

indicator = import_module("utils", "indicator")
function = import_module("utils", "function")
language = import_module("language", "language_definition")

# import utils.indicator as indicator
# import utils.function as function
# import language.language_definition as language_definition

TAG = "[CalculateUnit]"


class Result:
    def __init__(self, id: str, start_date: str, end_date: str, progress: float):
        self.id = id
        self.progress = progress
        self.start_date = start_date
        self.end_date = end_date

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


class CalculateUnit:
    def __init__(self, id: str, save_result=True):
        self.compiler = Compiler()
        self.progress = 0.0
        self.dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:8000")
        self.result_table = self.dynamodb.Table("calculate_unit_result")
        self.id = id
        self.save_result = save_result

    def _calculate(self, code, df):
        exec(compile(code, "", mode="exec"))
        return df

    def calculate(
        self,
        source_code: str,
        priority_code: str,
        buy_price_code: str,
        sell_price_code: str,
        market: Market,
        start_date: date,
        end_date: date,
    ):
        logging.debug(f"{TAG} Start calculate start_date = {start_date}, end_date = {end_date}")
        compile_result = self.compiler.compile(source_code, priority_code, buy_price_code, sell_price_code)

        executor = Executor("")
        reader = Reader(executor)
        field_list = list(compile_result.fields)
        required_field_list = [Field.open, Field.close, Field.is_active]
        for field in required_field_list:
            if field not in field_list:
                field_list.append(field)
        rows = reader.get_simulating_data(Universe.total, field_list, start_date, end_date)

        if len(rows) == 0:
            return None

        now = time.time()
        total_df = pd.DataFrame(rows)
        total_job_count = len(compile_result.item_list)
        completed_job_count = 0

        for item in compile_result.item_list:
            # TODO: is_rank 값 잘 들어가는지 계속 확인하고, 검증할것
            # 랭크 함수는 날짜 단위로 동작
            if item.is_rank:
                y = total_df.groupby("date", as_index=False).apply(lambda df: self._calculate(item.code, df))
            else:  # 랭크 함수 이외의 함수는 종목 단위로 동작
                y = total_df.groupby("ticker_id", as_index=False).apply(lambda df: self._calculate(item.code, df))

            different_columns = total_df.columns.symmetric_difference(y.columns)
            for column in different_columns:
                total_df.insert(0, column, y[column])
            completed_job_count += 1
            self.progress = Decimal(total_job_count / completed_job_count)

            if self.save_result:
                response = self.result_table.put_item(
                    Item=Result(self.id, str(start_date), str(end_date), self.progress).__dict__
                )

        logging.debug("{} execute time : {:0.3f}s".format(TAG, time.time() - now))
        return total_df
