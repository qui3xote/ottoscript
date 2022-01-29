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
    parser = Group(HOUR("string"))

    @property
    def seconds(self):
        return 3600


class Minute(OttoBase):
    parser = Group(MINUTE("string"))

    @property
    def seconds(self):
        return 60


class Second(OttoBase):
    parser = Group(SECOND('string'))

    @property
    def seconds(self):
        return 1


class TimePart(OttoBase):

    @classmethod
    def pre_parse(cls, *args, **kwargs):
        cls.parser.set_name(cls.__name__)
        parser = Or(cls.parser, Var())
        parser = parser.set_parse_action(lambda x: cls(x, *args, **kwargs))
        return parser


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


class TimeStamp(TimePart):
    digits = Combine(Char(nums) * 2)
    parser = Group(digits("hour")
                   + ":" + digits("minute")
                   + Optional(":" + digits("second"))
                   )

    def __init__(self, tokens):
        if not hasattr(self, 'seconds'):
            self.second = '00'
        super().__init__(tokens)

    @property
    def seconds(self):
        return int(self.hour) * 3600 \
            + int(self.minute) * 60 \
            + int(self.second)

    @property
    def string(self):
        return ":".join([self.hour, self.minute, self.second])


class RelativeTime(TimePart):
    parser = Group(Numeric()("count")
                   + (Hour()("unit")
                   | Minute()("unit")
                   | Second()("unit"))
                   )

    @property
    def seconds(self):
        return self.count.value * self.unit.seconds

    @property
    def string(self):
        return f"{str(self.count.value)} {self.unit.string}"


class Date(TimePart):
    date = common.iso8601_date
    parser = Group(date("string"))


class DateTime(TimePart):
    parser = Group(Date()("date") + TimeStamp()("time"))

    @property
    def string(self):
        return f"{self.date.string} {self.time.string}"
