import os
from pyparsing import *
#rom utils import add_subclasses_parseres_to_scope

digit = Char(nums)
digits = Combine(OneOrMore(digit)).set_parse_action(lambda x: int(x[0]))
real_num = Combine(digits + Literal(".") + digits).set_parse_action(lambda x: float(x[0]))
ident = Word(alphanums + '_')


class BaseVocab:
    _parser = None

    def __init__(self,tokens):
        self.tokens = tokens
        for k,v in self.tokens.as_dict().items():
            setattr(self,k,v)


    def __str__(self):
        return f"{''.join(self.tokens)}"

    @property
    def value(self):
        pass

    @classmethod
    def parser(cls):
        return cls._parser.set_parse_action(cls)

    @classmethod
    def fromstring(cls,string):
        return cls.parser().parse_string(string)

class StringValue(BaseVocab):
    _parser = QuotedString("'",unquoteResults=False)

class Numeric(BaseVocab):
    _parser = (real_num | digits)("_value")

    def __str__(self):
        return f"{self._value}"

    @property
    def value(self):
        return self._value


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
        return self._count * self._unit.as_seconds


term = Or([x.parser() for x in BaseVocab.__subclasses__()])


class Entity(BaseVocab):
    _parser = ident("_domain") + Group(OneOrMore("." + ident))("_name") + Optional(":" + ident("_attribute"))
    _set_state = lambda fullname, value, attr_kwargs: f"state.set({arg},{value},{*attr_kwargs}"
    _get_state = lambda fullname: f"state.get({arg}"
    #_set_attr = lambda fullname, value: f"state.setattr({name},{value}"
    #_get_attr = lambda name: f"state.getattr({name}"
    _service_call = lambda domain, name, kwargs: f"service.call({domain},{name},{*kwargs}"

    def __str__(self):
        return f"{self._domain}{self._name}.{self._attribute}"

    @property
    def name(self):
        return "".join(self._name)

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
    def fullname(self):
        return f"{self.domain}{self.name}"

    @property
    def value(self, attr=self.attribute):
        if attr is not None:
            val = self._get_state(f"{self.fullname}.{attr}")
        else:
            val = self._get_state(f"{self.fullname}")
        return val

    @value.setter
    def value(self, newvalue=None, attr=self.attribute, attr_kwargs=None):
        if attr_kwargs is not None:
            self._set_state(f"{self.fullname}", value=newvalue, attr_kwargs=attr_kwargs)
        elif attr is not None:
            self._set_state(f"{self.fullname}.{attr}", value=newvalue, attr_kwargs=None)
        elif newvalue is not None:
            self._set_state(f"{self.fullname}", value=newvalue, attr_kwargs=None)
        else:
            pass


class Var(BaseVocab):
    _parser = Word('@',alphanums+'_')

    def __init__(self,tokens):
        self.tokens = tokens
        self._name = tokens[0][1:]
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
