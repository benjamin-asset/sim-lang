from language.executor import execute_term
from language.enum.stock_type import StockType
from datetime import date, timedelta
import pandas as pd
from language.language_utils import import_module

# indicator = import_module('utils', 'indicator')
# function = import_module('utils', 'function')
indicator = import_module('utils', 'indicator')
function = import_module('utils', 'function')
language = import_module('language_definition')


def __fun(code, df):
    exec(compile(code, '', mode='exec'))
    return df


def execute(source_code, stock_type: StockType, from_date: date, to_date: date):
    diff_date = to_date - from_date
    # TODO: 계산식이 복잡하면 term 을 더 작게하여 잘게 쪼갤 수 있는 기능 구현하기
    term = 365
    offset = 30

    origin_from_date = from_date
    result_list = list()
    extra = 0
    if diff_date.days % term > 0 or diff_date.days == 0:
        extra = 1
    for i in range(int(diff_date.days / term) + extra):
        local_to_date = from_date + timedelta(days=term - 1)
        if to_date < local_to_date:
            print('local_to_date is greater than to_date')
            local_to_date = to_date

        # 앞뒤로 여유 일수를 붙여줌
        effective_from_date = from_date - timedelta(days=offset)
        effective_to_date = local_to_date + timedelta(days=offset)
        result = execute_term(source_code, stock_type, effective_from_date, effective_to_date)
        if result is not None:
            result_list.append(result)
        from_date = local_to_date + timedelta(days=1)

    if len(result_list) == 1:
        combined_result = result_list[0]
    else:
        combined_result = pd.concat(result_list).drop_duplicates(subset=['date', 'ticker_id']).reset_index(drop=True)
    execution_result = combined_result[combined_result['date'] >= origin_from_date]
    return execution_result


if __name__ == '__main__':
    result = execute(
        # ts_delay(increase_from_lowest_price(low, close, 3), 1) >= 0.125 and ts_delay(increase_from_lowest_price(low, close, 3), 2) >= 0.125 and decrease_from_highest_price(high, close, 3) < 0 and ibs(high, low, close) <= 0.25 and sma(close, 20) > ts_delay(sma(close, 20), 1) and sma(close, 10) > ts_delay(sma(close, 10), 1) and rank(sma(tr_val, 5)) > 0.8
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) >= 0.125 and ts_delay(increase_from_lowest_price(low, close, 3), 2) >= 0.125
        """,
        StockType.ALL,
        date(2017, 1, 1),
        date(2019, 12, 31)
    )
    print(result)
