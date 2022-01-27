from .ottobase import OttoBase
from .keywords import *
from .datatypes import *
from .interpreters import ExampleInterpreter

# from pyparsing import (OneOrMore,
#                        Or,
#                        Suppress,
#                        Optional,
#                        ParseException,
#                        ZeroOrMore,
#                        Group)
# from .keywords import WHEN
# from .conditionals import IfThenElse, Then, Case
# from .triggers import Trigger
# from .ottobase import OttoBase
# from .controls import AutoDefinition
# from .expressions import Assignment
#
#
# class Actions(OttoBase):
#     _conditionals = (IfThenElse.parser() | Case.parser())
#     _parser = OneOrMore(_conditionals | Then.parser())("_clauses")
#
#     @property
#     def clauses(self):
#         if type(self._clauses) != list:
#             return [self._clauses]
#         else:
#             return self._clauses
#
#     async def eval(self, interpreter):
#         for clause in self.clauses:
#             await clause.eval(interpreter)
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
# class OttoScript:
#     _globals = GlobalVarHandler.parser()
#     _trigger = Or(Trigger.child_parsers())
#     _when_expr = Suppress(WHEN) + _trigger
#     _parser = _globals("globals") \
#         + Optional(AutoDefinition.parser())("_controls") \
#         + OneOrMore(_when_expr)("triggers") \
#         + Group(Actions.parser())('actions')
#
#     def __init__(self, script, passed_globals={}):
#         GlobalVarHandler.clear_vars()
#         GlobalVarHandler.update_vars(passed_globals)
#
#         try:
#             self.script = self._parser.parse_string(script)
#         except ParseException as error:
#             raise(error)
#
#     @property
#     def parser(self):
#         return self._parser
#
#     @property
#     def global_vars(self):
#         return GlobalVarHandler.fetch()
#
#     @property
#     def triggers(self):
#         return self.script.triggers.as_list()
#
#     @property
#     def controls(self):
#         if self.script._controls != '':
#             return self.script._controls[0]
#         else:
#             return None
#
#     @property
#     def actions(self):
#         return self.script.actions[0]
#
#     async def update_globals(self, interpreter):
#         await self.script.globals.eval(interpreter)
