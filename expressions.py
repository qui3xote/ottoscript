import operator as op
from pyparsing import (one_of,
                       Literal,
                       delimited_list,
                       Forward,
                       Group,
                       Optional,
                       Or,
                       dict_of,
                       Suppress,
                       Word,
                       alphas,
                       alphanums
                       )

from .ottobase import OttoBase
from .vocab import (WITH,
                    StringValue,
                    Numeric,
                    Var,
                    Entity,
                    Hour,
                    Minute,
                    Second
                    )


class Expression(OttoBase):

    def __str__(self):
        return f"{' '.join(self.tokens)}"


class RelativeTime(Expression):
    _parser = Numeric.parser()("_count") \
              + (Hour.parser()
                 | Minute.parser()
                 | Second.parser())("_unit")

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

    _term = (StringValue.parser()
             | Numeric.parser()
             | Var.parser()
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

    async def eval(self):
        left = await self._left.eval()
        right = await self._right.eval()
        result = self._opfunc(left, right)

        msg = f"Condition {result}: {self._opfunc.__name__}"
        msg += f"{str(self._right)}, {str(self._left)}"
        msg += f" evaluated to ({right}, {left})"
        await self.interpreter.log_debug(msg)
        return result


class Assignment(Expression):
    _terms = (StringValue.parser()
              | Numeric.parser()
              | Var.parser()
              | Entity.parser())
    _parser = Var.parser()("_left") \
        + Literal('=') \
        + _terms("_right")

    def __str__(self):
        return ' '.join([str(x) for x in self.tokens])

    async def eval(self):
        self._left.value = self._right


class List(Expression):
    _allowed_contents = Forward()
    _contents = delimited_list(_allowed_contents, allow_trailing_delim=True)
    _parser = Literal("(") + _contents("_value") + Literal(")")

    @classmethod
    def parser(cls, allowed=None):
        if allowed is None:
            allowed = Or([StringValue.parser(),
                          Numeric.parser(),
                          Entity.parser(),
                          Var.parser()
                          ])

        cls._allowed_contents <<= allowed
        return super().parser()


class Dict(Expression):
    _allowed_values = Or([StringValue.parser(),
                          Numeric.parser(),
                          Entity.parser(),
                          Var.parser()
                          ])
    _attr_label = Word(alphas + '_', alphanums + '_')
    _attr_value = Suppress("=") + _allowed_values + Optional(Suppress(","))
    _dict = dict_of(_attr_label, _attr_value)
    _parser = Literal("(") + _dict("_value") + Literal(")")

    def __str__(self):
        return str(self._value)

    @property
    def value(self):
        return {key: value.value for key, value in self._value.items()}


class With(Expression):
    _parser = WITH + Group(Dict.parser())("_value")

    @property
    def value(self):
        return self._value.value
