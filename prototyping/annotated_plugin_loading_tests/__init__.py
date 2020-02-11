# Import all classes in this directory so that classes with @register_class are registered.

from glob import glob
from os.path import basename, dirname, join

pwd = dirname(__file__)

for x in glob(join(pwd, '*.py')):
    if not x.startswith('__'):
        __import__(basename(x)[:-3], globals(), locals())

__all__ = [
    'REGISTERED_PLUGINS'
]
