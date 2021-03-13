from datetime import datetime, date
import pandas as pd
from pandas import DataFrame
from utils.executor import Executor
from utils.reader import Reader
from utils.indicator import sma, ibs, pivot_standard, pdi, stochastic_fast_k
from utils.function import rank, increase_from_lowest_price, decrease_from_highest_price, pct_change, \
    ts_max
from utils.parameter import Universe, MovingAverage
def add_data_to_day_price(day_price: DataFrame, index_day_price: DataFrame) -> DataFrame:
    group_list = []
    grouped = day_price.groupby('ticker')
    for key, group in grouped:
        group = group.reset_index(drop=True)
        group['sma_10'] = sma(group['close'], 10)
        group['sma_20'] = sma(group['close'], 20)
        group['sma_tr_val_5'] = sma(group['tr_val'], 5)
        group['pct_change_1'] = pct_change(group['close'], 1)
        group['ts_max_20'] = ts_max(group['close'], 20)
        group['ibs'] = ibs(group['high'], group['low'], group['close'])
        group['increase_ratio_3'] = increase_from_lowest_price(group['low'], group['close'], 3)
        group['increase_ratio_5'] = increase_from_lowest_price(group['low'], group['close'], 5)
        group['decrease_ratio_3'] = decrease_from_highest_price(group['high'], group['close'], 3)
        group['pdi_5'] = pdi(group['high'], group['low'], group['close'], 5, MovingAverage.ema)
        group['pdi_5_sto'] = stochastic_fast_k(group['pdi_5'], group['pdi_5'], group['pdi_5'], 20)
        group['pdi_5_sto_pct_change_3'] = pct_change(group['pdi_5_sto'], 3)
        group['pivot_standard'] = pivot_standard(group['high'], group['low'], group['close'])
        group_list.append(group)
    day_price = pd.concat(group_list, axis=0)
    day_price = day_price.reset_index(drop=True)
    group_list = []
    grouped = day_price.groupby('date')
    for key, group in grouped:
        group = group.reset_index(drop=True)
        group['rank_tr_val_5'] = rank(group['sma_tr_val_5'])
        group_list.append(group)
    day_price = pd.concat(group_list, axis=0)
    day_price = day_price.reset_index(drop=True)
    group_list = []
    grouped = day_price.groupby('ticker')
    for key, group in grouped:
        increase_condition1 = (group['pdi_5_sto_pct_change_3'].shift(1) >= 0.1) | \
                              (group['pdi_5_sto_pct_change_3'].shift(2) >= 0.1)
        increase_condition = increase_condition1
        decrease_condition1 = group['open'] > group['close']
        decrease_condition2 = (group['pct_change_1'] < 0)
        decrease_condition3 = group['ibs'] < 0.25
        decrease_condition = (decrease_condition1 | decrease_condition2) & decrease_condition3
        liquidity_condition1 = group['rank_tr_val_5'] > 0.8
        liquidity_condition = liquidity_condition1
        # Result
        group['#final_result'] = increase_condition & decrease_condition & liquidity_condition
        group['#priority'] = (group['increase_ratio_3'].shift(1) + group['increase_ratio_3'].shift(2))
        group_list.append(group)
    day_price = pd.concat(group_list, axis=0)
    day_price = day_price.reset_index(drop=True)
    # Market Timing
    index_day_price['sma_3'] = sma(index_day_price['close'], 3)
    index_day_price['sma_5'] = sma(index_day_price['close'], 5)
    index_day_price['sma_10'] = sma(index_day_price['close'], 10)
    index_day_price['#market_timing'] = (index_day_price['close'] > index_day_price['sma_3']) | \
                                        (index_day_price['close'] > index_day_price['sma_5']) | \
                                        (index_day_price['close'] > index_day_price['sma_10'])
    index_day_price = index_day_price.set_index('date')
    return day_price, index_day_price
def change_to_dictionary(day_price: DataFrame) -> dict:
    day_price_dict = {}
    grouped = day_price.groupby('ticker')
    for key, group in grouped:
        group = group.reset_index(drop=True)
        group = group.set_index('date')
        day_price_dict[key] = group
    return day_price_dict
def back_test(generator, start_date, end_date):
    # 0. 변수
    max_basket_size = 10
    liquidation_holding_days = 1
    cut_period = 0
    seed_money = 1000000000
    fee = 0.00015  # when using kiwoom
    basket = {}  # key:ticker, value:buy_price, stock_num, holding_days
    pnl = {'date': [start_date], 'balance': [seed_money]}
    # 1. 거래일 가져오기
    trading_days_list = generator.get_trading_day_list(start_date, end_date)
    print(trading_days_list[-5:])
    # 2. 일봉 가져오기
    day_price = generator.get_day_price_data(Universe.total, True, False, date(2016, 11, 1), date(2017, 12, 31))
    index_day_price = generator.get_index_day_price_data(Universe.kosdaq, date(2016, 11, 1), date(2017, 12, 31))
    # 3. 매수 조건 및 우선순위 생성
    day_price, index_day_price = add_data_to_day_price(day_price, index_day_price)
    day_price = day_price[['date', 'ticker_id', 'open', 'close', '#final_result', '#priority']]
    return day_price


def run(from_date: datetime.date, to_date: datetime.date):
    executor = Executor("")
    reader = Reader(executor)
    return back_test(reader, from_date, to_date)
