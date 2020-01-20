"""
    Prototype attempt of a wrapper ish type class which will be used to store information that will be populated at the
    initiation of a scan. The goal is to improve efficiency in program and plugin operation by providing information
    readily.

    Some plugins require the same information such as Network Interface Information, and program elevation level, by creating
    an object in memory of this information efficiency can be improved because there will be less reads to the system if
    the information is only read and stored once.
"""


def get_network_interfaces():
    """
    TODO: This function

    Based on current research the two "best" ways of getting network interface is with two different python packages.
    Those being psutil, and  netifaces.

    The difficult with a function like comes from the lack of a built in system call which would work cross platform.

    netifaces is good but requires compiling and may have other issues unbeknown because its untested
    psutil is already used in other places within network guardian, but provides less information than NG
    """

    pass
