from setuptools import setup, find_packages

setup(
    name = 'pyIATI',
    version = '0.3.0',
    description = 'Python library representing the IATI Schemas, Codelists and Rulesets',
    author = 'IATI Technical Team and other authors',
    author_email = 'code@iatistandard.org',
    url='http://iatistandard.org/',
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        # detecting character encoding of files
        'chardet==3.0.4',
        # JSON schema parsing validation
        'jsonschema==2.6.0',
        # XML handling library
        'lxml==4.1.1',
        # YAML parsing for validation error codes
        'PyYAML==3.12',
        # SemVer library
        'semantic_version==2.6.0'
        ],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: XML'
        ],
)
