import re
from datetime import datetime
from pytz import timezone

def string_to_datetime(date, tz):
    """Convert date string to datetime object"""

    # Format and return date
    try:
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
    except:
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M")

    # Convert date to timezone
    if timezone:
        date = date.astimezone(timezone(tz))
    
    return date

def valid_deviceID(string):
    """Return true if string contains only characters"""
    
    string = str(string)
    string = "".join(string.split())

    # Ensure length is valid
    if len(string) < 10:
        return False

    # Ensure numbers are provided
    if string.isalpha():
        return False
    
    # Ensure no special characters
    try:
        string.encode('ascii')
    except UnicodeEncodeError:
        return False
    return True