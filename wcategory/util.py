import glob
import os
import sys

import click

from wcategory.conf import DOMAINS_FILE, INPUT_DIR, OUTPUT_DIR, CONF_DIR, CONF_EXTENSION


def write_file(path, string, mode):
    file = open(path, mode)
    file.write(string)
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


def write_lines(path, lines):
    file = open(path, "w")
    for line in lines:
        file.write(line)
    file.close()


def remove_line(path, line_to_remove):
    lines = read_lines(path)
    if lines:
        file = open(path, "w")
        for line in lines:
            line = remove_line_feed(line)
            if line != line_to_remove:
                file.write(line)
        file.close()


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def remove_directory(path):
    if not os.path.exists(path):
        os.removedirs(path)


def fix_path(path):
    if path[0] == "/" or path[0] == "\/":
        path = path[1:]
    if path[-1] == "/" or path[-1] == "\/":
        path = path[:-1]
    return path


def get_file_name(file_path):
    base_name = os.path.basename(file_path)
    return os.path.splitext(base_name)[0]


def find_domain_files(path=None):
    if path:
        path_pattern = "{}/**/{}".format(path, DOMAINS_FILE)
    else:
        path_pattern = "{}".format(DOMAINS_FILE)
    return glob.glob(path_pattern, recursive=True)


def find_conf_files(files_to_exclude, service=None):
    if service:
        path_pattern = "{}/{}{}".format(CONF_DIR, service, CONF_EXTENSION)
    else:
        path_pattern = "{}/**{}".format(CONF_DIR, CONF_EXTENSION)
    conf_files = glob.glob(path_pattern)
    return [conf for conf in conf_files if conf not in files_to_exclude]


def find_add_remove_conf_files(prefix):
    path_pattern = "{}/{}**{}".format(CONF_DIR, prefix, CONF_EXTENSION)
    return glob.glob(path_pattern)


def search_line_in_files(line_to_find, files):
    found = False
    for file in files:
        lines = read_lines(file)
        for line_number, line in enumerate(lines):
            if line_to_find in line:
                print_found_message(line_to_find, line_number + 1, file)
                found = True
    if not found:
        print_not_found_message(line_to_find)


def print_found_message(line_text, line_number, file):
    message = "\"{}\" is found at line {} in file \"{}\"".format(line_text, line_number, file)
    click.echo(message)


def print_not_found_message(line_text):
    message = "\"{}\" is not found".format(line_text)
    click.echo(message)


def check_root_permission():
    if os.getuid() != 0:
        click.echo("Permission Denied")
        sys.exit()


def check_necessary_files():
    input_dir_exists = os.path.exists(INPUT_DIR)
    output_dir_exists = os.path.exists(OUTPUT_DIR)
    conf_dir_exists = os.path.exists(CONF_DIR)
    if not (input_dir_exists and output_dir_exists and conf_dir_exists):
        click.echo("You should first run \"init\" command")
        sys.exit()


def create_necessary_files():
    necessary_files = [INPUT_DIR, OUTPUT_DIR, CONF_DIR]
    for file in necessary_files:
        create_directory(file)


def check_environment():
    check_necessary_files()


def requires_environment_check(function):
    def check_environment_and_execute(*args, **kwargs):
        check_environment()
        function()
    return check_environment_and_execute


def exit_if_false(ctx, param, value):
    if not value:
        sys.exit()


def sort_uniquify_lines(path):
    import functools
    lines = read_lines(path)
    lines = functools.reduce(lambda l_list, element: l_list + [element] if element not in l_list else l_list, lines, [])
    lines.sort()
    write_lines(path, lines)
    return lines


def map_domains_to_path(domain_files, map_path):
    content = ""
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
    return command.split(" ")[:2]


def parse_add_remove(command):
    return command.split(" ")[1:3]


def check_prefix(prefix, line):
    try:
        return line[0] == prefix
    except IndexError:
        return False


def invoke_map_commands(file, command_function, prefix):
    service = get_file_name(file)
    lines = read_lines(file)
    for line in lines:
        if check_prefix(prefix, line):
            line = remove_line_feed(line)
            args = parse_map(line)
            command_function(service, *args)


def invoke_add_remove_commands(file, command_function, prefix):
    lines = read_lines(file)
    for line in lines:
        if check_prefix(prefix, line):
            line = remove_line_feed(line)
            args = parse_add_remove(line)
            command_function(*args)


def fix_content_to_append(content):
    if content:
        if content[-1] != "\n":
            content += "\n"
    return content


def fix_file_to_append(path, content_to_add):
    content_to_check = read_file(path)
    if content_to_check:
        if content_to_check[-1] != "\n":
            content_to_add = "\n" + content_to_add
    return content_to_add


def save_map_command_to_conf(service, category_path, map_category_path):
    line_to_save = "/{} /{}\n".format(fix_path(category_path), fix_path(map_category_path))
    conf_file_path = "{}/{}{}".format(CONF_DIR, service, CONF_EXTENSION)
    line_to_save = fix_file_to_append(conf_file_path, line_to_save)
    write_file(conf_file_path, line_to_save, "a+")


def save_add_remove_command_to_conf(domain, category_path, prefix, file_prefix):
    line_to_save = "{} {} /{}\n".format(prefix, domain, fix_path(category_path))
    conf_file_path = "{}/{}{}".format(CONF_DIR, file_prefix, CONF_EXTENSION)
    line_to_save = fix_file_to_append(conf_file_path, line_to_save)
    write_file(conf_file_path, line_to_save, "a+")
