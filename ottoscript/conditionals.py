import operator as op
from pyparsing import (Group, Or, OneOrMore, opAssoc,
                       infixNotation, Forward, Optional, MatchFirst)
from .datatypes import String, Number, Var, Entity
from .ottobase import OttoBase
from .keywords import IF, AND, OR, NOT, THEN, ELSE, CASE, END
from .commands import Command, Assignment


class Comparison(OttoBase):

    operators = {
        '==': op.eq,
        '<=': op.le,
        '>=': op.ge,
        '!=': op.ne,
        '<': op.lt,
        '>': op.gt
    }

    term = (String()
            | Number()
            | Entity()
            | Var()
            )

    parser = Group(term("left")
                   + MatchFirst([x for x in operators.keys()])("operand")
                   + term("right")
                   )

    def __init__(self, tokens):
        super().__init__(tokens)
        self.opfunc = self.operators[self.operand]
        self.left = self.left[0]
        self.right = self.right[0]

    async def eval(self):
        left = await self.left.eval()
        right = await self.right.eval()
        result = self.opfunc(left, right)

        msg = f"Comparison {result}:"
        msg += f" {str(self)}"
        msg += f" evaluated to ({right} {self.operand} {left})"
        await self.ctx.interpreter.log.debug(msg)
        return result


class Conditional(OttoBase):
    forward = Forward()


class Then(Conditional):
    instructions = Or(Command.parsers())
    parser = Group(Optional(THEN)
                   + OneOrMore(MatchFirst(Command.parsers())
                               | Assignment("local")
                               | Conditional.forward)("commands")
                   )

    async def eval(self):
        results = []
        for command in self.commands:
            await self.ctx.interpreter.log.info(f"Executing {str(command)}")
            result = await command.eval()
            results.append(result)
        return results


class If(Conditional):
    operators = {
        'AND': all,
        'OR': any,
        'NOT': lambda x: not x
    }

    parser = Group(IF
                   + infixNotation(Comparison(), [
                       (NOT, 1, opAssoc.RIGHT, ),
                       (AND, 2, opAssoc.LEFT, ),
                       (OR, 2, opAssoc.LEFT, ),
                   ])("conditions")
                   )

    def __init__(self, tokens):
        super().__init__(tokens)
        if type(self.conditions) == Comparison:
            conditions = ["AND", self.conditions]
        else:
            conditions = self.conditions

        self._eval_tree = self.build_evaluator_tree(conditions)

    def __str__(self):
        if type(self.conditions) == list:
            return " ".join(['IF'] + [str(x) for x in self.conditions])
        else:
            return " ".join([str(x) for x in self.tokens])

    async def eval(self):
        result = await self.eval_tree(self._eval_tree)
        await self.ctx.interpreter.log.info(
            f"'{str(self)}' is {result}. "
            + f"{'Executing' if result else 'Skipping'}"
            + " commands."
        )
        return result

    async def eval_tree(self, tree):
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

        return result

    def build_evaluator_tree(self, conditions):
        comparisons = []

        for item in conditions:
            if type(item) == list:
                comparisons.append(self.build_evaluator_tree(item))
            elif type(item) == str:
                opname = item.upper()
                operand = self.operators[opname]
            else:
                comparisons.append(item)

        return {'opfunc': operand, 'items': comparisons}


class IfThen(Conditional):
    parser = Group(If()("conditions")
                   + Then()("actions")
                   + END
                   )

    async def eval(self):
        conditions_result = await self.conditions.eval()
        if conditions_result is True:
            result = await self.actions.eval()
            return result

        return False


class IfThenElse(Conditional):
    parser = Group(If()("conditions")
                   + Then()("actions")
                   + Optional(ELSE + (Conditional.forward("fallback")
                                      | Then()("fallback")
                                      )
                              )
                   + END
                   )

    async def eval(self):
        conditions_result = await self.conditions.eval()

        result = None
        if conditions_result is True:
            result = await self.actions.eval()
        else:
            if hasattr(self, "fallback"):
                result = await self.fallback.eval()

        return result


class Case(Conditional):
    parser = Group(CASE
                   + OneOrMore(IfThen())("options")
                   + Optional(ELSE + Then()("fallback"))
                   + END)

    async def eval(self):
        selected = None

        for n, statement in enumerate(self.options):
            if await statement.eval() is not False:
                selected = n + 1
                break

        if selected is None:
            if hasattr(self, 'fallback'):
                await self.fallback.eval()
                selected = 0

        return selected


Conditional.forward <<= Or(IfThenElse(), Case())
