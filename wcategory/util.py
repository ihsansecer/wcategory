import os


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


def get_current_directory():
    return os.path.dirname(os.path.abspath(__file__))


def fix_path(path):
    if path[0] == "/" or path[0] == "\/":
        path = path[1:]
    if path[-1] == "/" or path[-1] == "\/":
        path = path[:-1]
    return path
