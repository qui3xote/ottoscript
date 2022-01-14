from pyparsing import (CaselessKeyword,
                       Or,
                       Optional,
                       )
from .ottobase import OttoBase
from .vocab import Entity, FROM, TO, FOR, Vocab, TimeStamp
from .expressions import RelativeTime, List


class Trigger(OttoBase):
    _parser = None

    def __str__(self):
        return " ".join([str(x) for x in self.tokens])


class StateChange(Trigger):
    term = Or(Vocab.child_parsers())
    _parser = List.parser([Entity])("_entities") \
        + CaselessKeyword("CHANGES") \
        + Optional(FROM + term("_old")) \
        + Optional(TO + term("_new")) \
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
