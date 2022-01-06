from pyparsing import *
from .vocab import *
#from .expressions import *
from .commands import Command
from .conditionals import Conditional
from .triggers import Trigger


class OttoScript:
    command = Or(Command.child_parsers())
    trigger = Or(Trigger.child_parsers())
    conditional = Or(Conditional.child_parsers())

    when_expr = WHEN.suppress() + Group(trigger)("when")
    then_clause = THEN.suppress() + Group(OneOrMore(command))("actions")
    conditionclause = conditional("conditions") + then_clause
    _parser = when_expr + OneOrMore(Group(conditionclause))("condition_clauses")

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
        for conditions, commands in self._parsobj.condition_clauses.as_list():
            await self.interpreter.log_info("In loop")
            result = await conditions.eval()
            await self.interpreter.log_info(f"{result}")
            if result == True:
                await self.interpreter.log_info("Conditions True")
                for command in commands:
                    await command.eval()
            else:
                await self.interpreter.log_info(f"Condition Failed")
