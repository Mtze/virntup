import topology
import topology_generator


# logging.basicConfig(level=logging.DEBUG)


#topo = topology_generator.create_3_node_topo()
#topo = topology_generator.create_4_node_topo()
topo = topology_generator.create_multi_layer_topo()
#topo = topology_generator.create_2_layer_topo()

topo.update_all_routing_tables()


dot_visit = topology.DotRepresentationVisitor(True)

topo.apply_visitor(dot_visit)
print(dot_visit.get_representation())

