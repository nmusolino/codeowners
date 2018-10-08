from pathlib import Path

# Possible locations of CODEOWNERS file, relative to repository root.
# The location of the final element is actually important: it makes unit tests in `test_git_utils` pass on
# case-sensitive filesystems.
_CODEOWNERS_REL_LOCATIONS = [Path('docs/CODEOWNERS'), Path('.github/CODEOWNERS'), Path('CODEOWNERS')]


def git_repository_root(base_dir: Path, search_parent_directories=True) -> Path:
    dir = base_dir
    while dir != Path():
        if (dir / '.git').exists():
            return dir

        if not search_parent_directories:
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
            '; '.join(candidate_paths)))
    return path
