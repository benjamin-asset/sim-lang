import copy
import datetime

from language.constant import RESULT_COLUMN, PRIORITY_COLUMN, BUY_PRICE_COLUMN, SELL_PRICE_COLUMN
from utils.tools import get_bid_price, get_ask_price
from utils.parameter import Market


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

        return (
            self.ticker_id == other.ticker_id
            and self.buy_price == other.buy_price
            and self.sell_price
            and other.sell_price
            and self.quantity
            and other.quantity
        )

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

        return self.ticker_id == other.ticker_id and self.price == other.price and self.quantity and other.quantity

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class ResultItem:
    def __init__(
        self,
        date: datetime.date,
        cash: int,
        holding_stock_list: list,
        buying_stock_list: list,
        selling_stock_list: list,
    ):
        self.date = date
        self.cash = cash
        self.holding_stock_list = holding_stock_list
        self.buying_stock_list = buying_stock_list
        self.selling_stock_list = selling_stock_list

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.__dict__)


def simulate(calculation_result, market: Market, max_holding_stock_quantity: int, cash: int, min_amount_per_stock):
    """
    날짜단위로 돌며 매수/매도 시뮬레이션을 하는 함수
    :param calculation_result: 시뮬레이팅 데이터
    :param market: 장 (kospi, kosdaq)
    :param max_holding_stock_quantity: 최대 보유 가능한 종목 수
    :param cash: 보유 현금
    :param min_amount_per_stock: 종목 당 최소 구매 금액
    :return: 날짜별 매수/매도 리스트
    """
    # 매수 가능 종목+일자만 추출
    buying_candidate_list = calculation_result.loc[calculation_result[RESULT_COLUMN]]
    date_grouped_buying_candidate_list = buying_candidate_list.groupby(["date"])

    date_grouped_calculation_result = calculation_result.groupby(["date"])

    # 매수 요청 리스트 : 반드시 매수된다는 보장은 없기 때문임
    buy_request_list = []

    # 매도 요청 리스트 : 반드시 매도된다는 보장은 없기 때문임
    sell_request_list = []

    # 보유 종목 리스트
    holding_stock_list = []

    # 최종 결과
    final_result = []

    for today, today_data in date_grouped_calculation_result:
        # 오늘 매수한 주식 리스트
        buying_stock_list = []

        # 오늘 매도한 주식 리스트
        selling_stock_list = []

        if len(buy_request_list) > 0:
            # 매수 시도
            for item in buy_request_list:
                target = today_data.loc[(today_data["ticker_id"] == item.ticker_id)]

                # TODO: 상폐?
                if len(target) == 0:
                    continue

                # 보유 최대 종목 수를 초과할 경우
                if len(holding_stock_list) >= max_holding_stock_quantity:
                    break

                # 매수가보다 저가가 낮으므로 매수 성공
                if target["low"].values[0] < item.buy_price:
                    cash -= item.buy_price * item.quantity
                    buying_stock_list.append(Stock(item.ticker_id, item.buy_price, item.quantity))
                    holding_stock_list.append(item)

            buy_request_list.clear()

        if len(sell_request_list) > 0:
            # 매도 시도
            for item in sell_request_list:
                target = today_data.loc[(today_data["ticker_id"] == item.ticker_id)]

                # TODO: 상폐?
                if len(target) == 0:
                    continue

                # 매도 성공
                if target["high"].values[0] > item.sell_price:
                    cash += item.sell_price * item.quantity
                    selling_stock_list.append(Stock(item.ticker_id, item.sell_price, item.quantity))
                    holding_stock_list.remove(item)

            sell_request_list.clear()

        # 추가 매수 할 수 있음
        if len(holding_stock_list) < max_holding_stock_quantity and cash >= min_amount_per_stock:
            candidate_group = date_grouped_buying_candidate_list.get_group(today)
            sorted_group = candidate_group.sort_values(by=[PRIORITY_COLUMN])

            # 주식 당 매수 최소 금액을 넘기면서도 최대한 많은 종목을 살 수 있도록 종목 당 매수 금액을 조정
            count = max_holding_stock_quantity - len(holding_stock_list)
            available_cash = cash // count
            while available_cash < min_amount_per_stock:
                count -= 1
                available_cash = cash // count

            # 매수 시도 리스트에 종목 담기
            for el in sorted_group.iterrows():
                buy_price = get_bid_price(el[1][BUY_PRICE_COLUMN], market)

                quantity = int(available_cash // buy_price)
                item = Item(
                    el[1]["ticker_id"],
                    buy_price,
                    get_ask_price(el[1][SELL_PRICE_COLUMN], market),
                    quantity,
                    el[1]["close"],  # 현재가를 종가로 기준잡음
                )

                # 이미 담겨있는 종목이거나, 이미 구매한 종목이라면 제외
                if item in buy_request_list or item in holding_stock_list:
                    continue

                buy_request_list.append(item)

                count -= 1
                if count == 0:
                    break

        # 매도할(보유한) 주식이 있음
        if len(holding_stock_list) > 0:
            for item in holding_stock_list:
                target = today_data.loc[(today_data["ticker_id"] == item.ticker_id)]
                # TODO: 이런거 상폐 당한건가?
                if len(target) == 0:
                    continue

                # 현재가 조정
                item.current_price = target["close"].values[0]

                if target[SELL_PRICE_COLUMN].values[0] > item.sell_price:
                    sell_request_list.append(item)

        today_result = ResultItem(
            today, cash, copy.deepcopy(holding_stock_list), buying_stock_list, selling_stock_list
        )
        final_result.append(today_result)

    return final_result
