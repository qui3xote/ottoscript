from pyparsing import CaselessKeyword, Group, Combine, Or, Char, nums
from .ottobase import OttoBase, Var
from .keywords import HOUR, MINUTE, SECOND
from .datatypes import Numeric, List

MONDAY = Or(map(CaselessKeyword, "MONDAY M".split()))
TUESDAY = Or(map(CaselessKeyword, "TUESDAY T".split()))
WEDNESDAY = Or(map(CaselessKeyword, "WEDNESDAY W".split()))
THURSDAY = Or(map(CaselessKeyword, "THURSDAY TH".split()))
FRIDAY = Or(map(CaselessKeyword, "FRIDAY F".split()))
SATURDAY = Or(map(CaselessKeyword, "SATURDAY SA".split()))
SUNDAY = Or(map(CaselessKeyword, "SUNDAY SU".split()))


class DayOfWeek(OttoBase):
    _days = [MONDAY.set_parse_action(lambda x: 1),
                TUESDAY.set_parse_action(lambda x: 2),
                WEDNESDAY.set_parse_action(lambda x: 3),
                THURSDAY.set_parse_action(lambda x: 4),
                FRIDAY.set_parse_action(lambda x: 5),
                SATURDAY.set_parse_action(lambda x: 6),
                SUNDAY.set_parse_action(lambda x: 7)
                ]
    _parser = Group(List.parser(_days))("_value")

    @property
    def value(self):
        return self._value


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


class TimeStamp(OttoBase):
    _digits = Combine(Char(nums) * 2).set_parse_action(lambda x: int(x[0]))
    _parser = _digits("_hours") \
        + ":" + _digits("_minutes") \
        + ":" + _digits("_seconds")

    @property
    def as_seconds(self):
        return self._hours * 3600 + self._minutes * 60 + self._seconds

    @classmethod
    def parser(cls):
        cls._parser.set_name(cls.__name__)
        cls._parser.set_parse_action(cls)
        return Or(cls._parser, Var.parser())


class RelativeTime(OttoBase):
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

    @classmethod
    def parser(cls):
        cls._parser.set_name(cls.__name__)
        cls._parser.set_parse_action(cls)
        return Or(cls._parser, Var.parser())


# When 07:30 on Sun, Mon, Tue, Wed, Thu, Fri, Sat
# - When List(TimeStamp) on List(DayOfWeek)
# RelativeTime BEFORE/AFTER Event on M,T,W,Th,F,Sa,Su
# Every RelativeTime BETWEEN
# When DateTime
