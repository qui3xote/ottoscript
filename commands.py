from pyparsing import CaselessKeyword, Optional, Or, MatchFirst, Group, Literal
from .ottobase import OttoBase
from .datatypes import Numeric, Entity, String, List, Area, ident, Dict, Var, Target
from .keywords import WITH, ON, TO, OFF, AREA
#from .time import RelativeTime, TimeStamp

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


class Assignment(OttoBase):
    parser = Group(Var(fetch=False)("var")
                   + Literal('=')
                   + (Var()
                      ^ Entity()
                      ^ Dict()
                      ^ Numeric()
                      ^ String()
                      ^ (AREA + List(Area()))
                      ^ List()
                      )("value")
                   )

    def __init__(self, tokens):
        super().__init__(tokens)
        self.vars.update(self.var.name, self.value[0])


class With(OttoBase):
    parser = Group(WITH + Dict()("value"))

    async def eval(self, interpreter):
        return await self.value.eval()


class Command(OttoBase):
    pass

    async def eval(self, interpreter):

        targets = await self.targets.eval(interpreter)
        if hasattr(self, "with"):
            data = await self.data.eval(interpreter)
            targets.update(data)

        result = await interpreter.call_service(self.domain,
                                                self.service_name,
                                                targets)
        return result


class Pass(Command):
    parser = Group(PASS('pass'))

    async def eval(self, interpreter):
        await interpreter.log.info("Passing")


class Set(Command):
    parser = Group(SET
                   + List(Entity())("targets")
                   + (TO | "=")
                   + (Var()("new_value")
                      ^ Entity()("new_value")
                      ^ String()("new_value")
                      ^ Numeric()("new_value"))
                   )

    async def eval(self, interpreter):
        callfunc = interpreter.set_state
        value = await self.new_value.eval(interpreter)

        results = []
        for e in self.targets.contents:
            results.append(await callfunc(e.name, value=value))

        return results


# class Wait(Command):
#     parser = WAIT + (TimeStamp() | RelativeTime())("_time")
#
#     def __str__(self):
#         return f"task.sleep({self._time.as_seconds})"
#
#     async def eval(self, interpreter):
#         result = await interpreter.sleep(self._time.as_seconds)
#         return result

#
class Turn(Command):
    parser = Group(TURN + (ON ^ OFF)('command')
                   + ident("domain")
                   + Target()("targets")
                   + Optional(With()("data")))

    @property
    def service_name(self):
        return 'turn_'+self.command.lower()




#
# class Toggle(Command):
#     parser = TOGGLE \
#               + ident("_domain") \
#               + Target()("_targets")
#
#     @property
#     def service_name(self):
#         return 'toggle'
#
#
# class Dim(Command):
#     parser = DIM \
#         + Target()("_targets") \
#         + (CaselessKeyword("TO") | CaselessKeyword("BY"))("_type") \
#         + Numeric()("_number") \
#         + Optional('%')("_use_pct")
#
#     @property
#     def with_data(self):
#         if self._type.upper() == 'TO':
#             param = 'brightness'
#         else:
#             param = 'brightness_step'
#
#         if hasattr(self, '_use_pct'):
#             param += '_pct'
#
#         return {param: self._number.value}
#
#     @property
#     def service_name(self):
#         if self._number.value > 0 or hasattr(self, '_use_pct'):
#             return "turn_on"
#         else:
#             return "turn_off"
#
#     @property
#     def domain(self):
#         return "light"
#
#
# class Lock(Command):
#     parser = (LOCK | UNLOCK)("_type") \
#         + Target()("_targets") \
#         + Optional(With())("_with")
#
#     @property
#     def service_name(self):
#         return self._type.lower()
#
#     @property
#     def domain(self):
#         return "lock"
#
#
# class Arm(Command):
#     _states = map(CaselessKeyword, "HOME AWAY NIGHT VACATION".split(" "))
#     parser = ARM \
#         + MatchFirst(_states)("_type") \
#         + Target()("_targets") \
#         + Optional(With())("_with")
#
#     @property
#     def service_name(self):
#         return f"alarm_arm_{self._type.lower()}"
#
#     @property
#     def domain(self):
#         return "alarm_control_panel"
#
#
# class Disarm(Command):
#     parser = DISARM \
#         + Target()("_targets") \
#         + Optional(With())("_with")
#
#     @property
#     def service_name(self):
#         return "alarm_disarm"
#
#     @property
#     def domain(self):
#         return "alarm_control_panel"
#
#
# class OpenClose(Command):
#     parser = (OPEN | CLOSE)("_type") \
#         + Target()("_targets") \
#         + Optional(TO + Numeric()("_position"))
#
#     @property
#     def with_data(self):
#         if hasattr(self, "_position"):
#             position = self._position._value
#         else:
#             position = 100
#
#         if self._type.lower == 'close':
#             position = 100 - position
#
#         return {'position': position}
#
#     @property
#     def service_name(self):
#         return "set_cover_position"
#
#     @property
#     def domain(self):
#         return "cover"
#
#
# class Call(Command):
#     parser = CALL \
#         + Entity()("_service") \
#         + Optional(ON + Target()("_targets")) \
#         + Optional(With())("_with")
#
#     @property
#     def domain(self):
#         return self._service.domain
#
#     @property
#     def service_name(self):
#         return self._service.id
