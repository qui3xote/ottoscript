from pyparsing import (CaselessKeyword,
                       Combine,
                       Or,
                       Char,
                       nums,
                       Optional,
                       common)
from .ottobase import OttoBase, Var
from .keywords import HOUR, MINUTE, SECOND
from .datatypes import Numeric

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
    _parser = HOUR

    @property
    def as_seconds(self):
        return 3600


class Minute(OttoBase):
    _parser = MINUTE

    @property
    def as_seconds(self):
        return 60


class Second(OttoBase):
    _parser = SECOND

    @property
    def as_seconds(self):
        return 1


class TimePart(OttoBase):

    @classmethod
    def parser(cls):
        cls._parser.set_name(cls.__name__)
        cls._parser.set_parse_action(cls)
        return Or(cls._parser, Var.parser())


class DayOfWeek(TimePart):
    _days = [MONDAY.set_parse_action(lambda x: 'mon'),
             TUESDAY.set_parse_action(lambda x: 'tue'),
             WEDNESDAY.set_parse_action(lambda x: 'wed'),
             THURSDAY.set_parse_action(lambda x: 'thu'),
             FRIDAY.set_parse_action(lambda x: 'fri'),
             SATURDAY.set_parse_action(lambda x: 'sat'),
             SUNDAY.set_parse_action(lambda x: 'sun'),
             WEEKDAY.set_parse_action(lambda x: 'weekday'),
             WEEKEND.set_parse_action(lambda x: 'weekend')
             ]
    _parser = Or(_days)("_value")

    @property
    def value(self):
        return self._value


class TimeStamp(TimePart):
    _digits = Combine(Char(nums) * 2)
    _parser = _digits("_hours") \
        + ":" + _digits("_minutes") \
        + Optional(":" + _digits("_seconds"))

    def __init__(self, tokens):
        if not hasattr(self, '_seconds'):
            self._seconds = '00'
        super().__init__(tokens)

    def __str__(self):
        return ":".join([self._hours, self._minutes, self._seconds])

    @property
    def as_seconds(self):
        return int(self._hours) * 3600 \
               + int(self._minutes) * 60 \
               + int(self._seconds)

    @property
    def value(self):
        return "".join(self.tokens)


class RelativeTime(TimePart):
    _parser = Numeric.parser()("_count") \
              + (Hour.parser()
                 | Minute.parser()
                 | Second.parser())("_unit")

    @property
    def as_seconds(self):
        return self._count.value * self._unit.as_seconds

    @property
    def value(self):
        return self.as_seconds


class Date(TimePart):
    _date = common.iso8601_date
    _parser = _date.set_parse_action(common.convert_to_date)("_value")


class DateTime(TimePart):
    _datetime = common.iso8601_datetime
    _parser = _datetime.set_parse_action(common.convert_to_datetime)("_value")


# When 07:30 on Sun, Mon, Tue, Wed, Thu, Fri, Sat
# - When List(TimeStamp) on List(DayOfWeek)
# RelativeTime BEFORE/AFTER Event on M,T,W,Th,F,Sa,Su
# Every RelativeTime BETWEEN
# When DateTime
