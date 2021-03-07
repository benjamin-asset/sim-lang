from language.execute.calculating_unit import CalculateUnit
import datetime
import pandas as pd
from utils.parameter import Market
import logging


TAG = '[Calculator]'


class Calculator:

    def calculate(self, source_code: str, priority_code: str, buying_price_code: str, selling_price_code: str,
                  market: Market, from_date: datetime.date, to_date: datetime.date):
        logging.debug(f'{TAG} Start calculate start_date = {from_date}, end_date = {to_date}')
        diff_date = to_date - from_date
        # TODO: 계산식이 복잡하면 term 을 더 작게하여 잘게 쪼갤 수 있는 기능 구현하기
        term = 500
        offset = 30

        origin_from_date = from_date
        result_list = list()
        extra = 0
        if diff_date.days % term > 0 or diff_date.days == 0:
            extra = 1
        for i in range(int(diff_date.days / term) + extra):
            local_to_date = from_date + datetime.timedelta(days=term - 1)
            if to_date < local_to_date:
                print('local_to_date is greater than to_date')
                local_to_date = to_date

            # 앞뒤로 여유 일수를 붙여줌
            effective_from_date = from_date - datetime.timedelta(days=offset)
            effective_to_date = local_to_date + datetime.timedelta(days=offset)
            unit = CalculateUnit()
            result = unit.calculate(source_code, priority_code, buying_price_code, selling_price_code,
                                          market, effective_from_date, effective_to_date)
            if result is not None:
                result_list.append(result)
            from_date = local_to_date + datetime.timedelta(days=1)

        if len(result_list) == 1:
            combined_result = result_list[0]
        else:
            combined_result = pd.concat(result_list).drop_duplicates(subset=['date', 'ticker_id']).reset_index(drop=True)
        return combined_result[(combined_result['date'] >= origin_from_date) & (combined_result['date'] <= to_date)]


if __name__ == '__main__':
    calculator = Calculator()
    calculator.calculate(
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
        datetime.date(2017, 1, 1),
        datetime.date(2017, 12, 31)
    )
