import ipaddress
import json
import socket
import xml
from contextlib import closing

import networkx
import psutil
from libnmap.parser import NmapParser
from libnmap.process import NmapProcess
from netaddr import IPNetwork
from networkx.readwrite import json_graph
from nmap import nmap


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


def get_ip():
    """
    Finds and returns the local IP address as dotted-quad ints on my host computer.
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.connect(("8.8.8.8", 53))
        ip = s.getsockname()[0]

    return ip


def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent + 1)
        else:
            print('\t' * (indent + 1) + str(value))


def get_node_data(host):
    print(dir(host.os_fingerprint))
    data = {
        "hostname": host.hostnames,
        "ports": host.get_ports(),
        "os": host.os_fingerprint,
    }
    return data


if __name__ == '__main__':
    networks = get_networks()
    graph = networkx.Graph()
    print(networks)

    nm = nmap.PortScanner()
    for interface_name, network in networks.items():
        nm.scan(str(network), arguments="-A -n")
        all_hosts = nm.all_hosts()
        for key in all_hosts:
            host = nm[key]
            print(key)

            print(host)
            print(host.hostname())
            print(host.all_tcp())
            print(host.all_udp())
            print(host.all_ip())
            for osclass in host['osclass']:
                print('OsClass.type : {0}'.format(osclass['type']))
                print('OsClass.vendor : {0}'.format(osclass['vendor']))
                print('OsClass.osfamily : {0}'.format(osclass['osfamily']))
                print('OsClass.osgen : {0}'.format(osclass['osgen']))
                print('OsClass.accuracy : {0}'.format(osclass['accuracy']))

    exit(0)

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
                graph.add_node(host.address, **get_node_data(host))
                if len(trace_list) > 0:
                    print("edge")
                    graph.add_edge(host.address, trace_list[0])

        data = json_graph.node_link_data(graph)
        print(json.dumps(data, indent=4))
        exit()
