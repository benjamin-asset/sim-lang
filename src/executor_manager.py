from connection_manager import query
from executor import execute_ticker
from stock_type import StockType
from compiler import Compiler
from datetime import date
import pandas as pd


compiler = Compiler()


def execute(source_code, stock_type: StockType, from_date: date):
    result = compiler.compile(source_code)
    df = pd.DataFrame()

    # rank 가 종목 단위인지 날짜 단위인지도 중요함
    # 종목 단위 rank
    if len(result.rank_function_list) > 0:
        if stock_type == StockType.KOSPI:
            sql = f""
        elif stock_type == StockType.KOSPI_150:
            sql = f""
        elif stock_type == StockType.KOSDAQ:
            sql = f""
        elif stock_type == StockType.KOSDAQ_200:
            sql = f""
        else:
            sql = f"select * from data_candleday where date >= '{from_date}' order by date;"

        rows = query(sql)

        # 열 : 종목, 행 : 날짜, 값 : 순위인 판다스 데이터 프레임을 만들어내고 -> 이를 날짜로 정렬한 뒤 리스트로 쪼개어서 각 람다에 전달해야함(종목에 맞게)
        exec("df['a'] = rows(d)")

    # TODO: 종목 몇개 단위로 쪼개어서 실행
    execute_ticker(result.code, None, None)


if __name__ == '__main__':
    execute(
        """
        a = 10
        """,
        0,
        date(2020, 12, 1)
    )
