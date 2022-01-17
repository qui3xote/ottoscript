from pyparsing import (
    QuotedString,
    Or,
    Suppress,
    Word,
    Forward,
    delimited_list,
    Literal,
    Optional,
    dict_of,
    alphas,
    alphanums
)
from pyparsing import common

from .ottobase import OttoBase, Var


class DataType(OttoBase):

    def __str__(self):
        return f"{''.join([str(x) for x in self.tokens])}"

    @classmethod
    def parser(cls):
        cls._parser.set_name(cls.__name__)
        cls._parser.set_parse_action(cls)
        return Or([cls._parser, Var.parser()])


class StringValue(DataType):
    _parser = QuotedString(quote_char="'", unquoteResults=True)("_value") \
                | QuotedString(quote_char='"', unquoteResults=True)("_value")


class Numeric(DataType):
    _parser = common.number("_value")

    def __str__(self):
        return f"{self._value}"


class Entity(DataType):
    _parser = common.identifier("_domain") \
        + Literal(".") \
        + common.identifier("_id") \
        + Optional(":" + common.identifier("_attribute"))

    def __str__(self):
        attribute = f":{self.attribute}" if self.attribute is not None else ''
        return f"{self.domain}.{self.id}{attribute}"

    async def eval(self):
        self._value = await self.interpreter.get_state(self.name)
        return self._value

    @property
    def id(self):
        return self._id

    @property
    def domain(self):
        return self._domain

    @property
    def attribute(self):
        if hasattr(self, '_attribute'):
            return self._attribute
        else:
            return None

    @property
    def name(self):
        if self.attribute is not None:
            val = f"{self.domain}.{self._id}.{self.attribute}"
        else:
            val = f"{self.domain}.{self._id}"
        return val


class List(DataType):
    _allowed_contents = Forward()
    _content = delimited_list(_allowed_contents)
    _parser = Optional("(") + _content("_contents") + Optional(")")

    @property
    def contents(self):
        if type(self._contents) != list:
            return [self._contents]
        else:
            return self._contents

    @classmethod
    def parser(cls, allowed_classes=None):
        if allowed_classes is None:
            allowed_classes = [StringValue,
                               Numeric,
                               Entity,
                               Var
                               ]
        allowed = [x.parser() for x in allowed_classes]
        cls._allowed_contents <<= Or(allowed)
        return super().parser()


class Dict(DataType):
    _allowed_values = Or([StringValue.parser(),
                          Numeric.parser(),
                          Entity.parser()
                          ])
    _attr_label = Word(alphas + '_', alphanums + '_')
    _attr_value = Suppress("=") + _allowed_values + Optional(Suppress(","))
    _dict = dict_of(_attr_label, _attr_value)
    _parser = Optional(Literal("(")) + _dict("_value") + Optional(Literal(")"))

    def __str__(self):
        return str(self._value)

    @property
    def value(self):
        return {key: value.value for key, value in self._value.items()}
