import datetime


class DateUtils:

    @staticmethod
    def str_day_to_date(day: str) -> datetime.date:
        """
        :param day: "2023-09-15" like format
        :return: datetime of this day
        """
        return datetime.date.fromisoformat(day)

    @staticmethod
    def get_closest_valid_date(date: datetime.date) -> datetime.date:
        """
        :param date: datetime.date
        :return: itself. if sunday or saturday, returns last friday
        """
        while date.weekday() > 4:
            date = date - datetime.timedelta(days=1)
        return date

    @staticmethod
    def get_previous_valid_date(date: datetime.date) -> datetime.date:
        """
        :param date: datetime.date
        :return: yesterday. if sunday or saturday, return last Thursday
        """
        return DateUtils.get_closest_valid_date(date - datetime.timedelta(days=1))

    @staticmethod
    def is_stocks_day(date: datetime.date) -> bool:
        return date.weekday() <= 4

    @staticmethod
    def get_date_x_days_back_from_now(days: int) -> datetime.date:
        """
        :param days: days back
        :return: datetime.date - wanted date
        """
        return datetime.date.today() - datetime.timedelta(days=days)


class PrintUtils:
    ENTRY = "******************\n"

    @staticmethod
    def note_me_print(sentence: str) -> None:
        print(PrintUtils.ENTRY + sentence + PrintUtils.ENTRY)
