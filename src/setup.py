from setuptools import setup, find_packages

from networkguardian import application_version

readme = open('../README.md').read()
license = open('../LICENSE').read()

setup(
    name='Network Guardian',
    version=application_version,  # TODO: get version from __init__.py
    description='Network scanning automation platform',
    long_description=readme,
    author='Pentagon',
    license=license,
    url='http://github.com/notdeclan/Network-Guardian',
    packages=find_packages(),
    install_requires=[  # TODO: get this from the requirements file / remove the license file and just use dis
        "jinja2",
        "flask",
        "pywebview",
        "psutil",
        "PyQt5==5.11.3"
    ],
)
