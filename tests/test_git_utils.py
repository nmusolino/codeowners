import pathlib

import pytest

from codeowners import git_utils


def test_git_repository_root():
    this_file = pathlib.Path(__file__)
    assert git_utils.git_repository_root(this_file) == this_file.parent.parent


def test_git_repository_root_no_parents():
    with pytest.raises(FileNotFoundError):
        git_utils.git_repository_root(pathlib.Path(__file__), search_parent_directories=False)


def test_git_repository_root_outside_repository():
    with pytest.raises(FileNotFoundError):
        git_utils.git_repository_root(pathlib.Path())
        git_utils.git_repository_root(pathlib.Path('/'))


def test_codeowners_path():
    this_file = pathlib.Path(__file__)
    expected_path = this_file.parent.parent / '.github'/ 'CODEOWNERS'
    assert expected_path.exists()
    assert git_utils.codeowners_path(this_file) == expected_path
    assert git_utils.codeowners_path(this_file.parent) == expected_path
    assert git_utils.codeowners_path(this_file.parent.parent) == expected_path

    with pytest.raises(FileNotFoundError):
        git_utils.codeowners_path(pathlib.Path())
