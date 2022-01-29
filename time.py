from pyparsing import (CaselessKeyword,
                       Group,
                       Combine,
                       Or,
                       Char,
                       nums,
                       Optional,
                       common)
from .ottobase import OttoBase
from .keywords import HOUR, MINUTE, SECOND
from .datatypes import Numeric,  Var

MONDAY = Or(map(CaselessKeyword, "MONDAY MON".split()))
TUESDAY = Or(map(CaselessKeyword, "TUESDAY TUE".split()))
WEDNESDAY = Or(map(CaselessKeyword, "WEDNESDAY WED".split()))
THURSDAY = Or(map(CaselessKeyword, "THURSDAY THU".split()))
FRIDAY = Or(map(CaselessKeyword, "FRIDAY FRI".split()))
SATURDAY = Or(map(CaselessKeyword, "SATURDAY SAT".split()))
SUNDAY = Or(map(CaselessKeyword, "SUNDAY SUN".split()))
WEEKDAY = Or(map(CaselessKeyword, "WEEKDAY WEEKDAYS".split()))
WEEKEND = Or(map(CaselessKeyword, "WEEKEND WEEKENDS".split()))


class Hour(OttoBase):
    parser = Group(HOUR('time_unit'))

    @property
    def seconds(self):
        return 3600


class Minute(OttoBase):
    parser = Group(MINUTE('time_unit'))

    @property
    def seconds(self):
        return 60


class Second(OttoBase):
    parser = Group(SECOND('time_unit'))

    @property
    def seconds(self):
        return 1


class TimePart(OttoBase):

    @classmethod
    def pre_parse(cls):
        cls.parser.set_name(cls.__name__)
        cls.parser.set_parse_action(cls)
        return Or(cls.parser, Var())


class DayOfWeek(TimePart):
    parser = Group(MONDAY.set_parse_action(lambda x: 'mon')("string")
                   | TUESDAY.set_parse_action(lambda x: 'tue')("string")
                   | WEDNESDAY.set_parse_action(lambda x: 'wed')("string")
                   | THURSDAY.set_parse_action(lambda x: 'thu')("string")
                   | FRIDAY.set_parse_action(lambda x: 'fri')("string")
                   | SATURDAY.set_parse_action(lambda x: 'sat')("string")
                   | SUNDAY.set_parse_action(lambda x: 'sun')("string")
                   | WEEKDAY.set_parse_action(lambda x: 'weekday')("string")
                   | WEEKEND.set_parse_action(lambda x: 'weekend')("string")
                   )

    # @property
    # def string(self):
    #     return self.value


class TimeStamp(TimePart):
    digits = Combine(Char(nums) * 2)
    parser = Group(digits("hour")
                   + ":" + digits("minutes")
                   + Optional(":" + digits("seconds"))
                   )

    def __init__(self, tokens):
        if not hasattr(self, 'seconds'):
            self.seconds = '00'
        super().__init__(tokens)

    @property
    def seconds(self):
        return int(self.hour) * 3600 \
               + int(self.minutes) * 60 \
               + int(self.seconds)

    @property
    def value(self):
        return "".join(self.tokens)


class RelativeTime(TimePart):
    parser = Group(Numeric()("count")
                   + (Hour()
                   | Minute()
                   | Second())("unit")
                   )

    @property
    def seconds(self):
        return self.count.value * self.unit.seconds

    @property
    def string(self):
        return f"{self.count} {self.unit}"


class Date(TimePart):
    date = common.iso8601_date
    date = date.set_parse_action(common.convert_to_date)
    parser = Group(date("string"))


class DateTime(TimePart):
    datetime = common.iso8601_datetime
    datetime = datetime.set_parse_action(common.convert_to_datetime)
    parser = Group(datetime("string"))
