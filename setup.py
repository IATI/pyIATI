from setuptools import setup, find_packages

setup(
    name = 'iati.core',
    version = '0.1dev',
    description = 'Python library representing the IATI Schemas, Codelists and Rulesets',
    author = 'IATI Technical Team and other authors',
    author_email = 'code@iatistandard.org',
    url='http://iatistandard.org/',
    packages = find_packages(exclude='iati/core/tests'),
    install_requires = [
        # XML handling library
        'lxml==3.8.0',
        # python2/python3 compatibility library
        'six==1.10.0'
        ],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: XML'
        ],
)
