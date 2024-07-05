class AlphaVantageConsts:
    """
    Consts related to alphavantage site and API
    """

    class Frequencies:
        """
        Data frequencies
        """
        FREQUENCY_CONST = 'TIME_SERIES_'
        FOUR_HOURS = FREQUENCY_CONST + 'INTRADARY'
        DAILY = FREQUENCY_CONST + 'DAILY'
        WEEKLY = FREQUENCY_CONST + 'WEEKLY'

    API_KEY = 'Q97NXTM53RT88GB3'
    ANOTHER_KEYS = ['ZE70F57S0GXRHDBA', '3D0NTKO0Y5E4UU33', 'PWBUPH1JXMEPO4PI', 'Z4FDOBMD5GJ7P8NR', 'VELPOHADKDDV6Y8I',
                    'RLH5TLNONOJOUSKZ', 'GNARXBBEGR4PN5J5']
    INTRADARY_DATA_URL = r"https://www.alphavantage.co/query?function={frequency}&symbol={symbol}&interval={interval}&apikey={api_key}"
    RAW_DATA_URL = r"https://www.alphavantage.co/query?function={frequency}&symbol={symbol}&apikey={api_key}"


class YahooFinancesConsts:
    """
    Consts related to yfinance dataframes
    """

    DAILY = '1d'
    DAYS_BACK = 90


class ListingConsts:
    NASDAQ_LISTING_URL = "http://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
    OTHER_LISTING_URL = "http://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"

    TRADING_VIEW_LISTING_URL = "https://symbol-search.tradingview.com/symbol_search/v3/?text=&hl=1&country=US&lang=en&search_type=stocks&start={start}&domain=production&sort_by_country=US"
    MAX = 'max'
    TOP = 'top'
    TRADING_VIEW_MAX_SYMBOLS = 10000
    NOTIFY_CHUNK = 1000


class MethodsConsts:
    ALPHAVANTAGE = 'ALPHAVANTAGE'
    YAHOOFINANCE = "YAHOOFINANCE"
