import ipaddress
import xml

import networkx
import psutil
from libnmap.parser import NmapParser
from libnmap.process import NmapProcess
from netaddr import IPNetwork
from networkx.readwrite import json_graph

from networkguardian.framework.plugin import PluginCategory, AbstractPlugin, executor
from networkguardian.framework.registry import register_plugin


@register_plugin("Network Visualization", PluginCategory.NETWORK, "Declan", 1.0)
class NetworkVisualization(AbstractPlugin):

    @staticmethod
    def get_networks():
        networks = {}
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

                print(f"Interface: {interface_name}")
                print("\tNetwork:", ipn[0])
                print("\tBroadcast:", ipn.broadcast)
                print("\tNetmask:", interface.netmask)
                print("\tCIDR:", ipn.cidr)
                print("\tNetbit", ipn._prefixlen)
                print("\tTotal IP's:", ipn.cidr.size)

                networks[interface_name] = ipn

        return networks

    @staticmethod
    def get_node_data(host):
        data = {
            "hostname": host.hostnames,
            "ports": host.get_ports(),
            "os": host.os_fingerprint,
        }
        return data

    @executor("template.html", requires_elevation=True)
    def execute(self):
        networks = self.get_networks()
        graph = networkx.Graph()
        print(networks)

        for interface_name, network in networks.items():
            print(f"Scanning {network} on interface {interface_name}")

            # Host Discovery
            network_scan = NmapProcess(str(network), options="-A -n")
            network_scan.run()
            parsed = NmapParser.parse(network_scan.stdout)

            # Traceroute
            traceroute_scan = NmapProcess("google.com", options="--traceroute")
            traceroute_scan.run()
            collection = xml.etree.ElementTree.fromstring(traceroute_scan.stdout)
            traceroute_nodes = collection.getiterator("hop")

            trace_list = []
            pre_node = ''

            for node in traceroute_nodes:
                print(node.attrib)

                trace_list.append(node.attrib["ipaddr"])
                graph.add_node(node.attrib["ipaddr"])

                if pre_node != '':
                    print("pre node")
                    graph.add_edge(node.attrib["ipaddr"], pre_node)

                pre_node = node.attrib["ipaddr"]

            for host in parsed.hosts:
                if host.is_up():
                    graph.add_node(host.address, **self.get_node_data(host))
                    if len(trace_list) > 0:
                        print("edge")
                        graph.add_edge(host.address, trace_list[0])

        return {
            "graph_json": json_graph.node_link_data(graph)
        }
