from pyparsing import (Group, Optional, MatchFirst,
                       Suppress, OneOrMore, ZeroOrMore)
from .keywords import AUTOMATION, RESTART, WHEN
from .ottobase import OttoBase
from .datatypes import ident, Var
from .commands import Assignment
from .conditionals import IfThenElse, Case, Then
from .triggers import StateTrigger, TimeTrigger


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
    conditionals = (IfThenElse() | Case())
    parser = Group(OneOrMore(conditionals | Then())("clauses"))

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
        + MatchFirst(StateTrigger.parsers() + TimeTrigger.parsers())

    parser = Group(AutoControls()("controls")
                   + OneOrMore(trigger)("triggers")
                   + Group(Actions())('actions'))


class GlobalParser(OttoBase):
    parser = Group(ZeroOrMore(Assignment("external"))("assignments"))

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
