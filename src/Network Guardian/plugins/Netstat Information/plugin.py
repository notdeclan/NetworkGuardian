import socket

import psutil

from networkguardian.framework.plugin import PluginCategory, AbstractPlugin, executor
from networkguardian.framework.registry import register_plugin


@register_plugin("NetStat Information", PluginCategory.NETWORK, "Owen", 1.0)
class NetStatInformation(AbstractPlugin):
    """
        Netstat Information v1.0
        This plugin is based on and uses the psutil (process and system utilities)  cross-platform library to retrieve information and store it into variables.
        The plugin tells you about the different connections and information about them such as the protocol, local address, remote address, status, PID and the program name.
    """

    @executor("template.html")
    def execute(self):
        """
            Get information using psutil and stores into variables
        """
        AD = "-"
        AF_INET6 = getattr(socket, 'AF_INET6', object())
        proto_map = {
            (socket.AF_INET, socket.SOCK_STREAM): 'tcp',
            (AF_INET6, socket.SOCK_STREAM): 'tcp6',
            (socket.AF_INET, socket.SOCK_DGRAM): 'udp',
            (AF_INET6, socket.SOCK_DGRAM): 'udp6',
        }

        main_list = {}
        i = 1
        proc_names = {}

        for p in psutil.process_iter(attrs=['pid', 'name']):
            proc_names[p.info['pid']] = p.info['name']
        for c in psutil.net_connections(kind='inet'):
            laddr = "%s:%s" % (c.laddr)
            raddr = ""
            if c.raddr:
                raddr = "%s:%s" % (c.raddr)

                main_list.update({i: {
                    "Protocol": proto_map[(c.family, c.type)],
                    "LocalAddress": laddr,
                    "RemoteAddress": raddr or "-",
                    "Status": c.status,
                    "PID": c.pid or "-",
                    "ProgramName": proc_names.get(c.pid, '?')[:15],
                }})
                i += 1

        return {"result": main_list}
