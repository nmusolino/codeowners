""" Tests for `codeowners` module.  """

from pathlib import PurePath

import pytest

from codeowners import codeowners



def test_parse_pattern():
    with pytest.raises(ValueError):
        codeowners.parse_pattern('a/**b/c')

    pat1 = codeowners.parse_pattern('!a/b')
    assert pat1.invert, "Prefix '!' should negate the pattern."
    assert pat1.pattern == PurePath('a/b')

    pat2 = codeowners.parse_pattern('a/b/')
    assert pat2.dir_only, "Prefix '!' should negate the pattern."
    assert pat2.pattern == PurePath('a/b')

def test_pattern_str():
    pat = codeowners.Pattern.parse('a/b')
    assert str(pat) == 'a/b'
    repr(pat)    # Confirm this does not raise.

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
    pat1 = codeowners.parse_pattern('*.py')
    assert pat1.match('file.py')
    assert pat1.match('a/file.py')
    assert pat1.match('a/b/file.py')
    assert not pat1.match('file.txt')

    assert codeowners.parse_pattern('*.txt').match('test.txt')

    pat2 = codeowners.parse_pattern('docs*')
    assert pat2.match('docs.txt')
    assert pat2.match('docs1/', is_dir=True)
    assert pat2.match('docs1/output.txt')
    assert pat2.match('output/docs1/', is_dir=True)
    assert pat2.match('output/docs1/output.txt', is_dir=True)


@pytest.mark.xfail
def test_pattern_match_recursive():
    rec_pat = codeowners.parse_pattern('a/**/b')
    assert rec_pat.match('a/b')
    assert rec_pat.match('a/x/b')
    assert rec_pat.match('a/x/y/z/b')
    assert rec_pat.match('a/x/y/z/c')


def test_pattern_match_trailing_spaces():
    pat = codeowners.parse_pattern('a/b ')
    assert pat.match('a/b ')
    assert not pat.match('a/b')


def test_pattern_match_rooted():
    root_pat = codeowners.parse_pattern('/a')
    assert root_pat.match('a')
    assert root_pat.match('a/b')
    assert not root_pat.match('x/a')
    assert not root_pat.match('b')


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

def test_is_rule():
    assert codeowners.is_rule('*.py ')
    assert codeowners.is_rule('a/b')
    assert not codeowners.is_rule('# Comment')
    assert not codeowners.is_rule('')
    assert not codeowners.is_rule(' ')

def test_parse_codeowners():
    # Test that comments are properly ignored, and that
    lines = ['*.*     @general_owner',
             '*.py    @a @b',
             '# Text files',
             '*.txt   @x @y',]
    rules = codeowners.parse_codeowners(lines, source_filename='CODEOWNERS')

    result1 = codeowners.match(rules, 'file.py')
    assert result1.path == 'file.py'
    assert result1.owners == ['@a', '@b']
    assert result1.source_lineno == 2
    assert result1.source_filename == 'CODEOWNERS'
    assert result1.source_line == lines[1]

    result2 = codeowners.match(rules, 'test.txt')
    assert result2.path == 'test.txt'
    assert result2.owners == ['@x', '@y']
    assert result2.source_lineno == 4
    assert result2.source_filename == 'CODEOWNERS'
    assert result2.source_line == lines[3]

    result3 = codeowners.match(rules, 'sample.pyc')
    assert result3.owners == ['@general_owner']
    assert result3.source_lineno == 1

    result4 = codeowners.match(rules, 'c')
    assert result4 is None

def test_parse_codeowners_escaped_spaces():
    lines = ['*\ docs.txt  @owner1',
             'ab\          @owner2']
    rules = codeowners.parse_codeowners(lines, source_filename='CODEOWNERS')

    result1 = codeowners.match(rules, 'my docs.txt')
    assert result1 is not None
    assert result1.owners == ['@owner1']

    result2 = codeowners.match(rules, 'ab ')
    assert result2 is not None
    assert result2.owners == ['@owner2']

    assert codeowners.match(rules, 'ab') is None
