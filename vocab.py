from pyparsing import (
    CaselessKeyword,
    QuotedString,
    Or,
    Combine,
    Word,
    Char,
    alphanums,
    nums,
    Literal,
    Optional,
    Group
)
from pyparsing import common

from .ottobase import OttoBase

# Keywords
WHEN = CaselessKeyword('WHEN')
IF = CaselessKeyword('IF')
THEN = CaselessKeyword('THEN')
ELSE = CaselessKeyword('ELSE')
FROM = CaselessKeyword('FROM')
WITH = CaselessKeyword('WITH')
IS = CaselessKeyword('IS')
FOR = CaselessKeyword('FOR')
TRUE = CaselessKeyword('TRUE')
CHANGES = CaselessKeyword('CHANGES')
AND = CaselessKeyword('AND')
OR = CaselessKeyword('OR')
NOT = CaselessKeyword('NOT')
END = CaselessKeyword('END')
CASE = CaselessKeyword('CASE')
TO = CaselessKeyword('TO')
ON = CaselessKeyword('ON')


class Vocab(OttoBase):

    def __str__(self):
        return f"{''.join([str(x) for x in self.tokens])}"


class StringValue(Vocab):
    _parser = QuotedString(quote_char="'", unquoteResults=True)("_value") \
                | QuotedString(quote_char='"', unquoteResults=True)("_value")


class Numeric(Vocab):
    _parser = common.number("_value")

    def __str__(self):
        return f"{self._value}"


class Hour(Vocab):
    _parser = Or(map(CaselessKeyword, ["HOUR", "HOUR"]))

    @property
    def as_seconds(self):
        return 3600


class Minute(Vocab):
    _parser = Or(map(CaselessKeyword, ["MINUTE", "MINUTES"]))

    @property
    def as_seconds(self):
        return 60


class Second(Vocab):
    _parser = Or(map(CaselessKeyword, ["SECOND", "SECONDS"]))

    @property
    def as_seconds(self):
        return 1


class TimeStamp(Vocab):
    _digits = Combine(Char(nums) * 2).set_parse_action(lambda x: int(x[0]))
    _parser = _digits("_hours") \
        + ":" + _digits("_minutes") \
        + ":" + _digits("_seconds")

    @property
    def as_seconds(self):
        return self._hours * 3600 + self._minutes * 60 + self._seconds


class Entity(Vocab):
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


class Var(Vocab):
    _parser = Group(Word("@", alphanums+'_')("_name"))

    def __init__(self, tokens):
        # This is an annoying hack to force
        # Pyparsing to preserve the namespace.
        # It undoes the 'Group' in the parser.
        tokens = tokens[0]
        super().__init__(tokens)

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._vars[self.name].value

    @value.setter
    def value(self, new_value):
        self._vars[self.name] = new_value
