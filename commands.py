from pyparsing import CaselessKeyword, Optional, Or, MatchFirst, Group
from .ottobase import OttoBase, Var
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
        if hasattr(self, "_with"):
            return self._with._value
        else:
            return {}

    async def eval(self, interpreter):
        await interpreter.log_debug(f"COMMAND: {self}")
        kwargs = self.with_data

        if hasattr(self, "_targets"):
            targets = self._targets.as_dict()
            await interpreter.log_debug(f"TARGETS: {targets}")
            for domain in targets.keys():
                await interpreter.log_debug(f"TARGET DOMAIN: {domain}")
                kwargs.update(targets[domain])

                if hasattr(self, 'domain'):
                    domain = self.domain

                await interpreter.call_service(domain,
                                               self.service_name,
                                               kwargs)
        else:
            await interpreter.log_debug(f"COMMAND DOMAIN: {self.domain}")
            await interpreter.call_service(self.domain,
                                           self.service_name,
                                           kwargs)


class Target(OttoBase):
    _parser = Group(Var.parser()("_var")
                    ^ List.parser(Entity.parser())("_values")
                    ^ (AREA + List.parser(Area.parser())("_values"))
                    )("_targets")

    def __init__(self, tokens):
        super().__init__(tokens)

        if "_var" in self._targets.keys():
            var = self.get_var(self._targets['_var'].varname)
            if type(var) == List:
                values = var.contents
            else:
                values = [var]
        else:
            values = self._targets["_values"][0].contents

        if type(values[0]) == Entity:
            self.entities = values
            self.areas = None

        if type(values[0]) == Area:
            self.entities = None
            self.areas = values

    def as_dict(self):
        # Outputs {domain1: 'area_id': [area_id1, area_id2],
        #                   'entity_id': [entity_id1, entity_id2]
        #          domain2: 'area_id': [area_id1, area_id2] ...}
        target_dict = {}
        # TODO This is hideous and needs to be cleaned up.
        if self.areas is not None:
            target_dict['areas'] = {'area_id': []}

            for area in self.areas:
                target_dict['areas']['area_id'].extend(self.expand(area.name))

        if self.entities is not None:
            for entity in self.entities:
                if entity.domain in target_dict.keys():
                    if 'entity_id' in target_dict[entity.domain].keys():
                        name = entity.name
                        target_dict[entity.domain]['entity_id'].append(name)
                    else:
                        target_dict[entity.domain]['entity_id'] = [entity.name]
                else:
                    target_dict[entity.domain] = {'entity_id': [entity.name]}

        return target_dict

    def expand(self, area_name):
        areas = []

        if area_name in self._vars['area_shortcuts'].keys():
            for area in self._vars['area_shortcuts'][area_name]:
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
        + Target.parser()("_targets") \
        + (TO | "=") \
        + Or(Numeric.parser() | StringValue.parser())("_newvalue")

    async def eval(self, interpreter):
        callfunc = interpreter.set_state
        targets = self._targets.as_dict()

        for key in targets.keys():
            for e in targets[key]['entity_id']:
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
                   + ident("_domain") \
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

    @property
    def domain(self):
        return self._domain


class Toggle(Command):
    _parser = TOGGLE \
              + ident("_domain") \
              + Target.parser()("_targets")

    @property
    def service_name(self):
        return 'toggle'


class Dim(Command):
    _parser = DIM \
        + Target.parser()("_targets") \
        + (CaselessKeyword("TO") | CaselessKeyword("BY"))("_type") \
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
        return "lock"


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

        if self._type == 'Close':
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
