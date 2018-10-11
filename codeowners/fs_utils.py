from itertools import chain
from pathlib import Path
import typing

import toolz


# Possible locations of CODEOWNERS file, relative to repository root.
_CODEOWNERS_REL_LOCATIONS = [Path('docs/CODEOWNERS'), Path('.github/CODEOWNERS'), Path('CODEOWNERS')]


def git_repository_root(base_dir: Path, search_parent_directories=True) -> Path:
    dir = base_dir
    while True:
        if (dir / '.git').exists():
            return dir

        if not search_parent_directories:
            break

        if dir == Path('/') or dir == Path():
            break

        dir = dir.parent

    raise FileNotFoundError("Could not find .git directory in:  {base_dir}{msg}".format(
        base_dir=base_dir, msg=' (or any parent)' if search_parent_directories else ''))


def codeowners_path(base_dir: Path) -> Path:
    repo_root = git_repository_root(base_dir=base_dir)
    candidate_paths = [repo_root / location for location in _CODEOWNERS_REL_LOCATIONS]
    path = next((p for p in candidate_paths if p.exists()), None)
    if path is None:
        raise FileNotFoundError("Could not find CODEOWNERS file in any of the following locations: ".format(
            '; '.join(map(str, candidate_paths))))
    return path


def unique_paths(paths: typing.Iterable[Path], recursive: bool = False):
    """ Return an iterable of Path objects, representing files. """
    paths = list(map(Path, paths))

    if recursive:
        paths = chain(paths, chain.from_iterable(p.glob('**/*') for p in paths))

    return toolz.itertoolz.unique(paths)
