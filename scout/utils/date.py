import datetime
import re


def match_date(date):
    """Check if a string is a valid date

    Args:
        date(str)

    Returns:
        bool
    """
    date_pattern = re.compile("^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])")
    if re.match(date_pattern, date):
        return True

    return False


def get_date(date, date_format=None):
    """Return a datetime object if there is a valid date

    Raise exception if date is not valid
    Return todays date if no date where added

    Args:
        date(str)
        date_format(str)

    Returns:
        date_obj(datetime.datetime)
    """
    date_obj = datetime.datetime.now()
    if date:
        if date_format:
            date_obj = datetime.datetime.strptime(date, date_format)
        else:
            if match_date(date):
                if len(date.split("-")) == 3:
                    date = date.split("-")
                elif len(date.split(" ")) == 3:
                    date = date.split(" ")
                elif len(date.split(".")) == 3:
                    date = date.split(".")
                else:
                    date = date.split("/")
                date_obj = datetime.datetime(*(int(number) for number in date))
            else:
                raise ValueError("Date %s is invalid" % date)

    return date_obj


def pretty_date(time=False):
    """Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc """
    now = datetime.datetime.now()
    if type(time) is int:
        diff = now - datetime.datetime.fromtimestamp(time)
    elif isinstance(time, datetime.datetime):
        diff = now - time
    elif not time:
        diff = 0
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff // 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff // 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff == 7:
        return str(day_diff // 7) + " week ago"
    if day_diff < 31:
        return str(day_diff // 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff // 30) + " months ago"
    return str(day_diff // 365) + " years ago"
