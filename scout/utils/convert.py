def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True


def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b


def make_bool(string):
    """Convert a string to boolean"""
    if str(string).lower() in ["yes", "true", "1", "t"]:
        return True
    return False


def convert_number(string):
    """Convert a string to number
    If int convert to int otherwise float

    If not possible return None
    """
    res = None
    if isint(string):
        res = int(float(string))
    elif isfloat(string):
        res = float(string)
    return res
