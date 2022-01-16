from pyparsing import Combine, Or, Char, nums
from .ottobase import OttoBase, Var
from .keywords import HOUR, MINUTE, SECOND
from .datatypes import Numeric


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
