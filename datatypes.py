from pyparsing import (
    Group,
    QuotedString,
    Or,
    Suppress,
    Word,
    delimited_list,
    Literal,
    Optional,
    dict_of,
    alphas,
    alphanums,
    common
)
from .keywords import reserved_words, AREA
from .ottobase import OttoBase

ident = ~reserved_words + common.identifier
ident = ident.set_parse_action(lambda x: x[0])


class Var(OttoBase):
    parser = Group(Word("@", alphanums + '_')("name")
                   + Optional(":" + common.identifier)("attribute"))

    @classmethod
    def post_parse(cls, tokens, fetch=True, *args, **kwargs):
        if fetch is True:
            parse_dict = tokens[0].as_dict()
            return cls.ctx.vars.get(parse_dict['name'])
        else:
            return cls(tokens, *args, **kwargs)


class String(OttoBase):
    parser = Group(QuotedString(quote_char="'", unquoteResults=True)("_value")
                   | QuotedString(quote_char='"',
                                  unquoteResults=True)("_value")
                   )


class Number(OttoBase):
    parser = Group(common.number("_value"))


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
        self._value = await interpreter.get_state(self.name)
        print(self._value)
        return self._value


class Area(OttoBase):
    parser = Group(ident("name"))


class List(OttoBase):

    @classmethod
    def pre_parse(cls, content_parser=None, *args, **kwargs):

        if content_parser is None:
            content_parser = (String() ^ Number() ^ Entity() ^ Var())
        else:
            content_parser = Var() ^ content_parser

        parser = Group(Optional("(")
                       + delimited_list(content_parser)("contents")
                       + Optional(")")
                       )
        parser.set_name(cls.__name__)
        return parser.set_parse_action(lambda x: cls(x, *args, **kwargs))


class Dict(OttoBase):
    _allowedvalues = Or([String(),
                         Number(),
                         Entity(),
                         Var()
                         ])
    _attr_label = Word(alphas + '_', alphanums + '_')
    _attrvalue = Suppress("=") + _allowedvalues + Optional(Suppress(","))
    _dict = dict_of(_attr_label, _attrvalue)
    parser = Group(Literal("(")
                   + _dict("contents")
                   + Literal(")")
                   + Optional(Suppress(":") + ident)("attribute")
                   )

    async def eval(self, interpreter):
        if hasattr(self, "attribute"):
            result = await self.contents.get(self.attribute).eval(interpreter)
        else:
            result = {}
            for k, v in self.contents.items():
                result[k] = await v.eval(interpreter)
        return result


class Target(OttoBase):
    parser = Group(List(Entity() ^ Var())("inputs")
                   ^ (AREA + List(Area() ^ Var())("inputs"))
                   )

    async def eval(self, interpreter):
        entities = []
        areas = []

        for i in self.inputs.contents:

            if type(i) == List:
                i = i.contents
            else:
                i = [i]
            for x in i:
                if type(x) == Entity:
                    entities.append(x.name)
                if type(x) == Area:
                    areas.append(x.name)

        return {'entity_id': entities, 'area_id': areas}


class Input(OttoBase):

    def __init__(self, tokens, result_type):
        super().__init__(tokens)
        self.result_type = result_type

    async def eval(self, interpreter):
        result = await self.input.eval(interpreter)

        if self.result_type == 'numeric':
            try:
                result = float(result)
                return result
            except ValueError as error:
                print(error)
        else:
            return result

    @classmethod
    def pre_parse(cls, result_type, *args, **kwargs):
        if result_type == "numeric":
            parser = Group(Number()("input")
                           | Entity()("input")
                           | Var()("input")
                           )
        elif result_type == "text":
            parser = Group(String()("input")
                           | Entity()("input")
                           | Var()("input")
                           )
        elif result_type == "any":
            parser = Group(Number()("input")
                           | String()("input")
                           | Entity()("input")
                           | Var()("input")
                           )

        parser.set_name(cls.__name__)
        parser.set_parse_action(lambda x: cls(x, result_type, *args, **kwargs))
        return parser


# class Single(OttoBase):
#     parser = Group((Var()
#                    ^ Entity()
#                    ^ Number()
#                    ^ String()
#                     )("inputs")
#                    )
#
#     @classmethod
#     def pre_parse(cls, parser=None, *args, **kwargs):
#
#         if parser is None:
#             parser = (String() ^ Number() ^ Entity() ^ Var())
#         else:
#             parser = Var() ^ parser
#
#         return parser.set_parse_action(lambda x: cls(x, *args, **kwargs))
