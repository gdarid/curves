import lsystc as ls
import pytest


@pytest.mark.parametrize("axiom, rules, expected_result", [
    ('A', [('A', 'AB'), ('B', 'BB')], 'AB'),
    ('AB', [('A', 'AB'), ('B', 'BB')], 'ABBB'),
])
def test_single_iteration(axiom, rules, expected_result):
    syst = ls.Lsystc(ls.Config(), axiom, rules, nbiter=1)
    assert syst.dev == expected_result


@pytest.mark.parametrize("axiom, rules, nbiterations, expected_result", [
    ('A', [('A', 'AB'), ('B', 'BB')], 2, 'ABBB'),
    ('AB', [('A', 'AB'), ('B', 'BB')], 3, 'ABBBBBBBBBBBBBBB'),
])
def test_more_iterations(axiom, rules, nbiterations, expected_result):
    syst = ls.Lsystc(ls.Config(), axiom, rules, nbiter=nbiterations)
    assert syst.dev == expected_result


@pytest.mark.parametrize("axiom, expected_result", [
    ('F', [([0, 10], [0, 0], [0, 0], (228, 26, 28))]),
    ('F+F', [([0, 10, 10], [0, 0, 10], [0, 0, 0], (228, 26, 28))]),
])
def test_turt(axiom, expected_result):
    syst = ls.Lsystc(ls.Config(), axiom, [], nbiter=1)
    syst.turtle()
    assert syst.turt == expected_result


@pytest.mark.parametrize("axiom, expected_result", [
    ('⇧F', [([0, 0, 10], [0, 0, 0], [0, 10, 10], (228, 26, 28))]),
    ('⇩F', [([0, 0, 10], [0, 0, 0], [0, -10, -10], (228, 26, 28))]),
])
def test_turt_3d(axiom, expected_result):
    syst = ls.Lsystc(ls.Config(), axiom, [], nbiter=1)
    syst.turtle()
    assert syst.turt == expected_result


@pytest.mark.parametrize("axiom, expected_result", [
    ('uF', [([0, 10.1], [0, 0], [0, 0], (228, 26, 28))]),
    ('vF', [([0, 9.9], [0, 0], [0, 0], (228, 26, 28))]),
])
def test_turt_delta(axiom, expected_result):
    syst = ls.Lsystc(ls.Config(), axiom, [], nbiter=1)
    syst.turtle()
    assert syst.turt == expected_result
