from language.language_utils import import_module
from language.execute.calculator import Calculator

import datetime
import time
from utils.parameter import Market
import math


Indicator = import_module('utils', 'indicator')
Function = import_module('utils', 'function')


from_date = datetime.date(2017, 1, 1)
to_date = datetime.date(2017, 12, 31)


def test_basic():
    from test.test_code.calculate.basic import run
    expected, actual = get_result(
        """
        (ts_delay(increase_from_lowest_price(low, close, 3), 1) >= 0.1 or ts_delay(increase_from_lowest_price(low, close, 3), 2) >= 0.1) and decrease_from_highest_price(high, close, 3) < 0 and decrease_from_highest_price(high, close, 3) > -0.1 and ibs(high, low, close) < 0.25 and rank(sma(tr_val, 5)) > 0.8
        """,
        """
        increase_from_lowest_price(low, close, 3)
        """,
        run,
        from_date,
        to_date
    )
    assert check(expected, actual, from_date, to_date)


def test_1():
    from test.test_code.calculate.test1 import run
    expected, actual = get_result(
        """
        (ts_delay(pct_change(stochastic_fast_k(pdi(high, low, close, 5, ema), pdi(high, low, close, 5, ema), pdi(high, low, close, 5, ema), 20), 3), 1) >= 0.1 or ts_delay(pct_change(stochastic_fast_k(pdi(high, low, close, 5, ema), pdi(high, low, close, 5, ema), pdi(high, low, close, 5, ema), 20), 3), 2) >= 0.1) and (open > close or pct_change(close, 1) < 0) and ibs(high, low, close) < 0.25 and rank(sma(tr_val, 5)) > 0.8
        """,
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) + ts_delay(increase_from_lowest_price(low, close, 3), 2)
        """,
        run,
        from_date,
        to_date
    )
    assert check(expected, actual, from_date, to_date)


def test_2():
    from test.test_code.calculate.test2 import run
    expected, actual = get_result(
        """
        rank(sma(tr_val, 5)) > 0.8
        """,
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) + ts_delay(increase_from_lowest_price(low, close, 3), 2)
        """,
        run,
        from_date,
        to_date
    )
    assert check(expected, actual, from_date, to_date)


def test_3():
    from test.test_code.calculate.test3 import run
    expected, actual = get_result(
        """
        (open > close or pct_change(close, 1) < 0) and ibs(high, low, close) < 0.25
        """,
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) + ts_delay(increase_from_lowest_price(low, close, 3), 2)
        """,
        run,
        from_date,
        to_date
    )
    assert check(expected, actual, from_date, to_date)


def test_4():
    from test.test_code.calculate.test4 import run
    expected, actual = get_result(
        """
        (ts_delay(pct_change(stochastic_fast_k(pdi(high, low, close, 5, ema), pdi(high, low, close, 5, ema), pdi(high, low, close, 5, ema), 20), 3), 1) >= 0.1 or ts_delay(pct_change(stochastic_fast_k(pdi(high, low, close, 5, ema), pdi(high, low, close, 5, ema), pdi(high, low, close, 5, ema), 20), 3), 2) >= 0.1)
        """,
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) + ts_delay(increase_from_lowest_price(low, close, 3), 2)
        """,
        run,
        from_date,
        to_date
    )
    assert check(expected, actual, from_date, to_date)


def test_5():
    from test.test_code.calculate.test5 import run

    expected, actual = get_result(
        """
        pct_change(stochastic_fast_k(pdi(high, low, close, 5, ema), pdi(high, low, close, 5, ema), pdi(high, low, close, 5, ema), 20), 3) >= 0.1
        """,
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) + ts_delay(increase_from_lowest_price(low, close, 3), 2)
        """,
        run,
        from_date,
        to_date
    )
    assert check(expected, actual, from_date, to_date)


def test_6():
    from test.test_code.calculate.test6 import run

    expected, actual = get_result(
        """
        stochastic_fast_k(pdi(high, low, close, 5, ema), pdi(high, low, close, 5, ema), pdi(high, low, close, 5, ema), 20) >= 0.1
        """,
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) + ts_delay(increase_from_lowest_price(low, close, 3), 2)
        """,
        run,
        from_date,
        to_date
    )
    assert check(expected, actual, from_date, to_date)


