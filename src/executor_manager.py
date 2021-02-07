from connection_manager import query
from executor import execute_term
from stock_type import StockType
from datetime import date, timedelta
import pandas as pd
from language_utils import import_class


Indicator = import_class('utils', 'Indicator')
Function = import_class('utils', 'function', 'Function')


def __fun(code, df):
    exec(compile(code, '', mode='exec'))
    return df


def execute(source_code, stock_type: StockType, from_date: date):
    diff_date = date.today() - from_date
    # TODO: 계산식이 복잡하면 term 을 더 작게하여 잘게 쪼갤 수 있는 기능 구현하기
    term = 30

    origin_from_date = from_date
    result_list = list()
    extra = 0
    if diff_date.days % term > 0 or diff_date.days == 0:
        extra = 1
    for i in range(int(diff_date.days / term) + extra):
        to_date = from_date + timedelta(days=term - 1)

        # 앞뒤로 여유 일수를 붙여줌
        effective_from_date = from_date - timedelta(days=30)
        effective_to_date = to_date + timedelta(days=30)
        result = execute_term(source_code, stock_type, effective_from_date, effective_to_date)
        result_list.append(result)
        from_date = to_date + timedelta(days=1)

    if len(result_list) == 1:
        combined_result = result_list[0]
    else:
        combined_result = pd.concat(result_list).drop_duplicates(subset=['date', 'ticker_id']).reset_index(drop=True)
    return combined_result[combined_result['date'] >= origin_from_date]


if __name__ == '__main__':
    execute(
        """
        rank(rank(sma(close, 3))) < 0.5
        """,
        0,
        date(2021, 1, 1)
    )
