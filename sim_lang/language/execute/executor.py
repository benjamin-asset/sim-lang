import datetime
from utils.parameter import Market
from language.execute.calculator import Calculator
import language.execute.simulator as simulator


def execute(
    source_code: str,
    priority_code: str,
    buying_price_code: str,
    selling_price_code: str,
    market: Market,
    from_date: datetime.date,
    to_date: datetime.date,
    max_holding_stock_quantity: int,
    cash: int,
    min_amount_per_stock=0,
):
    calculator = Calculator()
    calculation_result = calculator.calculate(
        source_code, priority_code, buying_price_code, selling_price_code, market, from_date, to_date
    )

    return simulator.simulate(calculation_result, market, max_holding_stock_quantity, cash, min_amount_per_stock)


if __name__ == "__main__":
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
        2000000,
    )
    for r in result:
        print(r)


def test(event, context):
    print(event)
    print(context)
