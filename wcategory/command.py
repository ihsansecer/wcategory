import click

from wcategory.conf import OUTPUT_DIR, MANUAL_DIR, DOMAINS_FILE
from wcategory.util import (fix_path, create_directory, append_file, remove_line, find_domain_files,
                            search_line_in_files)


@click.group()
def cli():
    """
    \b
    Input directory structure:
    For category: input/service/category/domains.txt
    For subcategory: input/service/category/subcategory/domains.txt
    """
    pass


@cli.command()
@click.argument("domain")
@click.argument("category_path")
def add(domain, category_path):
    """
    Add DOMAIN to a CATEGORY_PATH under manual directory
    """
    folder_path = "{}/{}/{}".format(OUTPUT_DIR, MANUAL_DIR, fix_path(category_path))
    create_directory(folder_path)
    file_path = "{}/{}".format(folder_path, DOMAINS_FILE)
    string_to_append = "{}\n".format(domain)
    append_file(file_path, string_to_append)


@cli.command()
@click.argument("domain")
@click.argument("category_path")
def remove(domain, category_path):
    """
    Remove DOMAIN from a CATEGORY_PATH under manual directory
    """
    folder_path = "{}/{}/{}".format(OUTPUT_DIR, MANUAL_DIR, fix_path(category_path))
    file_path = "{}/{}".format(folder_path, DOMAINS_FILE)
    line_to_remove = "{}\n".format(domain)
    remove_line(file_path, line_to_remove)


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
