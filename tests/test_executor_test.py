from language.compiler import Compiler
from language.language_utils import import_module
from language import executor_manager

import datetime
from utils.parameter import Market

Indicator = import_module('utils', 'indicator')
Function = import_module('utils', 'function')

compiler = Compiler()


def test_simplest_code():
    '''
    Period: 2017/1/1~2019/12/31
    Buy condition:
        ts_delay(increase_from_lowest_price(low, close, 3), 1) >= 0.125 and ts_delay(increase_from_lowest_price(low, close, 3), 2) >= 0.125 and decrease_from_highest_price(high, close, 3) < 0 and ibs(high, low, close) <= 0.25 and sma(close, 20) > ts_delay(sma(close, 20), 1) and sma(close, 10) > ts_delay(sma(close, 10), 1) and rank(sma(tr_val, 5)) > 0.8
    Priority:
        ts_delay(increase_from_lowest_price(low, close, 3), 1) + ts_delay(increase_from_lowest_price(low, close, 3), 2)
    '''
    from tests.test_code.basic import run

    result = executor_manager.execute(
        # ts_delay(increase_from_lowest_price(low, close, 3), 1) >= 0.125 and ts_delay(increase_from_lowest_price(low, close, 3), 2) >= 0.125 and decrease_from_highest_price(high, close, 3) < 0 and ibs(high, low, close) <= 0.25 and sma(close, 20) > ts_delay(sma(close, 20), 1) and sma(close, 10) > ts_delay(sma(close, 10), 1) and rank(sma(tr_val, 5)) > 0.8
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) >= 0.125 and ts_delay(increase_from_lowest_price(low, close, 3), 2) >= 0.125
        """,
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) + ts_delay(increase_from_lowest_price(low, close, 3), 2)
        """,
        """
        ts_delay(close, 1) * 0.98
        """,
        """
        ts_delay(close, 1) * 1.02
        """,
        Market.kospi,
        datetime.date(2017, 1, 1),
        datetime.date(2017, 2, 1),
        4,
        2000000
    )

    result = to_test_format(result)
    test_result = to_test_format(run())
    assert result == test_result


def to_test_format(df):
    result = df.loc[df['#result']]
    sorted_result = result.sort_values(by=['date', '#priority', 'open', 'close'])
    subset = sorted_result[['date', 'ticker_id', '#priority']]
    return subset
