import multiprocessing


"""
    Class contains a prototype function that can be used by Network Guardian to determine the amount of threads used by
    the software
"""


max_allowed_threads = 4


def get_thread_count(max_required: int = None, max_threads: int = max_allowed_threads):
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
    if max_required is int:
        if max_required < thread_count:  # if the required is smaller than thread count
            thread_count = max_required  # just set it the required amount

    if thread_count > max_threads:  # if the thread count is higher than the max allowed threads set by the user
        thread_count = max_threads # set the thread count

    return thread_count
