"""
    Prototype is for testing and developing ways the user can load custom plugins into Network Guardian from a file, and
    how network guardian will store the location, etc...



    **** IDEA FOR HANDLING HOW A PLUGIN WILL BE LOADED IF IT REQUIRES A NON STANDARD PYTHON PACKAGE ****
        When installing, processing a plugin, use sys.modules[__name__] to get the list of packages required by the
    plugin, then check if it is installed on the system, attempt to include the plugin and if it raises a ImportError,
    throw an error to the user asking them to install the module to the running python environment

    OR ...

        Create a plugin installation error, and provide documentation in the exception which can be displayed in the GUI.
    For example, if import error is given because the plugin requires uninstalled python package, display "Plugin
    requires extra installation, python package "psutil" requires installation.
"""