from setuptools import setup, find_packages

setup(
    name = 'iati.core',
    version = '0.1dev',
    description = 'Python library representing the IATI Schemas, Codelists and Rulesets',
    author = 'IATI Technical Team and other contributors',
    author_email = 'code@iatistandard.org',
    licence = 'TBC', #TODO
    packages = find_packages(exclude='iati/core/tests')
)
