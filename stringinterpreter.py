class TestInterpreter:
    def __init__(self):
        pass

    def get_state(self, name):
        return f"{name}"

    def set_state(self, name, value=None, attr_kwargs=None):
        try:
            state.set(name, value, **attr_kwargs)
            return True
        except:
            log.warn(f"Unable to complete operation state.set({name}, {value}, **{attr_kwargs})")
            return False


    def service_call(self, domain, servicename, kwargs):
        try:
            service.call(domain,servicename,kwargs)
            return True
        except:
            log.warn(f"Unable to complete operation state.set({name}, {value}, **{attr_kwargs})")
            return False

    def log(self, msg, level):
        print(f"{level.upper()}: {msg}")
