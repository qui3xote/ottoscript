from pyparsing import (Group, Optional, MatchFirst, Suppress, OneOrMore)
from .keywords import AUTOMATION, RESTART, WHEN
from .datatypes import ident
from .triggers import StateTrigger, TimeTrigger
from .ottobase import OttoBase, Var
from .conditionals import IfThenElse, Case, Then


class AutoControls(OttoBase):
    parser = Group(AUTOMATION
                   + ident("name")
                   + Optional(Var()('trigger_var'))
                   + Optional(RESTART('restart_option'))
                   )

    @property
    def trigger_var(self):
        if hasattr(self, 'trigger_var'):
            return self.trigger_var.name
        else:
            return '@trigger'

    @property
    def restart(self):
        return hasattr(self, 'restart_option')


class Actions(OttoBase):
    conditionals = (IfThenElse.parser() | Case.parser())
    parser = Group(OneOrMore(conditionals | Then.parser())("clauses"))

    # @property
    # def clauses(self):
    #     if type(self._clauses) != list:
    #         return [self._clauses]
    #     else:
    #         return self._clauses

    async def eval(self, interpreter):
        for clause in self.clauses:
            await clause.eval(interpreter)


class Auto(OttoBase):
    trigger = Suppress(WHEN) \
        + MatchFirst(StateTrigger.parsers() | TimeTrigger.parsers())

    parser = Group(AutoControls()("controls")
                   + OneOrMore(trigger)("triggers")
                   + Group(Actions())('actions'))



#
#
#
#
# class GlobalVarHandler(OttoBase):
#     _parser = Group(ZeroOrMore(Assignment.parser())("_assignments"))
#     _stashed_vars = None
#
#     def __init__(self, tokens):
#         tokens = tokens[0]
#         super().__init__(tokens)
#
#     @property
#     def assignments(self):
#         if not hasattr(self, "_assignments"):
#             return []
#         elif type(self._assignments) != list:
#             return [self._assignments]
#         else:
#             return self._assignments
#
#     async def eval(self, interpreter):
#         for assignment in self.assignments:
#             await assignment.eval(interpreter)
#
#         self.stash(self._vars)
#
#     @classmethod
#     def stash(cls, vars):
#         cls._stashed_vars = vars
#
#     @classmethod
#     def fetch(cls):
#         return cls._stashed_vars
#
#
