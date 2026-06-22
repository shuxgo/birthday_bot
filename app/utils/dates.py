from datetime import date, datetime, time
from zoneinfo import ZoneInfo


def parse_birth_date(value: str) -> date:
    """Parse DD.MM or DD.MM.YYYY; year is kept only for storage compatibility."""
    parts = value.strip().split(".")
    if len(parts) not in (2, 3):
        raise ValueError("Введите дату в формате ДД.ММ или ДД.ММ.ГГГГ")
    day, month = int(parts[0]), int(parts[1])
    year = int(parts[2]) if len(parts) == 3 else 2000
    return date(year, month, day)


def parse_publication_datetime(value: str, tz: ZoneInfo, now: datetime | None = None) -> datetime:
    try:
        parsed = datetime.strptime(value.strip(), "%d.%m.%Y %H:%M")
    except ValueError as exc:
        raise ValueError("Введите дату и время в формате ДД.ММ.ГГГГ ЧЧ:ММ") from exc

    aware = parsed.replace(tzinfo=tz)
    now = now or datetime.now(tz)
    if aware <= now:
        raise ValueError("Дата публикации должна быть в будущем")
    return aware


def default_publication_datetime(birth_date: date, tz: ZoneInfo, now: datetime | None = None) -> datetime:
    now = now or datetime.now(tz)
    year = _next_valid_year(now.year, birth_date.month, birth_date.day)
    candidate = datetime.combine(
        date(year, birth_date.month, birth_date.day), time(hour=9), tzinfo=tz
    )
    if candidate <= now:
        year = _next_valid_year(year + 1, birth_date.month, birth_date.day)
        candidate = datetime.combine(
            date(year, birth_date.month, birth_date.day), time(hour=9), tzinfo=tz
        )
    return candidate


def format_dt(value: datetime) -> str:
    return value.strftime("%d.%m.%Y %H:%M")


def _next_valid_year(start_year: int, month: int, day: int) -> int:
    year = start_year
    while True:
        try:
            date(year, month, day)
            return year
        except ValueError:
            year += 1
