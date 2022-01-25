from pyparsing import (CaselessKeyword,
                       Optional,
                       )
from .ottobase import OttoBase
from .keywords import FROM, TO, FOR, ON, BEFORE, AFTER, SUNRISE, SUNSET
from .datatypes import Entity, Numeric, List, StringValue
from .time import RelativeTime, TimeStamp, DayOfWeek


class Trigger(OttoBase):
    _parser = None

    def __str__(self):
        return " ".join([str(x) for x in self.tokens])


class StateChange(Trigger):
    _term = (Entity.parser() | Numeric.parser() | StringValue.parser())
    _parser = List.parser(Entity.parser())("_entities") \
        + CaselessKeyword("CHANGES") \
        + Optional(FROM + _term("_old")) \
        + Optional(TO + _term("_new")) \
        + Optional(FOR + (TimeStamp.parser() | RelativeTime.parser())("_hold"))

    @property
    def hold_seconds(self):
        if hasattr(self, '_hold'):
            return self._hold.as_seconds
        else:
            return None

    @property
    def old(self):
        if hasattr(self, "_old"):
            return self._old.value
        else:
            return None

    @property
    def new(self):
        if hasattr(self, "_new"):
            return self._new.value
        else:
            return None

    @property
    def type(self):
        return 'state'

    @property
    def entities(self):
        return [e.name for e in self._entities.contents]


class TimeTrigger(Trigger):
    _parser = List.parser([TimeStamp.parser()])("_times") \
            + Optional(ON + List.parser([DayOfWeek.parser()])("_days"))

    @property
    def days(self):
        print(type(self._days))
        if not hasattr(self, "_days"):
            return ['']
        else:
            return [x.value for x in self._days.contents]

    @property
    def times(self):
        return [x.value for x in self._times.contents]

    @property
    def offset_seconds(self):
        return 0

    @property
    def type(self):
        return 'time'


class SunEvent(Trigger):
    # _relative = Optional(RelativeTime.parser()("_time")
    #                      + (BEFORE | AFTER)("_relative"))("_offset")
    # _days = Optional(ON + List.parser([DayOfWeek.parser()])("_days"))
    _parser = Optional(RelativeTime.parser()("_time")
                       + (BEFORE | AFTER)("_relative")
                       )("_offset") \
              + (SUNRISE | SUNSET)("_sunevent") \
              + Optional(ON + List.parser([DayOfWeek.parser()])("_days"))

    @property
    def offset_seconds(self):
        if not hasattr(self, "_offset"):
            return 0
        else:
            sign = 1 if self._relative == "AFTER" else -1
            return sign * self._time.as_seconds

    @property
    def days(self):
        if not hasattr(self, "_days"):
            return ['']
        else:
            print(type(self._days))
            return [x.value for x in self._days.contents]

    @property
    def times(self):
        return [self._sunevent.lower()]

    @property
    def type(self):
        return 'time'
