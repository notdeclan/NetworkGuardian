from prototyping.annotated_plugin_loading_tests import REGISTERED_PLUGINS

if __name__ == '__main__':
    for p in REGISTERED_PLUGINS:
        print(p().name)
