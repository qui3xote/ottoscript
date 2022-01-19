from pyparsing import OneOrMore, Or, Suppress, Optional, ParseException
from .keywords import WHEN
from .conditionals import IfThenElse, Then, Case
from .triggers import Trigger
# from .ottobase import OttoBase
from .controls import AutoDefinition


class OttoScript:
    trigger = Or(Trigger.child_parsers())
    conditionals = (IfThenElse.parser() | Case.parser())
    when_expr = Suppress(WHEN) + trigger
    _parser = Optional(AutoDefinition.parser())("_controls") \
        + OneOrMore(when_expr)("triggers") \
        + OneOrMore(conditionals | Then.parser())("clauses")

    def __init__(self, script):
        # OttoBase.set_interpreter(interpreter)
        # OttoBase.set_vars(globals)
        # interpreter = interpreter

        try:
            self.script = self._parser.parse_string(script)
        except ParseException as error:
            raise(error)

    @property
    def parser(self):
        return self._parser

    @property
    def triggers(self):
        return self.script.triggers.as_list()

    @property
    def controls(self):
        if self.script._controls != '':
            return self.script._controls[0]
        else:
            return None

    @property
    def clauses(self):
        return self.script.clauses.as_list()
