"""
Module contains exceptions raised within Network Guardian
"""


# TODO: Start raising and handling these properly...

class PluginException(Exception):
    """
    Base Exception for all custom exceptions that are raised from a Plugin
    """
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
