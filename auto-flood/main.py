import datetime

from consts import MethodsConsts
import objects
import floods
from datetime import date
from errors import NotInRange
from utils import PrintUtils


def history_okr(stock_data: objects.StocksData) -> None:
    floods.OKRCandle.locate_history_okr(stock_data.candles)


def current_okr(stock_data: objects.StocksData) -> bool:
    two_last_candles = stock_data.get_two_last_candles_from_date(date.today() - datetime.timedelta(days=1))
    return floods.OKRCandle.okr_recommend(two_last_candles[1], two_last_candles[0])


if __name__ == '__main__':
    print(datetime.datetime.now())
    stock_list = objects.StockList('top')
    print(f"working by list from that last updated in {stock_list.last_updated}, total:{len(stock_list.all_symbols)}")
    print("OKR recommendations:")
    for index, symbol in enumerate(stock_list.all_symbols):
        print(str(index) + ". " + symbol)
        stock_data = objects.StocksData(symbol, MethodsConsts.YAHOOFINANCE)
        try:
            if current_okr(stock_data):
                PrintUtils.note_me_print(stock_data.symbol + floods.OKRCandle.WIN_STRING)
        except (IndexError, NotInRange):
            print(f"{stock_data.symbol} not found on yahoo, trying alphavantage")
            try:
                stock_data = objects.StocksData(symbol, MethodsConsts.ALPHAVANTAGE)
                if current_okr(stock_data):
                    PrintUtils.note_me_print(stock_data.symbol + floods.OKRCandle.WIN_STRING)
            except NotInRange:
                if len(stock_data.candles) < 2:
                    print(f"{stock_data.symbol} don't have enough candles")
            except Exception as e:
                if "/" in stock_data.symbol:
                    print("stupid API bug with the '/', skipping stock")
                else:
                    raise e

        history_okr(stock_data)

    print(datetime.datetime.now())

