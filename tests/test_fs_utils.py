import os
from pathlib import Path
import tempfile
import subprocess

import pytest

from codeowners import fs_utils


@pytest.fixture(scope='function')
def repository_directory():
    """ Return a temporary directory, with a fake (empty) .git directory contained within. """
    with tempfile.TemporaryDirectory(prefix='test_fs_utils_') as temp_dir_name:
        subprocess.run(['git', 'init'], cwd=temp_dir_name)

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir_name)
            yield Path(temp_dir_name)
        finally:
            os.chdir(original_cwd)


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


def test_list_files(repository_directory):
    assert list(fs_utils.list_files(['.'], untracked=True)) == []
    assert list(fs_utils.list_files(['.'], untracked=False)) == []

    # File 'a' is tracked; file 'b' is untracked.
    a = repository_directory / 'a'
    a.touch()
    subprocess.run(['git', 'add', str(a)])

    b = repository_directory / 'b'
    b.touch()

    assert sorted(fs_utils.list_files([repository_directory], untracked=True)) == [Path('a'), Path('b')]
    assert sorted(fs_utils.list_files([repository_directory], untracked=False)) == [Path('a')]
