from pyparsing import CaselessKeyword, Optional, Or
from .ottobase import OttoBase
from .datatypes import Numeric, Entity, StringValue, List
from .keywords import ON, TO, OFF
from .time import RelativeTime, TimeStamp
from .expressions import With

PASS = CaselessKeyword("PASS")
SET = CaselessKeyword("SET")
WAIT = CaselessKeyword("WAIT")
TURN = CaselessKeyword("TURN")
TOGGLE = CaselessKeyword("TOGGLE")
LOCK = CaselessKeyword("LOCK")
UNLOCK = CaselessKeyword("UNLOCK")
CALL = CaselessKeyword("CALL")


class Command(OttoBase):
    _kwd = None

    def __str__(self):
        return " ".join([str(x) for x in self.tokens.as_list()])

    async def eval(self, interpreter):
        await interpreter.log_info("Command")

    async def call_service(self, domain, kwargs):
        return await interpreter.call_service(domain,
                                                   self.service_name,
                                                   kwargs)


class Pass(Command):
    _parser = PASS

    async def eval(self, interpreter):
        await interpreter.log_info("Passing")


class Set(Command):
    _parser = SET + List.parser(Entity.parser())("_entities") \
        + (TO | "=") \
        + Or(Numeric.parser() | StringValue.parser())("_newvalue")

    async def eval(self, interpreter):
        callfunc = interpreter.set_state
        for e in self._entities.contents:
            await callfunc(e.name, value=self._newvalue.value)


class Wait(Command):
    _parser = WAIT + (TimeStamp.parser() | RelativeTime.parser())("_time")

    def __str__(self):
        return f"task.sleep({self._time.as_seconds})"

    async def eval(self, interpreter):
        result = await interpreter.sleep(self._time.as_seconds)
        return result


class Turn(Command):
    _parser = TURN + (ON | OFF)('_newstate') \
                   + List.parser(Entity.parser())("_entities") \
                   + Optional(With.parser())("_with")

    @property
    def service_name(self):
        return 'turn_'+self._newstate.lower()

    # def kwargs(self, entity):
    #     return {'entity_id': entity.name}

    async def eval(self, interpreter):
        callfunc = interpreter.call_service
        kwargs = {}

        if hasattr(self, "_with"):
            kwargs.update(self._with.value)

        for e in self._entities.contents:
            kwargs.update({'entity_id': e.name})
            await callfunc(e.domain,
                           self.service_name,
                           kwargs)


class Toggle(Command):
    _parser = TOGGLE + Entity.parser()("_entity")

    @property
    def service_name(self):
        return 'toggle'

    async def eval(self, interpreter):
        callfunc = interpreter.call_service
        for e in self._entities.contents:
            await callfunc(e.domain,
                           self.service_name,
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

    async def eval(self, interpreter):
        if self._number.value > 0 or hasattr(self, '_use_pct'):
            service_name = "turn_on"
        else:
            service_name = "turn_off"

        callfunc = interpreter.call_service
        for e in self._entities.contents:
            await callfunc(service_name,
                           e.domain,
                           self.kwargs(e))


class Lock(Command):
    _parser = (LOCK | UNLOCK)("_type") + \
        List.parser(Entity.parser())("_entities") \
        + Optional(With.parser())("_with")

    async def eval(self, interpreter):
        service_name = self._type.lower()

        if hasattr(self, "_with"):
            kwargs = self._with.value
        else:
            kwargs = {}

        callfunc = interpreter.call_service
        for e in self._entities.contents:
            kwargs.update({'entity_id': e.name})
            await callfunc(service_name,
                           e.domain,
                           kwargs)


class Call(Command):
    _parser = CALL \
        + Entity.parser()("_service") \
        + Optional(ON + List.parser(Entity.parser())("_entities")) \
        + Optional(With.parser())("_with")

    async def eval(self, interpreter):
        domain = self._service.domain.lower()
        service_name = self._service.id.lower()
        kwargs = {}
        callfunc = interpreter.call_service

        if hasattr(self, "_with"):
            kwargs.update(self._with.value)

        if hasattr(self, "_entities"):
            for e in self._entities.contents:
                kwargs.update({'entity_id': e.name})
                await callfunc(domain,
                               service_name,
                               kwargs)
        else:
            await callfunc(domain, service_name, kwargs)
