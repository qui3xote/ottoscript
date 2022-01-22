from pyparsing import CaselessKeyword, Optional, Or, Group
from .ottobase import OttoBase
from .datatypes import Numeric, Entity, StringValue, List, Area
from .keywords import ON, TO, OFF, AREA
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
DIM = CaselessKeyword("DIM")


class Command(OttoBase):
    _kwd = None

    def __str__(self):
        return " ".join([str(x) for x in self.tokens.as_list()])

    @property
    def with_data(self):
        return {}

    async def eval(self, interpreter):
        kwargs = self.with_data

        if hasattr(self, "_targets"):
            targets = self._targets.as_dict()

            for domain in targets.keys():
                kwargs.update(targets[domain])

                if hasattr(self, 'domain'):
                    domain = self.domain

                await interpreter.call_service(domain, self.service_name, kwargs)
        else:
            await interpreter.call_service(self.domain, self.service_name, kwargs)


class Target(OttoBase):
    _parser = Group(List.parser(Entity.parser())("_entities")
                    | (AREA + List.parser(Area.parser())("_areas"))
                    )("_targets")

    def as_dict(self):
        target_dict = {}

        if '_areas' in self._targets.keys():
            for area in self._targets['_areas'][0].contents:
                if area.domain in target_dict.keys():
                    if 'area_id' in target_dict[area.domain].keys():
                        target_dict[area.domain]['area_id'].append(area.name)
                    else:
                        target_dict[area.domain]['area_id'] = [area.name]
                else:
                    target_dict[area.domain] = {'area_id': [area.name]}

        if '_entities' in self._targets.keys():
            for entity in self._targets['_entities'][0].contents:
                if entity.domain in target_dict.keys():
                    if 'entity_id' in target_dict[entity.domain].keys():
                        target_dict[entity.domain]['entity_id'].append(entity.name)
                    else:
                        target_dict[entity.domain]['entity_id'] = [entity.name]
                else:
                    target_dict[entity.domain] = {'entity_id': [entity.name]}

        return target_dict


class Pass(Command):
    _parser = PASS

    async def eval(self, interpreter):
        await interpreter.log_info("Passing")


class Set(Command):
    _parser = SET \
        + List.parser(Entity.parser())("_entities") \
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
                   + Target.parser()("_targets") \
                   + Optional(With.parser())("_with")

    @property
    def service_name(self):
        return 'turn_'+self._newstate.lower()

    @property
    def with_data(self):
        if hasattr(self, "_with"):
            return self._with.value
        else:
            return {}


class Toggle(Command):
    _parser = TOGGLE + Target.parser()("_targets")

    @property
    def service_name(self):
        return 'toggle'


class Dim(Command):
    _kwd = DIM
    _parser = _kwd + Target.parser()("_targets") + \
        (CaselessKeyword("TO") | CaselessKeyword("BY"))("_type") \
        + Numeric.parser()("_number") \
        + Optional('%')("_use_pct")

    @property
    def with_data(self):
        if self._type.upper() == 'TO':
            param = 'brightness'
        else:
            param = 'brightness_step'

        if hasattr(self, '_use_pct'):
            param += '_pct'

        return {param: self._number.value}

    @property
    def service_name(self):
        if self._number.value > 0 or hasattr(self, '_use_pct'):
            return "turn_on"
        else:
            return "turn_off"

    @property
    def domain(self):
        return "light"


class Lock(Command):
    _parser = (LOCK | UNLOCK)("_type") + \
        List.parser(Entity.parser())("_entities") \
        + Optional(With.parser())("_with")

    @property
    def service_name(self):
        return self._type.lower()

    @property
    def domain(self):
        return "light"


class Call(Command):
    _parser = CALL \
        + Entity.parser()("_service") \
        + Optional(ON + Target.parser()("_targets")) \
        + Optional(With.parser())("_with")

    @property
    def with_data(self):
        if hasattr(self, "_with"):
            return self._with.value
        else:
            return {}

    @property
    def domain(self):
        return self._service.domain

    @property
    def service_name(self):
        return self._service.name
