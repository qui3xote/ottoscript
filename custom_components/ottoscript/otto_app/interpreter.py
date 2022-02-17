
pyscript_registry = {}


class Logger:

    def __init__(self, log_id='test', task=None, debug_as_info=False):
        self.log_id = log_id
        self.debug_as_info = debug_as_info
        self.task = task

    def set_task(self, task):
        self.info(f"Setting log name to {task}")
        self.task = task

    def info(self, message):
        log.info(f'{self.log_id}/{self.task} {message}')

    def error(self, message):
        log.error(f'{self.log_id}/{self.task} {message}')

    def warning(self, message):
        log.warning(f'{self.log_id}/{self.task} {message}')

    def debug(self, message):
        if self.debug_as_info:
            log.info(f'{self.log_id}/{self.task} {message}')
        else:
            log.debug(f'{self.log_id}/{self.task} {message}')


class Registrar:
    """Register functions and hold runtime vars"""

    def __init__(self, logger):
        self.log = logger
        self.log.set_task('registrar')
        self.registry = pyscript_registry

    def add(self, controls, triggers, actions):
        namespace = controls.ctx.log.log_id
        name = controls.name
        key = (namespace, name)

        if namespace not in self.registry.keys():
            self.log.debug(f"Adding {namespace} to registry")
            self.registry[namespace] = {}

        self.registry[namespace].update(
            {
                name:
                {
                    'actions': actions,
                    'controls': controls,
                    'triggers': triggers,
                    'trigger_funcs': []
                }
            }
        )

        # if key not in pyscript_registry:
        #     pyscript_registry.update({(namespace, name): []})

        self.log.debug(f"{name} has triggers {triggers.as_list()}")
        for trigger in triggers.as_list():
            self.log.debug(
                f"Registering {name} with trigger '{trigger['string']}'."
            )

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

            self.registry[namespace][name]['trigger_funcs'].append(func)
            # pyscript_registry[key].append(func)

    def eval(self, key, kwargs):
        actions = self.registry[key[0]][key[1]]['actions']
        controls = self.registry[key[0]][key[1]]['controls']
        actions.ctx.update_vars({controls.trigger_var: Wrapper(kwargs)})
        self.log.debug(f"{controls.name} triggered by {kwargs}")
        self.log.info(f"Running {controls.name}")
        actions.eval()


def state_trigger_factory(registrar, key, controls, string, hold):

    @task_unique(controls.name, kill_me=controls.restart)
    @state_trigger(string, state_hold=hold)
    def otto_state_func(**kwargs):
        nonlocal registrar, key
        registrar.eval(key, kwargs)

    return otto_state_func


def time_trigger_factory(registrar, key, controls, string):

    @task_unique(controls.name, kill_me=controls.restart)
    @time_trigger(string)
    def otto_time_func(**kwargs):
        nonlocal registrar, key
        registrar.eval(key, kwargs)

    return otto_time_func


class Interpreter:
    """Convert ottoscript commands to pyscript commands"""

    def __init__(self, logger=None):

        if logger is None:
            self.log = Logger()
        else:
            self.log = logger

    def set_state(self, entity_name, value=None,
                  new_attributes=None, kwargs={}):

        message = f"state.set(entity_name={entity_name},"
        message += f" value={value},"
        message += f" new_attributes={new_attributes},"
        message += f" kwargs = **{kwargs})"

        try:
            self.log.debug(message)
            return state.set(
                entity_name,
                value=value,
                new_attributes=new_attributes,
                **kwargs)

        except Exception as error:
            self.log_error(f"Failed to set {entity_name} to {value}: {error}")
            return False

    def get_state(self, entity_name):
        try:
            value = state.get(entity_name)
            self.log.debug(f"{entity_name} evaluated to {value}")
            return value
        except Exception as error:
            self.log.error(f"Error getting state of {entity_name}: {error}")
            return None

    def call_service(self, domain, service_name, **kwargs):
        message = f"service.call({domain}, {service_name}, **{kwargs}))"

        try:
            self.log.debug(message)
            service.call(domain, service_name, **kwargs)
            return True
        except Exception as error:
            log.error(f"Service {message} failed: {error}")
            return False

    def sleep(self, seconds):
        self.log.debug(f"task.sleep({seconds}))")
        task.sleep(seconds)
        return True

class Wrapper:
    def __init__(self, value):
        self.value = value

    def eval(self, attribute=None):
        log.info(self.value)
        log.info(attribute)
        if attribute is None:
            return self.value
        else:
            return self.value[attribute]
