import click

from wcategory.conf import (ADD_FILE_PREFIX, ADD_PREFIX, REMOVE_FILE_PREFIX, REMOVE_PREFIX, CONF_DIR, CONF_EXTENSION,
                            MANUAL_DIR)
from wcategory.util import (exit_if_no, save_map_command_to_conf, save_add_remove_command_to_conf, check_environment,
                            sort_uniquify_lines, get_working_directory)
from wcategory.command import (add_domain_to_category, remove_domain_from_category, search_text_in_directory,
                               map_categories_of_service, initialize_environment, merge_into_output)


@click.group()
def cli():
    """
    \b
    Input directory structure:
    For category: input/service/category/domains
    For subcategory: input/service/category/subcategory/domains

    \b
    Output directory structure will be same as input's except its directory (output/...)

    \b
    Conf directory structure:
    For service conf files: conf/service.conf
    For add conf files: conf/add.conf or conf/add_specific_name.conf
    For remove conf files: conf/rmv.conf or conf/rmv_specific_name.conf


    \b
    Format of conf files:
    There is three type of conf file:
    For services (like alexa.conf), for removes (like rmv_foo.conf) and for adds (like add_foo.conf)
    \b
    Format of service conf files:
    Service conf files are just for mapping function
    For one specific category (You could have unlimited subcategories or not have at all)
    /from_category/sub_category /to_category
    For recursively mapping category (Mapping all categories under from_category)
    /from_category/** /to_category
    \b
    Format of add conf files:
    + domain.com /from_category
    \b
    Format of remove conf files:
    - domain.com /from_category

    \b
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
    sort_uniquify_lines(category_path)
    save_add_remove_command_to_conf(domain, category_path, ADD_PREFIX, ADD_FILE_PREFIX)


@cli.command()
@click.argument("domain")
@click.argument("category_path")
def remove(domain, category_path):
    """
    Remove DOMAIN from a CATEGORY_PATH under output directory
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
    Maps domains from CATEGORY_PATH to MAP_CATEGORY_PATH under a SERVICE inside input directory
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
    click.secho("If you want to run merge command second time, run init to clear output files", fg="yellow")


@cli.command()
@click.option('--yes', is_flag=True, callback=exit_if_no,
              expose_value=False,
              prompt='This command will remove the output file (if exists). Are you sure you want to continue?')
def init():
    """
    Initializes directory structure and removes existing output directory
    """
    initialize_environment()
    working_directory = get_working_directory()
    click.secho("You should now add conf files under {}/{} directory with extension {} (such as alexa.conf)"
                .format(working_directory, CONF_DIR, CONF_EXTENSION), fg="yellow")
    click.secho("If you want to add/remove domains, you should add conf files with {}/{} prefix (such as add_foo.conf)"
                .format(ADD_FILE_PREFIX, REMOVE_FILE_PREFIX), fg="yellow")
    click.secho("After adding domains (by using add command), you should map their categories under {}.conf"
                .format(MANUAL_DIR), fg="yellow")


if __name__ == '__main__':
    cli()
