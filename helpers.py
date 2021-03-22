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