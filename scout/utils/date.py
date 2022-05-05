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
    """Given time as datetime() or integer, return the time passed from now
    as a string in human readable format"""

    def more_than_a_day(days):
        """Return a string for passed time more than a day"""
        if days == 1:
            return "Yesterday"
        if days < 7:
            return str(days) + " days ago"
        if days == 7:
            return str(days // 7) + " week ago"
        if days < 31:
            return str(days // 7) + " weeks ago"
        if days < 365:
            return str(days // 30) + " months ago"
        return str(days // 365) + " years ago"

    def within_24_h(seconds):
        """Return a string for passed time is less than a day"""
        if seconds < 10:
            return "just now"
        if seconds < 60:
            return str(seconds) + " seconds ago"
        if seconds < 120:
            return "a minute ago"
        if seconds < 3600:
            return str(seconds // 60) + " minutes ago"
        if seconds < 7200:
            return "an hour ago"
        if seconds < 86400:
            return str(seconds // 3600) + " hours ago"

    (diff_seconds, diff_days) = get_time_diff(time)
    if diff_days == 0:
        return within_24_h(diff_seconds)
    return more_than_a_day(diff_days)


def get_time_diff(time):
    """Get diff from now() minus time."""
    now = datetime.datetime.now()
    if type(time) is int:
        diff = now - datetime.datetime.fromtimestamp(time)
    elif isinstance(time, datetime.datetime):
        diff = now - time
    diff_seconds = diff.seconds
    diff_days = diff.days
    return (diff_seconds, diff_days)
