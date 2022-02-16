from pyparsing import (
    Group,
    OneOrMore,
    opAssoc,
    infixNotation,
    Forward,
    Optional,
    MatchFirst
)
from .datatypes import String, Number, Var, Entity, Input
from .ottobase import OttoBase
from .keywords import (
    IF,
    AND,
    OR,
    NOT,
    THEN,
    ELSE,
    CASE,
    END,
    SWITCH,
    DEFAULT,
    OPERATORS)
from .commands import Command, Assignment


class Comparison(OttoBase):

    term = (
        String()
        | Number()
        | Entity()
        | Var()
    )

    parser = Group(
        term("left")
        + MatchFirst([x for x in OPERATORS.keys()])("operand")
        + term("right")
    )

    def __init__(self, tokens):
        super().__init__(tokens)
        self.opfunc = OPERATORS[self.operand]
        self.left = self.left[0]
        self.right = self.right[0]

    async def eval(self):
        left = await self.left.eval()
        right = await self.right.eval()
        result = self.opfunc(left, right)

        msg = f"Comparison {result}:"
        msg += f" {str(self)}"
        msg += f" evaluated to ({left} {self.operand} {right})"
        await self.ctx.interpreter.log.info(msg)
        return result


class Conditional(OttoBase):
    forward = Forward()


class CommandBlock(OttoBase):
    parser = Group(
        Optional(THEN)
        + OneOrMore(
            MatchFirst(Command.parsers())
            | Assignment("local")
            | Conditional.forward
        )("commands")
    )

    async def eval(self):
        results = []
        for command in self.commands:
            await self.ctx.interpreter.log.info(f"Executing {str(command)}")
            result = await command.eval()
            results.append(result)
        return results


class Condition(Conditional):
    operators = {
        'AND': all,
        'OR': any,
        'NOT': lambda x: not x
    }

    parser = Group(
        infixNotation(
            Comparison(),
            [
                (NOT, 1, opAssoc.RIGHT, ),
                (AND, 2, opAssoc.LEFT, ),
                (OR, 2, opAssoc.LEFT, ),
            ]
        )("conditions")
    )

    def __init__(self, tokens):
        super().__init__(tokens)
        if type(self.conditions) == Comparison:
            conditions = ["AND", self.conditions]
        else:
            conditions = self.conditions

        self._eval_tree = self.build_evaluator_tree(conditions)

    def __str__(self):
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


class IfThenElse(Conditional):
    parser = Group(
        IF + Condition()("conditions")
        + CommandBlock()("actions")
        + Optional(
            ELSE + CommandBlock()("fallback")
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


class Switch(Conditional):
    parser = Group(
        SWITCH
        + Optional(Input()('left'))
        + OneOrMore(
            Group(
                CASE
                + (Condition()("condition") | Input()("right"))
                + CommandBlock()("commands")
            )
        )("cases")
        + Optional(
            DEFAULT + CommandBlock()
        )("fallback")
        + END
    )

    async def eval(self):
        selected = None

        for n, case in enumerate(self.cases):
            print(case)
            run = False
            if hasattr(self, 'left') and 'right' in case.keys():
                left = await self.left.eval()
                right = await case['right'].eval()
                run = left == right
            else:
                run = await case['condition'].eval()

            if run is True:
                selected = n + 1
                await case['commands'].eval()
                break

        if selected is None:
            if hasattr(self, 'fallback'):
                await self.fallback[-1].eval()
                selected = 0

        return selected


Conditional.forward <<= MatchFirst(IfThenElse(), Switch())
