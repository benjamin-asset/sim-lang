import sys
import datetime

from language.execute.executor import execute
from utils.parameter import Market

def handler(event, context):
    result = execute(
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
    for r in result:
        return r
    return 'Hello from AWS Lambda using Python' + sys.version + '!'
