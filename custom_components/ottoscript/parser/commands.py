from pyparsing import CaselessKeyword, Optional, MatchFirst, Group, Literal
from .base import OttoBase
from .datatypes import (Number,
                        Entity,
                        String,
                        List,
                        Area,
                        ident,
                        Dict,
                        Var,
                        Target,
                        Input)
from .keywords import WITH, ON, TO, OFF, AREA
from .time import RelativeTime, TimeStamp

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
    parser = Group(
        Var()("var")
        + Literal('=')
        + (Var()
           | Entity()
           | Dict()
           | Number()
           | String()
           | (AREA + List(Area()))
           | List()
           )("_value")
    )

    def __init__(self, tokens, namespace='local'):
        super().__init__(tokens)
        self.namespace = namespace

    async def eval(self):
        self.exec()

    def exec(self):
        if self.namespace == 'local':
            self.ctx.update_vars({self.var.name: self._value[0]})
        elif self.namespace == 'global':
            self.ctx.update_global_vars({self.var.name: self._value[0]})


class With(OttoBase):
    parser = Group(WITH + Dict()("_value"))

    async def eval(self):
        return await self._value.eval()


class Command(OttoBase):

    async def eval(self):
        kwargs = self.kwargs

        if hasattr(self, 'targets'):
            targets = await self.targets.eval()
            kwargs.update(targets)

        if hasattr(self, "with_data"):
            data = await self.with_data.eval()
            kwargs.update(data)

        if hasattr(self, "static_data"):
            kwargs.update(self.static_data)

        result = await self.ctx.interpreter.call_service(self.domain,
                                                         self.service_name,
                                                         **kwargs)
        return result

    @property
    def kwargs(self):
        if hasattr(self, '_kwargs'):
            return self._kwargs
        else:
            return {}

    @kwargs.setter
    def kwargs(self, value: dict):
        if hasattr(self, '_kwargs'):
            self._kwargs.update(value)
        else:
            self._kwargs = value

    @classmethod
    def parsers(cls):
        return [subclass() for subclass in cls.__subclasses__()]


class Pass(Command):
    parser = Group(PASS('pass'))

    async def eval(self):
        await self.ctx.interpreter.log.debug("Passing")


class Set(Command):
    parser = Group(
        SET
        + List(Entity())("targets")
        + (TO | "=")
        + (Var()("new_value")
           ^ Entity()("new_value")
           ^ String()("new_value")
           ^ Number()("new_value"))
    )

    async def eval(self):
        callfunc = self.ctx.interpreter.set_state
        value = await self.new_value.eval()

        results = []
        for e in self.targets.contents:
            if type(e) == Var:
                e = e.fetch()
            results.append(await callfunc(e.name, value=value))

        return results


class Wait(Command):
    parser = Group(WAIT + (TimeStamp()("time") | RelativeTime()("time")))

    async def eval(self):
        result = await self.ctx.interpreter.sleep(self.time.seconds)
        return result


class Turn(Command):
    parser = Group(
        TURN + (ON ^ OFF)('command')
        + ident("domain")
        + Target()("targets")
        + Optional(
            With()("with_data")
        )
    )

    @property
    def service_name(self):
        return 'turn_' + self.command.lower()


class Toggle(Command):
    parser = Group(
        TOGGLE
        + ident("domain")
        + Target()("targets")
    )

    @property
    def service_name(self):
        return 'toggle'


class Dim(Command):
    parser = Group(
        DIM
        + Target()("targets")
        + (CaselessKeyword("TO") | CaselessKeyword("BY"))("type")
        + Input("numeric")("number")
        + Optional('%')("use_pct")
    )

    @property
    def param(self):
        if self.type.upper() == 'TO':
            param = 'brightness'
        else:
            param = 'brightness_step'

        if hasattr(self, 'use_pct'):
            param += '_pct'

        return param

    @property
    def domain(self):
        return "light"

    async def eval(self):

        number = await self.number.eval()

        if number > 0 or 'step' in self.param:
            self.service_name = "turn_on"
            self.kwargs = {self.param: number}
        else:
            self.service_name = "turn_off"

        return await super().eval()


class Lock(Command):
    parser = Group(
        (LOCK ^ UNLOCK)("type")
        + Target()("targets")
        + Optional(
            With()("with_data")
        )
    )

    @property
    def service_name(self):
        return self.type.lower()

    @property
    def domain(self):
        return "lock"


class Arm(Command):
    _states = map(CaselessKeyword, "HOME AWAY NIGHT VACATION".split(" "))
    parser = Group(
        ARM
        + MatchFirst(_states)("type")
        + Target()("targets")
        + Optional(
            With()("with_data")
        )
    )

    @property
    def service_name(self):
        return f"alarm_arm_{self.type.lower()}"

    @property
    def domain(self):
        return "alarm_control_panel"


class Disarm(Command):
    parser = Group(
        DISARM
        + Target()("targets")
        + Optional(
            With()("with_data")
        )
    )

    @property
    def service_name(self):
        return "alarm_disarm"

    @property
    def domain(self):
        return "alarm_control_panel"


class OpenClose(Command):
    parser = Group(
        (OPEN | CLOSE)("type")
        + Target()("targets")
        + Optional(
            TO + (
                Number()("position")
                | Var()("position")
                | Entity()("position"))
        )
    )

    @property
    def static_data(self):
        if hasattr(self, "position"):
            position = self.position._value
        else:
            position = 100

        if self.type.lower() == 'close':
            position = 100 - position

        return {'position': position}

    @property
    def service_name(self):
        return "set_cover_position"

    @property
    def domain(self):
        return "cover"


class Call(Command):
    parser = Group(
        CALL
        + Entity()("service")
        + Optional(
            ON + Target()("targets")
        )
        + Optional(
            With()("with_data")
        )
    )

    @property
    def domain(self):
        return self.service.domain

    @property
    def service_name(self):
        return self.service.id
