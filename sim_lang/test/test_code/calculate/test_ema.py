from datetime import datetime, date
import pandas as pd
from pandas import DataFrame
from utils.executor import Executor
from utils.reader import Reader
from utils.indicator import sma, ema, pivot_standard, pdi, stochastic_fast_k
from utils.function import rank, increase_from_lowest_price, decrease_from_highest_price, pct_change, ts_max
from utils.parameter import Universe, MovingAverage


def add_data_to_day_price(day_price: DataFrame, index_day_price: DataFrame) -> DataFrame:
    group_list = []
    grouped = day_price.groupby("ticker_id")
    for key, group in grouped:
        group = group.reset_index(drop=True)
        group["sma_10"] = sma(group["close"], 10)
        group["increase_ratio_3"] = increase_from_lowest_price(group["low"], group["close"], 3)
        group["ema"] = ema(group["close"], 5)
        group_list.append(group)

    day_price = pd.concat(group_list, axis=0)
    day_price = day_price.reset_index(drop=True)
    group_list = []
    grouped = day_price.groupby("ticker_id")
    for key, group in grouped:
        increase_condition = group["ema"] >= 0.1
        # Result
        group["#result"] = increase_condition
        group["#priority"] = group["increase_ratio_3"].shift(1) + group["increase_ratio_3"].shift(2)
        group_list.append(group)
    day_price = pd.concat(group_list, axis=0)
    day_price = day_price.reset_index(drop=True)
    # Market Timing
    index_day_price["sma_3"] = sma(index_day_price["close"], 3)
    index_day_price["sma_5"] = sma(index_day_price["close"], 5)
    index_day_price["sma_10"] = sma(index_day_price["close"], 10)
    index_day_price["#market_timing"] = (
        (index_day_price["close"] > index_day_price["sma_3"])
        | (index_day_price["close"] > index_day_price["sma_5"])
        | (index_day_price["close"] > index_day_price["sma_10"])
    )
    index_day_price = index_day_price.set_index("date")
    return day_price, index_day_price


def back_test(generator, start_date, end_date):
    # 0. 변수
    max_basket_size = 10
    liquidation_holding_days = 1
    cut_period = 0
    seed_money = 1000000000
    fee = 0.00015  # when using kiwoom
    basket = {}  # key:ticker, value:buy_price, stock_num, holding_days
    pnl = {"date": [start_date], "balance": [seed_money]}
    # 1. 거래일 가져오기
    trading_days_list = generator.get_trading_day_list(start_date, end_date)
    # 2. 일봉 가져오기ㄱ
    day_price = generator.get_day_price_data(Universe.total, True, False, start_date, end_date)
    index_day_price = generator.get_index_day_price_data(Universe.kosdaq, start_date, end_date)
    # 3. 매수 조건 및 우선순위 생성
    day_price, index_day_price = add_data_to_day_price(day_price, index_day_price)
    return day_price


def run(from_date: datetime.date, to_date: datetime.date):
    executor = Executor("")
    reader = Reader(executor)
    return back_test(reader, from_date, to_date)
