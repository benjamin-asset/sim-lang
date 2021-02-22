from language.compiler import Compiler
from language.language_utils import import_module

from language import executor_manager
from language.enum.stock_type import StockType
from datetime import date

Indicator = import_module('utils', 'indicator')
Function = import_module('utils', 'function')

compiler = Compiler()


def test_simplest_code():
    # Period: 2017/1/1~2019/12/31
    result = executor_manager.execute(
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) >= 0.125 and ts_delay(increase_from_lowest_price(low, close, 3), 2) >= 0.125 and decrease_from_highest_price(high, close, 3) < 0 and ibs(high, low, close) <= 0.25 and sma(close, 20) > ts_delay(sma(close, 20), 1) and sma(close, 10) > ts_delay(sma(close, 10), 1) and rank(sma(tr_val, 5)) > 0.8
        """,
        StockType.ALL,
        date(2017, 1, 1),
        date(2019, 12, 31)
    )
    print(result)
    assert True
