import p4runtime_sh.shell as shell


class TargetConnector:

    def __init__(self, target_ip, target_port, p4info_path=None, p4binary_path=None):
        self.target_ip = target_ip
        self.target_port = target_port

        if p4info_path is None or p4binary_path is None:
            shell.setup(device_id=0,
                        grpc_addr=str(self.target_ip) + ":" + str(self.target_port),
                        election_id=(0, 1)
                        )
        else: 

            shell.setup(device_id=0,
                        grpc_addr=str(self.target_ip) + ":" + str(self.target_port),
                        election_id=(0, 1),
                        config=shell.FwdPipeConfig(p4info_path,p4binary_path)
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

