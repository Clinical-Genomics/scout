from scout.utils.convert import (
    isfloat,
    isint,
    make_bool,
    convert_number,
    amino_acid_residue_change_3_to_1,
)


def test_is_float_float():
    ## GIVEN a string with a float
    a = "1.2"
    ## WHEN checking if float
    res = isfloat(a)
    ## THEN assert it is a float
    assert res is True


def test_is_float_int():
    ## GIVEN a string with a integer
    a = "4"
    ## WHEN checking if float
    res = isfloat(a)
    ## THEN assert it is a float
    assert res is True


def test_is_float_char():
    ## GIVEN a string with a non number
    a = "b"
    ## WHEN checking if float
    res = isfloat(a)
    ## THEN assert it is not a float
    assert res is False


def test_is_float_empty():
    ## GIVEN a empty string
    a = ""
    ## WHEN checking if float
    res = isfloat(a)
    ## THEN assert it is not a float
    assert res is False


def test_is_int_float():
    ## GIVEN a string with a float
    a = "1.2"
    ## WHEN checking if integer
    res = isint(a)
    ## THEN assert it is not a integer
    assert res is False


def test_is_int_int():
    ## GIVEN a string with a int
    a = "4"
    ## WHEN checking if int
    res = isint(a)
    ## THEN assert it is a int
    assert res is True


def test_is_int_char():
    ## GIVEN a string with a character
    a = "b"
    ## WHEN checking if integer
    res = isfloat(a)
    ## THEN assert it is not a integer
    assert res is False


def test_is_int_empty():
    ## GIVEN a string with a empty string
    a = ""
    ## WHEN checking if integer
    res = isint(a)
    ## THEN assert it is not a integer
    assert res is False


def test_is_int_tricky():
    ## GIVEN a string with a empty string
    a = "1.0"
    ## WHEN checking if integer
    res = isint(a)
    ## THEN assert it is not a integer
    assert res is True


def test_convert_number_float():
    ## GIVEN a string with a float
    a = "1.2"
    ## WHEN converting to number
    res = convert_number(a)
    ## THEN assert it is the float
    assert res == 1.2


def test_convert_number_int():
    ## GIVEN a string with a integer
    a = "4"
    ## WHEN converting to number
    res = convert_number(a)
    ## THEN assert it is the float
    assert res == 4


def test_convert_number_empty():
    ## GIVEN a empty string
    a = ""
    ## WHEN converting to number
    res = convert_number(a)
    ## THEN assert it is None
    assert res is None


def test_convert_number_tricky():
    ## GIVEN a empty string
    a = "1.0"
    ## WHEN converting to number
    res = convert_number(a)
    ## THEN assert it is None
    assert res is 1


def test_make_bool_one():
    ## GIVEN a string representing a boolean
    a = "1"
    ## WHEN making a boolean
    res = make_bool(a)
    ## THEN assert it is True
    assert res is True


def test_make_bool_zero():
    ## GIVEN a string representing a boolean
    a = "0"
    ## WHEN converting to a boolean
    res = make_bool(a)
    ## THEN assert it is False
    assert res is False


def test_make_bool_empty():
    ## GIVEN a empty string
    a = ""
    ## WHEN converting to a boolean
    res = make_bool(a)
    ## THEN assert it is False
    assert res is False


def test_make_bool_nonsense():
    ## GIVEN a nonsense string
    a = "nonsense asdlkfjalk"
    ## WHEN converting to a boolean
    res = make_bool(a)
    ## THEN assert it is False
    assert res is False


def test_make_bool_yes():
    ## GIVEN a empty string
    a = "yes"
    ## WHEN converting to a boolean
    res = make_bool(a)
    ## THEN assert it is True
    assert res is True


def test_make_bool_YES():
    ## GIVEN a empty string
    a = "YES"
    ## WHEN converting to a boolean
    res = make_bool(a)
    ## THEN assert it is True
    assert res is True


def test_amino_acid_residue_change_3_to_1():
    ## GIVEN a protein change on HGVS 3-letter format
    a = "p.Ser241Phe"
    ## WHEN converting to 1-letter change string
    r = amino_acid_residue_change_3_to_1(a)
    ## THEN the result is correct
    assert r == "S241F"


def test_amino_acid_residue_change_3_to_1_none():
    ## GIVEN a protein change on HGVS 3-letter format
    a = None
    ## WHEN converting to 1-letter change string
    r = amino_acid_residue_change_3_to_1(a)
    ## THEN the result is correct
    assert r is None


def test_amino_acid_residue_change_3_to_1_stop():
    ## GIVEN a protein change on HGVS 3-letter format
    a = "p.Ser241Ter"
    ## WHEN converting to 1-letter change string
    r = amino_acid_residue_change_3_to_1(a)
    ## THEN the result is correct
    assert r == "S241*"


def test_amino_acid_residue_change_3_to_1_synonymous():
    ## GIVEN a protein change on HGVS 3-letter format
    a = "p.="
    ## WHEN converting to 1-letter change string
    r = amino_acid_residue_change_3_to_1(a)
    ## THEN the result is correct
    assert r is None


def test_amino_acid_residue_change_3_to_1_fs():
    ## GIVEN a protein change on HGVS 3-letter format
    a = "p.Arg544GlufsTer3"
    ## WHEN converting to 1-letter change string
    r = amino_acid_residue_change_3_to_1(a)
    ## THEN the result is undefined
    assert r is None


def test_amino_acid_residue_change_3_to_1_fs_ext():
    ## GIVEN a protein change on HGVS 3-letter format
    a = "p.Arg544Glnext*17"
    ## WHEN converting to 1-letter change string
    r = amino_acid_residue_change_3_to_1(a)
    ## THEN the result is undefined
    assert r is None


def test_amino_acid_residue_change_3_to_1_multiple():
    ## GIVEN a protein change on HGVS 3-letter format
    a = "p.MetLys997ArgGlu"
    ## WHEN converting to 1-letter change string
    r = amino_acid_residue_change_3_to_1(a)
    ## THEN the result is undefined
    assert r is None


def test_amino_acid_residue_change_3_to_1_del():
    ## GIVEN a protein change on HGVS 3-letter format
    a = "p.Phe2_Met46del"
    ## WHEN converting to 1-letter change string
    r = amino_acid_residue_change_3_to_1(a)
    ## THEN the result is undefined
    assert r is None
