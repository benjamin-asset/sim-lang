from datetime import date


def build(fields, from_date: date, to_date: date) -> str:
    # TODO: 날짜별 kospi, kosdaq 종목 리스트 로딩

    field_sql = ", ".join([f"{x.db_prefix}.{x.en_name}" for x in fields])
    if len(fields) > 0:
        field_sql += ", "

    table_set = set()
    for field in fields:
        table_set.add(field.db_prefix)

    table_sql = ""
    for table in table_set:
        if table == "tt":
            content = "left join data_daytradingtrend tt using(date, ticker_id)\n"
        elif table == "ti":
            content = "left join data_daytradinginfo ti using(date, ticker_id)\n"
        else:
            content = ""
        table_sql += content

    return """
    select c.date, c.ticker_id, c.high, c.low, c.open,
        {}
       ded.close usd,
       dey.close yen,
       deu.close euro
    from data_candleday c
    {}
    left join data_exchangeratecandleday ded on c.date = ded.date and ded.ticker = 'USDKRW'
    left join data_exchangeratecandleday dey on c.date = dey.date and dey.ticker = 'YENKRW'
    left join data_exchangeratecandleday deu on c.date = deu.date and deu.ticker = 'EUROKRW'
    where c.date between '{}' and '{}'
    """.format(
        field_sql, table_sql, from_date, to_date
    )
