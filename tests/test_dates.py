from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.utils.dates import default_publication_datetime, parse_birth_date, parse_publication_datetime


def test_default_publication_uses_current_year_when_future():
    tz = ZoneInfo("Asia/Tashkent")
    birth_date = parse_birth_date("10.03")
    now = datetime(2026, 1, 1, 12, tzinfo=tz)
    assert default_publication_datetime(birth_date, tz, now).year == 2026


def test_default_publication_moves_to_next_year_when_past():
    tz = ZoneInfo("Asia/Tashkent")
    birth_date = parse_birth_date("10.03")
    now = datetime(2026, 3, 11, 12, tzinfo=tz)
    assert default_publication_datetime(birth_date, tz, now).year == 2027


def test_publication_datetime_rejects_past():
    tz = ZoneInfo("Asia/Tashkent")
    with pytest.raises(ValueError):
        parse_publication_datetime(
            "10.03.2026 09:00",
            tz,
            now=datetime(2026, 3, 11, 12, tzinfo=tz),
        )


def test_default_publication_handles_february_29():
    tz = ZoneInfo("Asia/Tashkent")
    birth_date = parse_birth_date("29.02")
    now = datetime(2026, 1, 1, 12, tzinfo=tz)
    assert default_publication_datetime(birth_date, tz, now).year == 2028
