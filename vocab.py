import os
from pyparsing import *
from pyparsing import common

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
class BaseVocab:
    _parser = None
    _value = None
    _interpreter = None

    def __init__(self,tokens):
        self.tokens = tokens
        for k,v in self.tokens.as_dict().items():
            if type(v) == list and len(v) == 1:
                setattr(self,k,v[0])
            else:
                setattr(self,k,v)


    def __str__(self):
        return f"{''.join(self.tokens)}"

    @property
    def interpreter(self):
        return self._interpreter

    @interpreter.setter
    def interpreter(self, interpreter):
        self._interpreter = interpreter

    @property
    def value(self):
        return self._value

    async def eval(self):
        return self.value

    @classmethod
    def parser(cls):
        return cls._parser.set_parse_action(cls)

    @classmethod
    def set_interpreter(cls, interpreter):
        cls._interpreter = interpreter

    @classmethod
    def from_string(cls,string):
        return cls.parser().parse_string(string)

class StringValue(BaseVocab):
    _parser = QuotedString("'",unquoteResults=True)("_value")

class Numeric(BaseVocab):

    _parser = common.number("_value")

    def __str__(self):
        return f"{self._value}"


class Hour(BaseVocab):
    _parser = Or(map(CaselessKeyword,["HOUR","HOUR"]))

    @property
    def as_seconds(self):
        return 3600

class Minute(BaseVocab):
    _parser = Or(map(CaselessKeyword,["MINUTE","MINUTES"]))

    @property
    def as_seconds(self):
        return 60

class Second(BaseVocab):
    _parser = Or(map(CaselessKeyword,["SECOND","SECONDS"]))

    @property
    def as_seconds(self):
        return 1


class TimeStamp(BaseVocab):
    _digits = Combine(Char(nums) * 2).set_parse_action(lambda x: int(x[0]))
    _parser = _digits("_hours") + ":" + _digits("_minutes") + ":" +  _digits("_seconds")

    @property
    def as_seconds(self):
        return self._hours * 3600 + self._minutes * 60 + self._seconds



class RelativeTime(BaseVocab):
    _parser = Numeric.parser()("_count") + (Hour.parser() | Minute.parser() | Second.parser())("_unit")

    @property
    def as_seconds(self):
        return self._count.value * self._unit.as_seconds

    @property
    def value(self):
        return self.as_seconds

term = Or([x.parser() for x in BaseVocab.__subclasses__()])


class Entity(BaseVocab):
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

class Var(BaseVocab):
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
