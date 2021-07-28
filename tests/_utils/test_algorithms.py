from scout.utils.algorithms import ui_score


def test_compare_ui_score():
    ## GIVEN three sets
    a = set(["a", "b"])
    b = set(["b", "a", "d"])
    c = set(["b", "c", "d"])

    ## WHEN finding the similarity
    similarity_ab = ui_score(a, b)
    similarity_ac = ui_score(a, c)

    ## THEN assert a and b are more similar than a and c
    assert similarity_ab > similarity_ac


def test_get_almost_identical_ui_score():
    ## GIVEN two disjunct sets
    a = set(["a", "b"])
    b = set(["b", "a", "d"])

    ## WHEN finding the similarity
    similarity = ui_score(a, b)

    ## THEN assert 0 < similarity < 1
    assert 0 < similarity
    assert similarity < 1


def test_get_identical_ui_score():
    ## GIVEN two disjunct sets
    a = set(["a", "b"])
    b = set(["b", "a"])

    ## WHEN finding the similarity
    similarity = ui_score(a, b)

    ## THEN assert similarity is 1
    assert similarity == 1


def test_get_similar_ui_score():
    ## GIVEN two disjunct sets
    a = set(["a", "b"])
    b = set(["b", "c", "d"])

    ## WHEN finding the similarity
    similarity = ui_score(a, b)

    ## THEN assert similarity is larger than 0
    assert similarity > 0


def test_get_disjunct_ui_score():
    ## GIVEN two disjunct sets
    a = set(["a", "b"])
    b = set(["c", "d"])

    ## WHEN finding the similarity
    similarity = ui_score(a, b)

    ## THEN assert similarity is 0
    assert similarity == 0


def test_get_one_empty_ui_score():
    ## GIVEN one empty sets
    a = set(["a", "b"])
    b = set()

    ## WHEN finding the similarity
    similarity = ui_score(a, b)

    ## THEN assert similarity is 0
    assert similarity == 0


def test_get_two_empty_ui_score():
    ## GIVEN two empty sets
    a = set()
    b = set()

    ## WHEN finding the similarity
    similarity = ui_score(a, b)

    ## THEN assert similarity is 0

    assert similarity == 0
