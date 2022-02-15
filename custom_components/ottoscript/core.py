from pyparsing import ParseResults, CaselessKeyword
from .interpreters import Interpreter, PrintLogger


class OttoContext:
    def __init__(self, interpreter=None, logger=None):

        self.local_vars = {}
        self.global_vars = {}

        if logger is None:
            self.log = PrintLogger('none')
        else:
            self.log = logger

        if interpreter is None:
            self.interpreter = Interpreter(logger=self.log)
        else:
            self.interpreter = interpreter

    def set_name(self, name):
        self.log.set_task(name)

    def get_var(self, key):
        local = self.local_vars.get(key)

        if local is None:
            return self.global_vars.get(key)
        else:
            return local

    def update_vars(self, dictionary):
        self.local_vars.update(dictionary)

    def update_global_vars(self, dictionary):
        self.global_vars.update(dictionary)


class OttoBase:

    def __new__(cls, *args, **kwargs):
        if len(args) > 0 and type(args[0]) == ParseResults:
            return super(OttoBase, cls).__new__(cls)

        return cls.pre_parse(*args, **kwargs)

    def __init__(self, tokens, *args, **kwargs):
        super().__init__(*[], **{})

        self.ctx = type(self).ctx
        self.parse_results = tokens
        self.tokens = tokens[0]

        try:
            for k, v in self.tokens.as_dict().items():
                setattr(self, k, v)
        except Exception as error:
            print(f"Failed to init {type(self)}")
            print(tokens)
            print(error)

    def __str__(self):
        return " ".join([str(x) for x in self.tokens])

    def copy(self):
        return type(self)(self.parse_results)

    def debugtree(self, levels=5):
        if levels == 0:
            return {'type': type(self), 'string': 'Level Limit Reached'}

        dictionary = {'type': type(self), 'string': str(self)}
        for k, v in self.dictionary.items():
            if type(v) in (str, list, int, float, dict, CaselessKeyword):
                dictionary[k] = v
            else:
                dictionary[k] = v.debugtree(levels=levels - 1)
        return dictionary

    async def eval(self):
        return self._value

    @classmethod
    def pre_parse(cls, *args, **kwargs):
        cls.parser.set_name(cls.__name__)
        prs = cls.parser.copy()
        return prs.set_parse_action(lambda x:
                                    cls.post_parse(x, *args, **kwargs))

    @classmethod
    def post_parse(cls, tokens, *args, **kwargs):
        return cls(tokens, *args, **kwargs)

    @classmethod
    def set_context(cls, context=None):
        if context is None:
            cls.ctx = OttoContext()
        else:
            cls.ctx = context

    @classmethod
    def from_string(cls, string, *args, **kwargs):
        parser = cls.__new__(cls, *args, **kwargs)
        return parser.parse_string(string)[0]
