class ExampleInterpreter:

    def __init__(self, log_id=None):
        self.log_id = log_id

    def set_state(self, entity_name, value=None, new_attributes=None, kwargs=None):
        self.log_info("state.set(entity_name={entity_name}, \
                            value={value}, \
                            new_attributes={new_attributes}, \
                            kwargs = **{kwargs})")
        return True

    def get_state(self, entity_name):
        self.log_info(f"Getting State of {entity_name}")
        # return 1 because it can be used to test >, =, etc.
        return 1

    def call_service(self, domain, service_name, kwargs):
        self.log_info(f"service.call({domain}, {service_name}, **{kwargs}))")
        return True

    def sleep(self,seconds):
        self.log_info(f"task.sleep({seconds}))")

    def log_info(self, message):
        print(f'INFO: {self.log_id} {message}')

    def log_error(self, message):
        log.error(f'ERROR: {self.log_id} {message}')

    def log_warning(self, message):
        log.warning(f'WARNING: {self.log_id} {message}')

    def log_debug(self, message):
        if DEBUG_AS_INFO:
            log.info(message)
        else:
            log.debug(message)
