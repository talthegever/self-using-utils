from objects import Candle
from typing import List
import datetime


class OKRCandle:
    WIN_STRING = " -> WIN!!! OKR in last candle\n"

    @staticmethod
    def _is_opposite(first_candle: Candle, following_candle: Candle) -> bool:
        return following_candle.color != first_candle.color

    @staticmethod
    def _is_okr(first_candle: Candle, following_candle: Candle) -> bool:
        if following_candle.start < first_candle.lowest and following_candle.finish > first_candle.highest:
            return True
        if following_candle.start > first_candle.highest and following_candle.finish < first_candle.lowest:
            return True
        return False

    @staticmethod
    def locate_history_okr(candles: List[Candle]) -> None:
        for first, following in zip(candles[1:], candles[:-1]):
            if OKRCandle.okr_recommend(first, following):
                print(f"{following.date} is {following.color} OKR in {following.symbol}" + (
                    " --> relevant!" if datetime.date.today() - following.date < datetime.timedelta(days=3) else ""))

    @staticmethod
    def okr_recommend(first_candle: Candle, following_candle: Candle) -> bool:
        return OKRCandle._is_okr(first_candle, following_candle) and OKRCandle._is_opposite(first_candle,
                                                                                            following_candle)
