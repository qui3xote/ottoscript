from pyparsing import (CaselessKeyword,
                       Or,
                       Optional,
                       )
from .ottobase import OttoBase
from .keywords import FROM, TO, FOR
from .datatypes import Entity, Numeric, List, StringValue
from .time import RelativeTime, TimeStamp


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

    def __str__(self):
        triggers = []
        if hasattr(self, "_new"):
            triggers.append(f"{self._entity.name} == '{self._new.value}'")
        if hasattr(self, "_old"):
            triggers.append(f"{self._entity.name}.old == '{self._old.value}'")
        if len(triggers) == 0:
            triggers = [f"{self._entity.name}"]

        return " and ".join(triggers)

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
    def trigger_type(self):
        return 'state_change'

    @property
    def value(self):
        trigger_list = []
        for e in self._entities.contents:
            trigger = {"type": self.trigger_type,
                       "entity": e.name,
                       "old": self.old,
                       "new": self.new,
                       "hold_seconds": self.hold_seconds
                       }
            trigger_list.append(trigger)

        return trigger_list
