import topology
import logging

logging.basicConfig(level=logging.INFO)

root = topology.vRouter()

topo = topology.V_topology(root)

root.add_link(topology.Host())
root.add_link(topology.Host())


print_v = topology.PrintNodesVisitor()

topo.apply_visitor(print_v)
