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

    test_result = run(from_date, to_date)
    assert check(result, test_result, from_date, to_date)


def check(lhs, rhs, from_date, to_date):
    lhs = to_test_format(lhs, from_date, to_date)
    rhs = to_test_format(rhs, from_date, to_date)

    lhs = lhs.to_dict()
    rhs = rhs.to_dict()
    return lhs == rhs


def to_test_format(df, from_date: datetime.date, to_date: datetime.date):
    result = df.loc[df['#result']]
    sorted_result = result.sort_values(by=['date', '#priority', 'open', 'close'])
    subset = sorted_result[['date', 'ticker_id', '#priority']]
    subset = subset[(subset['date'] >= from_date) & (subset['date'] <= to_date)]
    return subset.reset_index(drop=True)


if __name__ == '__main__':
    test_basic()
