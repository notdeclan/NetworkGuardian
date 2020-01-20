"""
    Prototype file to assist in developing the procedure in which Network Guardian will process all of the loaded plugins,
    and then generate a report, implements a thread worker pool similar to the version found in thread_pool.py

    Declan W. 20/01/2020
"""
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor

from networkguardian.plugin import Platform
from networkguardian.standard_plugins import SystemInformationPlugin
from prototyping.thread_count_util import get_thread_count


def done_callback(future):
    """
    Callback for when the plugin has finished executing the in thread, could maybe used to update a progress bar etc or
    print exceptions to the console as they happen

    :param future: the future of the function that was called, can be used to gain access to the data it returns such as
    the template
    """
    print(f"has finished")


if __name__ == '__main__':
    # plugin object list
    plugins = [SystemInformationPlugin()]

    # list to store the results, in software will be used to generate the final report html etc

    # load plugins
    for plugin in plugins:
        plugin.load(Platform.detect())

    # create thread pool with the amount of cpu cores in the system, in real software offer user the ability to set
    # max threads as an option

    # use with operator to ensure threads are deconstructed / cleaned up properly

    thread_count = get_thread_count(max_required=len(plugins))
    print(f'Thread Count: {thread_count}')
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        future_to_plugin = {
            executor.submit(p.execute): p for p in plugins
        }

        print(future_to_plugin)

        for future in futures.as_completed(future_to_plugin):
            plugin = future_to_plugin[future]
            try:
                print(plugin.name)
                print(plugin.template.render(future.result()))
            except Exception as exc:
                print(exc)
