from pyparsing import OneOrMore, Or, Suppress, ParseException
from .keywords import WHEN
from .conditionals import IfThenElse, Then, Case
from .triggers import Trigger
from .ottobase import OttoBase


class OttoScript:
    trigger = Or(Trigger.child_parsers())
    conditionals = (IfThenElse.parser() | Case.parser())
    when_expr = Suppress(WHEN) + trigger
    _parser = OneOrMore(when_expr)("triggers") + \
        OneOrMore(conditionals | Then.parser())("clauses")

    def __init__(self, interpreter, script, globals={}):
        OttoBase.set_interpreter(interpreter)
        OttoBase.set_vars(globals)
        self.parsed = False
        self.interpreter = interpreter
        self.script = script

    @property
    def parser(self):
        return self._parser

    async def parse(self):
        try:
            self.script = self.parser.parse_string(self.script)
            self.parsed = True
        except ParseException as error:
            await self.interpreter.log_error(error)
            raise(ParseException)

    @property
    def triggers(self):
        triggers = []
        for trigger in self.script.triggers.as_list():
            triggers.extend(trigger.value)
        return triggers

    async def eval(self):
        if not self.parsed:
            await self.parse()
        await self.interpreter.log_info("Executing")
        for clause in self.script.clauses.as_list():
            await clause.eval()
