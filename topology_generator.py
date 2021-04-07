import topology
import logging


def reset_topo_id_counter():
    topology._Node.next_id = 1


def create_3_node_topo():
    logging.info("Instantiate new 3 node topology")

    reset_topo_id_counter()

    root = topology.vRouter()
    topo = topology.V_topology(root)

    root.add_link(topology.Host())
    root.add_link(topology.Host())

    return topo


def create_multi_layer_topo():
    logging.info("Instantiate new multilayer topology")

    reset_topo_id_counter()

    root = topology.vRouter()
    topo = topology.V_topology(root)

    for i in range(3):
        l1 = topology.vRouter()
        root.add_link(l1)
        for j in range(3):
            l2 = topology.vRouter()
            l1.add_link(l2)
            for j in range(2):
                l2.add_link(topology.Host())
    return topo
