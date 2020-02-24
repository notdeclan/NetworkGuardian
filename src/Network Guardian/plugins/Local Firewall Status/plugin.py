import subprocess

from networkguardian.framework.plugin import PluginCategory, AbstractPlugin, SystemPlatform, executor
from networkguardian.framework.registry import register_plugin


@register_plugin("Local Firewall Status", PluginCategory.NETWORK, "Velislav", 1.0)
class LocalFirewallStatus(AbstractPlugin):

    @executor("mac.template.html", SystemPlatform.MAC_OS)
    def mac(self):
        process = subprocess.Popen(["defaults", "read", "/Library/Preferences/com.apple.alf", "globalstate"],
                                   stdout=subprocess.PIPE)
        """ Checks the state of the firewall in a command line and returns the result back to the user. """
        return bool(int(process.communicate()[0].rstrip()))

    @executor("windows.template.html", SystemPlatform.WINDOWS)
    def windows(self):
        """
        Windows Firewall Checker
        """
        process = subprocess.Popen(["netsh", "advfirewall", "show", "allprofiles", "state"], stdout=subprocess.PIPE)
        """ Checks whether or not the Firewall State is ON or OFF and Returns the result in a table. """
        output = process.communicate()[0].decode()
        lines = output.split("\n")
        domain = "ON" in lines[3]
        private = "ON" in lines[7]
        public = "ON" in lines[11]

        return {"Domain": domain, "Private": private, "Public": public}
