import pytest
from ottoscript.base import OttoBase
from ottoscript.datatypes import String
from ottoscript.commands import (Assignment,
                                 Pass,
                                 Set,
                                 Turn,
                                 Toggle,
                                 Dim,
                                 Lock,
                                 Arm,
                                 Disarm,
                                 OpenClose,
                                 Call,
                                 Wait
                                 )
from ottoscript.interpreters import Interpreter

interpreter = Interpreter()
OttoBase.set_context()


@pytest.mark.asyncio
async def test_assign_local_vars():
    """Verify we correctly assign vars"""

    n = Assignment().parse_string("@foo = 'foostring'")[0]
    await n.eval()
    assert type(n.ctx.get_var('@foo')) == String
    assert n.ctx.get_var('@foo')._value == 'foostring'
    assert n.ctx.local_vars.get('@foo')._value == 'foostring'
    assert n.ctx.global_vars.get('@foo') is None


@pytest.mark.asyncio
async def test_assign_global_vars():
    """Verify we correctly assign global vars"""

    OttoBase.set_context()
    n = Assignment("global").parse_string("@foo = 'foostring'")[0]

    await n.eval()
    assert type(n.ctx.get_var('@foo')) == String
    assert n.ctx.get_var('@foo')._value == 'foostring'
    assert n.ctx.local_vars.get('@foo') is None
    assert n.ctx.global_vars.get('@foo')._value == 'foostring'


@pytest.mark.asyncio
async def test_pass():

    n = Pass().parse_string('pass')[0]
    assert await n.eval() is None


@pytest.mark.asyncio
async def test_set():

    n = Set().parse_string('set ship.crew to 15')[0]
    expected = [{'entity_name': 'ship.crew',
                 'value': 15,
                 'new_attributes': None,
                 'kwargs': None}]

    assert await n.eval() == expected


@pytest.mark.asyncio
async def test_turn():

    n = Turn().parse_string("turn off light light.cupola_lights")[0]
    expected = {'domain': 'light',
                'service_name': 'turn_off',
                'kwargs': {'entity_id': ['light.cupola_lights'],
                           'area_id': []}}

    assert await n.eval() == expected


@pytest.mark.asyncio
async def test_toggle():

    n = Toggle().parse_string("toggle light AREA cupola")[0]
    expected = {'domain': 'light',
                'service_name': 'toggle',
                'kwargs': {'entity_id': [],
                           'area_id': ['cupola']}}

    assert await n.eval() == expected


@pytest.mark.asyncio
async def test_dim():

    n1 = Dim().parse_string("dim AREA cupola to 100")[0]
    expected1 = {'domain': 'light',
                 'service_name': 'turn_on',
                 'kwargs': {'entity_id': [],
                            'area_id': ['cupola'],
                            'brightness': 100}}

    n2 = Dim().parse_string("dim AREA cupola to 50%")[0]
    expected2 = {'domain': 'light',
                 'service_name': 'turn_on',
                 'kwargs': {'entity_id': [],
                            'area_id': ['cupola'],
                            'brightness_pct': 50}}

    n3 = Dim().parse_string("dim AREA cupola BY 50%")[0]
    expected3 = {'domain': 'light',
                 'service_name': 'turn_on',
                 'kwargs': {'entity_id': [],
                            'area_id': ['cupola'],
                            'brightness_step_pct': 50}}

    n4 = Dim().parse_string("dim AREA cupola BY 50")[0]
    expected4 = {'domain': 'light',
                 'service_name': 'turn_on',
                 'kwargs': {'entity_id': [],
                            'area_id': ['cupola'],
                            'brightness_step': 50}}

    assert await n1.eval() == expected1
    assert await n2.eval() == expected2
    assert await n3.eval() == expected3
    assert await n4.eval() == expected4


@pytest.mark.asyncio
async def test_lock():

    n = Lock().parse_string("lock lock.front_door with (code=5555)")[0]
    expected = {'domain': 'lock',
                'service_name': 'lock',
                'kwargs': {'entity_id': ['lock.front_door'],
                           'area_id': [],
                           'code': 5555
                           }
                }

    assert await n.eval() == expected


@pytest.mark.asyncio
async def test_arm():

    n = Arm().parse_string("ARM HOME alarm_control_panel.honeywell")[0]
    expected = {'domain': 'alarm_control_panel',
                'service_name': 'alarm_arm_home',
                'kwargs': {'entity_id': ['alarm_control_panel.honeywell'],
                           'area_id': [],
                           }
                }

    assert await n.eval() == expected


@pytest.mark.asyncio
async def test_disarm():

    n = Disarm().parse_string("DISARM alarm_control_panel.honeywell")[0]
    expected = {'domain': 'alarm_control_panel',
                'service_name': 'alarm_disarm',
                'kwargs': {'entity_id': ['alarm_control_panel.honeywell'],
                           'area_id': [],
                           }
                }

    assert await n.eval() == expected


@pytest.mark.asyncio
async def test_openclose():

    n1 = OpenClose().parse_string("OPEN AREA downstairs to 50")[0]
    n1_expected = {'domain': 'cover',
                   'service_name': 'set_cover_position',
                   'kwargs': {'entity_id': [],
                              'area_id': ['downstairs'],
                              'position': 50,
                              }
                   }

    n2 = OpenClose().parse_string("CLOSE cover.downstairs_window")[0]
    n2_expected = {'domain': 'cover',
                   'service_name': 'set_cover_position',
                   'kwargs': {'entity_id': ['cover.downstairs_window'],
                              'area_id': [],
                              'position': 0,
                              }
                   }

    assert await n1.eval() == n1_expected
    assert await n2.eval() == n2_expected


@pytest.mark.asyncio
async def test_call():

    n1 = Call().parse_string("CALL cloud.disconnect")[0]
    n1_expected = {'domain': 'cloud',
                   'service_name': 'disconnect',
                   'kwargs': {}
                   }

    n2_string = "CALL cover.close_cover ON cover.downstairs_window"
    n2 = Call().parse_string(n2_string)[0]
    n2_expected = {'domain': 'cover',
                   'service_name': 'close_cover',
                   'kwargs': {'entity_id': ['cover.downstairs_window'],
                              'area_id': [],
                              }
                   }

    n3_string = """CALL light.turn_on ON
                     light.kitchen_light with (brightness=50)"""
    n3 = Call().parse_string(n3_string)[0]
    n3_expected = {'domain': 'light',
                   'service_name': 'turn_on',
                   'kwargs': {'entity_id': ['light.kitchen_light'],
                              'area_id': [],
                              'brightness': 50
                              }
                   }

    assert await n1.eval() == n1_expected
    assert await n2.eval() == n2_expected
    assert await n3.eval() == n3_expected


@pytest.mark.asyncio
async def test_wait():

    n1 = Wait().parse_string("WAIT 30 SECOND")[0]
    expected1 = 30

    n2 = Wait().parse_string("WAIT 45 MINUTE")[0]
    expected2 = 45 * 60

    n3 = Wait().parse_string("WAIT 00:45")[0]
    expected3 = 45 * 60

    assert await n1.eval() == expected1
    assert await n2.eval() == expected2
    assert await n3.eval() == expected3
