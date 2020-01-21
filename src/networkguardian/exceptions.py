"""
Module contains exceptions raised within Network Guardian
"""


class PluginException(Exception):
    ...


class PluginInitializationError(PluginException):
    """
    Exception should be raised when a plugin's initialization method is called and the plugin determines itself
    as unable to execute, so therefore it cannot be run...
    """
    ...


class PluginProcessingError(PluginException):
    """
    Exception should be raised when a plugin is attempting to process, but cannot complete for whatever reason,
    developers should always suggest the reason in the exception message if possible
    """
    ...
