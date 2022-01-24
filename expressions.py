import operator as op
from pyparsing import (one_of,
                       Literal,
                       Group,
                       Or,
                       MatchFirst
                       )
from .ottobase import OttoBase
from .keywords import WITH
from .datatypes import (StringValue,
                        Numeric,
                        Var,
                        Entity,
                        Dict,
                        DataType
                        )


class Expression(OttoBase):
    pass


class Comparison(Expression):

    _operators = {
                    '<': op.lt,
                    '<=': op.le,
                    '>': op.gt,
                    '>=': op.ge,
                    '!=': op.ne,
                    '==': op.eq
                    }

    _term = (StringValue.parser()
             | Numeric.parser()
             | Entity.parser())

    _parser = _term("_left") \
        + one_of([x for x in _operators.keys()])("_operand") \
        + _term("_right")

    def __init__(self, tokens):
        super().__init__(tokens)
        # TODO: This call to the class shouldn't be necessary.
        self._operators = type(self)._operators
        self._opfunc = self._operators[self._operand]

    def __str__(self):
        return ' '.join([str(x) for x in self.tokens])

    @property
    def value(self):
        return self._opfunc(self._left.value, self._right.value)

    async def eval(self, interpreter):
        left = await self._left.eval(interpreter)
        right = await self._right.eval(interpreter)
        result = self._opfunc(left, right)

        msg = f"Condition {result}: {self._opfunc.__name__}"
        msg += f"{str(self._right)}, {str(self._left)}"
        msg += f" evaluated to ({right}, {left})"
        await interpreter.log_debug(msg)
        return result


class Assignment(Expression):
    #_terms =
    _parser = Var.parser()("_left") \
        + Literal('=') \
        + MatchFirst(DataType.child_parsers())("_right")

    def __str__(self):
        return ' '.join([str(x) for x in self.tokens])

    @property
    def right(self):
        if type(self._right) == list:
            return self._right[0]
        else:
            return self._right

    async def eval(self, interpreter):
        await interpreter.log_debug(f"Assign: {self._left.varname} to {self.right} {type(self.right)}")
        self.update_vars({self._left.varname: self.right})


class With(Expression):
    _parser = WITH + Group(Dict.parser())("_value")

    @property
    def value(self):
        return self._value.value
