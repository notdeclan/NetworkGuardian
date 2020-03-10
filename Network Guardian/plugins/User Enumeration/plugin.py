import csv
import os
from io import StringIO

import psutil

from networkguardian.framework.plugin import PluginCategory, AbstractPlugin, executor, SystemPlatform
from networkguardian.framework.registry import register_plugin


@register_plugin("User Enumeration", PluginCategory.ENUMERATION, "Alexandra", 1.0)
class UserEnumerationPlugin(AbstractPlugin):
    """
    User Enumeration v1.0
    This plugin uses the grp module that provides access to the Unix group Database. It is a Unix specific service, so all the methods of this module are available on Unix versions only.

    """

    @executor("windows.template.html", SystemPlatform.WINDOWS)
    def windows(self):
        process = os.subprocess.Popen(["wmic", "useraccount", "list", "full", "/format:csv"], stdout=os.subprocess.PIPE)
        users_output = process.communicate()[0]
        file_stream = StringIO(users_output.decode())
        for i in range(2):
            file_stream.readline()

        reader = csv.reader(file_stream)
        return {"reader": reader}

    @executor("linux.template.html", SystemPlatform.MAC_OS, SystemPlatform.LINUX)
    def linux(self):
        import grp
        return {
            "users": {
                user[0]: grp.getgrgid(user[3])[0] for user in psutil.pwd.getpwall()
            }
        }

    @executor("mac.template.html", SystemPlatform.MAC_OS)
    def mac(self):
        return {
            "users": [
                user[0] for user in psutil.pwd.getpwall()
            ]
        }
