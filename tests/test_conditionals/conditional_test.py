import pytest
from collections import Counter
from ottoscript.conditionals import (
    Comparison,
    CommandBlock,
    Condition,
    IfThenElse,
    Switch
)
from ottoscript.interpreters import Interpreter
from ottoscript.base import OttoContext, OttoBase
from ottoscript.datatypes import String

interpreter = Interpreter()


@pytest.mark.asyncio
async def test_comparison():
    """Verify we correctly parse a comparison"""

    strings = [("light.cupola_lights == 'light.cupola_lights'", True),
               ("light.cupola_lights != 'light.office_lights'", True),
               ("15 >= 10", True),
               ("'foobar' > 'foo'", True),
               ("@foo == 'bar'", True)]

    ctx = OttoContext()
    ctx.update_vars(
        {
            "@foo": String().parse_string("'bar'")[0]
        }
    )

    OttoBase.set_context(ctx)

    for s in strings:
        n = Comparison().parse_string(s[0])[0]
        assert await n.eval() == s[1]


@pytest.mark.asyncio
async def test_then():
    """Verify we correctly parse a comparison"""

    strings = ["ARM HOME alarm_control_panel.honeywell",
               """ ARM HOME alarm_control_panel.honeywell
                   DISARM alarm_control_panel.honeywell
               """
               ]

    expected = [[{'domain': 'alarm_control_panel',
                 'service_name': 'alarm_arm_home',
                  'kwargs': {
                      'entity_id': ['alarm_control_panel.honeywell'],
                      'area_id': [],
                  }
                  }],
                [{'domain': 'alarm_control_panel',
                            'service_name': 'alarm_arm_home',
                            'kwargs': {
                                'entity_id': ['alarm_control_panel.honeywell'],
                                'area_id': [],
                            }
                  },
                 {'domain': 'alarm_control_panel',
                  'service_name': 'alarm_disarm',
                  'kwargs': {'entity_id': ['alarm_control_panel.honeywell'],
                             'area_id': [],
                             }
                  }
                 ]
                ]

    for n, s in enumerate(strings):
        t = CommandBlock().parse_string(s)[0]
        results = await t.eval()
        for num, result in enumerate(results):
            assert result == expected[n][num]


@pytest.mark.asyncio
async def test_condition():
    """Verify we correctly parse an if statement"""

    tests = [("light.cupola_lights == 'light.cupola_lights'", True),
             ("10 > 5 AND 'string' == 'string'", True),
             ("5 > 10 OR (10 > 5 AND 'string' == 'string')", True),
             ("'foobar' < 'foo'", False)]

    for t in tests:
        n = Condition().parse_string(t[0])[0]
        assert await n.eval() == t[1]


@pytest.mark.asyncio
async def test_ifthenelse():
    """Verify we correctly parse an IfThenElse statement"""

    tests = [("""IF light.cupola_lights == 'light.cupola_lights'
                 WAIT 30 seconds
                 ELSE WAIT 60 seconds
                 END""", [30]),
             ("""IF light.cupola_lights != 'light.cupola_lights'
                  WAIT 30 seconds
                  ELSE WAIT 60 seconds
                  END""", [60]),
             ("""IF light.cupola_lights != 'light.cupola_lights'
                  WAIT 30 seconds
                  END""", None)
             ]

    for t in tests:
        n = IfThenElse().parse_string(t[0])[0]
        x = await n.eval()
        if type(t[1]) == list:
            assert Counter(x) == Counter(t[1])
        else:
            assert x == t[1]


@pytest.mark.asyncio
async def test_switch():
    """Verify we correctly parse an IfThenElse statement"""

    tests = [("""SWITCH
                 CASE light.cupola_lights == 'light.cupola_lights'
                    WAIT 30 seconds
                 CASE light.office_lights == 'light.office_lights'
                    WAIT 30 seconds
                 DEFAULT
                    WAIT 60 seconds
                 END""", 1),
             ("""SWITCH
                  CASE light.cupola_lights == 'light.office_lights'
                     WAIT 30 seconds
                  CASE light.office_lights == 'light.office_lights'
                     WAIT 30 seconds
                  DEFAULT
                    WAIT 60 seconds
                  END""", 2),
             ("""SWITCH
                  CASE light.cupola_lights == 'light.office_lights'
                     WAIT 30 seconds
                  CASE light.office_lights == 'light.cupola_lights'
                     WAIT 30 seconds
                  DEFAULT
                    WAIT 60 seconds
                  END""", 0),
             ("""SWITCH
                   CASE light.cupola_lights == 'light.office_lights'
                      WAIT 30 seconds
                   CASE light.office_lights == 'light.cupola_lights'
                      WAIT 30 seconds
                   END""", None)
             ]

    for t in tests:
        n = Switch().parse_string(t[0])[0]
        x = await n.eval()
        assert x == t[1]


@pytest.mark.asyncio
async def test_switch_left():
    """Verify we correctly parse a switch statement"""

    tests = [("""SWITCH light.cupola_lights
                 CASE 'light.cupola_lights'
                    WAIT 30 seconds
                 CASE 'light.office_lights'
                    WAIT 30 seconds
                 DEFAULT
                    WAIT 60 seconds
                 END""", 1),
             ("""SWITCH light.cupola_lights
                  CASE 'light.office_lights'
                     WAIT 30 seconds
                  CASE 'light.cupola_lights'
                     WAIT 30 seconds
                  DEFAULT
                    WAIT 60 seconds
                  END""", 2),
             ("""SWITCH light.cupola_lights
                  CASE 'light.office_lights'
                     WAIT 30 seconds
                  CASE 'light.den_lights'
                     WAIT 30 seconds
                  DEFAULT
                    WAIT 60 seconds
                  END""", 0),
             ("""SWITCH light.cupola_lights
                   CASE  'light.office_lights'
                      WAIT 30 seconds
                   CASE 'light.den_lights'
                      WAIT 30 seconds
                   END""", None)
             ]

    for n, t in enumerate(tests):
        s = Switch().parse_string(t[0])[0]
        x = await s.eval()
        assert x == t[1]
