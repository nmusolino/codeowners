from pathlib import Path
import subprocess
import typing


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


def list_files(paths: typing.Iterable[Path], untracked: bool = False, recursive: bool = True):
    """ Return an iterable of Paths representing non-ignored files recognized by git. """
    if not recursive:
        raise NotImplementedError('Only recursive traversal supported right now; got recursive: {!r}'.format(recursive))

    tracked_options = ['--cached', '--others'] if untracked else ['--cached']

    # In the future, we should process the output in a streaming fashion.
    ls_result = subprocess.run(['git', 'ls-files', *tracked_options, *map(str, paths)],
                               check=True, stdout=subprocess.PIPE, universal_newlines=True)
    return [Path(p) for p in ls_result.stdout.splitlines()]
