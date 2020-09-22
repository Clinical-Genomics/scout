import re
import datetime


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
