""" Functions and classes for identifying code owners.

"""
from collections import namedtuple
import itertools
import fnmatch
import logging
from pathlib import PurePath
import shlex
import typing


__all__ = []

_logger = logging.getLogger(__file__)


class Pattern:
    @classmethod
    def parse(cls, pattern: str):
        return parse_pattern(pattern)

    def __init__(self, pattern: PurePath, dir_only: bool, root_only: bool, invert: bool):
        self.pattern = pattern
        self.dir_only = dir_only
        self.root_only = root_only
        self.invert = invert

        if any(part == '**' for part in pattern.parts):
            self._match_impl = self._match_recursive
        elif len(self.pattern.parts) == 1:
            self._match_impl = self._match_any_part
        else:
            self._match_impl = self._match_leading

    def __str__(self):
        notes = (['directory only'] if self.dir_only else []) + (['inverted'] if self.invert else [])
        return '{}{}'.format(self.pattern, ' [{}]'.format(', '.join(notes)) if notes else '')

    def __repr__(self):
        return '{cls}(pattern={pattern!r}, dir_only={dir_only!r}, invert={invert!r}'.format(
            cls=self.__class__.__name__, pattern=self.pattern, dir_only=self.dir_only, invert=self.invert)

    def _match_leading(self, path: PurePath):
        return all(path_part is not None and fnmatch.fnmatch(path_part, pat_part)
                   for pat_part, path_part in zip(self.pattern.parts,
                                                  itertools.chain(path.parts, itertools.repeat(None))))

    def _match_recursive(self, path: PurePath):
        raise NotImplementedError()

    def _match_any_part(self, path: PurePath):
        assert len(self.pattern.parts) == 1
        pattern_part = self.pattern.parts[0]
        return any(fnmatch.fnmatch(part, pattern_part) for part in path.parts)

    def match(self, path: typing.Union[PurePath, str], is_dir=False):
        path = PurePath(path)

        match_result = self._match_impl(path)
        is_root_match = self._match_leading(path)

        match_result &= (is_dir or not self.dir_only)
        match_result &= (is_root_match or not self.root_only)
        return (not match_result) if self.invert else match_result


def is_rule(line: str) -> bool:
    """ Return whether the given line is a pattern.  Does not validate input.  """
    return not (line.startswith('#') or (line.strip() == ''))


def parse_pattern(pattern: str) -> Pattern:
    # Note that this function must not rstrip() the pattern:  escaped spaces are handled
    # elsewhere, so by the time pattern reaches this functions, the spaces are desired and
    # should be preserved.

    dir_only, root_only, invert = False, False, False

    if pattern[0] == '!':
        invert = True
        pattern = pattern[1:]

    if pattern[-1] == '/':
        dir_only = True
        pattern = pattern[:-1]

    if pattern[0] == '/':
        root_only = True
        pattern = pattern[1:]

    path = PurePath(pattern)
    for part in path.parts:
        if '**' in part and part != '**':
            raise ValueError("Recursive wildcard '**' must constitute entire path component: {!r}".format(pattern))

    return Pattern(path, dir_only=dir_only, root_only=root_only, invert=invert)


class MatchResult(namedtuple('MatchResultData', 'path, owners, source_line, source_filename, source_lineno')):
    def summary(self) -> str:
        return '{path}: {owners}'.format(path=self.path, owners=' '.join(self.owners))


class Rule(namedtuple('RuleData', 'pattern, owners, source_line, source_filename, source_lineno')):
    def match(self, path, is_dir=False) -> typing.Optional[MatchResult]:
        return (MatchResult(path=path, owners=self.owners, source_line=self.source_line,
                            source_filename=self.source_filename, source_lineno=self.source_lineno)
                if self.pattern.match(path, is_dir=is_dir) else None)


def parse_codeowners(lines: typing.Iterable[str], source_filename: str) -> typing.List[Rule]:
    def parse_line(line, source_lineno):
        pattern, *owners = shlex.split(line)  # Handle escaped spaces.

        return Rule(pattern=parse_pattern(pattern), owners=owners,
                    source_filename=source_filename, source_lineno=source_lineno, source_line=line)

    return [parse_line(line, i) for i, line in enumerate(lines, start=1) if is_rule(line)][::-1]


def match(rules, path, is_dir=False) -> typing.Optional[MatchResult]:
    return next(filter(lambda res: res is not None, (rule.match(path, is_dir=is_dir) for rule in rules)),
                None)
