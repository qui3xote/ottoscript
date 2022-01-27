from itertools import product


class VarHandler:
    def __init__(self):
        self.locals = {}
        self.globals = {}

    def get(self, key):
        return self.locals.get(key)

    def update(self, key, value):
        self.locals.update({key: value})


class ExampleInterpreter:
    def __init__(self, log_id='Test', debug_as_info=True):
        self.log_id = log_id
        self.debug_as_info = debug_as_info
        self.trigger_funcs = {'state': self.state_trigger,
                              'time': self.time_trigger,
                              }
        self.vars = VarHandler()

    def set_controls(self, controller=None):
        self.controls = controller
        if controller is not None:
            self.name = controller.name
            self.restart = controller.restart
            self.trigger_var = controller.trigger_var

    async def register(self, trigger):
        await self.trigger_funcs[trigger.type](trigger)

    async def state_trigger(self, trigger):
        trigger_strings = []

        for name in trigger.entities:
            string = []
            if trigger.new is not None:
                string.append(f"{name} == '{trigger.new}'")

            if trigger.old is not None:
                string.append(f"{name}.old == '{trigger.old}'")

            if len(string) == 0:
                string.append(f"{name}")

            trigger_strings.append(" and ".join(string))
            await self.log_info(f"state: {self.name}: {string} {self.actions}")

    async def time_trigger(self, trigger):
        days = trigger.days
        times = trigger.times
        offset = trigger.offset_seconds

        prod = product(days, times)
        triggers = [f"once({x[0]} {x[1]} + {offset}s)" for x in prod]
        for t in triggers:
            await self.log_info(f"time: {self.name} {t} {self.actions}")

    async def set_state(self,
                        entity_name,
                        value=None,
                        new_attributes=None,
                        kwargs=None):

        await self.log_info(f"state.set(entity_name={entity_name},"
                            + f" value={value},"
                            + f" new_attributes={new_attributes},"
                            + f" kwargs = **{kwargs})")

    async def get_state(self, entity_name):
        await self.log_info(f"Getting State of {entity_name}")
        return 1
        # return 1 because it can be used to test >, =, etc.

    async def call_service(self, domain, service_name, kwargs):
        message = f"service.call({domain}, {service_name}, **{kwargs}))"
        await self.log_debug(message)

    async def sleep(self, seconds):
        await self.log_info(f"task.sleep({seconds}))")

    async def log_info(self, message):
        print(f'INFO: {self.log_id} {message}')

    async def log_error(self, message):
        print(f'Error: {self.log_id} {message}')

    async def log_warning(self, message):
        print(f'Warning: {self.log_id} {message}')

    async def log_debug(self, message):
        if self.debug_as_info:
            print(f'DEBUG: {self.log_id} {message}')
        else:
            pass
