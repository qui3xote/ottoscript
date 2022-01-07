import sys
from pyparsing import *
from .vocab import *
from .expressions import *


class Trigger(OttoBase):
    _parser = None

    def __str__(self):
        return " ".join([str(x) for x in self.tokens])



class StateChange(Trigger):
    term = Or(Vocab.child_parsers())
    _parser =  Entity.parser()("_entity") \
        + CaselessKeyword("CHANGES") \
        + Optional(CaselessKeyword("FROM") + term("_old")) \
        + Optional(CaselessKeyword("TO") + term("_new")) \
        + Optional(CaselessKeyword("FOR") + (TimeStamp.parser() | RelativeTime.parser())("_hold"))

    def __str__(self):
        triggers = []
        if hasattr(self,"_new"):
            triggers.append(f"{self._entity.name} == '{self._new.value}'")
        if  hasattr(self,"_old"):
            triggers.append(f"{self._entity.name}.old == '{self._old.value}'")

        if len(triggers) == 0:
            triggers = [f"{self._entity.name}"]

        return " and ".join(triggers)

    @property
    def kwargs(self):
        return {"state_hold": self._hold.as_seconds if hasattr(self,'_hold') else None}


#add_subclasses_parseres_to_scope(sys.modules[__name__], BaseTrigger)
