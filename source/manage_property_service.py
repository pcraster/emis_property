#!/usr/bin/env python
import os
import sys
import requests
try:
    # Python 3
    from urllib.parse import urlsplit
except ImportError:
    # Python 2
    from urlparse import urlsplit
import docopt
import lue


doc_string = """\
Manage the property service

usage: {command} [--help] <uri> (scan|remove) [<arguments>...]

options:
    -h --help   Show this screen
    --version   Show version

Commands:
    scan    Scan files or directories and add property resources to service
    remove  Remove property resources

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

usage: {command} <uri> scan [--rewrite_path=<pattern>] <file>...

options:
    -h --help       Show this screen
    --rewrite_path=<pattern>  Replace prefix of certain paths

arguments:
    file    Names of files and/or directories to scan

This command scans datasets for properties. Properties found which are
not yet present in the service are added. Properties found which are
already present in the service are not touched. Properties present in
the service which are not in the scanned directory are also not touched.

The names of files and/or directories can be passed. Filenames must point
to LUE dataset. Directory-names must point to directories. All LUE datasets
present in the directory will be scanned.

Optionally, the prefix of dataset pathnames can be replaced by some
other prefix. This allows for scanning of local datasets that are
mounted into a container at some other path. To use this feature,
a <from_prefix>:<to_prefix> pattern must be passed.
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
    rewrite_path = arguments["--rewrite_path"]
    rewrite_path = [] if rewrite_path is None else rewrite_path.split(":")

    properties = []

    for pathname in pathnames:
        properties += scan_for_properties(pathname)

    if rewrite_path is not None:
        for property in properties:
            if property.dataset_pathname.startswith(rewrite_path[0]):
                property.dataset_pathname = property.dataset_pathname.replace(
                    rewrite_path[0], rewrite_path[1])

    response = requests.get(uri)

    if response.status_code != 200:
        raise RuntimeError("cannot get collection of properties")

    available_properties = response.json()["properties"]

    for property in properties:

        if not property_already_available(available_properties, property):
            add_property(uri, property)


remove_doc_string = """\
Remove property resources

usage: {command} <uri> remove [<properties>...]

options:
    -h --help       Show this screen
    properties      Properties to remove
""".format(
        command = os.path.basename(sys.argv[0]))


def remove(
        uri,
        argv):
    arguments = docopt.docopt(remove_doc_string, argv=argv)
    properties = arguments["<properties>"]
    response = requests.get(uri)

    if response.status_code != 200:
        raise RuntimeError("cannot get collection of properties")

    parts = urlsplit(uri)
    uri = "{}://{}".format(parts.scheme, parts.netloc)
    available_properties = response.json()["properties"]
    properties_to_remove = []

    if not properties:
        # Remove all properties.
        properties_to_remove = available_properties
    else:
        # Filter available properties by the ones passed in.
        uris = [property["_links"]["self"] for property in \
            available_properties]

        for property_uri in properties:
            idx = uris.index(property_uri)

            if idx == -1:
                raise RuntimeError("property to remove does not exist")

            properties_to_remove.append(available_properties[idx])

    for property in properties_to_remove:
        delete_uri = property["_links"]["self"]
        response = requests.delete(uri + delete_uri)

        if response.status_code != 204:
            raise RuntimeError("cannot delete property")


if __name__ == "__main__":
    arguments = docopt.docopt(doc_string, version="0.0.0", options_first=True)
    uri = arguments["<uri>"]

    if arguments["remove"]:
        command = "remove"
    elif arguments["scan"]:
        command = "scan"

    argv = [uri] + [command] + arguments["<arguments>"]
    functions = {
        "remove": remove,
        "scan": scan,
    }

    status = 1

    try:
        functions[command](uri, argv)
        status = 0
    except SystemExit:
        raise
    except RuntimeError as exception:
        sys.stderr.write("{}\n".format(exception))

    # status = docker_base.call_subcommand(functions[command], uri, argv)

    sys.exit(status)
