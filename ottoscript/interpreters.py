
pyscript_registry = {}


class PrintLogger:

    def __init__(self, log_id='test', task=None, debug_as_info=False):
        self.log_id = log_id
        self.debug_as_info = debug_as_info
        self.task = task

    def set_task(self, task):
        self.task = task

    async def info(self, message):
        print(f'INFO: {self.log_id} {self.task} {message}')

    async def error(self, message):
        print(f'ERROR: {self.log_id} {self.task} {message}')

    async def warning(self, message):
        print(f'WARNING: {self.log_id}  {self.task} {message}')

    async def debug(self, message):
        if self.debug_as_info:
            print(f'DEBUG: {self.log_id}  {self.task} {message}')


class Service:

    def call(self, domain, service_name, **kwargs):
        return {'domain': domain,
                'service_name': service_name, 'kwargs': kwargs}


class State:

    def set(self, entity_name, value=None, new_attributes=None, kwargs=None):
        return {
            'entity_name': entity_name,
            'value': value,
            'new_attributes': new_attributes,
            'kwargs': kwargs
        }

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
        self.log.set_task('registrar')
        self.registry = {}

    async def add(self, controls, triggers, actions):
        namespace = controls.ctx.log.log_id
        name = controls.name
        key = (namespace, name)

        if namespace not in self.registry.keys():
            self.registry[namespace] = {}

        self.registry[namespace].update(
            {
                name:
                {
                    'actions': actions,
                    'controls': controls,
                    'triggers': triggers
                }
            }
        )

        if key not in pyscript_registry:
            pyscript_registry.update({key: []})

        for trigger in triggers.as_list():
            await self.log.debug(trigger)

            if trigger['type'] == 'state':
                func = state_trigger_factory(
                    self,
                    key,
                    controls,
                    trigger['string'],
                    trigger['hold']
                )

            elif trigger['type'] == 'time':
                func = time_trigger_factory(
                    self,
                    key,
                    controls,
                    trigger['string']
                )

            pyscript_registry[key].append(func)

    async def eval(self, key, kwargs):
        controls = self.registry[key[0]][key[1]]['controls']
        actions = self.registry[key[0]][key[1]]['actions']
        await self.log.info(f"Running {controls.name}")
        actions.ctx.update_vars(kwargs)
        await actions.eval()


def state_trigger_factory(registrar, key, controls, string, hold):

    # self.log.debug(f"Registering {key} with trigger '{string}'")

    # @task_unique(controls.name, kill_me=controls.restart)
    # @state_trigger(string, state_hold=hold)
    async def otto_state_func(**kwargs):
        nonlocal registrar, key
        await registrar.eval(key, kwargs)

    return otto_state_func


def time_trigger_factory(registrar, key, controls, string):
    # self.log_debug(f"Registering {self.name} with trigger '{string}'")

    # @task_unique(self.name, kill_me=self.restart)
    # @time_trigger(string)
    async def otto_time_func(**kwargs):
        nonlocal registrar, key
        await registrar.eval(key, kwargs)

    return otto_time_func

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


class Interpreter:
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

        await self.log.debug(message)

        return state.set(entity_name, value, new_attributes, kwargs)

    async def get_state(self, entity_name):
        await self.log.debug(f"Getting State of {entity_name}")
        return state.get(entity_name)

    async def call_service(self, domain, service_name, **kwargs):
        message = f"service.call({domain}, {service_name}, **{kwargs}))"
        await self.log.debug(message)
        return service.call(domain, service_name, **kwargs)

    async def sleep(self, seconds):
        await self.log.debug(f"task.sleep({seconds}))")
        return task.sleep(seconds)
