def parse_telegram_id(value: str) -> int:
    cleaned = value.strip()
    if cleaned.startswith("@"):
        raise ValueError("Для MVP добавление по username не поддержано: укажите Telegram ID")
    try:
        return int(cleaned)
    except ValueError as exc:
        raise ValueError("Введите числовой Telegram ID") from exc

