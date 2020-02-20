import ipaddress

import psutil
from netaddr import IPNetwork

from networkguardian.framework.plugin import PluginCategory, AbstractPlugin, executor
from networkguardian.framework.registry import register_plugin


@register_plugin("Subnet Information", PluginCategory.NETWORK, "Declan", 1.0)
class SubnetInformation(AbstractPlugin):

    @executor("template.html")
    def execute(self):
        networks = {}
        for interface_name, interfaces in psutil.net_if_addrs().items():
            for interface in interfaces:

                # Validate
                try:
                    if ipaddress.ip_address(interface.address).is_loopback:  # if loopback
                        continue  # goto next one
                except ValueError:  # not valid ip address
                    continue  # goto next one

                ipn = IPNetwork(f"{interface.address}/{interface.netmask}")
                networks[interface_name] = [ipn[0], ipn.broadcast, interface.netmask, ipn.cidr, ipn._prefixlen,
                                            ipn.cidr.size]

        return {"interfaces": networks}
