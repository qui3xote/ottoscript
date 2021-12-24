import operator as op
from pyparsing import *
from ottolib.vocab import *


class Comparison(BaseVocab):
    _operators = {
                    '<': op.lt,
                    '<=': op.le,
                    '>': op.gt,
                    '>=': op.ge,
                    '!=': op.ne,
                    '==': op.eq
                    }
    _term = StringValue.parser() | Numeric.parser() | Var.parser() | Entity.parser()
    _parser = _term("_left") \
        + one_of([x for x in _operators.keys()])("_operand") \
        + _term("_right")

    def __init__(self,tokens):
        super().__init__(tokens)
        self._operators = type(self)._operators
        self._opfunc = self._operators[self._operand]

    @property
    def value(self):
        return self._opfunc(self._left[0].value, self._right[0].value)

    def eval(self):
        return self.value

class BaseCondition(BaseVocab):
    pass

class IfClause(BaseConditions):
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
        self._eval = type(self).build_evaluator(self._conditions)

    @property
    def value(self):
        return self._eval()

    @classmethod
    def build_evaluator(cls, tokens):
        comparisons = []

        for item in tokens:
            if type(item) == list:
                comparisons.append(cls.build_evaluator(item))
            elif type(item) == str:
                operand = cls._operators[item.upper()]
            else:
                comparisons.append(item.eval)

        def _eval():
            return operand([x() for x in comparisons])

        return _eval
