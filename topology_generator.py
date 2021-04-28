import logging
import topology


def _reset_topo_id_counter():
    """_reset_topo_id_counter.
    Only necessary to perform unit tests.
    """
    # pylint: disable=protected-access
    topology._Node.next_id = 1


def create_3_node_topo():
    """create_3_node_topo.

    Creates one router and two hosts connected to the router.
    In this case the router is just a forwarder.
    """
    logging.info("Instantiate new 3 node topology")

    _reset_topo_id_counter()

    root = topology.vRouter()
    topo = topology.V_topology(root)

    root.add_link(topology.Host())
    root.add_link(topology.Host())

    return topo


def create_4_node_topo():
    """create_4_node_topo.

    Creates two vRouters connected to each other.
    Each vRouter is connected to one Host.

    This topology is the minimal 2 vRouter setup.
    """

    logging.info("Instantiate new 4 node topology")

    _reset_topo_id_counter()

    root = topology.vRouter()
    topo = topology.V_topology(root)

    tmp = topology.vRouter()
    root.add_link(tmp)
    root.add_link(topology.Host())
    tmp.add_link(topology.Host())

    return topo


def create_multi_layer_topo():
    """create_multi_layer_topo.

    Creates 1 core router connected to 3 vRouters.
    Each of these vRouters is again connected to 3 vRouters.
    Each of these vRouter is then connected to 2 Hosts.
    """
    logging.info("Instantiate new multilayer topology")

    _reset_topo_id_counter()

    root = topology.vRouter()
    topo = topology.V_topology(root)

    for _ in range(3):
        l1 = topology.vRouter()
        root.add_link(l1)
        for _ in range(3):
            l2 = topology.vRouter()
            l1.add_link(l2)
            for _ in range(2):
                l2.add_link(topology.Host())
    return topo
