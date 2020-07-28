import pytest

from manifest import Manifest


def test_create_and_applications():
    m = Manifest()
    m.create('manifest.json', 'test-guid', 'test-app', 'test-description', 'overview....', 'jesseward', 'utility')
    assert m.applications() == ['test-app']


def test_add_application():
    m = Manifest()
    m.create('manifest.json', 'test-guid', 'test-app', 'test-description', 'overview....', 'jesseward', 'utility')

    # attempting to add a duplicate application should trigger a look-up errors
    with pytest.raises(LookupError):
        m.add_application('test-guid', 'test-app', 'test-description', 'overview....', 'jesseward', 'utility')

    # add a second application and ensure it persists.
    m.add_application('test-guid', 'test-app-2', 'test-description', 'overview....', 'jesseward', 'utility')
    assert len(m.applications()) == 2


def test_add_version():
    m = Manifest()
    m.create('manifest.json', 'test-guid', 'test-app', 'test-description', 'overview....', 'jesseward', 'utility')

    # add a single version and verify it exists
    m.add_version('test-app', '1.0.0.0', 'this is my changelog', '1.1.1.1', 'source-url', 'checksum', '2020')
    assert len(m.versions('test-app')) == 1

    # attempt to add duplicate, expect a lookup error
    with pytest.raises(LookupError):
        m.add_version('test-app', '1.0.0.0', 'this is my changelog', '1.1.1.1', 'source-url', 'checksum', '2020')

    # assert we can add a second version.
    m.add_version('test-app', '1.0.0.1', 'this is my changelog', '1.1.1.1', 'source-url', 'checksum', '2020')
    assert len(m.versions('test-app')) == 2


def test_remove_application():
    # create a pair of applications in the manifest
    m = Manifest()
    m.create('manifest.json', 'test-guid', 'test-app-0', 'test-description', 'overview....', 'jesseward', 'utility')
    m.add_application('test-guid', 'test-app-1', 'test-description', 'overview....', 'jesseward', 'utility')
    assert len(m.applications()) == 2

    # remove index 0 / application test-app-0
    m.remove_application('test-app-0')
    assert len(m.applications()) == 1


def test_remove_version():
    m = Manifest()
    m.create('manifest.json', 'test-guid', 'test-app-0', 'test-description', 'overview....', 'jesseward', 'utility')
    m.add_version('test-app-0', '0.0.0', 1, 2, 3, 4, 5)
    m.add_version('test-app-0', '1.0.0', 1, 2, 3, 4, 5)
    assert len(m.versions('test-app-0')) == 2

    # remove version at index 1
    m.remove_version('test-app-0', '1.0.0')
    assert len(m.versions('test-app-0')) == 1
    m.close()