def test_7():
    from test.test_code.calculate.test7 import run
    expected, actual = get_result(
        """
        pdi(high, low, close, 5, ema) >= 0.1
        """,
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) + ts_delay(increase_from_lowest_price(low, close, 3), 2)
        """,
        run,
        from_date,
        to_date
    )
    assert check(expected, actual, from_date, to_date)


def test_ema():
    from test.test_code.calculate.test_ema import run

    expected, actual = get_result(
        """
        ema(close, 5) >= 0.1
        """,
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) + ts_delay(increase_from_lowest_price(low, close, 3), 2)
        """,
        run,
        from_date,
        to_date
    )
    assert check(expected, actual, from_date, to_date)


def test_sma():
    from test.test_code.calculate.test_sma import run
    expected, actual = get_result(
        """
        sma(close, 5) >= 0.1
        """,
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) + ts_delay(increase_from_lowest_price(low, close, 3), 2)
        """,
        run,
        from_date,
        to_date
    )
    assert check(expected, actual, from_date, to_date)


def test_ewma():
    from test.test_code.calculate.test_ewma import run
    expected, actual = get_result(
        """
        ewma(close, 5) >= 0.1
        """,
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) + ts_delay(increase_from_lowest_price(low, close, 3), 2)
        """,
        run,
        from_date,
        to_date
    )
    assert check(expected, actual, from_date, to_date)


def test_count():
    from test.test_code.calculate.test_count import run

    expected, actual = get_result(
        """
        close >= 0
        """,
        """
        ts_delay(increase_from_lowest_price(low, close, 3), 1) + ts_delay(increase_from_lowest_price(low, close, 3), 2)
        """,
        run,
        from_date,
        to_date
    )
    assert check(expected, actual, from_date, to_date)


def get_result(source_code, priority_code, actual_function, start_date, end_date):
    calculator = Calculator(False)
    expected = calculator.calculate(
        source_code,
        priority_code,
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
    actual = actual_function(start_date - datetime.timedelta(days=30), end_date + datetime.timedelta(days=30))
    return expected, actual


def check(expected, actual, from_date, to_date):
    expected = to_test_format(expected, from_date, to_date)
    actual = to_test_format(actual, from_date, to_date)

    # expected.to_csv("/Users/dongkyoo/Desktop/expected.csv")
    # actual.to_csv("/Users/dongkyoo/Desktop/actual.csv")

    expected = expected.to_dict()
    actual = actual.to_dict()
    print("expected size = {}".format(len(expected['date'])))
    print("actual size = {}".format(len(actual['date'])))

    if len(expected['date']) != len(actual['date']):
        return False

    eq_date = expected['date'] == actual['date']
    eq_ticker = expected['ticker_id'] == actual['ticker_id']
    count = 0

    for i in range(len(expected['#priority'])):
        e = expected['#priority'][i]
        a = actual['#priority'][i]
        if math.isnan(e) and math.isnan(a):
            continue

        if e != a:
            print('expected', expected['date'][i], expected['ticker_id'][i], expected['#priority'][i])
            print('actual', actual['date'][i], actual['ticker_id'][i], actual['#priority'][i])
            count += 1

    eq_priority = count == 0
    print(f'eq_date = {eq_date}')
    print(f'eq_ticker = {eq_ticker}')
    print(f'eq_priority = {eq_priority}')
    return eq_date and eq_ticker and eq_priority


def to_test_format(df, from_date: datetime.date, to_date: datetime.date):
    result = df.loc[df['#result']]
    sorted_result = result.sort_values(by=['date', 'ticker_id', '#priority'])
    subset = sorted_result[(sorted_result['date'] >= from_date) & (sorted_result['date'] <= to_date)]
    subset = subset[['date', 'ticker_id', '#priority']]
    return subset.reset_index(drop=True)


def diff(df1, df2):
    comparison_df = df1.merge(
        df2,
        indicator=True,
        how='outer'
    )
    return comparison_df[comparison_df['_merge'] != 'both']

if __name__ == '__main__':
    test_basic()
