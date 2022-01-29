from itertools import product


class Logger:

    def __init__(self, log_id='test', name=None, debug_as_info=False):
        self.log_id = log_id
        self.name = name
        self.debug_as_info = debug_as_info

    async def info(self, message):
        print(f'INFO: {self.log_id} {message}')

    async def error(self, message):
        print(f'Error: {self.log_id} {message}')

    async def warning(self, message):
        print(f'Warning: {self.log_id} {message}')

    async def debug(self, message):
        if self.debug_as_info:
            print(f'DEBUG: {self.log_id} {message}')
        else:
            print(f'DEBUG: {self.log_id} {message}')


class Service:

    def call(self, domain, service_name, **kwargs):
        return {'domain': domain,
                'service_name': service_name, 'kwargs': kwargs}


class State:

    def set(self, entity_name, value=None, new_attributes=None, kwargs=None):
        return {'entity_name': entity_name,
                'value': value,
                'new_attributes': new_attributes,
                'kwargs': kwargs}

    def get(self, entity_name):
        return entity_name


class Task:

    def sleep(self, seconds):
        return seconds


state = State()
service = Service()
task = Task()


class ExampleInterpreter:
    def __init__(self, log_id='Test', debug_as_info=True):
        self.debug_as_info = debug_as_info
        self.trigger_funcs = {'state': self.state_trigger,
                              'time': self.time_trigger,
                              }
        self.log = Logger(log_id)

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
            await self.log.info(f"state: {self.name}: {string} {self.actions}")

    async def time_trigger(self, trigger):
        days = trigger.days
        times = trigger.times
        offset = trigger.offset_seconds

        prod = product(days, times)
        triggers = [f"once({x[0]} {x[1]} + {offset}s)" for x in prod]
        for t in triggers:
            await self.log.info(f"time: {self.name} {t} {self.actions}")

    async def set_state(self,
                        entity_name,
                        value=None,
                        new_attributes=None,
                        kwargs=None):

        await self.log.info(f"state.set(entity_name={entity_name},"
                            + f" value={value},"
                            + f" new_attributes={new_attributes},"
                            + f" kwargs = **{kwargs})")

        return state.set(entity_name, value, new_attributes, kwargs)

    async def get_state(self, entity_name):
        await self.log.info(f"Getting State of {entity_name}")
        return state.get(entity_name)

    async def call_service(self, domain, service_name, **kwargs):
        message = f"service.call({domain}, {service_name}, **{kwargs}))"
        await self.log.debug(message)
        return service.call(domain, service_name, **kwargs)

    async def sleep(self, seconds):
        await self.log.info(f"task.sleep({seconds}))")
        return task.sleep(seconds)
