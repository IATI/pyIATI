# Resources: IATI Standard

The folder (and sub-folders) contain data that is used by the library that relates to the IATI Standard.

Data for a given version of the Standard is stored within a corresponding folder – for example version 2.02 data is contained with the `2-02` folder.  Note that this contains all content for that version of the standard, symlinks are used to ensure content replicated across multiple versions of the Standard - for example non-embedded codelists – is not replicated for each version of the Standard.

Currently non-embedded codelists are stored within the `codelists_non_embedded` folder. Due to the relevant modification schedule, it may be desired to nest them within a `2` or `2xx` folder; or move them to `version_independent/codelists/` due to how the pyIATI resources module works.

Non-Embedded Codelists must be symlinked from each version at which they occur. This can be done by changing to the folder you wish to symlink files from:
* `cd [path/to/pyIATI]/iati/resources/standard/[versionFolder]/codelists/`

And running:
* `ln -s ../../codelists_non_embedded/* .`
