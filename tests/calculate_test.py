from language.compiler import Compiler
from language.language_utils import import_module
import language.execute.calculator as calculator

import datetime
from utils.parameter import Market

Indicator = import_module("utils", "indicator")
Function = import_module("utils", "function")

compiler = Compiler()


def test_simplest_code():
    from tests.test_code.basic import run

    from_date = datetime.date(2017, 1, 1)
    to_date = datetime.date(2017, 12, 31)

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
        to_date,
    )

    result = to_test_format(result, from_date, to_date)
    test_result = to_test_format(run(), from_date, to_date)
    print(f"result = {result}")
    print(f"test_result = {test_result}")
    assert result == test_result


def to_test_format(df, from_date: datetime.date, to_date: datetime.date):
    result = df.loc[df["#result"]]
    sorted_result = result.sort_values(by=["date", "#priority", "open", "close"])
    subset = sorted_result[["date", "ticker_id", "#priority"]]
    subset = subset[(subset["date"] >= from_date) & (subset["date"] <= to_date)]
    return subset
