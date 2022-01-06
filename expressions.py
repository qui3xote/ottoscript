import operator as op
from pyparsing import *
from pyparsing import common

from .ottobase import OttoBase
from .vocab import *


### Classes
class Expression(OttoBase):

    def __str__(self):
        return f"{' '.join(self.tokens)}"


class RelativeTime(Expression):
    _parser = Numeric.parser()("_count") + (Hour.parser() | Minute.parser() | Second.parser())("_unit")

    @property
    def as_seconds(self):
        return self._count.value * self._unit.as_seconds

    @property
    def value(self):
        return self.as_seconds

class Comparison(Expression):
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

    async def eval(self):
        left = await self._left.eval()
        right = await self._right.eval()
        result = self._opfunc(left, right)
        msg = f"Condition {result}: {self._opfunc.__name__} ({left}, {str(self._left)}) ({right}, {str(self._right)}) "
        await self.interpreter.log_info(msg)
        return result