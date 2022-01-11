from pyparsing import CaselessKeyword, Optional
from .ottobase import OttoBase
from .vocab import Var, Numeric, Entity, TimeStamp, StringValue, ON
from .expressions import RelativeTime, With


class Command(OttoBase):
    _kwd = None

    def __str__(self):
        return "command(values)"

    async def eval(self):
        await self.interpreter.log_info("Command")


class Pass(Command):
    _kwd = CaselessKeyword("PASS")
    _parser = _kwd

    async def eval(self):
        await self.interpreter.log_info("Passing")


class Set(Command):
    _kwd = CaselessKeyword("SET")
    _parser = _kwd + (Entity.parser()("_entity") | Var.parser()("_var")) \
        + (CaselessKeyword("TO") | "=") \
        + (Var.parser() | Numeric.parser() | StringValue.parser())("_newvalue")

    def __str__(self):
        return f"state.set({self._entity.name},{self._newvalue})"

    async def eval(self):
        result = await self.interpreter.set_state(self._entity.name,
                                                  value=self._newvalue.value)
        return result


class Wait(Command):
    _kwd = CaselessKeyword("WAIT")
    _parser = _kwd + (TimeStamp.parser() | RelativeTime.parser())("_time")

    def __str__(self):
        return f"task.sleep({self._time.as_seconds})"

    async def eval(self):
        result = await self.interpreter.sleep(self._time.as_seconds)
        return result


class Turn(Command):
    _kwd = CaselessKeyword("TURN")
    _parser = _kwd + (CaselessKeyword("ON") |
                      CaselessKeyword("OFF"))('_newstate') \
                   + Entity.parser()("_entity")

    def __str__(self):
        servicename = 'turn_'+self._newstate.lower()
        kwargs = {'entity_id': self._entity.name}
        return f"call_service({self._entity.domain}, {servicename}, {kwargs})"

    async def eval(self):
        servicename = 'turn_'+self._newstate.lower()
        kwargs = {'entity_id': self._entity.name}
        result = await self.interpreter.call_service(self._entity.domain,
                                                     servicename, kwargs)
        return result


class Toggle(Command):
    _kwd = CaselessKeyword("TOGGLE")
    _parser = _kwd + Entity.parser()("_entity")

    async def eval(self):
        servicename = 'toggle'
        kwargs = {'entity_id': self._entity.name}
        result = await self.interpreter.call_service(self._entity.domain,
                                                     servicename, kwargs)
        return result


class Dim(Command):
    _kwd = CaselessKeyword("DIM")
    _parser = _kwd + Entity.parser()("_entity") + \
        (CaselessKeyword("TO") | CaselessKeyword("BY"))("_type") \
        + (Var.parser() | Numeric.parser())("_number") \
        + Optional('%')("_use_pct")

    async def eval(self):

        if self._number.value > 0 or hasattr(self, '_use_pct'):
            servicename = "turn_on"
        else:
            servicename = "turn_off"

        kwargs = {'entity_id': self._entity.name}

        if self._type.upper() == 'TO':
            param = 'brightness'
        else:
            param = 'brightness_step'

        if hasattr(self, '_use_pct'):
            param += '_pct'

        kwargs[param] = self._number.value

        result = await self.interpreter.call_service(self._entity.domain,
                                                     servicename, kwargs)
        return result


class Lock(Command):
    _kwd = (CaselessKeyword("LOCK") | CaselessKeyword("UNLOCK"))
    _parser = _kwd("_type") + \
        Entity.parser()("_entity") + Optional(With.parser()("_with"))

    async def eval(self):
        servicename = self._type.lower()
        kwargs = {'entity_id': self._entity.name}

        if hasattr(self, "_with"):
            kwargs.update(self._with.value)

        result = await self.interpreter.call_service(self._entity.domain,
                                                     servicename, kwargs)
        return result


class Call(Command):
    _kwd = CaselessKeyword("CALL")
    _parser = _kwd \
        + Entity.parser()("_service") \
        + Optional(ON + Entity.parser())("_entity") \
        + Optional(With.parser()("_with"))

    def __str__(self):
        domain = self._service.domain.lower()
        servicename = self._service.id.lower()
        kwargs = {}

        if hasattr(self, "_entity"):
            kwargs['entity_id'] = self._entity.name

        if hasattr(self, "_with"):
            kwargs.update(self._with.value)

        return f"call_service({domain}, {servicename}, {kwargs})"

    async def eval(self):
        domain = self._service.domain.lower()
        servicename = self._service.id.lower()
        kwargs = {}

        if hasattr(self, "_entity"):
            kwargs['entity_id'] = self._entity.name

        if hasattr(self, "_with"):
            kwargs.update(self._with.value)

        result = await self.interpreter.call_service(domain,
                                                     servicename, kwargs)
        return result
