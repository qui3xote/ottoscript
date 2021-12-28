import sys
from pyparsing import *
from ottolib.vocab import *
#from utils import add_subclasses_parseres_to_scope

class BaseCommand(BaseVocab):
    _kwd = None

    def __str__(self):
        return f"command(values)"

    def run(self):
        return print(str(self))


class Set(BaseCommand):
    _kwd = CaselessKeyword("SET")
    _parser = _kwd + Entity.parser()("_entity") + (CaselessKeyword("TO") | "=") + (Var.parser() | Numeric.parser() | StringValue.parser())("_newvalue")

    def run(self):
        self._entity.value = self._newvalue

    def __str__(self):
        return f"state.set({self._entity.fullname},{self._newvalue})"

class Wait(BaseCommand):
    _kwd = CaselessKeyword("WAIT")
    _parser = _kwd + (TimeStamp.parser() | RelativeTime.parser())("_time")

    def __str__(self):
        return f"task.sleep({self._time.as_seconds})"

class Run(BaseCommand):
    _kwd = CaselessKeyword("RUN")
    _parser = _kwd + (ident | Var.parser())("_routine")

    def __str__(self):
        return f"RUN {self._routine}"




#add_subclasses_parseres_to_scope(sys.modules[__name__], BaseCommand)

#command = Or([cls.parser() for cls in BaseCommand.__subclasses__()])
#COMMAND_KW = Or([cls._kwd for cls in BaseCommand.__subclasses__()])
