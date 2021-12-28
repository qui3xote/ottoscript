import os
from pyparsing import *

from ottolib.stringinterpreter import StringInterpreter
#rom utils import add_subclasses_parseres_to_scope

digit = Char(nums)
digits = Combine(OneOrMore(digit)).set_parse_action(lambda x: int(x[0]))
real_num = Combine(digits + Literal(".") + digits).set_parse_action(lambda x: float(x[0]))
ident = Word(alphanums + '_')


class BaseVocab:
    _parser = None
    _value = None
    _interpreter = StringInterpreter()

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
    def value(self):
        return self._value

    @classmethod
    def parser(cls):
        return cls._parser.set_parse_action(cls)

    @classmethod
    def fromstring(cls,string):
        return cls.parser().parse_string(string)

class StringValue(BaseVocab):
    _parser = QuotedString("'",unquoteResults=True)("_value")

class Numeric(BaseVocab):
    _parser = (real_num("_value") | digits("_value"))

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
    _parser = Group(digit * 2)("_hours") + ":" + Group(digit * 2)("_minutes") + ":" +  Group(digit * 2)("_seconds")

    def __str__(self):
        return f"value: {self.as_string}"

    @property
    def as_seconds(self):
        return self._hours * 3600 + self._minutes * 60 + self._seconds

    @property
    def as_string(self):
        return ''.join(self.tokens)



class RelativeTime(BaseVocab):
    _parser = Numeric.parser()("_count") + (Hour.parser() | Minute.parser() | Second.parser())("_unit")

    @property
    def as_seconds(self):
        return self._count.value * self._unit.as_seconds


term = Or([x.parser() for x in BaseVocab.__subclasses__()])


class Entity(BaseVocab):
    _parser = ident("_domain") + Group(OneOrMore(Literal(".").suppress() + ident))("_id") + Optional(":" + ident("_attribute"))
    #_set_state_func = lambda self, fullname, value, attr_kwargs: print(f"state.set({fullname},{value},{attr_kwargs})")
    #_get_state_func = lambda self, fullname: f"state.get({fullname})"
    #_set_attr = lambda fullname, value: f"state.setattr({name},{value}"
    #_get_attr = lambda name: f"state.getattr({name}"
    #_service_call_func = lambda self, domain, name, kwargs: print(f"service.call({domain},{name},{kwargs}")

    def __str__(self):
        return f"{self.domain}{self.name}.{self.attribute}"

    @property
    def id(self):
        return ".".join(self._id)

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

    @property
    def value(self):
        value = self._interpreter.get_state(self.name)
        self._interpreter.log(value,'debug')
        return value

    @value.setter
    def value(self, newvalue=None, attr_kwargs=None):
        if self.attribute is not None:
            self._interpreter.set_state(f"{self.fullname}.{attr}", \
                value=newvalue, attr_kwargs=None)

        elif attr_kwargs is not None:
            self._interpreter.set_state(f"{self.fullname}", \
                value=newvalue, attr_kwargs=attr_kwargs)

        elif newvalue is not None:
            self._interpreter.set_state(f"{self.fullname}", \
                value=newvalue, attr_kwargs=None)
                
        else:
            pass


class Var(BaseVocab):
    _parser = Word('@',alphanums+'_')

    def __init__(self,tokens):
        self.tokens = tokens
        self._name = tokens[1:]
        self._value = None

    def __str__(self):
        return f"{self._value}"

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,new_value):
        self._value = new_value

#expressions
