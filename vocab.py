import os
from pyparsing import *
from pyparsing import common
from .ottobase import OttoBase

### Keywords
WHEN = CaselessKeyword('WHEN')
IF = CaselessKeyword('IF')
THEN = CaselessKeyword('THEN')
ELSE = CaselessKeyword('ELSE')
FROM = CaselessKeyword('TO')
WITH = CaselessKeyword('WITH')
IS = CaselessKeyword('IS')
FOR = CaselessKeyword('FOR')
TRUE = CaselessKeyword('TRUE')
CHANGES = CaselessKeyword('CHANGES')

### Classes
class Vocab(OttoBase):

    def __str__(self):
        return f"{''.join(self.tokens)}"

class StringValue(Vocab):
    _parser = QuotedString("'",unquoteResults=True)("_value")

class Numeric(Vocab):

    _parser = common.number("_value")

    def __str__(self):
        return f"{self._value}"


class Hour(Vocab):
    _parser = Or(map(CaselessKeyword,["HOUR","HOUR"]))

    @property
    def as_seconds(self):
        return 3600

class Minute(Vocab):
    _parser = Or(map(CaselessKeyword,["MINUTE","MINUTES"]))

    @property
    def as_seconds(self):
        return 60

class Second(Vocab):
    _parser = Or(map(CaselessKeyword,["SECOND","SECONDS"]))

    @property
    def as_seconds(self):
        return 1

class TimeStamp(Vocab):
    _digits = Combine(Char(nums) * 2).set_parse_action(lambda x: int(x[0]))
    _parser = _digits("_hours") + ":" + _digits("_minutes") + ":" +  _digits("_seconds")

    @property
    def as_seconds(self):
        return self._hours * 3600 + self._minutes * 60 + self._seconds

class Entity(Vocab):
    _parser = common.identifier("_domain") + Literal(".") + common.identifier("_id") + Optional(":" + common.identifier("_attribute"))

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
        if hasattr(self,'_attribute'):
            return self._attribute
        else:
            return None

    @property
    def name(self):
        if self.attribute is not None:
            val = f"{self.domain}.{self._id}.{attribute}"
        else:
            val = f"{self.domain}.{self._id}"
        return val

class Var(Vocab):
    _parser = Word('@',alphanums+'_')

    def __init__(self,tokens):
        self.tokens = tokens
        self._name = tokens[1:]
        self._value = None

    def __str__(self):
        return f"{''.join(self.tokens)}"

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value.value

    @value.setter
    def value(self, new_value):
        self._value = new_value

#expressions
