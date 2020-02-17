REGISTERED_PLUGINS = []


def register_plugin(cls):
    print(cls)
    REGISTERED_PLUGINS.append(cls)
