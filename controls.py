from pyparsing import (Word,
                       Optional,
                       alphas,
                       alphanums
                       )
from .keywords import AUTOMATION, RESTART
from .ottobase import OttoBase, Var


class AutoDefinition(OttoBase):
    parser = AUTOMATION \
              + Word(alphas + "_", alphanums+"_")("_name") \
              + Optional(Var()('_trigger_var')) \
              + Optional(RESTART('_restart'))

    @property
    def name(self):
        return self._name

    @property
    def trigger_var(self):
        if hasattr(self, '_trigger_var'):
            return self._trigger_var.varname
        else:
            return '@trigger'

    @property
    def restart(self):
        if hasattr(self, '_restart'):
            return True
        else:
            return False
