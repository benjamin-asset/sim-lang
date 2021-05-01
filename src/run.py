from language.language_utils import import_module
from language.execute.calculator import Calculator

import datetime
import time
from utils.parameter import Market
import math


Indicator = import_module('utils', 'indicator')
Function = import_module('utils', 'function')

indicator = import_module('utils', 'indicator')
function = import_module('utils', 'function')
language = import_module('language', 'language_definition')


from_date = datetime.date(2017, 1, 1)
to_date = datetime.date(2017, 2, 1)


if __name__ == '__main__':
    calculator = Calculator()
    result = calculator.calculate(
        """
        sma(close, 5) >= 0.1
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
        from_date,
        to_date
    )
    print(result)
