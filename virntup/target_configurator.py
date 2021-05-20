import socket
import logging
import p4runtime_sh.shell as shell

from time import sleep


class TargetConnector:
    """TargetConnector.

    Module to connect to an P4 Target. This class assumes that the target either
    already uses the virntup.p4 program or can be configured with P4Runtime to
    use virntup.p4.

    """

    def __init__(self, target_ip, target_port, p4info_path=None, p4binary_path=None):
        """__init__.

        Parameters
        ----------
        target_ip :
            str - ip address or hostname of the target
        target_port :
            int - P4 Runtime gRPC port used by the target (in most cases this is 50051)
        p4info_path :
            (optional) path to p4info file that should be deployed to the target
        p4binary_path :
            (optional) p4binary_path path to binary which should be deployed.
            IMPORTANT: For tofino tagets this binary has to be modified!
            See -> https://github.com/p4lang/p4runtime-shell#target-specific-support
        """
        self.target_ip = target_ip
        self.target_port = target_port

        if p4info_path is None or p4binary_path is None:
            shell.setup(device_id=0,
                        grpc_addr=str(self.target_ip) + ":" +
                        str(self.target_port),
                        election_id=(0, 1)
                        )
        else:

            shell.setup(device_id=0,
                        grpc_addr=str(self.target_ip) + ":" +
                        str(self.target_port),
                        election_id=(0, 1),
                        config=shell.FwdPipeConfig(p4info_path, p4binary_path)
                        )

    def insert_route(self, match_vRouter_number,
                     match_ipv4address,
                     action_dest_mac,
                     action_egress_port):
        """insert_route.

        Add routing table entry for a specific vRouter

        Parameters
        ----------
        match_vRouter_number :
            int
        match_ipv4address :
            string
        action_dest_mac :
            string
        action_egress_port :
            int
        """

        entry = shell.TableEntry("MyIngress.ipv4NextHopLPM")(
            action="MyIngress.ipv4Forward")
        entry.match["vRouterNumber"] = str(match_vRouter_number)
        entry.match["hdr.ipv4.dstAddr"] = str(match_ipv4address)
        entry.action["port"] = str(action_egress_port)
        entry.action["dstAddr"] = str(action_dest_mac)
        entry.insert()

    def insert_vRouter_port_mapping(self, match_ingress_port, action_vRouter_number):
        """insert_vRouter_port_mapping.

        Assing ingress port to vRouter

        Parameters
        ----------
        match_ingress_port :
            int
        action_vRouter_number :
            int
        """

        entry = shell.TableEntry("MyIngress.vRouterNumberMatching")(
            action="MyIngress.setVSwitchNumber")
        entry.match["standard_metadata.ingress_port"] = str(match_ingress_port)
        entry.action["vRouterNumberFromTable"] = str(action_vRouter_number)
        entry.insert()

    def send_bf_shell_commands(self, telnet_port,  port_config_fd):
        """send_bf_shell_command
        Opens a telnet connection to the p4 target and sends the contents of the provided file to it.

        Parameters
        ----------
        telnet_port :
            int - Port to connect to 
        port_config_fd :
            port_config_fd - file-descriptor to the file, containing the bf_shell commands 
        """
        logging.info("Connecting to {}:{}".format(self.target_ip, telnet_port))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.target_ip, telnet_port))
        s_fd = s.makefile('rw')

        logging.info("Submiting content of {}".format(port_config_fd))

        for line in port_config_fd:
            logging.debug(line.rstrip('\n'))
            s_fd.write(line)
            s_fd.flush()
            sleep(0.05)

        logging.info("Closing Telnet")
        s_fd.close()
        s.close()

    def teardown(self):
        """teardown.
        """
        shell.teardown()
