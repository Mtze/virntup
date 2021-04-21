import json
import logging
import topology
import topology_generator
import target_configurator
from topology_controller import TopologyController

import argparse
LOG_FORMAT = '%(levelname)s - %(module)s - %(message)s'

# topo = topology_generator.create_4_node_topo()
# topo = topology_generator.create_multi_layer_topo()
# topo.update_all_routing_tables()
#
# topo_controller = TopologyController(
#    topo, "../testbed-env-setup/environments/large/env.json")
#
# topo_controller.store_host_config_json('host-test.json')
#
# connector = target_configurator.TargetConnector('localhost', 50051)
#
# topo_controller.deploy(connector)


def main():

    parser = argparse.ArgumentParser(
        description="Virntup - Virtualized network topologies using P4")

    parser.add_argument('--debug',
                        action='store_true',
                        help='Print Debug log')

    parser.add_argument('--info',
                        action='store_true',
                        help='Print Info log')

    subparsers = parser.add_subparsers(dest='command')

    # Define sub-parsers for all subssytems
    topogen_parser = subparsers.add_parser(
        'topogen', help='Generate Toplogoies')
    envgen_parser = subparsers.add_parser(
        'envgen', help='Generate Host-configuration for Toplogy')
    deploy_parser = subparsers.add_parser(
        'deploy', help='Deploy Toplogoy to Target')

    # Define Arguments for the topology_generator subsystem
    topogen_parser.add_argument(
        '-t', '--type',
        help="Toplogoy type to be generated",
        required=True,
        choices=['minimal', 'medium', 'large']
    )
    topogen_parser.add_argument(
        '-o', '--out-file',
        type=argparse.FileType('w'),
        default='ir.json',
        help="Path to the file in which the topology representation should be stored"
    )

    # Define Arguments for the env generation
    envgen_parser.add_argument(
        '-ir', '--intermediate-representation',
        default='ir.json',
        type=argparse.FileType('r'),
        help='Path to the intermediate representation json file'
    )
    envgen_parser.add_argument(
        '-o', '--out-file',
        default='host.json',
        type=argparse.FileType('w'),
        help='Path to the file the host-configuration should be stored'
    )
    envgen_parser.add_argument(
        '-t', '--target',
        type=argparse.FileType('r'),
        required=True,
        help='Path to the target definition json file'
    )
    envgen_parser.add_argument(
        '-e', '--env',
        type=argparse.FileType('r'),
        required=True,
        help='Path to the env definition json file'
    )

    # Define Arguments for deployment subsystem
    deploy_parser.add_argument(
        '-t', '--target',
        required=True,
        type=argparse.FileType('r'),
        help='Path to the target definition json file'
    )

    deploy_parser.add_argument(
        '-ir', '--intermediate-representation',
        default='ir.json',
        type=argparse.FileType('r'),
        help='Path to the intermediate representation json file'
    )

    deploy_parser.add_argument(
        '-e', '--env',
        type=argparse.FileType('r'),
        required=True,
        help='Path to the env definition json file'
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

    if args.info:
        logging.basicConfig(level=logging.INFO)

    logging.debug(
        "virntup_4 called with the following arguments: {}".format(args))

    if args.command == 'topogen':
        print("topogen")
        if args.type == 'minimal':
            topo = topology_generator.create_2_layer_topo()

        elif args.type == 'medium':
            topo = topology_generator.create_4_node_topo()

        elif args.type == 'large':
            topo = topology_generator.create_multi_layer_topo()

        topo.update_all_routing_tables()
        ir = topo.get_IR_representation()
        json.dump(ir, args.out_file, indent=4)

    elif args.command == 'envgen':
        print("envgen")

        topo_controller = TopologyController(
            args.env, ir_fd=args.intermediate_representation)
        topo_controller.store_host_config_json(args.out_file)

        # TODO TARGET! Depending on the target the host file should either contain the mininet setup or ip commands 
        args.target

    elif args.command == 'deploy':
        print("deploy")

        topo_controller = TopologyController(
            args.env, ir_fd=args.intermediate_representation)
       
        target = json.load(args.target)
        logging.debug(target)

        connector = target_configurator.TargetConnector(target['hostname'], target['port'])

        #topo_controller.deploy(connector)

if __name__ == '__main__':
    main()
