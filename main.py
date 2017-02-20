import click

from wcategory.util import requires_environment_check, exit_if_false
from wcategory.command import add as _add, remove as _remove, search as _search, map as _map, init as _init


@click.group()
def cli():
    """
    \b
    Input directory structure:
    For category: input/service/category/domains.txt
    For subcategory: input/service/category/subcategory/domains.txt
    """
    pass


@requires_environment_check
@cli.command()
@click.argument("domain")
@click.argument("category_path")
def add(domain, category_path):
    """
    Add DOMAIN to a CATEGORY_PATH under manual directory
    """
    _add(domain, category_path)


@requires_environment_check
@cli.command()
@click.argument("domain")
@click.argument("category_path")
def remove(domain, category_path):
    """
    Remove DOMAIN from a CATEGORY_PATH under manual directory
    """
    _remove(domain, category_path)


@requires_environment_check
@cli.command()
@click.argument("domain")
@click.option("--directory", "-in", help="Search files under specific directory")
def search(domain, directory):
    """
    Search DOMAIN in domain files under current or specific DIRECTORY
    """
    _search(domain, directory)


@requires_environment_check
@cli.command()
@click.argument("service")
@click.argument("category_path")
@click.argument("map_category_path")
def map(service, category_path, map_category_path):
    """
    Maps domains from CATEGORY_PATH to MAP_CATEGORY_PATH under a SERVICE
    """
    _map(service, category_path, map_category_path)


@cli.command()
@click.option('--yes', is_flag=True, callback=exit_if_false,
              expose_value=False,
              prompt='This command will remove the output file. Are you sure you want to continue?')
def init():
    """
    Initializes directory structure and removes existing output directory
    """
    _init()


if __name__ == '__main__':
    cli()
