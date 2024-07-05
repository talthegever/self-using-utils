import datetime
import time
import requests
from typing import List
import yfinance
import pickle

from consts import AlphaVantageConsts, ListingConsts, MethodsConsts, YahooFinancesConsts
from utils import DateUtils
from errors import NotInRange, NotAStocksDay, NotFoundInRaw


class Candle:
    """
    Represents single candle in stocks charts
    """
    DAYS = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

    def __init__(self, symbol: str, date: datetime.date, start: str, finish: str, lowest: str, highest: str,
                 volume: str):
        self.symbol: str = symbol.upper()
        self.date: datetime.date = date
        self.weekday: int = self.date.weekday()
        self.day_in_week: str = self.DAYS[self.weekday]
        self.start = float(start)
        self.finish = float(finish)
        self.lowest = float(lowest)
        self.highest = float(highest)
        self.volume = int(volume)
        self.color = "GREEN" if self.finish - self.start > 0 else "RED"

    def __eq__(self, other) -> bool:
        return (self.symbol == other.symbol and self.date == other.date and self.start == other.start and
                self.finish == other.finish and self.lowest == other.lowest and self.volume == other.volume)

    def __str__(self) -> str:
        volume = "{:,}".format(self.volume)
        return f"""{self.symbol}: {self.date} ({self.day_in_week})\nstart:\t{self.start}\nfinish:\t{self.finish}\nlowest:\t{self.lowest}\nhighest:{self.highest}\nvolume:\t{volume}\n{self.color}"""


class StocksData:
    """
    fetch data from alphavantage site using alphavantageAPI.
    use: x = AlphaVantage(symbol)
    x.<any_method_on_symbol>()
    """

    def __init__(self, symbol: str, method: MethodsConsts) -> None:
        """
        creates candles from one API method
        :param symbol: any symbol from US
        :param method: ALPHAVANTAGE or YAHOOFINANCE
        """
        self.symbol = symbol
        if method == MethodsConsts.ALPHAVANTAGE:
            self._create_from_alphavantage()
        elif method == MethodsConsts.YAHOOFINANCE:
            self._create_from_yahoofinances()
        else:
            print("UNRECOGNIZED METHOD")

    def _create_from_yahoofinances(self) -> None:
        """
        makes candles from yahoofinances API, unknown limits
        """
        self.raw = yfinance.Ticker(self.symbol).history(period=YahooFinancesConsts.DAILY,
                                                        start=str(DateUtils.get_date_x_days_back_from_now(
                                                            YahooFinancesConsts.DAYS_BACK)),
                                                        end=str(datetime.date.today())).to_dict('index')
        dates = list(self.raw.keys())
        dates.reverse()
        self.candles = [
            Candle(self.symbol, date.date(), self.raw[date]['Open'], self.raw[date]['Close'], self.raw[date]['Low'],
                   self.raw[date]['High'], self.raw[date]['Volume']) for date in dates]

    def _create_from_alphavantage(self) -> None:
        """
        makes candles from alphavantage API
        MAX: 5 per minute, 100 per day
        """
        self.raw = requests.get(AlphaVantageConsts.RAW_DATA_URL.format(frequency=AlphaVantageConsts.Frequencies.DAILY,
                                                                       symbol=self.symbol,
                                                                       api_key=AlphaVantageConsts.API_KEY)).json()
        if 'Note' in self.raw.keys():
            print("blocked, waiting 1 minute")
            time.sleep(60)
            self.raw = requests.get(
                AlphaVantageConsts.RAW_DATA_URL.format(frequency=AlphaVantageConsts.Frequencies.DAILY,
                                                       symbol=self.symbol,
                                                       api_key=AlphaVantageConsts.API_KEY)).json()
        elif "Information" in self.raw.keys():
            print("blocked finally")
        relevant_numbers = self.raw["Time Series (Daily)"]
        self.candles = [Candle(self.symbol, DateUtils.str_day_to_date(date), relevant_numbers[date]['1. open'],
                               relevant_numbers[date]['4. close'], relevant_numbers[date]['3. low'],
                               relevant_numbers[date]['2. high'], relevant_numbers[date]['5. volume'])
                        for date in relevant_numbers.keys()]

    def _get_last_date_from_list(self) -> datetime.date:
        """
        :return: most relevant datetime of the stock (retrieved)
        """
        return self.candles[0].date

    def _get_first_date_from_raw(self) -> datetime.date:
        """
        :return: oldest datetime of the stock (retrieved)
        """
        return self.candles[-1].date

    def _get_specific_day_candle(self, date: datetime.date) -> Candle:
        """
        :param date: datetime.date
        :return: the right candle or suitable error
        """
        if date > self.candles[0].date or date < self.candles[-1].date:
            raise NotInRange
        elif not DateUtils.is_stocks_day(date):
            raise NotAStocksDay
        else:
            for candle in self.candles:
                if candle.date == date:
                    return candle
            raise NotFoundInRaw

    def get_two_last_candles_from_date(self, date: datetime.date) -> List[Candle]:
        """
        :param date: datetime.date
        :return: two last candles from this date back, first is most updated
        """
        last = DateUtils.get_closest_valid_date(date)
        previous = DateUtils.get_previous_valid_date(last)
        return [self._get_specific_day_candle(last), self._get_specific_day_candle(previous)]

    def get_candles_since_date(self, date: datetime.date) -> List[Candle]:
        """
        :param date: datetime.date to start from
        :return: list of candles from date till now
        """
        return [candle for candle in self.candles if candle.date >= date]

    def get_candles_days_back(self, days: int) -> List[Candle]:
        """
        :param days: int, days to get candles
        :return: list of candles <days> days back
        """
        return self.get_candles_since_date(DateUtils.get_date_x_days_back_from_now(days))


