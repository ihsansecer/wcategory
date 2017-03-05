import click

from wcategory.conf import (INPUT_DIR, MANUAL_DIR, DOMAINS_FILE, OUTPUT_DIR, ADD_FILE_PREFIX, REMOVE_FILE_PREFIX,
                            ADD_PREFIX, MAP_PREFIX, REMOVE_PREFIX)
from wcategory.util import (fix_path, create_directory, remove_line, find_domain_files, search_text_in_files,
                            create_necessary_files, remove_directory, map_domains_to_path, write_file, find_conf_files,
                            invoke_map_commands, invoke_add_remove_commands, find_add_remove_conf_files,
                            sort_uniquify_lines, exclude_domain)


def add_domain_to_category(domain, category_path):
    directory_path = "{}/{}/{}".format(INPUT_DIR, MANUAL_DIR, fix_path(category_path))
    create_directory(directory_path)
    file_path = "{}/{}".format(directory_path, DOMAINS_FILE)
    string_to_append = "{}\n".format(domain)
    write_file(file_path, string_to_append, "a+")
    sort_uniquify_lines(file_path, False)


def remove_domain_from_category(domain, category_path):
    directory_path = "{}/{}".format(OUTPUT_DIR, fix_path(category_path))
    file_path = "{}/{}".format(directory_path, DOMAINS_FILE)
    line_to_remove = "{}".format(domain)
    remove_line(file_path, line_to_remove)


def search_text_in_directory(text, directory):
    domain_files = find_domain_files(path=directory)
    conf_files = find_conf_files([])
    line_to_search = "{}".format(text)
    files_to_search = domain_files + conf_files
    search_text_in_files(line_to_search, files_to_search)


def map_categories_of_service(service, category_path, map_category_path, exclude_path):
    directory_path = "{}/{}/{}".format(INPUT_DIR, service, fix_path(category_path))
    map_directory_path = "{}/{}".format(OUTPUT_DIR, fix_path(map_category_path))
    domain_files = find_domain_files(directory_path)
    excluded_domain_files = exclude_domain(domain_files, directory_path, exclude_path)
    map_domains_to_path(excluded_domain_files, map_directory_path)


def merge_into_output(service):
    add_conf_files = find_add_remove_conf_files(ADD_FILE_PREFIX)
    remove_conf_files = find_add_remove_conf_files(REMOVE_FILE_PREFIX)
    files_to_exclude = add_conf_files + remove_conf_files
    map_conf_files = find_conf_files(exclude=files_to_exclude, service=service)
    click.secho("Adding domains in add conf files", fg="blue")
    for file in add_conf_files:
        invoke_add_remove_commands(add_domain_to_category, file, ADD_PREFIX)
    click.secho("Mapping categories in conf files of services", fg="blue")
    for file in map_conf_files:
        invoke_map_commands(map_categories_of_service, file, MAP_PREFIX)
    click.secho("Removing domains in remove conf files", fg="blue")
    for file in remove_conf_files:
        invoke_add_remove_commands(remove_domain_from_category, file, REMOVE_PREFIX)


def initialize_environment():
    remove_directory(OUTPUT_DIR)
    create_necessary_files()
