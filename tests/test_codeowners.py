""" Tests for `codeowners` module.  """

from pathlib import PurePath

import pytest

from codeowners import codeowners


def test_is_pattern():
    assert codeowners.is_pattern('*.py')
    assert codeowners.is_pattern('a/b')
    assert not codeowners.is_pattern('# Comment')
    assert not codeowners.is_pattern('')
    assert not codeowners.is_pattern(' ')


def test_parse_pattern():
    with pytest.raises(ValueError):
        codeowners.parse_pattern('a/**b/c')

    pat1 = codeowners.parse_pattern('!a/b')
    assert pat1.invert, "Prefix '!' should negate the pattern."
    assert pat1.pattern == PurePath('a/b')

    pat2 = codeowners.parse_pattern('a/b/')
    assert pat2.dir_only, "Prefix '!' should negate the pattern."
    assert pat2.pattern == PurePath('a/b')


def test_pattern_match():
    nested_pat = codeowners.parse_pattern('a/b')
    assert not nested_pat.match('a')
    assert nested_pat.match('a/b')
    assert nested_pat.match('a/b/c')
    assert nested_pat.match('a/b/c/d')
    assert not nested_pat.match('a/z')
    assert not nested_pat.match('b')
    assert not nested_pat.match('a/bbbb')
    assert not nested_pat.match('z/a/b')

    pat = codeowners.parse_pattern('a/*.py')
    assert not pat.match('a')
    assert pat.match('a/file.py')
    assert not pat.match('file.py')
    assert not pat.match('b/file.py')
    assert not pat.match('b/c/file.py')


def test_pattern_match_single_component():
    bare_pat = codeowners.parse_pattern('*.py')
    assert bare_pat.match('file.py')
    assert bare_pat.match('a/file.py')
    assert bare_pat.match('a/b/file.py')
    assert not bare_pat.match('file.txt')

    bare_pat = codeowners.parse_pattern('docs*')
    assert bare_pat.match('docs.txt')
    assert bare_pat.match('docs1/', is_dir=True)
    assert bare_pat.match('docs1/output.txt')
    assert bare_pat.match('output/docs1/', is_dir=True)
    assert bare_pat.match('output/docs1/output.txt', is_dir=True)


@pytest.mark.xfail
def test_pattern_match_recursive():
    rec_pat = codeowners.parse_pattern('a/**/b')
    assert rec_pat.match('a/b')
    assert rec_pat.match('a/x/b')
    assert rec_pat.match('a/x/y/z/b')
    assert rec_pat.match('a/x/y/z/c')


@pytest.mark.xfail
def test_pattern_match_trailing_spaces():
    pat = codeowners.parse_pattern(r'a/b\ ')
    assert pat.match('a/b ')
    assert not pat.match('a/b')


@pytest.mark.xfail
def test_pattern_match_quoted_character():
    pat = codeowners.parse_pattern(r'a/b\?')
    assert pat.match('a/b?')
    assert not pat.match('a/bx')


@pytest.mark.xfail
def test_pattern_match_rooted():
    root_pat = codeowners.parse_pattern('/a')
    assert root_pat.match('a')
    assert root_pat.match('a/b')
    assert not root_pat.match('x/a')


def test_pattern_match_directory_only():
    dir_pat = codeowners.parse_pattern('bin/')
    assert dir_pat.match('bin', is_dir=True)
    assert dir_pat.match('output/bin', is_dir=True)

    assert not dir_pat.match('bin', is_dir=False)
    assert not dir_pat.match('output/bin', is_dir=False)


def test_pattern_match_inverted():
    inv_pat = codeowners.parse_pattern('!a/*.py')
    assert not inv_pat.match('a/file.py')
    assert inv_pat.match('file.py')
    assert inv_pat.match('b/file.py')
    assert inv_pat.match('b/file.txt')
