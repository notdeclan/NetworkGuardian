import socket

from nmap import nmap

from networkguardian.framework.plugin import PluginCategory, AbstractPlugin, executor
from networkguardian.framework.registry import register_plugin


@register_plugin("TCP Scan", PluginCategory.NETWORK, "Owen", 1.0)
class TCPScanner(AbstractPlugin):
    """
       Uses NMAP to scan the current machines open TCP ports
    """

    @executor("template.html")
    def execute(self):
        nested_dict = {}
        new_dict = {}
        i = 0

        hostname = socket.gethostname()
        ip_addr = socket.gethostbyname(hostname)

        nm = nmap.PortScanner()
        a = nm.scan(ip_addr)
        nested_dict.update({'tcp': {'Port': a['scan'][ip_addr]['tcp']}})
        keys = nested_dict['tcp']['Port'].keys()
        keys = list(keys)

        while i < len(keys):
            new_dict.update({keys[i]: {'State': nested_dict['tcp']['Port'][keys[i]]['state'],
                                       'Reason': nested_dict['tcp']['Port'][keys[i]]['reason'],
                                       'Name': nested_dict['tcp']['Port'][keys[i]]['name'],
                                       'Product': nested_dict['tcp']['Port'][keys[i]]['product']

                                       }})
            i += 1

        return {'results': new_dict}