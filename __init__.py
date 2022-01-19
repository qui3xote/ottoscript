from pyparsing import OneOrMore, Or, Suppress, Optional, ParseException
from .keywords import WHEN
from .conditionals import IfThenElse, Then, Case
from .triggers import Trigger
from .ottobase import OttoBase
from .controls import AutoDefinition


class OttoScript:
    trigger = Or(Trigger.child_parsers())
    conditionals = (IfThenElse.parser() | Case.parser())
    when_expr = Suppress(WHEN) + trigger
    _parser = Optional(AutoDefinition.parser())("_controls") \
        + OneOrMore(when_expr)("triggers") \
        + OneOrMore(conditionals | Then.parser())("clauses")

    def __init__(self, interpreter, script, globals={}):
        OttoBase.set_interpreter(interpreter)
        OttoBase.set_vars(globals)
        self.interpreter = interpreter

        try:
            self.script = self._parser.parse_string(script)
        except ParseException as error:
            raise(error)

        if type(self.script._controls) == 'AutoDefinition':
            print(f"{self.script._controls}")
            self.interpreter.set_controls(self.script._controls)

    @property
    def parser(self):
        return self._parser

    @property
    def triggers(self):
        return self.script.triggers.as_list()

    @property
    def clauses(self):
        return self.script.clauses.as_list()
