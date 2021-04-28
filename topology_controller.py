import topology
import json
import logging


class TopologyController:

    def __init__(self, env_json_fd, topo=None, ir_fd=None):
        logging.debug(
            "New TopologyController with \n|->env:{}, \n|->topo: {}, \n|->ir: {}".format(env_json_fd, topo, ir_fd))

        if topo is None and ir_fd is None:
            raise RuntimeError("Neither topology nor IR is defiend")

        self.ir = {}
        self.topo = topo

        if ir_fd is not None:
            self.ir = json.load(ir_fd)

        self.env = json.load(env_json_fd)

        # port_mapping contains {"vRouter": [physical switch ports]}
        self.port_mapping = {}
        # route_mapping contains {"vRouter": [("subnet", egress, MAC)]}
        self.route_mapping = {}

        self.host_env = {}

        # Optain the Intermediate Representation from the topology object
        if self.topo is not None:
            self.ir = topo.get_IR_representation()

        # Initialize the mapping dicts with all routers present in the toplogy
        for vRouter_id in self.ir['vRouter']:
            self.port_mapping[vRouter_id] = []
            self.route_mapping[vRouter_id] = []

        for vRouter_id in self.ir['vRouter']:
            router = self.ir['vRouter'][vRouter_id]
            current_router_rt_entries = []
            for neighbour in router["neighbors"]:
                if neighbour[2] == 'vRouter':

                    # Get one available link-loop from the environment file
                    link = self.env["links"].pop(0)

                    # Give Link-endpoints descriptive names
                    local_port = link[0]
                    remote_port = link[1]

                    # Assign link endpoints to current switch and current neighbor
                    self.port_mapping[vRouter_id].append(local_port)
                    self.port_mapping[neighbour[1]].append(remote_port)

                    # Iterate over Routingtable and find all entries which match the current port/neighbor
                    for entry in router['routingtable']:

                        # Check if current entry in routing table applies to the current neighbor
                        if entry[0] == neighbour[0]:

                            # Add routing entry to mapping
                            self.route_mapping[vRouter_id].append(
                                (entry[1], local_port, "08:00:00:00:00:00"))

                elif neighbour[2] == 'host':

                    # Get one available host link from environmnent file
                    link = self.env["host_links"].pop(0)

                    # Give Entry descriptive names
                    hostname = link[0]
                    switch_port = link[1]

                    self.host_env[hostname] = self.ir['Host'][neighbour[1]]

                    # Assign Link enpoint to current switch
                    self.port_mapping[vRouter_id].append(switch_port)

                    # Iterate over Routingtable and find all entries which match the current port/neighbor
                    for entry in router['routingtable']:

                        # Check if current entry in routing table applies to the current neighbor
                        if entry[0] == neighbour[0]:

                            # Get mac address of host from IR
                            mac = self.ir['Host'][neighbour[1]]['mac']

                            # Add routing entry to mapping
                            self.route_mapping[vRouter_id].append(
                                (entry[1], switch_port, mac))

    def deploy(self, target_connector):

        for router_index in self.port_mapping:
            ports = self.port_mapping[router_index]
            for port in ports:
                target_connector.insert_vRouter_port_mapping(
                    port, router_index)

            routing_entries = self.route_mapping[router_index]
            for entry in routing_entries:
                target_connector.insert_route(
                    router_index, entry[0], entry[2], entry[1])

            # Add default route to uplink router
            target_connector.insert_route(
                router_index, topology.ADDRESS_SPACE.compressed, "08:00:00:00:00:00", ports[0])

    def get_host_config(self):
        return json.dumps(self.host_env)

    def store_host_config_json(self, json_path):
        logging.info("Store host-config to json file at {}".format(json_path))

        json.dump(self.host_env, json_path, indent=4)