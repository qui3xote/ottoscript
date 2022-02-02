
class PrintLogger:

    def __init__(self, log_id='test', debug_as_info=False):
        self.log_id = log_id
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
        if len(entity_name.split('.')) == 2:
            return entity_name
        elif len(entity_name.split('.')) == 3:
            return 1


class Task:

    def sleep(self, seconds):
        return seconds


state = State()
service = Service()
task = Task()


class Registrar:
    """Register functions and hold runtime vars"""
    def __init__(self, logger):
        self.log = logger

    def add(self, ottofunc):
        pass
    # async def state_trigger(self, trigger):
    #     trigger_strings = []
    #
    #     for name in trigger.entities:
    #         string = []
    #         if trigger.new is not None:
    #             string.append(f"{name} == '{trigger.new}'")
    #
    #         if trigger.old is not None:
    #             string.append(f"{name}.old == '{trigger.old}'")
    #
    #         if len(string) == 0:
    #             string.append(f"{name}")
    #
    #         trigger_strings.append(" and ".join(string))
    #         message = f"state trigger: {self.name}: {string} {self.actions}"
    #         await self.log.debug(message)
    #
    # async def time_trigger(self, trigger):
    #     days = trigger.days
    #     times = trigger.times
    #     offset = trigger.offset_seconds
    #
    #     prod = product(days, times)
    #     triggers = [f"once({x[0]} {x[1]} + {offset}s)" for x in prod]
    #     for t in triggers:
    #         await self.log.debug(f"time: {self.name} {t} {self.actions}")


class TestInterpreter:
    """Convert ottoscript commands to pyscript commands"""

    def __init__(self, logger=None):

        if logger is None:
            self.log = PrintLogger()
        else:
            self.log = logger

    async def set_state(self, entity_name, value=None,
                        new_attributes=None, kwargs=None):

        message = f"state.set(entity_name={entity_name},"
        message += f" value={value},"
        message += f" new_attributes={new_attributes},"
        message += f" kwargs = **{kwargs})"

        await self.log.info(message)

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
