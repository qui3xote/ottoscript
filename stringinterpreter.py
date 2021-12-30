class TestInterpreter:
    def __init__(self):
        pass

    @property
    def parser(self):
        command = Or([cls.parser() for cls in BaseCommand.__subclasses__()])
        trigger = Or([cls.parser() for cls in BaseTrigger.__subclasses__()])
        condition = Or([cls.parser() for cls in BaseCondition.__subclasses__()])
        WHEN, THEN = map(CaselessKeyword, ["WHEN", "THEN"])


        when_expr = WHEN.suppress() + Group(trigger)("when")
        then_clause = THEN.suppress() + Group(OneOrMore(command))("actions")
        conditionclause = condition("conditions") + then_clause
        ottoparser = when_expr + OneOrMore(Group(conditionclause))("condition_clauses")
        return ottoparser


    def parse(self, script):
        obj = self.parser.parse_string(script)


    def get_state(self, name):
        return 1

    def set_state(self, name, value=None, attr_kwargs=None):
        try:
            state.set(name, value, **attr_kwargs)
            return True
        except:
            self.log.warn(f"Unable to complete operation state.set({name}, {value}, **{attr_kwargs})")
            return False


    def service_call(self, domain, servicename, kwargs):
        try:
            service.call(domain, servicename, kwargs)
            return True
        except:
            self.log.warn(f"Unable to complete operation state.set({name}, {value}, **{attr_kwargs})")
            return False

    def log(self, msg, level="info"):
        print(f"{level.upper()}: {msg}")

    def compare(self, comparison):
        operation = comparison.eval()

        for n, i in enumerate(operation['items']):
            self.log(f"Found: {type(i)}, {i}")

            if type(i) == Entity:
                self.log(f"Entity: {type(i)}, {i.name}, {self.get_state(i.name)}")
                operation['items'][n] = self.get_state(i.name)

        result = operation['opfunc'](*operation['items'])
        self.log(f"{result}: {operation['opfunc']}, {operation['items']}")
        return result


    def eval_tree(self, tree):
        statements = []

        for i in tree['items']:
            if type(i) == dict:
                statements.append(eval_tree(i))
            if type(i) == Comparison:
                statements.append(self.compare(i))

        result = tree['opfunc'](statements)
        self.log(f"{result}: {tree}")
        return result

    def add(self, script):
        automation = self.parser.parse_string(script)

        ifthens = []

        for conditions, commands in automation.condition_clauses.as_list():
            ifthens.append([conditions.eval(), [command.eval() for command in commands]])

        self.log(f"trigger: {str(automation.when[0])}",'info')

        for conditions, commands in ifthens:
            if self.eval_tree(conditions) == True:
                for command in commands:
                    self.log(command)
            else:
                self.log("conditions failed","info")
