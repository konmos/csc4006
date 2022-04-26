from analyse_entities import extract_entities


def test_bpg():
    """
    Test Byzantine Generals NER.
    """
    with open('byzantine.txt') as fd:
        ents = extract_entities(fd.read())

    assert 'Byzantine' in ents


def test_hg():
    """
    Test Hansel and Gretel NER.
    """
    with open('hansel_and_gretel.txt') as fd:
        ents = extract_entities(fd.read())

    assert 'Hansel' in ents
    assert 'Gretel' in ents


def test_dp():
    """
    Test Dining Philosophers NER.
    """
    with open('philosophers.txt') as fd:
        ents = extract_entities(fd.read())

    assert len(ents) == 0
