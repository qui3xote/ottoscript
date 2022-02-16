import pytest
from collections import Counter
from ottoscript.triggers import StateChange, WeeklySchedule, SunEvent
from ottoscript.interpreters import Interpreter

interpreter = Interpreter()


@pytest.mark.asyncio
async def test_weekly_schedule():
    """Verify we correctly parse WeeklySchedule"""

    strings = [("07:00", ["once( 07:00:00 + 0s)"]),
               ("07:00 ON weekend", ["once(sat 07:00:00 + 0s)",
                "once(sun 07:00:00 + 0s)"]),
               ("07:00 ON wed, thu",
                ["once(wed 07:00:00 + 0s)", "once(thu 07:00:00 + 0s)"]
                )
               ]

    for s in strings:
        n = WeeklySchedule().parse_string(s[0])[0]
        result = n.strings
        assert Counter(result) == Counter(s[1])


@pytest.mark.asyncio
async def test_sunevent():
    """Verify we correctly parse SunEvent"""

    strings = [("SUNRISE", ["once( sunrise + 0s)"]),
               ("30 SECONDS AFTER SUNSET", ["once( sunset + 30s)"]),
               ("30 SECONDS AFTER SUNSET ON WEEKEND",
                ["once(sat sunset + 30s)", "once(sun sunset + 30s)"]
                )
               ]

    for s in strings:
        n = SunEvent().parse_string(s[0])[0]
        result = n.strings
        assert Counter(result) == Counter(s[1])


@pytest.mark.asyncio
async def test_statechange():
    """Verify we correctly parse State triggers"""

    strings = [
        (
            "input_boolean.mode CHANGES",
            ["input_boolean.mode"]
        ),

        (
            "input_boolean.mode CHANGES from 'on'",
            ["input_boolean.mode.old == 'on'"]
        ),

        (
            "input_boolean.mode CHANGES to 'on'",
            ["input_boolean.mode == 'on'"]
        ),

        (
            "input_boolean.mode CHANGES from 'off' to 'on'",
            ["input_boolean.mode == 'on' "
             + "and input_boolean.mode.old == 'off'"]
        ),

        (
            "light.light1, light.light2 CHANGES from 'off' to 'on'",
            ["light.light1 == 'on' and light.light1.old == 'off'",
                "light.light2 == 'on' and light.light2.old == 'off'"]
        ),

        (
            "light.light1:brightness CHANGES from <= 1 to > 1",
            ["float(light.light1.brightness) > 1 and " +
                "float(light.light1.brightness.old) <= 1"]
        )
    ]

    for s in strings:
        n = StateChange().parse_string(s[0])[0]
        result = n.strings
        assert Counter(result) == Counter(s[1])
