from urllib.error import URLError
from urllib.request import urlopen

from networkguardian.framework.plugin import AbstractPlugin, PluginCategory, executor
from networkguardian.framework.registry import register_plugin


@register_plugin("Internet Connectivity", PluginCategory.NETWORK, "Velislav V", 1.0)
class CheckInternetConnectivityPlugin(AbstractPlugin):
    """
        Internet Connectivity Plugin v1.0
        This plugin determines whether the local machine has access to the internet.
        It works by using the urllib module which loops through three different URL’s, tries to connect to them and then returns the results back to the user.
    """

    @executor("template.html")
    def execute(self):
        """
        Function is used to return whether the local machine has internet access

        Works by looping through multiple URL's and connecting to them, if one successfully connects
        it will return True, otherwise False
        """

        urls = {
            "https://google.co.uk": False,
            "https://youtube.com": False,
            "https://bbc.co.uk": False
        }

        for url in urls.keys():  # loop through all URL's
            try:
                urlopen(url, timeout=5)
                urls[url] = True  # if connect, internet is working, return True
            except URLError:
                continue

        return {"results": urls}
