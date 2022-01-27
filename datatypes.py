from pyparsing import (
    Group,
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
    common,
    ParseResults
)
from .keywords import reserved_words, AREA
from .ottobase import OttoBase

ident = ~reserved_words + common.identifier
ident = ident.set_parse_action(lambda x: x[0])


class Var(OttoBase):
    parser = Group(Word("@", alphanums+'_')("name")
                   + Optional(":" + common.identifier)("attribute"))


class String(OttoBase):
    parser = Group(QuotedString(quote_char="'", unquoteResults=True)("value")
                   | QuotedString(quote_char='"', unquoteResults=True)("value")
                   )


class Numeric(OttoBase):
    parser = Group(common.number("value"))

    def __str__(self):
        return f"{self.value}"


class Entity(OttoBase):
    parser = Group(ident("domain")
                   + Literal(".")
                   + ident("id")
                   + Optional(":" + common.identifier("attribute"))
                   )

    @property
    def name(self):
        name = ".".join([self.domain, self.id])
        if hasattr(self, "attribute"):
            name = ".".join([name, self.attribute])
        return name

    async def eval(self, interpreter):
        self.value = await interpreter.get_state(self.name)
        return self.value


class Area(OttoBase):
    parser = Group(ident("name"))


class List(OttoBase):

    def __new__(cls, *args, **kwargs):
        allowed_contents = Forward()
        default = (String() ^ Numeric() ^ Entity() ^ Var())
        parser = Group(Optional("(")
                       + delimited_list(allowed_contents)("contents")
                       + Optional(")")
                       )

        if len(args) > 0 and type(args[0]) == ParseResults:
            return super(OttoBase, cls).__new__(cls)
        elif len(args) == 0:
            allowed_contents <<= default
            parser.set_name(cls.__name__)
            return parser.set_parse_action(lambda x: cls(x, default))
        else:
            allowed_contents <<= args[0]
            parser.set_name(cls.__name__)
            return parser.set_parse_action(lambda x: cls(x, args[0]))

    def __init__(self, tokens, forward, *args, **kwargs):
        super().__init__(tokens, *args, **kwargs)


class Dict(OttoBase):
    _allowedvalues = Or([String(),
                         Numeric(),
                         Entity(),
                         Var()
                         ])
    _attr_label = Word(alphas + '_', alphanums + '_')
    _attrvalue = Suppress("=") + _allowedvalues + Optional(Suppress(","))
    _dict = dict_of(_attr_label, _attrvalue)
    parser = Group(Literal("(")
                   + _dict("contents")
                   + Literal(")")
                   + Optional(":" + ident("attribute"))
                   )

    async def eval(self, interpreter):
        if hasattr(self, "_attribute"):
            result = await self.value.get(self.attribute).eval(interpreter)
        else:
            result = {}
            for k, v in self.value.items():
                result[k] = await v.eval(interpreter)
        return result


class Target(OttoBase):
    parser = Group(List(Entity() ^ Var())("entities")
                   | (AREA + List(Area() ^ Var())("areas"))
                   )

    async def eval(self, interpreter):

        if hasattr(self, 'entities'):
            return {'entity_id': [e.name for e in self.entities.contents]}

        if hasattr(self, 'areas'):
            return {'area_id': [a.name for a in self.areas.contents]}
