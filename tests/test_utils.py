import pytest
from app.utils import validate_date_format, convert_to_iso

# Tests for validate_date_format
def test_validate_date_format_valid_datetime():
    assert validate_date_format('2024-01-01T12:00:00Z') is True
    assert validate_date_format('2024-01-01T12:00:00+00:00') is True
    assert validate_date_format('2024-01-01T12:00:00') is True  # No timezone
    assert validate_date_format('2024-01-01T12:00') is True #no seconds
    assert validate_date_format('2024-01-01T12:00:00.123') is True #with milliseconds

def test_validate_date_format_invalid_datetime():
    assert validate_date_format('2024-01-01T25:00:00') is False  # Invalid hour
    assert validate_date_format('2024-01-01T00:60:00') is False  # Invalid minute
    assert validate_date_format('2024-01-01T00:00:60') is False  # Invalid second
    assert validate_date_format('2024/01/01 12:00:00') is False  # Invalid separators
    assert validate_date_format('invalid-date') is False
    assert validate_date_format('2024-13-01T12:00:00Z') is False  # Invalid month
    assert validate_date_format('2024-01-32T12:00:00Z') is False  # Invalid day

# Tests for convert_to_iso
def test_convert_to_iso_valid_datetime():
    assert convert_to_iso('2024-01-01T12:34:56Z') == '2024-01-01T12:34:56+00:00'
    assert convert_to_iso('2024-01-01T12:34:56+05:30') == '2024-01-01T12:34:56+05:30'
    assert convert_to_iso('2024-01-01T12:34:56') == '2024-01-01T12:34:56'
    assert convert_to_iso('2024-01-01T12:34') == '2024-01-01T12:34:00' #add seconds
    assert convert_to_iso('2024-01-01T12:34:56.123456') == '2024-01-01T12:34:56.123456' #milliseconds

def test_convert_to_iso_date_only():
    assert convert_to_iso('2024-01-01') == '2024-01-01T00:00:00+00:00'

def test_convert_to_iso_invalid_input():
    with pytest.raises(ValueError):  # Expect a ValueError
        convert_to_iso('invalid-date')
    with pytest.raises(ValueError):
        convert_to_iso('2024-13-01')  # Invalid month