import click

from wcategory.conf import ADD_FILE_PREFIX, ADD_PREFIX, REMOVE_FILE_PREFIX, REMOVE_PREFIX, CONF_DIR, CONF_EXTENSION
from wcategory.util import exit_if_false, save_map_command_to_conf, save_add_remove_command_to_conf, check_environment
from wcategory.command import (add_domain_to_category, remove_domain_from_category, search_text_in_directory,
                               map_categories_of_service, initialize_environment, merge_into_output)


@click.group()
def cli():
    """
    \b
    Input directory structure:
    For category: input/service/category/domains
    For subcategory: input/service/category/subcategory/domains

    Output file structure will be same as input's except its directory (output/...)

    Conf files structure:
    For service conf files: conf/service.conf
    For add conf files: conf/add.conf or conf/add_specific_name.conf
    For remove conf files: conf/rmv.conf or conf/rmv_specific_name.conf

    Type "python main.py command --help" for command usages
    """
    pass


@cli.command()
@click.argument("domain")
@click.argument("category_path")
def add(domain, category_path):
    """
    Add DOMAIN to a CATEGORY_PATH under output/manual directory
    """
    check_environment()
    add_domain_to_category(domain, category_path)
    save_add_remove_command_to_conf(domain, category_path, ADD_PREFIX, ADD_FILE_PREFIX)


@cli.command()
@click.argument("domain")
@click.argument("category_path")
def remove(domain, category_path):
    """
    Remove DOMAIN from a CATEGORY_PATH under input directory
    """
    check_environment()
    remove_domain_from_category(domain, category_path)
    save_add_remove_command_to_conf(domain, category_path, REMOVE_PREFIX, REMOVE_FILE_PREFIX)


@cli.command()
@click.argument("text")
@click.option("--directory", "-in", help="Search files under specific directory")
def search(text, directory):
    """
    Search TEXT in domain and conf files under current or specific DIRECTORY
    """
    check_environment()
    search_text_in_directory(text, directory)


@cli.command()
@click.argument("service")
@click.argument("category_path")
@click.argument("map_category_path")
def map(service, category_path, map_category_path):
    """
    Maps domains from CATEGORY_PATH to MAP_CATEGORY_PATH under a SERVICE
    """
    check_environment()
    map_categories_of_service(service, category_path, map_category_path)
    save_map_command_to_conf(service, category_path, map_category_path)


@cli.command()
@click.option("--service", "-s", help="Merge specific service")
def merge(service):
    """
    Merges input files or input file of specific SERVICE by using files under conf directory
    """
    check_environment()
    merge_into_output(service)
    click.secho("If you want to run merge command second time, run init to clear input files",
                bold=True, fg="yellow")


@cli.command()
@click.option('--yes', is_flag=True, callback=exit_if_false,
              expose_value=False,
              prompt='This command will remove the output file. Are you sure you want to continue?')
def init():
    """
    Initializes directory structure and removes existing output directory
    """
    initialize_environment()
    click.secho("You should now add conf files under {} directory with extension {}".format(CONF_DIR, CONF_EXTENSION),
                fg="yellow")
    click.secho("If you want to add/remove domains, you should add conf files with {}/{} prefix"
                .format(ADD_FILE_PREFIX, REMOVE_FILE_PREFIX), fg="yellow")


if __name__ == '__main__':
    cli()
