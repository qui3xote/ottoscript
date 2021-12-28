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

    def __str__(self):
        return ' '.join([str(x) for x in self.tokens])

    @property
    def value(self):
        return self._opfunc(self._left.value, self._right.value)

    def eval(self):
        result = self.value
        msg = f"""{result}: {self._opfunc.__name__}
                left({str(self._left)}, value={self._left.value})
                right({str(self._right)}, value={self._right.value})"""
        self._interpreter.log(msg, 'debug')
        return self.value

class BaseCondition(BaseVocab):
    pass

class IfClause(BaseCondition):
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
        return self._eval(self._interpreter)

    @classmethod
    def build_evaluator(cls, tokens):
        if type(tokens) == Comparison:
            tokens = ["AND", tokens]

        comparisons = []
        comparison_strings = []

        for item in tokens:
            if type(item) == list:
                comparisons.append(cls.build_evaluator(item))
            elif type(item) == str:
                opname = item.upper()
                operand = cls._operators[opname]
            else:
                comparisons.append(item.eval)
                comparison_strings.append(str(item))

        def _eval(interpreter):
            result = operand([x() for x in comparisons])
            if result == False:
                msg = f"If condition failed: {opname} {comparison_strings}"
                interpreter.log(msg, 'debug')
            return result

        return _eval
