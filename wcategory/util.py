import glob
import os
import sys

import click

from wcategory.conf import (DOMAINS_FILE, INPUT_DIR, OUTPUT_DIR, CONF_DIR, CONF_EXTENSION, ADD_PREFIX, MAP_PREFIX,
                            REMOVE_PREFIX)


def write_file(path, string, mode):
    file = open(path, mode)
    file.write(string)
    file.close()


def read_file(path):
    file = open(path, "r")
    content = file.read()
    file.close()
    return content


def read_lines(path):
    file = open(path, "r")
    lines = file.readlines()
    file.close()
    return lines


def write_lines(path, lines):
    file = open(path, "w")
    for line in lines:
        file.write(line)
    file.close()


def remove_line(path, line_to_remove):
    lines = read_lines(path)
    file = open(path, "w")
    for line in lines:
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
        path_pattern = "**/{}/**/{}**".format(path, DOMAINS_FILE)
    else:
        path_pattern = "**/{}**".format(DOMAINS_FILE)
    return glob.glob(path_pattern, recursive=True)


def find_conf_file(service=None):
    if service:
        path_pattern = "**/{}/**/{}{}".format(CONF_DIR, service, CONF_EXTENSION)
    else:
        path_pattern = "**/{}/**/**{}".format(CONF_DIR, CONF_EXTENSION)
    return glob.glob(path_pattern, recursive=True)


def search_line_in_files(line, files):
    line_text = line[:-1]
    for file in files:
        lines = read_lines(file)
        try:
            line_number = lines.index(line) + 1
            print_found_message(line_text, line_number, file)
        except ValueError:
            pass
    if "line_number" not in locals():
        print_not_found_message(line_text)


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
    create_directory(map_path)
    path_to_write = "{}/{}".format(map_path, DOMAINS_FILE)
    write_file(path_to_write, content, "a")
    sort_uniquify_lines(path_to_write)


def separate_conf_file_by_command(file):
    lines = read_lines(file)
    separated_lines = {"map": [], "add": [], "remove": []}
    for line in lines:
        line = remove_line_feed(line)
        if line[0] == MAP_PREFIX:
            separated_lines["map"] += [line]
        elif line[0] == ADD_PREFIX:
            separated_lines["add"] += [line]
        elif line[0] == REMOVE_PREFIX:
            separated_lines["remove"] += [line]
    return separated_lines


def remove_line_feed(line):
    if line[-1] == "\n":
        return line[:-1]
    return line


def parse_add_remove(command):
    return command.split(" ")[1:3]


def parse_map(command):
    return command.split(" ")[:2]


def invoke_add_remove_commands(command_list, command_function):
    for command in command_list:
        args = parse_add_remove(command)
        command_function(*args)


def invoke_map_commands(command_list, file, command_function):
    service = get_file_name(file)
    for command in command_list:
        args = parse_map(command)
        command_function(service, *args)
