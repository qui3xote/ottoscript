from pyparsing import Or, Group, OneOrMore
from .vocab import WHEN
from .conditionals import IfThenElse, Then, Case
from .triggers import Trigger
from .ottobase import OttoBase


class OttoScript:
    trigger = Or(Trigger.child_parsers())
    conditionals = (IfThenElse.parser() | Case.parser())
    when_expr = WHEN.suppress() + Group(trigger)("when")
    _parser = when_expr + \
        (OneOrMore(conditionals) | Then.parser())("condition_clauses")

    def __init__(self, interpreter, script):
        OttoBase.set_interpreter(interpreter)
        self.interpreter = interpreter
        self._parsobj = self.parse(script)

    @property
    def parser(self):
        return self._parser

    def parse(self, script):
        return self.parser.parse_string(script)

    @property
    def trigger(self):
        return self._parsobj.when[0]

    async def execute(self):
        await self.interpreter.log_info("Executing")
        for conditions in self._parsobj.condition_clauses.as_list():
            await self.interpreter.log_info("In loop")
            await conditions.eval()
