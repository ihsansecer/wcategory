import glob
import os
import sys

import click

from wcategory.conf import DOMAINS_FILE, INPUT_DIR, OUTPUT_DIR, CONF_DIR, CONF_EXTENSION


def write_file(path, string, mode):
    file = open(path, mode)
    file.write(string)
    file.close()


def write_lines(path, lines):
    file = open(path, "w")
    for line in lines:
        file.write(line)
    file.close()


def read_file(path):
    if os.path.exists(path):
        file = open(path, "r")
        content = file.read()
        file.close()
        return content
    else:
        print_not_found_message(path)
        return ""


def read_lines(path):
    if os.path.exists(path):
        file = open(path, "r")
        lines = file.readlines()
        file.close()
        return lines
    else:
        print_not_found_message(path)
        return []


def remove_line(path, line_to_remove):
    lines = read_lines(path)
    if lines:
        file = open(path, "w")
        for line in lines:
            line = remove_line_feed(line)
            if line != line_to_remove:
                file.write(line + "\n")
        file.close()


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        click.secho("Created directory {}".format(path), fg="green")


def remove_directory(path):
    import shutil
    if os.path.exists(path):
        shutil.rmtree(path)
        click.secho("Removed directory {}".format(path), fg="green")


def get_working_directory():
    return os.getcwd()


def fix_path(path):
    """
    Removes slash at the end and the beginning
    """
    try:
        if path[0] == "/" or path[0] == "\/":
            path = path[1:]
        if path[-1] == "/" or path[-1] == "\/":
            path = path[:-1]
        return path
    except IndexError:
        print_unexpected_path_exit(path)


def get_file_name(file_path):
    base_name = os.path.basename(file_path)
    return os.path.splitext(base_name)[0]


def find_domain_files(path=None):
    if path:
        path_pattern = "{}/{}".format(path, DOMAINS_FILE)
    else:
        path_pattern = "**/{}".format(DOMAINS_FILE)
    return glob.glob(path_pattern, recursive=True)


def find_conf_files(exclude=None, service=None):
    if service:
        path_pattern = "{}/{}{}".format(CONF_DIR, service, CONF_EXTENSION)
    else:
        path_pattern = "{}/**{}".format(CONF_DIR, CONF_EXTENSION)
    conf_files = glob.glob(path_pattern)
    if exclude:
        return [conf for conf in conf_files if conf not in exclude]
    return conf_files


def find_add_remove_conf_files(prefix):
    path_pattern = "{}/{}**{}".format(CONF_DIR, prefix, CONF_EXTENSION)
    return glob.glob(path_pattern)


def search_text_in_files(text, files):
    found = False
    counter = 0
    for file in files:
        lines = read_lines(file)
        for index, line in enumerate(lines):
            if text.lower() in line.lower():
                print_found_message(remove_line_feed(line), index + 1, file)
                found = True
                counter += 1
                print_found_count(text, counter)
    if not found:
        print_not_found_message(text)


def print_found_message(line_text, line_number, file):
    message = "\"{}\" is found at line {} in file \"{}\"".format(line_text, line_number, file)
    click.secho(message, fg="green")


def print_not_found_message(line_text):
    message = "\"{}\" is not found".format(line_text)
    click.secho(message, fg="red")


def print_found_count(text, count):
    message = "Searched text \"{}\" found {} times".format(text, count)
    click.secho(message, fg="blue")


def print_unique_count(path, count):
    message = "Sorted and uniquified {} domains under {}".format(count, path)
    click.secho(message, fg="green")


def print_unexpected_path_exit(path):
    message = "\"{}\" is not a valid path. Please, remove or edit it".format(path)
    click.secho(message, fg="red")
    sys.exit()


def create_necessary_files():
    necessary_files = [INPUT_DIR, OUTPUT_DIR, CONF_DIR]
    for file in necessary_files:
        create_directory(file)


def check_environment():
    input_dir_exists = os.path.exists(INPUT_DIR)
    output_dir_exists = os.path.exists(OUTPUT_DIR)
    conf_dir_exists = os.path.exists(CONF_DIR)
    if not (input_dir_exists and output_dir_exists and conf_dir_exists):
        click.secho("You should first run \"init\" command", fg="red")
        sys.exit()


def requires_environment_check(function):
    def check_environment_and_execute(*args, **kwargs):
        check_environment()
        function()
    return check_environment_and_execute


