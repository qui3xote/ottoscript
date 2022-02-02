import pytest
from ottoscript.ottobase import OttoBase, VarHandler
from ottoscript.commands import Assignment
from ottoscript.controls import GlobalParser
# from ottoscript.interpreters import TestInterpreter


@pytest.mark.asyncio
async def test_globalparser():
    """Verify we correctly parse globals"""

    OttoBase.set_context()
    n = GlobalParser().parse_string("@foo = 'foostring'")[0]
    assert n.ctx.vars.external.get("@foo")._value == 'foostring'
    assert n.ctx.vars.internal.get("@foo") is None
    assert n.ctx.vars.get("@foo")._value == 'foostring'
