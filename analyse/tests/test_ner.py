# This file is a part of the final year project "Story and Software" (CSC4006).
# Author: Konrad Mosoczy (Queen's University Belfast - QUB)
# https://github.com/konmos/csc4006 (also available on GitLab)
# ------------------------------------------------------------------------------
# Test the NER script (analyse_entities.py) with 3 sample stories.

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
