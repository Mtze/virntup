import p4runtime_sh.shell as shell


class TargetConnector:

    def __init__(self, target_ip, target_port):
        self.target_ip = target_ip
        self.target_port = target_port

        shell.setup(device_id=0,
                    grpc_addr=str(target_ip) + ":" + str(target_port),
                    election_id=(0, 1)
                    )

    def insert_route(self,
                     match_vRouter_number,
                     match_ipv4address,
                     action_dest_mac,
                     action_egress_port):

        entry = shell.TableEntry("MyIngress.ipv4NextHopLPM")(
            action="MyIngress.ipv4Forward")
        entry.match["vSwitchNumber"] = str(match_vRouter_number)
        entry.match["hdr.ipv4.dstAddr"] = str(match_ipv4address)
        entry.action["port"] = str(action_egress_port)
        entry.action["dstAddr"] = str(action_dest_mac)
        entry.insert()

    def insert_vRouter_port_mapping(self, match_ingress_port, action_vRouter_number):

        entry = shell.TableEntry("MyIngress.vSwitchNumberMatching")(
            action="MyIngress.setVSwitchNumber")
        entry.match["standard_metadata.ingress_port"] = str(match_ingress_port)
        entry.action["vSwitchNumberFromTable"] = str(action_vRouter_number)
        entry.insert()


# Only for testing
c = TargetConnector("localhost", 50051)
c.insert_route(1, "10.0.1.1/32", "08:00:00:00:01:11", 1)
c.insert_route(1, "10.0.2.2/32", "08:00:00:00:00:00", 2)
c.insert_route(2, "10.0.1.1/32", "08:00:00:00:00:00", 3)
c.insert_route(2, "10.0.2.2/32", "08:00:00:00:02:22", 4)
c.insert_vRouter_port_mapping(1, 1)
c.insert_vRouter_port_mapping(2, 1)
c.insert_vRouter_port_mapping(3, 2)
c.insert_vRouter_port_mapping(4, 2)
