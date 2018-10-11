"""Console script for codeowners."""
from pathlib import Path
import sys

import click

from codeowners import codeowners, fs_utils


@click.command()
@click.option('--recurse/--no-recurse', is_flag=True, default=True, help='Recursively walk the filesystem')
@click.argument('paths', type=click.Path(), nargs=-1)
def main(paths, recurse):
    click.echo('Paths: {}'.format(paths))
    if len(paths) == 0:
        paths = ('.',)

    paths = fs_utils.unique_paths(paths, recursive=recurse)

    codeowners_path = fs_utils.codeowners_path(Path.cwd())
    with open(codeowners_path, 'r') as codeowners_file:
        rules = codeowners.parse_codeowners(codeowners_file, source_filename=codeowners_path)

    repo_root = fs_utils.git_repository_root(base_dir=Path.cwd())
    click.echo('Repo root: {}'.format(repo_root))

    for p in paths:
        match_result = codeowners.match(rules, p.resolve().relative_to(repo_root), is_dir=p.is_dir())
        click.echo(match_result.summary() if match_result else '{}: <NONE>'.format(p))

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
