from setuptools import setup, find_packages

with open('../README.md') as f:  # TODO: move readme into here and basically restructure the whole thing ... fml
    readme = f.read()

# TODO: maybe import a license file here too prehaps... ask ethan about what license we should use if so

setup(
    name='Network Guardian',
    version='',  # TODO: get version from __init__.py
    description='Network scanning automation platform',
    long_description=readme,
    author='Pentagon',
    url='http://github.com/notdeclan/Network-Guardian',
    packages=find_packages(),
    install_requires=[
        "jinja2",
        "flask",
        "pywebview",
        "psutil",
        "PyQt5==5.11.3"
    ],
)
