from pyparsing import CaselessKeyword, Or, Optional
from .ottobase import OttoBase
from .vocab import Entity, FROM, TO, FOR, Vocab, TimeStamp
from .expressions import RelativeTime


class Trigger(OttoBase):
    _parser = None

    def __str__(self):
        return " ".join([str(x) for x in self.tokens])


class StateChange(Trigger):
    term = Or(Vocab.child_parsers())
    _parser = Entity.parser()("_entity") \
        + CaselessKeyword("CHANGES") \
        + Optional(FROM + term("_old")) \
        + Optional(TO + term("_new")) \
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
    def kwargs(self):
        return {"state_hold": self._hold.as_seconds
                if hasattr(self, '_hold') else None}
