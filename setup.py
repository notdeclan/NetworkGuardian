from setuptools import setup, find_packages

from networkguardian import application_version

readme = open('README.md').read()
license = open('LICENSE.md').read()
requirements = open('REQUIREMENTS.txt').read().split("\n")

setup(
    name='Network Guardian',
    version=application_version,  # TODO: get version from __init__.py
    description='Network scanning automation platform',
    long_description=readme,
    author='Pentagon',
    license=license,
    url='http://github.com/notdeclan/Network-Guardian',
    packages=find_packages(),
    install_requires=requirements,
)
