Releasing
=========

Steps to follow to release a new version of pyIATI.

1. In the `dev` branch.
    1. Ensure license information for any new dependencies has been added to `LICENSES-3RD-PARTY.txt`.
    2. Read the README to ensure it is up-to-date (if it isn't, fix it!).
    3. Ensure pyIATI includes the latest relevant version of SSOT content.
    4. Ensure that all relevant Pull Requests have been merged into `dev`.
    5. Ensure the `Unreleased` section in `CHANGELOG.md` covers all changes between `  dev` and `master`.
    6. Ensure all lines under `Unreleased` in `CHANGELOG.md` include a reference to a Pull Request or Issue.
    7. Prepare the release. You will need a new pull request for these steps:
        1. Bump the version, as per [SemVer](http://semver.org/). Run one of the following as appropriate:
            1. If the changes are bug fixes only: `bumpversion patch`
            2. If new features are added: `bumpversion minor`
            3. There **MUST NOT** be a `major` version increase (to `1.0.0`) until a suitable amount of functionality is stable and tested.
        2. Move content under `Unreleased` in `CHANGELOG.md` to a new section, with a heading in the format: `[version-number] - yyyy-mm-dd`.
        3. Ensure a blank `Unreleased` section is left in `CHANGELOG.md` (see later in doc for template).
    8. Merge `dev` into `master`.
2. On the `master` branch.
    1. Create a new [Github Release](https://github.com/IATI/pyIATI/releases).
        * Title: `v{{version-number}}`
        * Content: The relevant section from `CHANGELOG.md`
        * Create a new tag called: `v{{version-number}}`, target `master`
3. Download and check that the release is safe to be published
    1. Download the `.zip` or `.tar.gz` source code for the release on the [Releases page](https://github.com/IATI/pyIATI/releases).
    2. Unzip/uncompress, enter into the folder, [follow the instructions to set-up a development environment](https://github.com/IATI/pyIATI#dev-installation).
    3. Run the tests to check that the package is safe for release, [how to run the tests](https://github.com/IATI/pyIATI#tests).
4. If the tests passed: Publish to PyPi
    1. Install tools required for deployment: `apt-get install python3-setuptools twine`
    2. Check that you have a the iati login credentials for the PyPi test and production instances in a `~/.pypirc` file. A template file is below. [See here](https://docs.python.org/3.6/distutils/packageindex.html#pypirc) for an explanation of the file.
    3. From within the folder extracted from the zip file:
        1. Package the release ready to upload to PyPi: `python setup.py sdist`
        2. Upload to the PyPi test server: `twine upload dist/* -r pypi-test`
    4. Test installation from the PyPi test server:
        1. Create and activate a clean virtualenv: `deactivate; mkdir pyIATItest; cd pyIATItest; virtualenv -p python3 pyenv;source pyenv/bin/activate`
        2. Install pyIATI: `pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pyIATI` – this will install `pyIATI` from the test PyPi, but other dependencies (e.g. `lxml` and others) from the production server
        3. Ensure that all is well by running `pip freeze`. If the latest version of pyIATI is present, all is well.
    6. Publish to production PyPi:
        1. Change back to the virtualenv from the unzipped folder.
        2. Upload to the PyPi production server: `twine upload dist/* -r pypi-production`
    7. The package is now published and you can now run `pip install pyIATI` to download pyIATI!


Template for Unreleased Changes
-------------------------------

This template should be used to keep track of unreleased changes in `CHANGELOG.md`.

```
## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

```

Template for .pypirc
--------------------

```
[distutils]
index-servers =
  pypi-production
  pypi-test

[pypi-production]
username=iati
password=[PASSWORD_HERE]

[pypi-test]
repository: https://test.pypi.org/legacy/
username=iati
password=[PASSWORD_HERE]
```
