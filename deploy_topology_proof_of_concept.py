import target_configurator
import topology
import json
import topology_generator
import logging
import pprint


# logging.basicConfig(level=logging.DEBUG)


#topo = topology_generator.create_3_node_topo()
#topo = topology_generator.create_4_node_topo()
topo = topology_generator.create_multi_layer_topo()
#topo = topology_generator.create_2_layer_topo()
topo.update_all_routing_tables()


dot_visit = topology.DotRepresentationVisitor(True)

topo.apply_visitor(dot_visit)

ir = topo.get_IR_representation()
pp = pprint.PrettyPrinter(indent=4)

with open('env.json', 'r') as f:
    env = json.load(f)

pp.pprint(ir)
pp.pprint(env)


# port_mapping contains {"vRouter": [physical switch ports]}
port_mapping = {}
# route_mapping contains {"vRouter": [("subnet", egress)]}
route_mapping = {}

host_env = {}
for vRouter_id in ir['vRouter']:
    port_mapping[vRouter_id] = []
    route_mapping[vRouter_id] = []


for vRouter_id in ir['vRouter']:
    router = ir['vRouter'][vRouter_id]
    current_router_rt_entries = []
    for neighbour in router["neighbors"]:
        if neighbour[2] == 'vRouter':

            # Get one available link-loop from the environment file
            link = env["links"].pop(0)

            # Give Link-endpoints descriptive names
            local_port = link[0]
            remote_port = link[1]

            # Assign link endpoints to current switch and current neighbor
            port_mapping[vRouter_id].append(local_port)
            port_mapping[neighbour[1]].append(remote_port)

            # Iterate over Routingtable and find all entries which match the current port/neighbor
            for entry in router['routingtable']:

                # Check if current entry in routing table applies to the current neighbor
                if entry[0] == neighbour[0]:

                    # Add routing entry to mapping
                    route_mapping[vRouter_id].append(
                        (entry[1], local_port, "08:00:00:00:00:00"))

        elif neighbour[2] == 'host':

            # Get one available host link from environmnent file
            link = env["host_links"].pop(0)

            # Give Entry descriptive names
            hostname = link[0]
            switch_port = link[1]

            host_env[hostname] = ir['Host'][neighbour[1]]

            # Assign Link enpoint to current switch
            port_mapping[vRouter_id].append(switch_port)

            # Iterate over Routingtable and find all entries which match the current port/neighbor
            for entry in router['routingtable']:

                # Check if current entry in routing table applies to the current neighbor
                if entry[0] == neighbour[0]:

                    # Get mac address of host from IR
                    mac = ir['Host'][neighbour[1]]['mac']

                    # Add routing entry to mapping
                    route_mapping[vRouter_id].append(
                        (entry[1], switch_port, mac))


# print(dot_visit.get_representation())
print("############")
print()
print("## Port Mappingv ##")
pp.pprint(port_mapping)
print("############")
print()
print("## Route Mapping ##")
pp.pprint(route_mapping)

print("############")
print()
print("## Host env ##")
print(json.dumps(host_env))
print("############")

deploy = True

if deploy: 
    c = target_configurator.TargetConnector('localhost', 50051)

    for router_index in port_mapping:
        ports = port_mapping[router_index]
        for port in ports:
            c.insert_vRouter_port_mapping(port, router_index)

        routing_entries = route_mapping[router_index]
        for entry in routing_entries:
            c.insert_route(router_index, entry[0], entry[2], entry[1])

        c.insert_route(router_index, topology.ADDRESS_SPACE.compressed, "08:00:00:00:00:00", ports[0])



