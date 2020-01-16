import multiprocessing
import time
from concurrent.futures import ThreadPoolExecutor

"""
    Prototype attempt at an idea how plugins within Network Guardian will be processed in parallel with the use of
    multi-threading and pooling.
    
    Declan W. 16/01/2020
"""


class Plugin:
    """
    Dummy Plugin class
    """

    def __init__(self, name, sleep_time):
        self.name = name
        self.sleep_time = sleep_time

    def execute(self):
        print(f"EXECUTING {self.name} SLEEPING FOR {self.sleep_time}")
        time.sleep(self.sleep_time)

        return f"{self.name} RESULT"


def done_callback(future):
    """
    Callback for when the plugin has finished executing the in thread, could maybe used to update a progress bar etc or
    print exceptions to the console as they happen

    :param future: the future of the function that was called, can be used to gain access to the data it returns such as
    the template
    """
    print(f"has finished")


def start_pool():
    # pseudo plugin object list
    plugins = [Plugin("Test Plugin", 5), Plugin("Another Plugin", 4), Plugin("Short Plugin", 1)]

    # list to store the results, in software will be used to generate the final report html etc
    futures = []

    # create thread pool with the amount of cpu cores in the system, in real software offer user the ability to set
    # max threads as an option
    with ThreadPoolExecutor(max_workers=get_cpu_cores()) as executor:
        for plugin in plugins:
            future = executor.submit(plugin.execute)
            future.add_done_callback(done_callback)
            futures.append(future)

    for future in futures:
        try:
            print(future.result())
        except:
            print("Exception occurred in ")


def get_cpu_cores():
    """
    Returns the amount of CPU cores installed on the system to be used when creating the thread worker pool
    :return: CPU core count
    """
    return multiprocessing.cpu_count()


if __name__ == '__main__':
    start_pool()
