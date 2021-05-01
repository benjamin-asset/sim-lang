import datetime

from utils.parameter import Market

from sim_lang.language.execute.executor import execute
from sim_lang.language.language_utils import import_module

Indicator = import_module("utils", "indicator")
Function = import_module("utils", "function")

indicator = import_module("utils", "indicator")
function = import_module("utils", "function")
language = import_module("sim_lang", "language", "language_definition")


from_date = datetime.date(2020, 1, 1)
to_date = datetime.date(2021, 1, 1)


if __name__ == "__main__":
    result = execute(
        """
        sma(close, 5) >= 0.1
        """,
        """
        sma(close, 5) >= 0.1
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
        10,
        1000000,
    )
    for r in result:
        print(r.holding_stock_list)
        sum = 0
        for stock in r.holding_stock_list:
            sum += stock.quantity * stock.current_price
        print(sum)
