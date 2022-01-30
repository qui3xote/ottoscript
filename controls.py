from pyparsing import (Group,
                       Optional
                       )
from .keywords import AUTOMATION, RESTART
from .datatypes import ident
from .ottobase import OttoBase, Var


class AutoDefinition(OttoBase):
    parser = Group(AUTOMATION
                   + ident("name")
                   + Optional(Var()('trigger_var'))
                   + Optional(RESTART('restart_option'))
                   )

    @property
    def trigger_var(self):
        if hasattr(self, 'trigger_var'):
            return self.trigger_var.name
        else:
            return '@trigger'

    @property
    def restart(self):
        return hasattr(self, 'restart_option')
