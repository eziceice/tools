import os
import constant


def update_plugin_version(filename, version, work_directory):
    os.chdir(work_directory)
    lines = []
    with open(filename, "r") as file:
        for line in file.readlines():
            if constant.PLUGIN_VERSION in line:
                if " " in line:
                    line = line[0: line.find("=") + 2] + version
                else:
                    line = line[0: line.find("=") + 1] + version
            lines.append(line)

    with open(filename, "w") as outfile:
        for line in lines:
            outfile.write(line)


def read_plugin_version(filename, work_directory):
    os.chdir(work_directory)
    with open(filename, "r") as file:
        for line in file.readlines():
            if constant.PLUGIN_VERSION in line:
                line = line.replace(" ", "")
                version = line[line.find("=") + 1: len(line)]
    return version
