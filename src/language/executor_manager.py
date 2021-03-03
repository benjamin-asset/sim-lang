from language.executor import execute_term
import time
import logging
import copy
import datetime
import pandas as pd
from language.language_utils import import_module
from language.constant import RESULT_COLUMN, PRIORITY_COLUMN, BUY_PRICE_COLUMN, SELL_PRICE_COLUMN
from utils.tools import get_bid_price, get_ask_price
from utils.parameter import Market

indicator = import_module('utils', 'indicator')
function = import_module('utils', 'function')
language = import_module('language', 'language_definition')


class Item:
    def __init__(self, ticker_id: str, buy_price: int, sell_price: int, quantity: int, current_price: int):
        self.ticker_id = ticker_id
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.quantity = quantity
        self.current_price = current_price

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False

        return self.ticker_id == other.ticker_id and \
               self.buy_price == other.buy_price and \
               self.sell_price and other.sell_price and \
               self.quantity and other.quantity

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class Stock:
    def __init__(self, ticker_id: str, price: int, quantity: int):
        self.ticker_id = ticker_id
        self.price = price
        self.quantity = quantity

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False

        return self.ticker_id == other.ticker_id and \
               self.price == other.price and \
               self.quantity and other.quantity

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class ResultItem:
    def __init__(self, date: datetime.date, cash: int, holding_stock_list: list, buying_stock_list: list,
                 selling_stock_list: list):
        self.date = date
        self.cash = cash
        self.holding_stock_list = holding_stock_list
        self.buying_stock_list = buying_stock_list
        self.selling_stock_list = selling_stock_list

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.__dict__)


def __fun(code, df):
    exec(compile(code, '', mode='exec'))
    return df


def execute(source_code: str, priority_code: str, buying_price_code: str, selling_price_code: str,
            market: Market, from_date: datetime.date, to_date: datetime.date,
            max_holding_stock_quantity: int, cash: int, min_stock_amount=0):
    diff_date = to_date - from_date
    # TODO: 계산식이 복잡하면 term 을 더 작게하여 잘게 쪼갤 수 있는 기능 구현하기
    term = 365
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
        result = execute_term(source_code, priority_code, buying_price_code, selling_price_code,
                              market, effective_from_date, effective_to_date)
        if result is not None:
            result_list.append(result)
        from_date = local_to_date + datetime.timedelta(days=1)

    if len(result_list) == 1:
        combined_result = result_list[0]
    else:
        combined_result = pd.concat(result_list).drop_duplicates(subset=['date', 'ticker_id']).reset_index(drop=True)
    execution_result = combined_result[combined_result['date'] >= origin_from_date]

    buying_candidate_list = execution_result.loc[execution_result[RESULT_COLUMN]]
    date_grouped_buying_candidate_list = buying_candidate_list.groupby(['date'])
    date_grouped_execution_result = execution_result.groupby(['date'])

    buy_request_list = []
    sell_request_list = []
    holding_stock_list = []
    final_result = []

    for today, today_data in date_grouped_execution_result:
        buying_stock_list = []
        selling_stock_list = []

        if len(buy_request_list) > 0:
            # 매수 시도
            for item in buy_request_list:
                target = today_data.loc[(today_data['ticker_id'] == item.ticker_id)]
                if len(target) == 0:
                    continue

                if len(holding_stock_list) >= max_holding_stock_quantity:
                    break

                # 매수 성공
                if target['low'].values[0] < item.buy_price:
                    cash -= item.buy_price * item.quantity
                    buying_stock_list.append(Stock(item.ticker_id, item.buy_price, item.quantity))
                    holding_stock_list.append(item)

            buy_request_list.clear()

        if len(sell_request_list) > 0:
            # 매도 시도
            for item in sell_request_list:
                target = today_data.loc[(today_data['ticker_id'] == item.ticker_id)]
                if len(target) == 0:
                    continue

                # 매도 성공
                if target['high'].values[0] > item.sell_price:
                    cash += item.sell_price * item.quantity
                    selling_stock_list.append(Stock(item.ticker_id, item.sell_price, item.quantity))
                    holding_stock_list.remove(item)

            sell_request_list.clear()

        # 추가 매수 할 수 있음
        if len(holding_stock_list) < max_holding_stock_quantity and cash >= min_stock_amount:
            group = date_grouped_buying_candidate_list.get_group(today)
            sorted_group = group.sort_values(by=[PRIORITY_COLUMN])

            count = len(holding_stock_list)
            available_cash = cash / (max_holding_stock_quantity - count)
            while available_cash < min_stock_amount:
                count += 1
                available_cash = cash / (max_holding_stock_quantity - count)

            for el in sorted_group.iterrows():
                buy_price = get_bid_price(el[1][BUY_PRICE_COLUMN], market)

                quantity = int(available_cash // buy_price)
                item = Item(
                    el[1]['ticker_id'],
                    buy_price,
                    get_ask_price(el[1][SELL_PRICE_COLUMN], market),
                    quantity,
                    el[1]['close'] # 현재가를 종가로 기준잡음
                )
                if item in buy_request_list or item in holding_stock_list:
                    continue

                buy_request_list.append(item)

        # 매도할(보유한) 주식이 있음
        if len(holding_stock_list) > 0:
            for item in holding_stock_list:
                target = today_data.loc[(today_data['ticker_id'] == item.ticker_id)]
                # TODO: 이런거 상폐 당한건가?
                if len(target) == 0:
                    continue

                # 현재가 조정
                item.current_price = target['close'].values[0]

                if target[SELL_PRICE_COLUMN].values[0] > item.sell_price:
                    sell_request_list.append(item)

        today_result = ResultItem(
            today,
            cash,
            copy.deepcopy(holding_stock_list),
            buying_stock_list,
            selling_stock_list
        )
        final_result.append(today_result)

    # date_grouped_buying_candidate_list 에서 매수 시

    # 날짜별로 돌면서 매수/매도
    # buying_candidate_list 는 날짜별 매수 가능 후보군
    # 우선순위가 높은 애들을 max_holding_quantity 한도 내에서 (buying_price_code) 가격에 매수 신청 - 시뮬레이팅에서는 무조건 매수 되었다고 가정함
    # 매도는 execution_result 를 돌면서 (selling_price_code) 가격에 매도 신청

    return final_result


if __name__ == '__main__':
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
        print(r)


def test(event, context):
    print(event)
    print(context)
