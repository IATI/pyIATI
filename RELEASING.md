Releasing
=========

Steps to follow to release a new version of pyIATI.

1. In the `dev` branch.
    1. Ensure license information for any new dependencies has been added to `LICENSES-3RD-PARTY.txt`.
    2. Read the README to ensure it is up-to-date (if it isn't, fix it!).
    3. Ensure that all relevant Pull Requests have been merged into `dev`.
    4. Ensure the `Unreleased` section in `CHANGELOG.md` covers all changes between `  dev` and `master`.
    5. Ensure all lines under `Unreleased` in `CHANGELOG.md` include a reference to a Pull Request or Issue.
    6. Bump the version.
        1. If the changes are bug fixes only: `bumpversion patch`
        2. If new features are added: `bumpversion minor`
        3. There **MUST NOT** be a `major` version increase (to `1.0.0`) until a suitable amount of functionality is stable and tested.
    7. Move content under `Unreleased` in `CHANGELOG.md` to a new section, with a heading in the format: `[version-number] - yyyy-mm-dd`.
    8. Ensure a blank `Unreleased` section is left in `CHANGELOG.md` (see later in doc for template).
    9. Merge `dev` into `master`.
2. On the `master` branch.
    1. Create a new [Github Release](https://github.com/IATI/pyIATI/releases).
        * Title: `v{{version-number}}`
        * Content: The relevant section from `CHANGELOG.md`
        * Create a new tag called: `v{{version-number}}`, target `master`
3. Release on PyPi.
    1. TODO: Fill in

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
