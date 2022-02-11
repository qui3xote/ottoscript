import pytest
from ottoscript.time import TimeStamp, RelativeTime, Date, DateTime
from ottoscript.interpreters import Interpreter

interpreter = Interpreter()


@pytest.mark.asyncio
async def test_timestamp():
    """Verify we correctly assign vars"""

    n1 = TimeStamp().parse_string("07:00")[0]
    n2 = TimeStamp().parse_string("07:15:30")[0]

    assert n1.string == "07:00:00"
    assert n1.seconds == 7 * 60 * 60

    assert n2.string == "07:15:30"
    assert n2.seconds == 7 * 3600 + 15 * 60 + 30


@pytest.mark.asyncio
async def test_relativetime():
    """Verify we correctly assign vars"""

    n1 = RelativeTime().parse_string("30 Seconds")[0]
    n2 = RelativeTime().parse_string("30 MINUTES")[0]
    n3 = RelativeTime().parse_string("30 HOURS")[0]

    assert n1.string == "30 SECONDS"
    assert n1.seconds == 30

    assert n2.string == "30 MINUTES"
    assert n2.seconds == 30 * 60

    assert n3.string == "30 HOURS"
    assert n3.seconds == 30 * 60 * 60


@pytest.mark.asyncio
async def test_date():
    """Verify we correctly assign dates"""

    n1 = Date().parse_string("2021-06-06")[0]

    assert n1.string == "2021-06-06"


@pytest.mark.asyncio
async def test_datetime():
    """Verify we correctly assign datetimes"""

    n1 = DateTime().parse_string("2021-06-06 07:30:15")[0]

    assert n1.string == "2021-06-06 07:30:15"
