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
    _parser = _kwd + (Entity.parser()("_entity") | Var.parser()("_var")) + (CaselessKeyword("TO") | "=") + (Var.parser() | Numeric.parser() | StringValue.parser())("_newvalue")

    def __str__(self):
        return f"state.set({self._entity.name},{self._newvalue})"

    def eval(self):
        kwargs = {'value': self._entity.name}
        if hasattr(self,"_entity"):
            opfunc = 'set_state'
            args = [self._entity.name]
        elif hasattr(self,"_var"):
            opfunc = 'set_variable'
            args = [self._var.name]
        return [{'opfunc': 'set_state', 'args': args, 'kwargs': kwargs}]

class Wait(BaseCommand):
    _kwd = CaselessKeyword("WAIT")
    _parser = _kwd + (TimeStamp.parser() | RelativeTime.parser())("_time")

    def __str__(self):
        return f"task.sleep({self._time.as_seconds})"

    def eval(self):
        return [{'opfunc': 'sleep', 'args': self._time.as_seconds}]

class Turn(BaseCommand):
    _kwd = CaselessKeyword("TURN")
    _parser = _kwd + (CaselessKeyword("ON") | CaselessKeyword("OFF"))('_newstate') + Entity.parser()("_entity")

    def eval(self):
        args = [self._entity.domain, 'turn_'+self._newstate.lower()]
        kwargs = {'entity_id': self._entity.name}
        operation = {'opfunc':'service_call', 'args': args, 'kwargs': kwargs}
        return [operation]

class Toggle(BaseCommand):
    _kwd = CaselessKeyword("TOGGLE")
    _parser = _kwd + Entity.parser()("_entity")

    def eval(self):
        args = [self._entity.domain, 'toggle']
        kwargs = {'entity_id': self._entity.name}
        operation = {'opfunc':'service_call', 'args': args, 'kwargs': kwargs}
        return [operation]


class Dim(BaseCommand):
    _kwd = CaselessKeyword("DIM")
    _parser = _kwd + Entity.parser()("_entity") + \
        (CaselessKeyword("TO") | CaselessKeyword("BY"))("_type") + (Var.parser() | Numeric.parser())("_number") + Optional('%')("_use_pct")

    def eval(self):
        args = ["light", "turn_on" if self._number > 0 else "turn_off"]
        entity_id = self._entity.name
        kwargs =  {'entity_id': self._entity.name}

        if self._type.upper() == 'TO':
            param = 'brightness'
        else:
            param = 'brightness_step'

        if hasattr(self,'_use_pct'):
            param += '_pct'

        kwargs[param] = self._number.value

        operation = {'opfunc':'service_call', 'args':args, 'kwargs': kwargs}
        return [operation]

class Lock(BaseCommand):
    _kwd = (CaselessKeyword("LOCK") | CaselessKeyword("UNLOCK"))
    _parser = _kwd("_type") + Entity.parser()("_entity") \
            + Optional(CaselessKeyword("WITH") \
            + (Var.parser() | Numeric.parser())('_code'))

    def eval(self):
        args = ["lock", self._type.lower()]
        kwargs =  {'entity_id': self._entity.name}

        if hasattr(self,'_code'):
            kwargs['code'] += self._code.value

        operation = {'opfunc':'service_call', 'args':args, 'kwargs': kwargs}
        return [operation]
