from pyparsing import Or, OneOrMore, opAssoc, infixNotation, Forward, Optional
from .ottobase import OttoBase
from .vocab import IF, AND, OR, NOT, THEN, ELSE, CASE, END
from .expressions import Comparison, Assignment
from .commands import Command


class Conditional(OttoBase):
    forward = Forward()

    def __str__(self):
        return " ".join([str(x) for x in self.tokens])


class Then(Conditional):
    _instructions = Or(Command.child_parsers())
    _assignment = Assignment.parser()
    _parser = Optional(THEN) \
        + OneOrMore(_instructions | _assignment)("_commands")

    async def eval(self):
        if type(self._commands) != list:
            await self._commands.eval()
            return

        for command in self._commands:
            await command.eval()
            return


class If(Conditional):
    _operators = {
                    'AND': all,
                    'OR': any,
                    'NOT': lambda x: not x
                    }

    _parser = IF \
        + infixNotation(Comparison.parser(), [
                            (NOT, 1, opAssoc.RIGHT, ),
                            (AND, 2, opAssoc.LEFT, ),
                            (OR, 2, opAssoc.LEFT, ),
                            ])("_conditions")

    def __init__(self, tokens):
        super().__init__(tokens)
        self._eval_tree = self.build_evaluator_tree()

    async def eval(self):
        await self.interpreter.log_debug('In ifclause eval')
        result = await self.eval_tree(self._eval_tree)
        return result

    async def eval_tree(self, tree):
        await self.interpreter.log_debug('In ifclause eval_tree')
        statements = []
        strings = []

        for item in tree['items']:
            if type(item) == dict:
                statements.append(await self.eval_tree(item))
            if type(item) == Comparison:
                result = await item.eval()
                statements.append(result)
                strings.append(f"\n{item}: {result}")

        result = tree['opfunc'](statements)
        await self.interpreter.log_info(
            f"If clause result: {result}: {strings}")

        return result

    def build_evaluator_tree(self):
        if type(self._conditions) == Comparison:
            tokens = ["AND", self._conditions]
        else:
            tokens = self._conditions

        comparisons = []

        for item in tokens:
            if type(item) == list:
                comparisons.append(self.build_evaluator_tree(item))
            elif type(item) == str:
                opname = item.upper()
                operand = self._operators[opname]
            else:
                comparisons.append(item)

        return {'opfunc': operand, 'items': comparisons}


class IfThen(Conditional):
    _parser = If.parser()("_if") \
            + Then.parser()("_then")

    async def eval(self):
        conditions_result = await self._if.eval()
        if conditions_result is True:
            await self._then.eval()
            return True


class IfThenElse(Conditional):
    _parser = If.parser()("_if") \
            + Optional(Conditional.forward("_conditional")) \
            + Optional(Then.parser()("_then")) \
            + Optional(ELSE + Conditional.forward("_else"))

    async def eval(self):
        conditions_result = await self._if.eval()

        if conditions_result is True:
            if hasattr(self, "_conditional"):
                await self._conditional.eval()
            if hasattr(self, "_then"):
                await self._then.eval()
        else:
            if hasattr(self, "_else"):
                await self._else.eval()


class Case(Conditional):
    _parser = CASE  \
            + OneOrMore(IfThen.parser())("_statements") \
            + Optional(ELSE + Then.parser()("_else")) \
            + END

    async def eval(self):
        foundmatch = False
        for statement in self._statements:
            if await statement.eval() is True:
                foundmatch = True
                break

        if foundmatch is False:
            if hasattr(self, '_else'):
                await self._else.eval()


Conditional.forward <<= Or(IfThenElse.parser(), Case.parser())
