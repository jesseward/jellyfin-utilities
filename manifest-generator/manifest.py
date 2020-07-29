#!/usr/bin/env python
import datetime
import json
import sys
import os

from typing import Tuple
from typing import List


class Manifest:

    def __init__(self, manifest_file: str = None):
        self.manifest = {}
        self.manifest_file = manifest_file
        if manifest_file:
            self.manifest = self._read_manifest(manifest_file)

    def _read_manifest(self, url: str):
        with open(self.manifest_file) as fh:
            return json.load(fh)

    def applications(self) -> List[str]:
        """Returns the number of applications that exist within the manifest."""
        return [a['name'] for a in self.manifest]

    def versions(self, app_name: str) -> List[str]:
        """Returns the list of versions for a target application.

        :param app_name: target application name to match"""
        for a in self.manifest:
            if a['name'] == app_name:
                return a['versions']

    def remove_application(self, app_name: str) -> None:
        """remove an application from the manifest

        :param app_name: target application name to remove
        """
        app_location = self._application_exists(app_name)
        if self._application_exists(app_name) < 0:
            raise LookupError(f'{app_name} does not exist in manifest.')

        del self.manifest[app_location]

    def add_application(self, guid: str, app_name: str, description: str, overview: str, owner: str, category: str):
        if self._application_exists(app_name) >= 0:
            raise LookupError(f'{app_name} already exists in manifest.')

        self.manifest.append({
            'guid': guid,
            'name': app_name,
            'description': description,
            'overview': overview,
            'owner': owner,
            'category': category,
            'versions': [],
        })

    def create(self, manifest_file: str, guid: str, app_name: str, description: str, overview: str,
               owner: str, category: str) -> None:
        """create is called when building a new manifest file.

        :param manifest_file: the location of the output file.
        :param app_name: application target
        :param version: version string
        :param change_log: descriptive change log for version
        :param target_abi: minimum supported Jellyfin ABI version
        :param source_url: location of plugin zipfile
        :param checksum: the md5 checksum of the plugin zip file
        :param timestamp: addition timestamp.
        """
        self.manifest_file = manifest_file
        self.manifest = [{
            'guid': guid,
            'name': app_name,
            'description': description,
            'overview': overview,
            'owner': owner,
            'category': category,
            'versions': [],
        }]

    def add_version(self, app_name: str, version: str, change_log: str, target_abi: str,
                    source_url: str, checksum: str, timestamp: str):
        """insert a new version into the manifest.

        :param app_name: application target
        :param version: version string
        :param change_log: descriptive change log for version
        :param target_abi: minimum supported Jellyfin ABI version
        :param source_url: location of plugin zipfile
        :param checksum: the md5 checksum of the plugin zip file
        :param timestamp: addition timestamp.
        """
        app_location, version_location = self._version_exists(app_name, version)

        if version_location >= 0:
            raise LookupError(f'{app_name}, {version} already exists')

        self.manifest[app_location]['versions'].append({
            'version': version,
            'changelog': change_log,
            'targetAbi': target_abi,
            'sourceUrl': source_url,
            'checksum': checksum,
            'timestamp': timestamp})

    def remove_version(self, app_name: str, version: str) -> None:
        """removes a version from the catalog.

        :param app_name: the name of application to target
        :param version: version identifier to target
        """
        app_location, version_location = self._version_exists(app_name, version)

        if version_location < 0:
            raise LookupError(f'{app_name}, {version} does not exist, unable to remove')

        del self.manifest[app_location]['versions'][version_location]

    def _version_exists(self, app_name: str, version: str) -> Tuple[int, int]:
        """
        Checks the manifest object to determine if the target app_name already has version information
        present. If the app_name, version combination exists a tuple of the application, version index
        locations is returned. -1 is returned if the application or version is _not_ found.

        :param app_name: the name of application to target
        :param version: the version identifer to look-up
        """
        app_location = self._application_exists(app_name)
        if app_location < 0:
            raise LookupError(f'{app_name} does not exist in manifest')

        for i, ver in enumerate(self.manifest[app_location]['versions']):
            if ver['version'] == version:
                return app_location, i

        return app_location, -1

    def _application_exists(self, app_name: str) -> int:
        """returns the index within the list if the application exists. -1 is return if the
        target is _not_ found.

        :param app_name: the name of the target application.
        """
        for i, application in enumerate(self.manifest):

            if app_name == application['name']:
                return i
        return -1

    def close(self) -> None:
        """Persist the manifest metadata to disk."""
        with open(self.manifest_file, 'w') as fh:
            json.dump(self.manifest, fh)


if __name__ == '__main__':
    # python manifest.py -f ../manifest.json -app LastFM application -desc "Scrobble LastFM plays with Jellyfin" \
    # -ov "A plugin that scrobbles your Jellyfin music to LastFM" -owner "Jesse Ward" -cat "music" -guid "ASDFSDF"
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='Manifest file name')
    parser.add_argument('-app', help='Application name')
    parser.add_argument('-create', action='store_true', help='Create manifest file if doesn\'t exist')

    subparsers = parser.add_subparsers(dest='command')
    # application options
    app_parser = subparsers.add_parser('application')
    app_parser.add_argument('-desc', help='Application description')
    app_parser.add_argument('-ov', help='Application overview')
    app_parser.add_argument('-owner', help='Application owner')
    app_parser.add_argument('-cat', help='Applicaiton category')
    app_parser.add_argument('-guid', help='Plugin GUID')
    # version options
    version_parser = subparsers.add_parser('version')
    version_parser.add_argument('-ver', help='Version string')
    version_parser.add_argument('-cl', help='Version changelog')
    version_parser.add_argument('-ck', help='Version checksum')
    version_parser.add_argument('-abi', help='Version target abi')
    version_parser.add_argument('-url', help='Version url')
    version_parser.add_argument('-ts', help='Version timestamp', required=False,
                                default=datetime.datetime.utcnow().isoformat(timespec='seconds') + 'Z')

    del_version = subparsers.add_parser('delete-version')
    del_version.add_argument('-ver', help='version to remove from manifest')

    subparsers.add_parser('delete-application')
    args = parser.parse_args()

    if not args.f:
        parser.error('-f was not supplied.')

    if args.create and not os.path.isfile(args.f):
        with open(args.f, 'w') as fh:
            json.dump([], fh)

    try:
        m = Manifest(manifest_file=args.f)
    except FileNotFoundError:
        sys.exit(f'[ERROR] unable to locate {args.f}, re-run with -create')

    if args.command == 'delete-application':
        m.remove_application(args.app)

    if args.command == 'delete-version':
        m.remove_version(args.app, args.ver)

    if args.command == 'application':
        try:
            m.add_application(args.guid, args.app, args.desc, args.ov, args.owner, args.cat)
        except LookupError:
            sys.exit('[ERROR] : Application already exists in manifest')

    if args.command == 'version':
        try:
            m.add_version(args.app, args.ver, args.cl, args.abi, args.url, args.ck, args.ts)
        except LookupError:
            sys.exit('[ERROR] : Version already exists in manifest')
    m.close()