class StockList:
    """
    gets up-to-date all stocks listing from america
    """

    def __init__(self, fullness: str, create=False) -> None:
        if fullness == ListingConsts.MAX:
            self._make_full_list()
        elif fullness == ListingConsts.TOP and create:
            self._make_tradingview_top_list()
        elif fullness == ListingConsts.TOP:
            self._get_tradingview_list()

    def _make_full_list(self) -> None:
        """
        contains something like 11500 symbols
        """
        all_nasdaq_symbols = [stock.split('|')[0] for stock in
                              requests.get(ListingConsts.NASDAQ_LISTING_URL).text.split('\r\n')][1:][:-1]
        all_other_symbols = [stock.split('|')[0] for stock in
                             requests.get(ListingConsts.OTHER_LISTING_URL).text.split('\r\n')][1:][:-1]
        self.all_symbols = all_nasdaq_symbols[:-1] + all_other_symbols[:-1]
        self.last_updated = datetime.datetime.strptime(all_nasdaq_symbols[-1].replace('File Creation Time: ', ''),
                                                       '%m%d%Y%H:%M')

    def _make_tradingview_top_list(self) -> None:
        """
        contains only **US** **stocks**
        fetched from trading view get requests backend
        """
        all_stocks: List[str] = []
        for i in range(0, ListingConsts.TRADING_VIEW_MAX_SYMBOLS, 50):
            all_stocks.extend([stock_data['symbol'] for stock_data in
                               requests.get(ListingConsts.TRADING_VIEW_LISTING_URL.format(start=str(i))).json()[
                                   'symbols'] if stock_data['type'] == 'stock'])
            if i % ListingConsts.NOTIFY_CHUNK == 0:
                print(f"fetched {i} from {ListingConsts.TRADING_VIEW_MAX_SYMBOLS}")
        self.all_symbols = all_stocks
        self.last_updated = datetime.datetime.now()
        with open(r"tradingviewstocksUS.txt", "wb") as stocklistfile:
            pickle.dump(all_stocks, stocklistfile)

    def _get_tradingview_list(self) -> None:
        try:
            with open(r"tradingviewstocksUS.txt", "rb") as stocklistfile:
                self.all_symbols = pickle.load(stocklistfile)
        except EOFError:
            self._make_tradingview_top_list()
            with open(r"tradingviewstocksUS.txt", "rb") as stocklistfile:
                self.all_symbols = pickle.load(stocklistfile)
        finally:
            self.last_updated = datetime.datetime.now()
