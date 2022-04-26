# This file is a part of the final year project "Story and Software" (CSC4006).
# Author: Konrad Mosoczy (Queen's University Belfast - QUB)
# https://github.com/konmos/csc4006 (also available on GitLab)
# ------------------------------------------------------------------------------
# Test the narrative analysis script (analyse_narrative.py) with 3 sample stories.

from analyse_narrative import perform_analysis, extract_nouns, simple_relationships


def test_bpg():
    """
    Test Byzantine Generals narrative analysis.
    """
    with open('byzantine.txt') as fd:
        txt = fd.read()

    analysis = perform_analysis(
        txt,
        relations=True,
        relations_r=True,
        svos=True,
        tokens=True
    )

    assert analysis is not None
    assert analysis['sentences'] is not None
    assert analysis['relations'] is not None
    assert analysis['relations_r'] is not None
    assert analysis['svos'] is not None
    assert analysis['tokens'] is not None

    nouns = extract_nouns(analysis)
    assert len(nouns) != 0

    rels = simple_relationships(txt, nouns)
    assert len(rels) != 0


def test_hg():
    """
    Test Hansel and Gretel narrative analysis.
    """
    with open('hansel_and_gretel.txt') as fd:
        txt = fd.read()

    analysis = perform_analysis(
        txt,
        relations=True,
        relations_r=True,
        svos=True,
        tokens=True
    )

    assert analysis is not None
    assert analysis['sentences'] is not None
    assert analysis['relations'] is not None
    assert analysis['relations_r'] is not None
    assert analysis['svos'] is not None
    assert analysis['tokens'] is not None

    nouns = extract_nouns(analysis)
    assert len(nouns) != 0

    rels = simple_relationships(txt, nouns)
    assert len(rels) != 0


def test_dp():
    """
    Test Dining Philosophers narrative analysis.
    """
    with open('philosophers.txt') as fd:
        txt = fd.read()

    analysis = perform_analysis(
        txt,
        relations=True,
        relations_r=True,
        svos=True,
        tokens=True
    )

    assert analysis is not None
    assert analysis['sentences'] is not None
    assert analysis['relations'] is not None
    assert analysis['relations_r'] is not None
    assert analysis['svos'] is not None
    assert analysis['tokens'] is not None

    nouns = extract_nouns(analysis)
    assert len(nouns) != 0

    rels = simple_relationships(txt, nouns)
    assert len(rels) != 0
