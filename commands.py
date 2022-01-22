from pyparsing import CaselessKeyword, Optional, Or, Group, MatchFirst
from .ottobase import OttoBase
from .datatypes import Numeric, Entity, StringValue, List, Area, ident
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
ARM = CaselessKeyword("ARM")
DISARM = CaselessKeyword("DISARM")
CLOSE = CaselessKeyword("CLOSE")
OPEN = CaselessKeyword("OPEN")


class Command(OttoBase):
    _kwd = None

    def __str__(self):
        return " ".join([str(x) for x in self.tokens.as_list()])

    @property
    def with_data(self):
        if hasattr(self,"_with"):
            return self._with._value
        else:
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
                    | (AREA
                       + List.parser(Area.parser())
                       + Optional(ident())("_area_domain")
                       )("_areas")
                    )("_targets")

    def as_dict(self):
        # Outputs {domain1: 'area_id': [area_id1, area_id2],
        #                   'entity_id': [entity_id1, entity_id2]
        #          domain2: 'area_id': [area_id1, area_id2] ...}
        target_dict = {}

        if '_areas' in self._targets.keys():
            for area in self._targets['_areas'][0].contents:
                if "area_domain" in target_dict.keys():
                    if 'area_id' in target_dict[area.domain].keys():
                        target_dict[area.domain]['area_id'].extend(self.expand(area.name))
                    else:
                        target_dict[area.domain]['area_id'] = self.expand(area.name)
                else:
                    target_dict[area.domain] = {'area_id': self.expand(area.name)}

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

    def expand(self, area_name):
        areas = []
        if area_name in self._vars['area_domains'].keys():
            for area in self._vars['area_domains'][area_name]:
                areas.extend(self.expand(area))
        else:
            areas = [area_name]

        return areas



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
    _parser = (LOCK | UNLOCK)("_type") \
        + Target.parser()("_targets") \
        + Optional(With.parser())("_with")

    @property
    def service_name(self):
        return self._type.lower()

    @property
    def domain(self):
        return "light"


class Arm(Command):
    _states = map(CaselessKeyword, "HOME AWAY NIGHT VACATION".split(" "))
    _parser = ARM \
        + MatchFirst(_states)("_type") \
        + Target.parser()("_targets") \
        + Optional(With.parser())("_with")

    @property
    def service_name(self):
        return f"alarm_arm_{self._type.lower()}"

    @property
    def domain(self):
        return "alarm_control_panel"


class Disarm(Command):
    _parser = DISARM \
        + Target.parser()("_targets") \
        + Optional(With.parser())("_with")

    @property
    def service_name(self):
        return "alarm_disarm"

    @property
    def domain(self):
        return "alarm_control_panel"


class OpenClose(Command):
    _parser = (OPEN | CLOSE)("_type") \
        + Target.parser()("_targets") \
        + Optional(TO + Numeric.parser()("_position"))

    @property
    def with_data(self):
        if hasattr(self, "_position"):
            position = self._position._value
        else:
            position = 100

        if self._type == 'Open':
            position = 100 - position

        return {'position': position}

    @property
    def service_name(self):
        return "set_cover_position"

    @property
    def domain(self):
        return "cover"


class Call(Command):
    _parser = CALL \
        + Entity.parser()("_service") \
        + Optional(ON + Target.parser()("_targets")) \
        + Optional(With.parser())("_with")

    @property
    def domain(self):
        return self._service.domain

    @property
    def service_name(self):
        return self._service.id
