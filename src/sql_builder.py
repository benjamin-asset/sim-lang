from datetime import date


def build(fields, from_date: date, to_date: date) -> str:
    # TODO: 날짜별 kospi, kosdaq 종목 리스트 로딩
    columns = ['td.date', 'dc.ticker_id', 'dc.close']
    joins = ['left join data_candleday dc on td.date = dc.date']

    return '''
    select c.date, c.ticker_id, c.open, c.high, c.low, c.close, c.vol, c.tr_val,
       tt.p_buy_vol, tt.org_buy_vol, tt.f_buy_vol, tt.pen_buy_vol, tt.f_buy_tr_val,
       tt.org_buy_tr_val, tt.p_buy_tr_val, tt.pen_buy_tr_val, tt.etc_buy_tr_val, tt.etc_buy_vol,
       ded.close usd,
       dey.close yen,
       deu.close euro
    from data_candleday c
    left join data_daytradingtrend tt using(date, ticker_id)
    left join data_daytradinginfo ti using(date, ticker_id)
    left join data_exchangeratecandleday ded on c.date = ded.date and ded.ticker = 'USDKRW'
    left join data_exchangeratecandleday dey on c.date = dey.date and dey.ticker = 'YENKRW'
    left join data_exchangeratecandleday deu on c.date = deu.date and deu.ticker = 'EUROKRW'
    where c.date between '{}' and '{}'
    '''.format(from_date, to_date)

    # return '''
    # select {}
    # from data_iskoreatradingday td
    # {}
    # where td.is_tradable = 1
    # and td.date between '{}' and '{}'
    # '''.format(','.join(columns), '\n'.join(joins), from_date, to_date)
