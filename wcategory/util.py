import glob
import os

import click

from wcategory.conf import DOMAINS_FILE


def append_file(path, string):
    file = open(path, "a")
    file.write(string)
    file.close()


def read_lines(path):
    file = open(path, "r")
    lines = file.readlines()
    file.close()
    return lines


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


def fix_path(path):
    if path[0] == "/" or path[0] == "\/":
        path = path[1:]
    if path[-1] == "/" or path[-1] == "\/":
        path = path[:-1]
    return path


def find_domain_files(path=None):
    if path:
        path_pattern = "**/{}/**/{}".format(path, DOMAINS_FILE)
    else:
        path_pattern = "**/{}".format(DOMAINS_FILE)
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
