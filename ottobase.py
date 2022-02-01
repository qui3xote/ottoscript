from pyparsing import ParseResults, CaselessKeyword


class VarHandler:
    def __init__(self):
        self.internal = {}
        self.external = {}

    def get(self, key):
        internal = self.internal.get(key)

        if internal is None:
            return self.external.get(key)
        else:
            return internal

    def update(self, dictionary):
        self.internal.update(dictionary)

    def update_global(self, dictionary):
        self.external.update(dictionary)


class OttoContext:
    def __init__(self, var_handler):
        self.vars = var_handler


class OttoBase:

    def __new__(cls, *args, **kwargs):
        if len(args) > 0 and type(args[0]) == ParseResults:
            return super(OttoBase, cls).__new__(cls)

        return cls.pre_parse(*args, **kwargs)

    def __init__(self, tokens, *args, **kwargs):
        super().__init__(*[], **{})
        self.tokens = tokens[0]
        try:
            for k, v in self.tokens.as_dict().items():
                setattr(self, k, v)
        except Exception as error:
            print(f"Failed to init {type(self)}")
            print(tokens)
            print(error)

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

    async def eval(self, interpreter):
        return self.value

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
            cls.ctx = OttoContext(VarHandler())
        else:
            cls.ctx = context
