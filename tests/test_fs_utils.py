from pathlib import Path
import tempfile

import pytest

from codeowners import fs_utils


@pytest.fixture(scope='function')
def repository_directory():
    """ Return a temporary directory, with a fake (empty) .git directory contained within. """
    with tempfile.TemporaryDirectory(prefix='test_fs_utils_') as temp_dir_name:
        temp_dir_path = Path(temp_dir_name)
        (temp_dir_path / '.git').mkdir()

        yield temp_dir_path


def test_git_repository_root(repository_directory):
    assert fs_utils.git_repository_root(repository_directory) == repository_directory
    assert fs_utils.git_repository_root(repository_directory / 'a') == repository_directory
    assert fs_utils.git_repository_root(repository_directory / 'a' / 'b') == repository_directory

    # When search_parent_directories is False, only the repository directory will work.
    assert fs_utils.git_repository_root(repository_directory, search_parent_directories=False) == repository_directory

    with pytest.raises(FileNotFoundError):
        fs_utils.git_repository_root(repository_directory / 'a', search_parent_directories=False)

    with pytest.raises(FileNotFoundError):
        fs_utils.git_repository_root(repository_directory / 'a' / 'b', search_parent_directories=False)


def test_git_repository_root_outside_repository():
    with pytest.raises(FileNotFoundError):
        fs_utils.git_repository_root(Path())
        fs_utils.git_repository_root(Path('/'))


def test_codeowners_path(repository_directory):
    with pytest.raises(FileNotFoundError):
        fs_utils.codeowners_path(repository_directory)

    docs_path = repository_directory / 'docs'
    docs_path.mkdir()
    codeowners_path = docs_path / 'CODEOWNERS'
    codeowners_path.touch()

    assert fs_utils.codeowners_path(repository_directory) == codeowners_path
    assert fs_utils.codeowners_path(repository_directory / 'a' / 'b') == codeowners_path

    with pytest.raises(FileNotFoundError):
        fs_utils.codeowners_path(repository_directory.parent)
        fs_utils.codeowners_path(Path())


def test_unique_paths(repository_directory):
    dir = repository_directory
    (dir / '.git').rmdir()
    (dir / 'a').mkdir()
    (dir / 'a' / 'b').mkdir()
    (dir / 'a' / 'c').touch()
    (dir / 'x').touch()

    paths = [repository_directory, repository_directory / 'a']

    # This ordered comparison is, strictly speaking,  too strict.
    assert list(fs_utils.unique_paths(paths)) == paths

    assert sorted(fs_utils.unique_paths(paths, recursive=True)) \
            == sorted([dir, dir/'a', dir/'a'/'b', dir/'a'/'c', dir/'x'])
