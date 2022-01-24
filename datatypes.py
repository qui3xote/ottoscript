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
    alphanums,
    common
)
from .keywords import reserved_words
from .ottobase import OttoBase, Var


ident = ~reserved_words + common.identifier


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
    _parser = ident("_domain") \
        + Literal(".") \
        + ident("_id") \
        + Optional(":" + common.identifier("_attribute"))

    def __str__(self):
        attribute = f":{self.attribute}" if self.attribute is not None else ''
        return f"{self.domain}.{self.id}{attribute}"

    async def eval(self, interpreter):
        self._value = await interpreter.get_state(self.name)
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

    async def eval_attribute(self, interpreter, attr_name):
        name = ".".join([self.domain, self.name, attr_name])
        return await interpreter.get_state(name)


class Area(DataType):
    _parser = ident("_id") \
        + Optional(Literal(".") + ident("_domain"))

    async def eval(self, interpreter):
        self._value = await interpreter.get_state(self.name)
        return self._value

    @property
    def id(self):
        return self._id

    @property
    def domain(self):
        if not hasattr(self, '_domain'):
            return ''
        else:
            return self._domain

    @property
    def name(self):
        return self.id


class List(DataType):
    _allowed_contents = Forward()
    _content = delimited_list(_allowed_contents)
    _parser = Literal("(") + _content("_contents") + Literal(")")

    @property
    def value(self):
        return self.contents

    @property
    def contents(self):
        if type(self._contents) != list:
            return [self._contents]
        else:
            return self._contents

    @classmethod
    def parser(cls, allowed_contents=None):
        if allowed_contents is None:
            allowed_contents = [StringValue.parser(),
                                Numeric.parser(),
                                Entity.parser(),
                                Var.parser()
                                ]
        content = delimited_list(Or(allowed_contents))
        parser = Optional("(") + content("_contents") + Optional(")")
        parser.set_parse_action(cls)

        return Or([parser.set_name(cls.__name__), Var.parser()])


class Dict(DataType):
    _allowed_values = Or([StringValue.parser(),
                          Numeric.parser(),
                          Entity.parser()
                          ])
    _attr_label = Word(alphas + '_', alphanums + '_')
    _attr_value = Suppress("=") + _allowed_values + Optional(Suppress(","))
    _dict = dict_of(_attr_label, _attr_value)
    _parser = Literal("(") + _dict("_value") + Literal(")") \
              + Optional(":" + ident("_attribute"))

    def __str__(self):
        return str(self._value)

    async def eval(self, interpreter):
        if hasattr(self, "_attribute"):
            return await self.eval_attribute(self,
                                             interpreter,
                                             self._attribute)

        return {key: value.eval() for key, value in self._value.items()}

    async def eval_attribute(self, interpreter, attr_name):
        if attr_name in self._value.keys():
            return await self._value.get(attr_name).eval(interpreter)
        else:
            return None
