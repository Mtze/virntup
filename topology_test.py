import topology
import logging

logging.basicConfig(level=logging.INFO)


p1 = topology.LogicalPort()
p2 = topology.LogicalPort()
p3 = topology.LogicalPort()
p4 = topology.LogicalPort()


topo = topology.V_topology()

topo.add_host(topology.Host(p1))
topo.add_host(topology.Host(p2))
topo.add_router(topology.vRouter([p3, p4]))


topo.create_link(p1, p3)
topo.create_link(p2, p4)


topo.routers[0].accept(topology.PrintNodesVisitor())
