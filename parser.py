from pyparsing import *
from ottolib import *

class OttoParser:
    def __init__(self):
        command = Or([cls.parser() for cls in BaseCommand.__subclasses__()])
        trigger = Or([cls.parser() for cls in BaseTrigger.__subclasses__()])
        condition = Or([cls.parser() for cls in BaseCondition.__subclasses__()])

        WHEN, THEN = map(CaselessKeyword, ["WHEN", "THEN"])

        when_expr = WHEN.suppress() + Group(trigger)("when")
        then_clause = THEN.suppress() + Group(OneOrMore(command))("actions")
        conditionclause = condition("conditions") + then_clause
        self._parser = when_expr + OneOrMore(Group(conditionclause))("condition_clauses")


    @property
    def parser(self):
        return self._parser

    def parse(self, script):
        return self.parser.parse_string(script)
