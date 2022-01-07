from pprint import PrettyPrinter

class OttoBase:
    _parser = None
    _value = None
    _interpreter = None

    def __init__(self,tokens):
        self.tokens = tokens
        self.dictionary = {}
        for k,v in self.tokens.as_dict().items():
            if type(v) == list and len(v) == 1:
                # Pyparsing often returns lists rather that single elements
                # This is a convenience hack to strip unnecessary lists
                setattr(self,k,v[0])
                self.dictionary[k] = v[0]
            else:
                setattr(self,k,v)
                self.dictionary[k] = v


    def __str__(self):
        return f"{''.join([str(x) for x in self.tokens])}"

    def debugtree(self):
        #printer = PrettyPrinter(indent = 5)
        dictionary = {'type': type(self), 'string': str(self)}
        for k, v in self.dictionary.items():
            if type(v) in (str, list, int, float):
                dictionary[k] = v
            else:
                dictionary[k] = v.debugtree()
        return dictionary

    async def eval(self):
        return self.value

    @property
    def interpreter(self):
        return self._interpreter

    @interpreter.setter
    def interpreter(self, interpreter):
        self._interpreter = interpreter

    @property
    def value(self):
        return self._value

    @classmethod
    def parser(cls):
        return cls._parser.set_parse_action(cls)

    @classmethod
    def set_interpreter(cls, interpreter):
        cls._interpreter = interpreter

    @classmethod
    def from_string(cls,string):
        return cls.parser().parse_string(string)

    @classmethod
    def child_parsers(cls):
        return [subclass.parser() for subclass in cls.__subclasses__()]