def exit_if_no(ctx, param, value):
    """
    Callback for yes/no option, exits if user's answer is no
    """
    if not value:
        sys.exit()


def sort_uniquify_lines(path, echo=True):
    lines = read_lines(path)
    unique_lines = set(lines)
    sorted_lines = sorted(unique_lines)
    if echo:
        count = len(sorted_lines)
        print_unique_count(path, count)
    write_lines(path, sorted_lines)
    return lines


def map_domains_to_path(domain_files, map_path):
    """
    Moves domains under domain_files to map_path
    """
    content = ""
    message = "Mapping to {}".format(map_path)
    with click.progressbar(domain_files, label=message) as domain_files:
        for file in domain_files:
            content += read_file(file)
            content = fix_content_to_append(content)
    create_directory(map_path)
    path_to_write = "{}/{}".format(map_path, DOMAINS_FILE)
    write_file(path_to_write, content, "a+")
    sort_uniquify_lines(path_to_write)


def remove_line_feed(line):
    if line[-1] == "\n":
        return line[:-1]
    return line


def parse_map(command):
    parsed = command.split(" ")
    return tuple(parsed[:2]), [exclude[1:] for exclude in parsed[2:]]


def parse_add_remove(command):
    return command.split(" ")[1:3]


def check_prefix(prefix, line):
    try:
        return line[0] == prefix
    except IndexError:
        return False


def invoke_map_commands(command_function, file, prefix):
    """
    Invokes cli's map command for conf files
    """
    service = get_file_name(file)
    lines = read_lines(file)
    for line in lines:
        if check_prefix(prefix, line):
            line = remove_line_feed(line)
            args = parse_map(line)
            category_paths, exclude_path = args[0], args[1]
            command_function(service, *category_paths, exclude_path)


def invoke_add_remove_commands(command_function, file, prefix):
    """
    Invokes cli's add/remove command for conf files
    """
    lines = read_lines(file)
    for line in lines:
        if check_prefix(prefix, line):
            line = remove_line_feed(line)
            args = parse_add_remove(line)
            command_function(*args)


def fix_content_to_append(content):
    """
    Needed when appending files
    If there is no line feed at the end of content, adds line feed at the end
    """
    if content:
        if content[-1] != "\n":
            content += "\n"
    return content


def fix_file_to_append(path, content_to_add):
    """
    Needed when appending files
    If there is no line feed at end of file, adds line feed at the beginning of content
    """
    content_to_check = read_file(path)
    if content_to_check:
        if content_to_check[-1] != "\n":
            content_to_add = "\n" + content_to_add
    return content_to_add


def save_map_command_to_conf(service, category_path, map_category_path, exclude_path):
    line_wo_exclude = "/{} /{}\n".format(fix_path(category_path), fix_path(map_category_path))
    line_to_save = save_map_exclude_to_conf(line_wo_exclude, exclude_path)
    conf_file_path = "{}/{}{}".format(CONF_DIR, service, CONF_EXTENSION)
    line_to_save = fix_file_to_append(conf_file_path, line_to_save)
    write_file(conf_file_path, line_to_save, "a+")


def save_add_remove_command_to_conf(domain, category_path, prefix, file_prefix):
    line_to_save = "{} {} /{}\n".format(prefix, domain, fix_path(category_path))
    conf_file_path = "{}/{}{}".format(CONF_DIR, file_prefix, CONF_EXTENSION)
    line_to_save = fix_file_to_append(conf_file_path, line_to_save)
    write_file(conf_file_path, line_to_save, "a+")


def save_map_exclude_to_conf(line_to_save, exclude_path):
    if exclude_path:
        line_to_save = line_to_save[:-1]
        for path in exclude_path:
            line_to_save += " -/{}".format(fix_path(path))
        line_to_save += "\n"
    return line_to_save


def exclude_domain(domain_files, directory_path, exclude_path):
    excluded_domain_files = []
    if exclude_path:
        for path in exclude_path:
            if directory_path[-1] == "*" and directory_path[-2] == "*":
                directory_path = directory_path[:-3]
            exclude_directory_path = "{}/{}".format(directory_path, fix_path(path))
            excluded_domain_files.extend(find_domain_files(exclude_directory_path))
    return [domain_file for domain_file in domain_files if domain_file not in excluded_domain_files]
