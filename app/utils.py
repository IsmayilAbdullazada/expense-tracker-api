from datetime import datetime
def validate_date_format(date_str):
    try:
        datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False