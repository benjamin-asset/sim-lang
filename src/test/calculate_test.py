from language.language_utils import import_module
import language.execute.calculator as calculator

import datetime
import time
from utils.parameter import Market

Indicator = import_module('utils', 'indicator')
Function = import_module('utils', 'function')


def test_basic():
    from test.test_code.calculate.basic import run

    from_date = datetime.date(2017, 1, 1)
    to_date = datetime.date(2017, 12, 31)

    now = time.time()
    result = calculator.calculate(
        """
        (ts_delay(increase_from_lowest_price(low, close, 3), 1) >= 0.1 or ts_delay(increase_from_lowest_price(low, close, 3), 2) >= 0.1) and decrease_from_highest_price(high, close, 3) < 0 and decrease_from_highest_price(high, close, 3) > -0.1 and ibs(high, low, close) < 0.25 and rank(sma(tr_val, 5)) > 0.8
        """,
        """
        increase_from_lowest_price(low, close, 3)
        """,
        """
        ts_delay(close, 1) * 0.98
        """,
        """
        ts_delay(close, 1) * 1.02
        """,
        Market.kospi,
        from_date,
        to_date
    )

    print('result time : {:.3f}s'.format(time.time() - now))
    result = to_test_format(result, from_date, to_date)

    now = time.time()
    test_result = run(from_date, to_date)
    test_result = to_test_format(test_result, from_date, to_date)
    print('test result time : {:.3f}s'.format(time.time() - now))

    result = result.to_dict()
    test_result = test_result.to_dict()
    assert result == test_result


def to_test_format(df, from_date: datetime.date, to_date: datetime.date):
    result = df.loc[df['#result']]
    sorted_result = result.sort_values(by=['date', '#priority', 'open', 'close'])
    subset = sorted_result[['date', 'ticker_id', '#priority']]
    subset = subset[(subset['date'] >= from_date) & (subset['date'] <= to_date)]
    return subset
