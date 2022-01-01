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

    async def eval(self):
        result = await self.interpreter.set_state(self._entity.name, value=self._newvalue)
        return result

class Wait(BaseCommand):
    _kwd = CaselessKeyword("WAIT")
    _parser = _kwd + (TimeStamp.parser() | RelativeTime.parser())("_time")

    def __str__(self):
        return f"task.sleep({self._time.as_seconds})"

    async def eval(self):
        result = await self.interpreter.sleep(self._time.as_seconds)
        return result

class Turn(BaseCommand):
    _kwd = CaselessKeyword("TURN")
    _parser = _kwd + (CaselessKeyword("ON") | CaselessKeyword("OFF"))('_newstate') + Entity.parser()("_entity")

    async def eval(self):
        servicename = 'turn_'+self._newstate.lower()
        kwargs = {'entity_id': self._entity.name}
        result = await self.interpreter.call_service(self._entity.domain, servicename, kwargs)
        return result

class Toggle(BaseCommand):
    _kwd = CaselessKeyword("TOGGLE")
    _parser = _kwd + Entity.parser()("_entity")

    async def eval(self):
        servicename = 'toggle'
        kwargs = {'entity_id': self._entity.name}
        result = await self.interpreter.call_service(self._entity.domain, servicename, kwargs)
        return result


class Dim(BaseCommand):
    _kwd = CaselessKeyword("DIM")
    _parser = _kwd + Entity.parser()("_entity") + \
        (CaselessKeyword("TO") | CaselessKeyword("BY"))("_type") + (Var.parser() | Numeric.parser())("_number") + Optional('%')("_use_pct")

    async def eval(self):

        if self._number.value > 0 or hasattr(self,'_use_pct'):
            servicename = "turn_on"
        else:
            servicename = "turn_off"

        kwargs =  {'entity_id': self._entity.name}

        if self._type.upper() == 'TO':
            param = 'brightness'
        else:
            param = 'brightness_step'

        if hasattr(self,'_use_pct'):
            param += '_pct'

        kwargs[param] = self._number.value

        result = await self.interpreter.call_service(self._entity.domain, servicename, kwargs)
        return result

class Lock(BaseCommand):
    _kwd = (CaselessKeyword("LOCK") | CaselessKeyword("UNLOCK"))
    _parser = _kwd("_type") + Entity.parser()("_entity") \
            + Optional(CaselessKeyword("WITH") \
            + (Var.parser() | Numeric.parser())('_code'))

    async def eval(self):
        servicename = self._type.lower()]
        kwargs =  {'entity_id': self._entity.name}

        if hasattr(self,'_code'):
            kwargs['code'] += self._code.value

        result = await self.interpreter.call_service(self._entity.domain, servicename, kwargs)
        return result
