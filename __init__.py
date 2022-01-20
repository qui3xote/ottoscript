from copy import deepcopy
from pyparsing import OneOrMore, Or, Suppress, Optional, ParseException, ZeroOrMore
from .keywords import WHEN
from .conditionals import IfThenElse, Then, Case
from .triggers import Trigger
from .ottobase import OttoBase
from .controls import AutoDefinition
from .expressions import Assignment


class Actions(OttoBase):
    _conditionals = (IfThenElse.parser() | Case.parser())
    _parser = OneOrMore(_conditionals | Then.parser())("_clauses")

    @property
    def clauses(self):
        if type(self._clauses) != list:
            return [self._clauses]
        else:
            return self._clauses

    async def eval(self, interpreter):
        for clause in self.clauses:
            clause.eval(interpreter)


class Global(OttoBase):
    _parser = ZeroOrMore(Assignment.parser())("_assignments")

    @property
    def assignments(self):
        if type(self._assignments) != list:
            return [self._assignments]
        else:
            return self._assignmentsrs

    async def eval(self, interpreter):
        for assignment in self.assignments:
            assignment.eval(interpreter)


class OttoScript:
    _globals = Global.parser()
    _trigger = Or(Trigger.child_parsers())
    _when_expr = Suppress(WHEN) + _trigger
    _parser = _globals("globals") \
        + Optional(AutoDefinition.parser())("_controls") \
        + OneOrMore(_when_expr)("triggers") \
        + Actions.parser()('actions')

    def __init__(self, script, passed_globals={}):
        Global.clear_vars()

        try:
            self.script = self._parser.parse_string(script)
        except ParseException as error:
            raise(error)

        self.script.globals.update_vars(passed_globals)
        self.script.globals.eval()

    @property
    def parser(self):
        return self._parser

    @property
    def globals(self):
        return deepcopy(self._script._vars)

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
    def actions(self):
        return self.script.actions[0]
