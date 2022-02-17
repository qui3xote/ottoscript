import pytest
from ottoscript.base import OttoBase
from ottoscript.controls import GlobalParser


@pytest.mark.asyncio
async def test_globalparser():
    """Verify we correctly parse globals"""

    OttoBase.set_context()
    n = GlobalParser().parse_string("@foo = 'foostring'")[0]

    assert n.ctx.global_vars.get("@foo")._value == 'foostring'
    assert n.ctx.local_vars.get("@foo") is None
    assert n.ctx.get_var("@foo")._value == 'foostring'
