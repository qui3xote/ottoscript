from pyparsing import (CaselessKeyword,
                       Group,
                       Combine,
                       MatchFirst,
                       MatchFirst,
                       Char,
                       nums,
                       Optional,
                       common)
from .base import OttoBase
from .keywords import HOUR, MINUTE, SECOND
from .datatypes import Number,  Var

MONDAY = MatchFirst(map(CaselessKeyword, "MONDAY MON".split()))
TUESDAY = MatchFirst(map(CaselessKeyword, "TUESDAY TUE".split()))
WEDNESDAY = MatchFirst(map(CaselessKeyword, "WEDNESDAY WED".split()))
THURSDAY = MatchFirst(map(CaselessKeyword, "THURSDAY THU".split()))
FRIDAY = MatchFirst(map(CaselessKeyword, "FRIDAY FRI".split()))
SATURDAY = MatchFirst(map(CaselessKeyword, "SATURDAY SAT".split()))
SUNDAY = MatchFirst(map(CaselessKeyword, "SUNDAY SUN".split()))
WEEKDAY = MatchFirst(map(CaselessKeyword, "WEEKDAY WEEKDAYS".split()))
WEEKEND = MatchFirst(map(CaselessKeyword, "WEEKEND WEEKENDS".split()))


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
        parser = MatchFirst(cls.parser, Var())
        parser = parser.set_parse_action(lambda x: cls(x, *args, **kwargs))
        return parser


class DayOfWeek(TimePart):
    parser = Group(MONDAY("option")
                   | TUESDAY("option")
                   | WEDNESDAY("option")
                   | THURSDAY("option")
                   | FRIDAY("option")
                   | SATURDAY("option")
                   | SUNDAY("option")
                   | WEEKDAY("option")
                   | WEEKEND("option")
                   )

    @property
    def days(self):
        if self.option == "WEEKDAY":
            return ["mon", "tue", "wed", "thu", "fri"]
        elif self.option == "WEEKEND":
            return ["sat", "sun"]
        else:
            return [self.option.lower()[:3]]


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
    parser = Group(Number()("count")
                   + (Hour()("unit")
                   | Minute()("unit")
                   | Second()("unit"))
                   )

    @property
    def seconds(self):
        return self.count._value * self.unit.seconds

    @property
    def string(self):
        return f"{str(self.count._value)} {self.unit.string}"


class Date(TimePart):
    date = common.iso8601_date
    parser = Group(date("string"))


class DateTime(TimePart):
    parser = Group(Date()("date") + TimeStamp()("time"))

    @property
    def string(self):
        return f"{self.date.string} {self.time.string}"
