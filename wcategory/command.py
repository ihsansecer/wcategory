import click

from wcategory.conf import INPUT_DIR, MANUAL_DIR, DOMAINS_FILE, OUTPUT_DIR
from wcategory.util import (fix_path, create_directory, append_file, remove_line, find_domain_files,
                            search_line_in_files, exit_if_false, create_necessary_files, remove_directory,
                            requires_environment_check, map_domains_to_path)


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
    directory_path = "{}/{}/{}".format(INPUT_DIR, MANUAL_DIR, fix_path(category_path))
    create_directory(directory_path)
    file_path = "{}/{}".format(directory_path, DOMAINS_FILE)
    string_to_append = "{}\n".format(domain)
    append_file(file_path, string_to_append)


@requires_environment_check
@cli.command()
@click.argument("domain")
@click.argument("category_path")
def remove(domain, category_path):
    """
    Remove DOMAIN from a CATEGORY_PATH under manual directory
    """
    directory_path = "{}/{}/{}".format(INPUT_DIR, MANUAL_DIR, fix_path(category_path))
    file_path = "{}/{}".format(directory_path, DOMAINS_FILE)
    line_to_remove = "{}\n".format(domain)
    remove_line(file_path, line_to_remove)


@requires_environment_check
@cli.command()
@click.argument("domain")
@click.option("--directory", "-in", help="Search files under specific directory")
def search(domain, directory):
    """
    Search DOMAIN in domain files under current or specific DIRECTORY
    """
    domain_files = find_domain_files(path=directory)
    line_to_search = "{}\n".format(domain)
    search_line_in_files(line_to_search, domain_files)


@requires_environment_check
@cli.command()
@click.argument("service")
@click.argument("category_path")
@click.argument("map_category_path")
def map(service, category_path, map_category_path):
    """
    Maps domains from CATEGORY_PATH to MAP_CATEGORY_PATH under a SERVICE
    """
    directory_path = "{}/{}/{}".format(INPUT_DIR, service, fix_path(category_path))
    map_directory_path = "{}/{}".format(OUTPUT_DIR, fix_path(map_category_path))
    domain_files = find_domain_files(directory_path)
    map_domains_to_path(domain_files, map_directory_path)


@cli.command()
@click.option('--yes', is_flag=True, callback=exit_if_false,
              expose_value=False,
              prompt='This command will remove the output file. Are you sure you want to continue?')
def init():
    """
    Initializes directory structure and removes existing output directory
    """
    remove_directory(OUTPUT_DIR)
    create_necessary_files()
