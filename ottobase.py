from pyparsing import (CaselessKeyword,
                       Word,
                       alphanums,
                       Group,
                       Optional,
                       common)


class OttoBase:
    """
    A class to hold an ottoscript parser.

    Class Attributes
    ________________
    _parser : PyparseObject
        a pyparsing expression which defines the grammar of the class
    _vars : dict
        instantiated dictionary which is shared among all classes

    Class Methods
    ________________
    parser():
        returns _parser with name and parse_action set to match the class.

    update_vars(vars):
        update the shared variable dictionary

    clear_vars():
        clear the shared variable dictionary.

    set_vars(vars):
        replace the shared variable dictionary.

    """
    _parser = None
    _vars = dict()

    def __init__(self, tokens):
        self.tokens = tokens
        self.dictionary = {}
        for k, v in self.tokens.as_dict().items():
            if type(v) == list and len(v) == 1:
                # Pyparsing often returns lists rather that single elements
                # This is a convenience hack to strip unnecessary lists
                setattr(self, k, v[0])
                self.dictionary[k] = v[0]
            else:
                setattr(self, k, v)
                self.dictionary[k] = v

    def __str__(self):
        return f"{' '.join([str(x) for x in self.tokens.as_list()])}"

    def debugtree(self, levels=5):
        if levels == 0:
            return {'type': type(self), 'string': 'Level Limit Reached'}

        dictionary = {'type': type(self), 'string': str(self)}
        for k, v in self.dictionary.items():
            if type(v) in (str, list, int, float, dict, CaselessKeyword):
                dictionary[k] = v
            else:
                dictionary[k] = v.debugtree(levels=levels-1)
        return dictionary

    async def eval(self, interpreter):
        return self.value

    async def eval_attribute(self, interpreter, attr_name):
        message = f"{type(self).__name__} does not support attribute access"
        interpreter.log_warning(message)

    @property
    def value(self):
        return self._value

    @classmethod
    def parser(cls):
        cls._parser.set_name(cls.__name__)
        return cls._parser.set_parse_action(cls)

    @classmethod
    def update_vars(cls, vars: dict):
        cls._vars.update(vars)

    @classmethod
    def clear_vars(cls):
        cls._vars.clear()

    @classmethod
    def set_vars(cls, vars: dict):
        cls._vars = vars

    @classmethod
    def get_var(cls, var):
        return cls._vars[var]

    @classmethod
    def from_string(cls, string):
        return cls.parser().parse_string(string)

    @classmethod
    def child_parsers(cls):
        return [subclass.parser() for subclass in cls.__subclasses__()]


class Var(OttoBase):
    _parser = Group(Word("@", alphanums+'_')("_varname")) \
              + Optional(":" + common.identifier("_attribute"))

    def __init__(self, tokens):
        # This is an annoying hack to force
        # Pyparsing to preserve the namespace.
        # It undoes the 'Group' in the parser.
        tokens = tokens[0]
        super().__init__(tokens)

    def __getattr__(self, name):
        return getattr(self.pointer, name)

    @property
    def varname(self):
        return self._varname

    @property
    def value(self):
        return self.pointer.value

    @value.setter
    def value(self, new_value):
        self.update_vars({self.varname: new_value})

    @property
    def pointer(self):
        try:
            return self.get_var(self.varname)
        except KeyError as error:
            # TODO better error message
            raise error

    async def eval(self, interpreter):
        if hasattr(self, "_attribute"):
            return await self.pointer.eval_attribute(interpreter,
                                                     self._attribute)

        return await self._vars[self.varname].eval(interpreter)
