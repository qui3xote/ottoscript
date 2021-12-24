import sys
from pyparsing import *
from ottolib.vocab import *

#from utils import add_subclasses_parseres_to_scope

#expressions
class BaseTrigger(BaseVocab):
    _parser = None

    def __str__(self):
        return f"{self.tokens[0]}:{' '.join(self.tokens[1:])}"

class StateChange(BaseTrigger):
    _parser =  Entity.parser()("_entity") \
        + CaselessKeyword("CHANGES") \
        + Optional(CaselessKeyword("FROM") + term("_old")) \
        + Optional(CaselessKeyword("TO") + term("_new")) \
        + Optional(CaselessKeyword("FOR") + (TimeStamp.parser() | RelativeTime.parser())("_hold"))

    def __str__(self):
        triggers = []
        if hasattr(self,"_new"):
            triggers.append(f"{self._entity.name} == {self._new}")
        if self._old:
            triggers.append(f"{self._entity.name}.old == {self._old}")

        if len(triggers) == 0:
            triggers = [f"{self._entity.name}"]

        return " and ".join(triggers)

    @property
    def kwargs(self):
        return {"hold": self._hold.as_seconds if self._hold is not None else None}


#add_subclasses_parseres_to_scope(sys.modules[__name__], BaseTrigger)
