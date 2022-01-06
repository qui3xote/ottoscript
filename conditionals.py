from pyparsing import *
from .vocab import *
from .expressions import *
from .commands import *


class Conditional(OttoBase):

    def __str__(self):
        return f"{' '.join(self.tokens)}"


class IfClause(Conditional):
    _operators = {
                    'AND': all,
                    'OR': any,
                    'NOT': lambda x: not x
                    }

    AND, OR, NOT, IF = map(CaselessKeyword,"AND OR NOT IF".split())
    _parser = IF + infixNotation(Comparison.parser(), [
                            ("NOT", 1, opAssoc.RIGHT, ),
                            ("AND", 2, opAssoc.LEFT, ),
                            ("OR", 2, opAssoc.LEFT, ),
                            ])("_conditions")

    def __init__(self,tokens):
        super().__init__(tokens)
        self._eval_tree = self.build_evaluator_tree()

    def __str__(self):
        return " ".join([str(x) for x in self.tokens])


    async def eval(self):
        await self.interpreter.log_info('In ifclause eval')
        result = await self.eval_tree(self._eval_tree)
        return result


    async def eval_tree(self, tree):
        await self.interpreter.log_info('In ifclause eval_tree')
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
        await self.interpreter.log_info(f"If clause result: {result}: {strings}")
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
