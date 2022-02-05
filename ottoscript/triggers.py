from itertools import product
from pyparsing import (CaselessKeyword,
                       Optional,
                       Group,
                       )
from .ottobase import OttoBase
from .keywords import FROM, TO, FOR, ON, BEFORE, AFTER, SUNRISE, SUNSET
from .datatypes import Entity, Number, List, String
from .time import RelativeTime, TimeStamp, DayOfWeek


class StateTrigger(OttoBase):

    @property
    def strings(self):
        strings = []
        try:
            for e in self.entities.contents:
                string = []
                if self.new is not None:
                    string.append(f"{e.name} == '{self.new}'")

                if self.old is not None:
                    string.append(f"{e.name}.old == '{self.old}'")

                if len(string) == 0:
                    string.append(f"{e.name}")

                strings.append(" and ".join(string))
        except Exception as error:
            self.ctx.log.error(f"Unable to parse state trigger {error}")

        return strings

    def as_dict(self):
        return {
            'type': self.type,
            'strings': self.strings,
            'hold': self.hold_seconds
        }

    @classmethod
    def parsers(cls):
        return [subclass() for subclass in cls.__subclasses__()]


class StateChange(StateTrigger):
    term = (Entity() | Number() | String())
    parser = Group(List(Entity())("entities")
                   + CaselessKeyword("CHANGES")
                   + Optional(FROM + (Entity()("_old")
                                      | Number()("_old") | String()("_old")))
                   + Optional(TO + (Entity()("_new")
                                    | Number()("_new") | String()("_new")))
                   + Optional(FOR + (TimeStamp()("_hold")
                                     | RelativeTime()("_hold")))
                   )

    @property
    def hold_seconds(self):
        if hasattr(self, '_hold'):
            return self._hold.seconds
        else:
            return 0

    @property
    def old(self):
        if hasattr(self, "_old"):
            return self._old._value
        else:
            return None

    @property
    def new(self):
        if hasattr(self, "_new"):
            return self._new._value
        else:
            return None

    @property
    def type(self):
        return 'state'

    def as_list(self):
        return [
            {
                'type': self.type,
                'string': string,
                'hold': self.hold_seconds
            }
            for string in self.strings
        ]


class TimeTrigger(OttoBase):

    @property
    def strings(self):
        prod = product(self.days, self.times)
        strings = [f"once({x[0]} {x[1]} + {self.offset}s)" for x in prod]
        return strings

    @property
    def type(self):
        return 'time'

    @property
    def days(self):
        if not hasattr(self, "_days"):
            return ['']
        else:
            result = []
            for parser in self._days.contents:
                result.extend(parser.days)

            return result

    def as_list(self):
        return [
            {'type': self.type, 'string': string}
            for string in self.strings
        ]

    @classmethod
    def parsers(cls):
        return [subclass() for subclass in cls.__subclasses__()]


class WeeklySchedule(TimeTrigger):
    parser = Group(List(TimeStamp())("_times")
                   + Optional(ON + List(DayOfWeek())("_days"))
                   )

    def __init__(self, tokens):
        super().__init__(tokens)

        self.times = [x.string for x in self._times.contents]

    @property
    def offset(self):
        return 0


class SunEvent(TimeTrigger):
    parser = Group(Optional(RelativeTime()("time")
                            + (BEFORE | AFTER)("relative")
                            )("_offset")
                   + (SUNRISE("_time")
                      | SUNSET("_time")
                      )
                   + Optional(ON + List(DayOfWeek())("_days"))
                   )

    @property
    def offset(self):
        if not hasattr(self, "_offset"):
            return 0
        else:
            sign = 1 if self._offset[1] == "AFTER" else -1
            return sign * self._offset[0].seconds

    @property
    def times(self):
        return [self._time.lower()]
