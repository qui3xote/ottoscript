import operator as op
from pyparsing import (Group, Or, OneOrMore, opAssoc,
                       infixNotation, Forward, Optional, MatchFirst)
from .datatypes import String, Numeric, Var, Entity
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
            | Numeric()
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

    async def eval(self, interpreter):
        left = await self.left.eval(interpreter)
        right = await self.right.eval(interpreter)
        result = self.opfunc(left, right)

        msg = f"Condition {result}: {self.opfunc.__name__}"
        msg += f" {str(self.right)} {self.operand} {self.left}"
        msg += f" evaluated to ({right} {self.operand} {left})"
        await interpreter.log.debug(msg)
        return result


class Conditional(OttoBase):
    forward = Forward()


class Then(Conditional):
    instructions = Or(Command.parsers())
    parser = Group(Optional(THEN)
                   + OneOrMore(MatchFirst(Command.parsers())
                               | Assignment("internal")
                               | Conditional.forward)("commands")
                   )

    async def eval(self, interpreter):
        results = []
        for command in self.commands:
            await interpreter.log.debug(f"THEN {command}")
            result = await command.eval(interpreter)
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

    async def eval(self, interpreter):
        await interpreter.log.debug('In ifclause eval')
        result = await self.eval_tree(self._eval_tree, interpreter)
        return result

    async def eval_tree(self, tree, interpreter):
        await interpreter.log.debug('In ifclause eval_tree')
        statements = []
        strings = []

        for item in tree['items']:
            if type(item) == dict:
                statements.append(await self.eval_tree(item, interpreter))
            if type(item) == Comparison:
                result = await item.eval(interpreter)
                statements.append(result)
                strings.append(f"\n{item}: {result}")

        result = tree['opfunc'](statements)
        await interpreter.log.info(
            f"If clause result: {result}: {strings}")

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

    async def eval(self, interpreter):
        conditions_result = await self.conditions.eval(interpreter)
        if conditions_result is True:
            result = await self.actions.eval(interpreter)
            print(result)
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

    async def eval(self, interpreter):
        conditions_result = await self.conditions.eval(interpreter)

        result = None
        if conditions_result is True:
            result = await self.actions.eval(interpreter)
        else:
            if hasattr(self, "fallback"):
                result = await self.fallback.eval(interpreter)

        return result


class Case(Conditional):
    parser = Group(CASE
                   + OneOrMore(IfThen())("options")
                   + Optional(ELSE + Then()("fallback"))
                   + END)

    async def eval(self, interpreter):
        selected = None

        for n, statement in enumerate(self.options):
            if await statement.eval(interpreter) is not False:
                selected = n + 1
                break

        if selected is None:
            if hasattr(self, 'fallback'):
                await self.fallback.eval(interpreter)
                selected = 0

        return selected


Conditional.forward <<= Or(IfThenElse(), Case())
