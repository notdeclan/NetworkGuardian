from networkguardian.framework.plugin import PluginCategory, AbstractPlugin, executor
from networkguardian.framework.registry import register_plugin


@register_plugin("Network Visualization", PluginCategory.NETWORK, "Declan", 1.0)
class NetworkVisualization(AbstractPlugin):

    @executor("template.html")
    def execute(self):
        # GET HOST IPS, INTERFACES, SUBNETS
        # GET DEFAULT GATEWAY
        # GET CIDR, NETWORK ADDRESS, BROADCAST ADDRESS
        # TRACE ROUTE SHIT
        # SCAN SUBNETS
        # Trace a non scanned IP in every subnets
        # SCAN GATEWAY
        # SCAN INTERNET GATEWAY
        # GET DEFAULT GATEWAYS AND ROUTES
        # ADD HOSTNAME TO IP
        # GATHER SCANEND IP's
        # COMPOSE DATA

        pass
