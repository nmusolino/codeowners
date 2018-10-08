""" Functions and classes for identifying code owners.

* All PurePath.  This ensures there is no filesystem access.
"""
import itertools
import fnmatch
import logging
from pathlib import PurePath
import typing


_logger = logging.getLogger(__file__)


class Pattern:
    def __init__(self, pattern: PurePath, dir_only: bool, invert: bool):
        self.pattern = pattern
        self.dir_only = dir_only
        self.invert = invert

        if any(part == '**' for part in pattern.parts):
            self._match_impl = self._match_recursive
        elif len(self.pattern.parts) == 1:
            self._match_impl = self._match_single_part
        else:
            self._match_impl = self._match_leading

    def _match_leading(self, path: PurePath):
        # This is wrong when `path` is shorter than `path.pattern`.

        return all(path_part is not None and fnmatch.fnmatch(path_part, pat_part)
                   for pat_part, path_part in zip(self.pattern.parts,
                                                  itertools.chain(path.parts, itertools.repeat(None))))

    def _match_recursive(self, path: PurePath):
        raise NotImplementedError()

    def _match_single_part(self, path: PurePath):
        assert len(self.pattern.parts) == 1
        pattern_part = self.pattern.parts[0]
        return any(fnmatch.fnmatch(part, pattern_part) for part in path.parts)

    def match(self, path: typing.Union[PurePath, str], is_dir=False):
        path = PurePath(path)
        match_result = self._match_impl(path)
        match_result &= (not self.dir_only or is_dir)
        return (not match_result) if self.invert else match_result


def is_pattern(line: str) -> bool:
    return not (line.startswith('#') or (line.strip() == ''))


def parse_pattern(pattern: str) -> Pattern:
    # Not handled:  trailing spaces quoted with backslash.
    pattern = pattern.rstrip()

    invert = False
    dir_only = False

    if pattern[0] == '!':
        invert = True
        pattern = pattern[1:]

    if pattern[-1] == '/':
        dir_only = True
        pattern = pattern[:-1]

    if pattern[0] == '/':
        logging.warning("Leading separator '/' to match files in repository root is not enforced:  %s", pattern)
        pattern = pattern[1:]

    path = PurePath(pattern)
    for part in path.parts:
        if '**' in part and part != '**':
            raise ValueError("Recursive wildcard '**' must constitute entire path component: {!r}".format(pattern))

    return Pattern(path, dir_only=dir_only, invert=invert)
