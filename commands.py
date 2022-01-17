from pyparsing import CaselessKeyword, Optional, Or
from .ottobase import OttoBase
from .datatypes import Numeric, Entity, StringValue, List
from .keywords import ON, TO
from .time import RelativeTime, TimeStamp
from .expressions import With


class Command(OttoBase):
    _kwd = None

    def __str__(self):
        return " ".join([str(x) for x in self.tokens.as_list()])

    async def eval(self):
        await self.interpreter.log_info("Command")

    async def call_service(self, domain, kwargs):
        return await self.interpreter.call_service(domain,
                                                   self.service_name,
                                                   kwargs)


class Pass(Command):
    _kwd = CaselessKeyword("PASS")
    _parser = _kwd

    async def eval(self):
        await self.interpreter.log_info("Passing")


class Set(Command):
    _kwd = CaselessKeyword("SET")
    _parser = _kwd + List.parser([Entity])("_entities") \
        + (TO | "=") \
        + Or(Numeric.parser() | StringValue.parser())("_newvalue")

    async def eval(self):
        callfunc = self.interpreter.set_state
        for e in self._entities.contents:
            await callfunc(e.name, value=self._newvalue.value)


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
                   + List.parser([Entity])("_entities") \
                   + Optional(With.parser())("_with")

    @property
    def service_name(self):
        return 'turn_'+self._newstate.lower()

    def kwargs(self, entity):
        return {'entity_id': entity.name}

    async def eval(self):
        callfunc = self.interpreter.call_service
        kwargs = {}

        if hasattr(self, "_with"):
            kwargs.update(self._with.value)

        for e in self._entities.contents:
            kwargs.update({'entity_id': e.name})
            await callfunc(self.service_name,
                           e.domain,
                           kwargs)


class Toggle(Command):
    _kwd = CaselessKeyword("TOGGLE")
    _parser = _kwd + Entity.parser()("_entity")

    @property
    def service_name(self):
        return 'toggle'

    async def eval(self):
        callfunc = self.interpreter.call_service
        for e in self._entities.contents:
            await callfunc(self.service_name,
                           e.domain,
                           {'entity_id': self._entity.name})


class Dim(Command):
    _kwd = CaselessKeyword("DIM")
    _parser = _kwd + Entity.parser()("_entities") + \
        (CaselessKeyword("TO") | CaselessKeyword("BY"))("_type") \
        + Numeric.parser()("_number") \
        + Optional('%')("_use_pct")

    def kwargs(self, entity):
        kwargs = {'entity_id': entity.name}

        if self._type.upper() == 'TO':
            param = 'brightness'
        else:
            param = 'brightness_step'

        if hasattr(self, '_use_pct'):
            param += '_pct'

        kwargs[param] = self._number.value
        return kwargs

    async def eval(self):
        if self._number.value > 0 or hasattr(self, '_use_pct'):
            service_name = "turn_on"
        else:
            service_name = "turn_off"

        callfunc = self.interpreter.call_service
        for e in self._entities.contents:
            await callfunc(service_name,
                           e.domain,
                           self.kwargs(e))


class Lock(Command):
    _kwd = (CaselessKeyword("LOCK") | CaselessKeyword("UNLOCK"))
    _parser = _kwd("_type") + \
        List.parser([Entity])("_entities") + Optional(With.parser())("_with")

    async def eval(self):
        service_name = self._type.lower()

        if hasattr(self, "_with"):
            kwargs = self._with.value
        else:
            kwargs = {}

        callfunc = self.interpreter.call_service
        for e in self._entities.contents:
            kwargs.update({'entity_id': e.name})
            await callfunc(service_name,
                           e.domain,
                           kwargs)


class Call(Command):
    _kwd = CaselessKeyword("CALL")
    _parser = _kwd \
        + Entity.parser()("_service") \
        + Optional(ON + List.parser([Entity]))("_entities") \
        + Optional(With.parser())("_with")

    async def eval(self):
        domain = self._service.domain.lower()
        service_name = self._service.id.lower()
        kwargs = {}
        callfunc = self.interpreter.call_service

        if hasattr(self, "_with"):
            kwargs.update(self._with.value)

        if hasattr(self, "_entities"):
            for e in self._entities.contents:
                kwargs.update({'entity_id': e.name})
                await callfunc(service_name,
                               domain,
                               kwargs)
        else:
            await callfunc(domain, service_name, kwargs)
