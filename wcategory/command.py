from wcategory.conf import INPUT_DIR, MANUAL_DIR, DOMAINS_FILE, OUTPUT_DIR
from wcategory.util import (fix_path, create_directory, remove_line, find_domain_files, search_line_in_files,
                            create_necessary_files, remove_directory, map_domains_to_path, write_file)


def add(domain, category_path):
    directory_path = "{}/{}/{}".format(INPUT_DIR, MANUAL_DIR, fix_path(category_path))
    create_directory(directory_path)
    file_path = "{}/{}".format(directory_path, DOMAINS_FILE)
    string_to_append = "{}\n".format(domain)
    write_file(file_path, string_to_append, "a")


def remove(domain, category_path):
    directory_path = "{}/{}/{}".format(INPUT_DIR, MANUAL_DIR, fix_path(category_path))
    file_path = "{}/{}".format(directory_path, DOMAINS_FILE)
    line_to_remove = "{}\n".format(domain)
    remove_line(file_path, line_to_remove)


def search(domain, directory):
    domain_files = find_domain_files(path=directory)
    line_to_search = "{}\n".format(domain)
    search_line_in_files(line_to_search, domain_files)


def map(service, category_path, map_category_path):
    directory_path = "{}/{}/{}".format(INPUT_DIR, service, fix_path(category_path))
    map_directory_path = "{}/{}".format(OUTPUT_DIR, fix_path(map_category_path))
    domain_files = find_domain_files(directory_path)
    map_domains_to_path(domain_files, map_directory_path)


def init():
    remove_directory(OUTPUT_DIR)
    create_necessary_files()
