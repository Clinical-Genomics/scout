import re

from scout.constants import AMINO_ACID_RESIDUE_3_TO_1


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


def make_bool_pass_none(string):
    if str(string).lower() == "none":
        return None
    return make_bool(string)


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


def amino_acid_residue_change_3_to_1(protein_sequence_name):
    if protein_sequence_name is None:
        return None

    p = re.compile("p.([A-Za-z]+)(\d+)([A-Za-z]+)")
    m = p.match(protein_sequence_name)
    if m is None:
        return None

    ref = AMINO_ACID_RESIDUE_3_TO_1.get(m.group(1), None)
    alt = AMINO_ACID_RESIDUE_3_TO_1.get(m.group(3), None)

    pos = m.group(2)

    if ref is None or m.group(2) is None or alt is None:
        return None

    protein_change = "".join([ref, pos, alt])

    return protein_change
