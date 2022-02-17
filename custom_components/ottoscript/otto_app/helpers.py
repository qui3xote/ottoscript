from importlib import reload


@pyscript_compile
def py_reload(module):
    reload(module)
    return module
