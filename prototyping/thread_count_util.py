import multiprocessing

"""
    Class contains a prototype function that can be used by Network Guardian to determine the amount of threads used by
    the software
    
    Declan W. 20/01/2020
"""


def get_thread_count(max_required: int = None, max_threads: int = None):
    """
    Function is used to calculate the amount of threads that should be used based on three different factors, the function
    can be used in multiple use cases

    The idea around the function is that it will return by default the max allowed threads if set, if not it will
    either return the maxmium amount of threads possible in the system unless the job count (ie how many threads are
    even needed) is lower, in that case it will use that

    :param max_required:
    :param max_threads:
    :return:
    """

    # by default use the amount of CPU cores installed in the system
    thread_count = multiprocessing.cpu_count()

    # if theres a max required specified, IE theres only like 2 plugins loaded so why bother creating a larger pool
    if isinstance(max_required, int):
        if max_required < thread_count:  # if the required is smaller than thread count
            thread_count = max_required  # just set it the required amount

    if isinstance(max_threads, int):
        if thread_count > max_threads:  # if the thread count is higher than the max allowed threads set by the user
            thread_count = max_threads  # set the thread count

    return thread_count


if __name__ == '__main__':
    # TODO: Copy this into unit tests for this function when in development
    print(get_thread_count())  # should return maximum amount of cpu cores installed in system
    print(get_thread_count(max_required=4))  # should return 4 because only 4 threads are required
    print(get_thread_count(max_threads=3))  # should return 3 because max allowed
    print(get_thread_count(max_required=4, max_threads=2))  # should return 2 because max allowed
    print(get_thread_count(max_required=2, max_threads=4))  # should return 2 despite max threads
