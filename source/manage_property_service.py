#!/usr/bin/env python
import os
import sys
import requests
from urlparse import urlsplit
import docopt
import docker_base
import lue


doc_string = """\
Manage the property service

usage: {command} [--help] <uri> (scan|clear) [<arguments>...]

options:
    -h --help   Show this screen
    --version   Show version

Commands:
    scan    Scan files or directories and add property resources to service
    clear   Clear property resources

See '{command} help <command>' for more information on a specific
command.
""".format(
        command = os.path.basename(sys.argv[0]))


def scan_for_regular_files(
        directory_pathname):

    for (_, _, filenames) in os.walk(directory_pathname):
        pathnames = [os.path.join(directory_pathname, n) for n in filenames]
        break

    return pathnames


class Property(object):

    def __init__(self,
            dataset_pathname,
            property_pathname):
        self.dataset_pathname = dataset_pathname
        self.property_pathname = property_pathname


def scan_phenomena_for_properties(
        phenomena):

    property_pathnames = []

    for phenomenon_name in phenomena.names:
        phenomenon = phenomena[phenomenon_name]
        property_sets = phenomenon.property_sets

        for property_set_name in property_sets.names:
            property_set = property_sets[property_set_name]
            properties_ = property_set.properties

            for property_name in properties_.names:
                property = properties_[property_name]
                property_pathnames.append(property.id.pathname)

    return property_pathnames


def scan_universes_for_properties(
        universes):

    property_pathnames = []

    for universe_name in universes.names:
        universe = universes[universe_name]
        phenomena = universe.phenomena
        property_pathnames += scan_phenomena_for_properties(phenomena)

    return property_pathnames


def scan_for_properties(
        pathname):

    properties = []

    if os.path.isdir(pathname):
        pathnames = scan_for_regular_files(pathname)

        for pathname in pathnames:
            properties += scan_for_properties(pathname)
    else:

        # See if we can open the file as a LUE dataset. If not, issue a
        # warning. If so, obtain the internal paths of properties.
        try:

            dataset = lue.open_dataset(pathname)
            properties += [Property(pathname, property_pathname) for
                property_pathname in scan_phenomena_for_properties(
                    dataset.phenomena)]
            properties += [Property(pathname, property_pathname) for
                property_pathname in scan_universes_for_properties(
                    dataset.universes)]

        except RuntimeError:
            pass
            # print("Skipping non-LUE file {}".format(pathname))

    return properties


scan_doc_string = """\
Scan one or more files or directories for LUE datasets containing properties

usage: {command} <uri> scan <file>...

options:
    -h --help       Show this screen

arguments:
    file    Names of files and/or directories to scan

This command scans datasets for properties. Properties found which are
not yet present in the service are added. Properties found which are
already present in the service are not touched. Properties present in
the service which are not in the scanned directory are also not touched.

The names of files and/or directories can be passed. Filenames must point
to LUE dataset. Directory-names must point to directories. All LUE datasets
present in the directory will be scanned.
""".format(
        command = os.path.basename(sys.argv[0]))


def property_equals(
        available_property,
        property):
    return \
        available_property["pathname"] == property.dataset_pathname and \
        available_property["name"] == property.property_pathname


def property_already_available(
        available_properties,
        property):

    return any([property_equals(available_property, property) for
        available_property in available_properties])


def add_property(
        uri,
        property):

    payload = {
        "name": property.property_pathname,
        "pathname": property.dataset_pathname
    }

    response = requests.post(uri, json={"property": payload})

    if response.status_code != 201:
        raise RuntimeError(response.json()["message"])


def scan(
        uri,
        argv):
    arguments = docopt.docopt(scan_doc_string, argv=argv)
    pathnames = arguments["<file>"]

    properties = []

    for pathname in pathnames:
        properties += scan_for_properties(pathname)

    response = requests.get(uri)

    if response.status_code != 200:
        raise RuntimeError("cannot get collection of properties")

    available_properties = response.json()["properties"]

    for property in properties:

        if not property_already_available(available_properties, property):
            add_property(uri, property)


clear_doc_string = """\
Clear all property resources

usage: {command} <uri> clear

options:
    -h --help       Show this screen
""".format(
        command = os.path.basename(sys.argv[0]))


def clear(
        uri,
        argv):
    arguments = docopt.docopt(clear_doc_string, argv=argv)
    response = requests.get(uri)

    if response.status_code != 200:
        raise RuntimeError("cannot get collection of properties")

    available_properties = response.json()["properties"]
    parts = urlsplit(uri)
    uri = "{}://{}".format(parts.scheme, parts.netloc)

    for property in available_properties:
        delete_uri = property["_links"]["self"]
        response = requests.delete(uri + delete_uri)

        if response.status_code != 204:
            raise RuntimeError("cannot delete property")


if __name__ == "__main__":
    arguments = docopt.docopt(doc_string, version="0.0.0", options_first=True)
    uri = arguments["<uri>"]

    if arguments["clear"]:
        command = "clear"
    elif arguments["scan"]:
        command = "scan"

    argv = [uri] + [command] + arguments["<arguments>"]
    functions = {
        "clear": clear,
        "scan": scan,
    }
    status = docker_base.call_subcommand(functions[command], uri, argv)

    sys.exit(status)
