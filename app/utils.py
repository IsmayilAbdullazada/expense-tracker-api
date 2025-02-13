from datetime import datetime, timezone

def validate_date_format(date_str):
    """
    Validates if a given string is a valid ISO 8601 date or datetime.

    Args:
        date_str: The string to validate.

    Returns:
        True if the string is a valid ISO 8601 date or datetime, False otherwise.
    """
    try:
        datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False
    
def convert_to_iso(date_str):
    """
    Converts a valid ISO 8601 date or datetime string to a full ISO 8601
    datetime string (including time, setting to UTC midnight if necessary).

    Args:
        date_str:  A *validated* ISO 8601 date or datetime string.

    Returns:
        A full ISO 8601 datetime string (YYYY-MM-DDTHH:MM:SS+00:00).

    Raises:
        ValueError: If the input string is not a valid ISO 8601 date/datetime.
    """
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        if date_obj.time() == datetime.min.time():  # If it's a date-only
            date_obj = datetime.combine(date_obj.date(), datetime.min.time()).replace(tzinfo=timezone.utc)
        return date_obj.isoformat()
    except ValueError:
        raise ValueError(f"Invalid date format: '{date_str}'.  Expected ISO 8601 (YYYY-MM-DDTHH:MM:SSZ or YYYY-MM-DD).")