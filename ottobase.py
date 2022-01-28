from pyparsing import ParseResults, CaselessKeyword


class VarHandler:
    def __init__(self):
        self.locals = {}
        self.globals = {}

    def get(self, key):
        return self.locals.get(key)

    def update(self, key, value):
        self.locals.update({key: value})


class OttoBase:
    parser = None
    vars = VarHandler()

    def __new__(cls, *args, **kwargs):

        if len(args) > 0 and type(args[0]) == ParseResults:
            return super(OttoBase, cls).__new__(cls)

        return cls.pre_parse(*args, **kwargs)

    def __init__(self, tokens, *args, **kwargs):
        super().__init__(*[], **{})
        self.args = args
        self.kwargs = kwargs
        self.tokens = tokens[0]
        for k, v in self.tokens.as_dict().items():
            setattr(self, k, v)

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

    @classmethod
    def pre_parse(cls, *args, **kwargs):
        cls.parser.set_name(cls.__name__)
        prs = cls.parser.set_parse_action(lambda x:
                                          cls.post_parse(x, *args, **kwargs))
        return prs

    @classmethod
    def post_parse(cls, tokens, *args, **kwargs):
        return cls(tokens, *args, **kwargs)
