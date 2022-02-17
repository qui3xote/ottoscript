from pyparsing import (
    Group,
    QuotedString,
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
from .base import OttoBase

ident = ~reserved_words + common.identifier
ident = ident.set_parse_action(lambda x: x[0])


class Var(OttoBase):
    parser = Group(
        Word("@", alphanums + '_')("name")
        + Optional(":" + common.identifier("attribute"))
    )

    def __str__(self):
        return " ".join([str(x) for x in self.tokens])

    def fetch(self):
        value = self.ctx.get_var(self.name)

        #
        # Return a copy of entities with attribute matching
        # the var request.
        #
        if type(value) == Entity and hasattr(self, 'attribute'):
            value = value.copy()
            value.attribute = self.attribute

        return value

    async def eval(self):
        value = self.fetch()

        if hasattr(value, 'eval'):
            if hasattr(self, 'attribute'):
                return await value.eval(attribute=self.attribute)
            else:
                return await value.eval()
        else:
            if hasattr(self, 'attribute'):
                return value.get(self.attribute)
            else:
                return value


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
                   + Optional(":" + common.identifier("_attribute"))
                   )

    def __str__(self):
        return "".join([str(x) for x in self.tokens])

    @property
    def attribute(self):
        if hasattr(self, "_attribute"):
            return self._attribute
        else:
            return None

    @attribute.setter
    def attribute(self, attr_name):
        self._attribute = attr_name

    @property
    def name(self):
        name = ".".join([self.domain, self.id])

        if self.attribute is not None:
            name = ".".join([name, self.attribute])

        return name

    async def eval(self, attribute=None):
        name = self.name

        if attribute is None:
            attribute = self.attribute

        if attribute is not None:
            if attribute == 'name':
                return ".".join([self.domain, self.id])
            if attribute == 'id':
                return self.id
            if attribute == 'domain':
                return self.domain
            else:
                name = ".".join([self.domain, self.id, attribute])
        else:
            name = self.name

        await self.ctx.log.info(f"fetching state of {name}")
        return await self.ctx.interpreter.get_state(name)


class Area(OttoBase):
    parser = Group(ident("name"))


class List(OttoBase):

    def __str__(self):
        return "".join([str(x) for x in self.tokens])

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
    _allowedvalues = (String()
                      | Number()
                      | Entity()
                      | Var()
                      )
    _attr_label = Word(alphas + '_', alphanums + '_')
    _attrvalue = Suppress("=") + _allowedvalues + Optional(Suppress(","))
    _dict = dict_of(_attr_label, _attrvalue)
    parser = Group(Literal("(")
                   + _dict("contents")
                   + Literal(")")
                   + Optional(Suppress(":") + ident("attribute"))
                   )

    async def eval(self, attribute=None):
        if attribute is not None:
            result = await self.contents.get(attribute).eval()
        elif hasattr(self, "attribute"):
            result = await self.contents.get(self.attribute).eval()
        else:
            result = {}
            for k, v in self.contents.items():
                result[k] = await v.eval()
        return result


class Target(OttoBase):
    parser = Group(
        List(Entity() ^ Var())("inputs")
        ^ (AREA + List(Area() ^ Var())("inputs"))
    )

    async def eval(self):
        entities = []
        areas = []

        for i in self.inputs.contents:
            if type(i) == Var:
                i = i.fetch()

            if type(i) == List:
                i = i.contents
            else:
                i = [i]
            for x in i:
                if type(x) == Var:
                    x = x.fetch()
                if type(x) == Entity:
                    entities.append(x.name)
                if type(x) == Area:
                    expanded = self.expand_areas(x.name)
                    areas.extend(expanded)

        return {'entity_id': entities, 'area_id': areas}

    def expand_areas(self, name):
        area_shortcuts = self.ctx.get_var('area_shortcuts')
        if area_shortcuts is None:
            return [name]

        if name not in area_shortcuts.keys():
            return [name]

        areas = []
        for new in area_shortcuts[name]:
            areas.extend(self.expand_areas(new))

        return areas


class Input(OttoBase):

    def __init__(self, tokens, result_type):
        super().__init__(tokens)
        self.result_type = result_type

    async def eval(self):
        if type(self.input) == Var:
            input = self.input.fetch()
        else:
            input = self.input

        result = await input.eval()

        if self.result_type == 'numeric':
            try:
                result = float(result)
                return result
            except ValueError as error:
                self.ctx.log.error(error)
        else:
            return result

    @classmethod
    def pre_parse(cls, result_type="any", *args, **kwargs):
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
