from pyparsing import (CaselessKeyword,
                       Word,
                       alphanums,
                       Group,
                       Optional,
                       common,
                       ParseResults)


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
    parser = None

    def __new__(cls, *args, **kwargs):
        if len(args) == 0:
            print("new parser")
            cls.parser.set_name(cls.__name__)
            return cls.parser.set_parse_action(lambda x: cls(x))
        elif type(args[0]) == ParseResults:
            print("new class")
            return super(OttoBase, cls).__new__(cls)
        else:
            print("new parser")
            cls.parser.set_name(cls.__name__)
            return cls.parser.set_parse_action(lambda x: cls(x))

    def __init__(self, tokens, *args, **kwargs):
        print('super initing')
        super().__init__(*args, **kwargs)
        print('initing')
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

    def update_vars(cls, vars: dict):
        cls._vars.update(vars)

    def clear_vars(cls):
        cls._vars.clear()

    def set_vars(cls, vars: dict):
        cls._vars = vars

    def get_var(cls, var):
        return cls._vars[var]

    def from_string(cls, string):
        return cls.parser().parse_string(string)

    def child_parsers(cls):
        return [subclass.parser() for subclass in cls.__subclasses__()]


class Var(OttoBase):
    parser = Group(Word("@", alphanums+'_')("var_name")
                   + Optional(":" + common.identifier)("attribute"))

    def __init__(self, tokens, *args, **kwargs):
        # This is an annoying hack to force
        # Pyparsing to preserve the namespace.
        # It undoes the 'Group' in the parser.
        super().__init__(tokens[0])


    # async def eval(self, interpreter):
    #     if hasattr(self, "_attribute"):
    #         return await self.pointer.eval_attribute(interpreter,
    #                                                  self._attribute)
    #
    #     return await self._vars[self.varname].eval(interpreter)
