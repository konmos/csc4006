# This file is a part of the final year project "Story and Software" (CSC4006).
# Author: Konrad Mosoczy (Queen's University Belfast - QUB)
# https://github.com/konmos/csc4006 (also available on GitLab)
# ------------------------------------------------------------------------------
# These are the test cases for the story-thinking framework.

import pytest
from formalisation.examples import bgp, dp, dp2, hg, paul_allens_apples


def test_bgp_complex():
    """
    Test the Byzantine Generals example.
    We do this twice to make sure that the callback worked as intended.
    """
    assert len(bgp.w.agents) == 0

    bgp.w.process_with_callback(
        lambda w, r: w.reset_agents(),
        ['camp', 'make_order']
    )

    assert len(bgp.w.agents) == 0
    assert bool(bgp.w._last_trace)

    bgp.w._last_trace = None

    bgp.w.process(
        ['camp', 'make_order']
    )

    assert len(bgp.w.agents) != 0
    assert bool(bgp.w._last_trace)


def test_dp1():
    """
    Test the Dining Philosophers with automatic origin event discovery.
    We also check that exception handling works as intended.
    """
    def _reset(w, r):
        w.reset_agents()
        w._last_trace = None

    dp.w.process_with_callback(_reset, ignore_exceptions=True)

    assert len(dp.w.agents) == 0
    assert not bool(dp.w._last_trace)

    with pytest.raises(dp.ForkInUse):
        dp.w.process()

    assert len(dp.w.agents) != 0
    assert not bool(dp.w._last_trace)


def test_dp2():
    """
    Test the threaded Dining Philosophers example.
    """
    dp2.w.process()
    assert bool(dp2.w._last_trace)


def test_hg():
    """
    Test Hansel and Gretel.
    """
    hg.w.process()
    assert bool(hg.w._last_trace)


def test_fdl_generation():
    """
    Test FDL generation for Hansel and Gretel.
    """
    assert bool(hg.w.generate_fdl())


def test_apples_stepping():
    """
    Test the apples example by live stepping through it.
    """
    while paul_allens_apples.w.step(['paul_rests', 'apple_falls']):
        ...

    assert bool(hg.w._last_trace)
