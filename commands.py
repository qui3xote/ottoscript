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

    def __str__(self):
        return f"state.set({self._entity.name},{self._newvalue})"

    def eval(self):
        return [{'operation': 'set', 'args': [self._entity], 'kwargs': {'value': self._newvalue.value}}]

class Wait(BaseCommand):
    _kwd = CaselessKeyword("WAIT")
    _parser = _kwd + (TimeStamp.parser() | RelativeTime.parser())("_time")

    def __str__(self):
        return f"task.sleep({self._time.as_seconds})"

    def eval(self):
        return [{'operation': 'sleep', 'args': self._time.as_seconds}]




#add_subclasses_parseres_to_scope(sys.modules[__name__], BaseCommand)

#command = Or([cls.parser() for cls in BaseCommand.__subclasses__()])
#COMMAND_KW = Or([cls._kwd for cls in BaseCommand.__subclasses__()])
