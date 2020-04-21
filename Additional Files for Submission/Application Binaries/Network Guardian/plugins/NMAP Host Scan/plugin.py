import ipaddress

import psutil
from netaddr import IPNetwork
from nmap import nmap

from networkguardian.framework.plugin import PluginCategory, AbstractPlugin, executor
from networkguardian.framework.registry import register_plugin


@register_plugin("NMAP Host Scan", PluginCategory.NETWORK, "Owen", 1.0)
class HostScanner(AbstractPlugin):
    """
        Uses Nmap to do a network scan and display information about each machine on the network
    """

    @staticmethod
    def get_networks():
        """Uses psutil to go through all network interfaces and excludes interfaces that are of no use such as
        loopbacks or if the interface is down"""
        network_list = []
        for interface_name, interfaces in psutil.net_if_addrs().items():
            for interface in interfaces:
                try:
                    # Validate Interface / Network
                    assert not ipaddress.ip_address(interface.address).is_loopback  # if loopback
                    assert not ipaddress.ip_address(interface.address).is_link_local  # if  link local
                    assert psutil.net_if_stats()[interface_name].isup  # if disabled (down)
                except (AssertionError, ValueError):  # not valid ip address
                    continue  # goto next one

                ipn = IPNetwork(f"{interface.address}/{interface.netmask}")

                network_list.append(ipn)

        return network_list

    @executor("template.html", requires_elevation=True)
    def execute(self):
        temp_dict = {}
        new_dict = {}
        c = 0
        d = 0

        networks = self.get_networks()
        nm = nmap.PortScanner()
        """Creates a dictionary the size of all the network interfaces in use"""
        for network in networks:
            new_dict[c] = {}
            c += 1

        """Starts a nmap scan for a network interface and then stores all the information into a dictionary,
        then loops and goes through next interface in the list"""
        for network in networks:
            temp_dict[d] = nm.scan(hosts=str(network.cidr), arguments="-O -F -T5")
            keys = temp_dict[d]['scan'].keys()
            keys = list(keys)
            i = 0
            while i < len(keys):
                x = 0
                key = list(temp_dict[d]['scan'][keys[i]].keys())
                while x < len(key):
                    new_dict[d][keys[i]] = temp_dict[d]['scan'][keys[i]]
                    x += 1
                i += 1
            d += 1
        return {'parent_dict': new_dict}
