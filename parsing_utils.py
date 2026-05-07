from datetime import datetime


DEFAULT_DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"


def normalize_decimal_text(value):
    return value.replace(",", ".")


def parse_coordinate_groups(groups, positive_hemisphere):
    if len(groups) == 1:
        return float(normalize_decimal_text(groups[0]))

    if len(groups) != 3:
        raise ValueError(f"Unsupported coordinate groups: {groups}")

    if len(groups[0]) == 1:
        hemisphere, degrees, minutes = groups
    else:
        degrees, minutes, hemisphere = groups

    decimal = float(normalize_decimal_text(degrees)) + (
        float(normalize_decimal_text(minutes)) / 60.0
    )
    return decimal if hemisphere == positive_hemisphere else decimal * -1


def build_datetime_from_parts(date_parts, time_parts, date_order="dmy"):
    if date_order == "ymd":
        year, month, day = date_parts
    elif date_order == "mdy":
        month, day, year = date_parts
    else:
        day, month, year = date_parts

    hour, minute, second = time_parts
    return datetime(
        year=int(year),
        month=int(month),
        day=int(day),
        hour=int(hour),
        minute=int(minute),
        second=int(second),
    )


def parse_textual_datetime(parts, fmt="%d/%b/%Y %H:%M:%S"):
    month, day, year, hour, minute, second = parts
    value = f"{day}/{month}/{year} {hour}:{minute}:{second}"
    return datetime.strptime(value, fmt)
