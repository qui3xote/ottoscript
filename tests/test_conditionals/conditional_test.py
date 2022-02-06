import pytest
from collections import Counter
from ottoscript.conditionals import (
    Comparison,
    Then,
    If,
    IfThen,
    IfThenElse,
    Case
)
from ottoscript.interpreters import TestInterpreter

interpreter = TestInterpreter()


@pytest.mark.asyncio
async def test_comparison():
    """Verify we correctly parse a comparison"""

    strings = [("light.cupola_lights == 'light.cupola_lights'", True),
               ("light.cupola_lights != 'light.office_lights'", True),
               ("15 >= 10", True),
               ("'foobar' > 'foo'", True)]

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
        t = Then().parse_string(s)[0]
        results = await t.eval()
        for num, result in enumerate(results):
            assert result == expected[n][num]


@pytest.mark.asyncio
async def test_if():
    """Verify we correctly parse an if statement"""

    tests = [("IF light.cupola_lights == 'light.cupola_lights'", True),
             ("IF 10 > 5 AND 'string' == 'string'", True),
             ("IF 5 > 10 OR (10 > 5 AND 'string' == 'string')", True),
             ("IF 'foobar' < 'foo'", False)]

    for t in tests:
        n = If().parse_string(t[0])[0]
        assert await n.eval() == t[1]


@pytest.mark.asyncio
async def test_ifthen():
    """Verify we correctly parse an IfThen statement"""

    tests = [("""IF light.cupola_lights == 'light.cupola_lights'
                 WAIT 30 seconds END""", [30]),
             ("""IF 10 > 5 AND 'string' == 'string'
                 WAIT 30 seconds WAIT 60 seconds END""", [30, 60])]

    for t in tests:
        n = IfThen().parse_string(t[0])[0]
        x = await n.eval()
        assert Counter(x) == Counter(t[1])

    false_string = "IF 'foobar' < 'foo' WAIT 30 SECONDS END"
    n = IfThen().parse_string(false_string)[0]
    assert await n.eval() is False


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
async def test_case():
    """Verify we correctly parse an IfThenElse statement"""

    tests = [("""CASE
                 IF light.cupola_lights == 'light.cupola_lights'
                    WAIT 30 seconds
                    END
                 IF light.office_lights == 'light.office_lights'
                    WAIT 30 seconds
                    END
                 ELSE WAIT 60 seconds
                 END""", 1),
             ("""CASE
                  IF light.cupola_lights == 'light.office_lights'
                     WAIT 30 seconds
                     END
                  IF light.office_lights == 'light.office_lights'
                     WAIT 30 seconds
                     END
                  ELSE WAIT 60 seconds
                  END""", 2),
             ("""CASE
                  IF light.cupola_lights == 'light.office_lights'
                     WAIT 30 seconds
                     END
                  IF light.office_lights == 'light.cupola_lights'
                     WAIT 30 seconds
                     END
                  ELSE WAIT 60 seconds
                  END""", 0),
             ("""CASE
                   IF light.cupola_lights == 'light.office_lights'
                      WAIT 30 seconds
                      END
                   IF light.office_lights == 'light.cupola_lights'
                      WAIT 30 seconds
                      END
                   END""", None)
             ]

    for t in tests:
        n = Case().parse_string(t[0])[0]
        x = await n.eval()
        assert x == t[1]
