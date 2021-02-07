from datetime import date


def build(fields, from_date: date, to_date: date) -> str:
    # TODO: 날짜별 kospi, kosdaq 종목 리스트 로딩
    columns = ['td.date', 'dc.ticker_id', 'dc.close']
    joins = ['left join data_candleday dc on td.date = dc.date']

    return '''
    select {}
    from data_iskoreatradingday td
    {}
    where td.is_tradable = 1
    and td.date between '{}' and '{}'
    '''.format(','.join(columns), '\n'.join(joins), from_date, to_date)
