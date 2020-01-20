"""
Module contains exceptions raised within Network Guardian
"""


class PluginInitializationError(Exception):
    """
    Exception should be raised when a plugin's initialization method is called and the plugin determines itself
    as unable to execute, so therefore it cannot be run...
    """
    ...
