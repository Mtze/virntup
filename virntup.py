import json
import sys
import logging

import argparse
from argparse import RawTextHelpFormatter

import topology_generator
import topology
import target_configurator
from topology_controller import TopologyController

LOG_FORMAT = '%(levelname)s - %(module)s - %(message)s'


def main():
    """main.

    Virntup main - CLI for virntup
    """

    parser = argparse.ArgumentParser(
        description="Virntup - Virtualized network topologies using P4", formatter_class=RawTextHelpFormatter)

    parser.add_argument('--debug',
                        action='store_true',
                        help='Print Debug log')

    parser.add_argument(
        '-c', '--conf',
        type=argparse.FileType('r'),
        help="""Path to the target definition json file.
This json file can contain all necessary configuration details. Like 
{   "target": "bmv2",               # bmv2 or tofino
    "env": "env.json",              # Path to the enviroment configuratioin file 
    "ir": "ir.json",                # Path where the ir should be stored 
    "host": "host.json",            # Path where the host config should be stored
    "hostname": "localhost",
    "port": 50051,
    "p4info": "/path/to/p4info",    # Absolute path to P4 info file created by P4 compiler
    "p4binary": "/path/to/p4binary" # Absolute path to P4 binary, which was modified by the P4Runtime shell script (see github)
}

CLI parameters will overwrite the configuration if set.
"""
    )
    subparsers = parser.add_subparsers(dest='command')

    # Define sub-parsers for all subssytems
    topogen_parser = subparsers.add_parser(
        'topogen', help='Generate Toplogoies', formatter_class=RawTextHelpFormatter)
    envgen_parser = subparsers.add_parser(
        'envgen', help='Generate Host-configuration for Toplogy', formatter_class=RawTextHelpFormatter)
    deploy_parser = subparsers.add_parser(
        'deploy', help='Deploy Toplogoy to Target', formatter_class=RawTextHelpFormatter)

    # Define Arguments for the topology_generator subsystem
    topogen_parser.add_argument(
        '-t', '--type',
        help="Toplogoy type to be generated",
        required=True,
        choices=['minimal', 'medium', 'large', 'n_hops']
    )

    topogen_parser.add_argument(
        '--hops',
        type=int,
        help="Only a valid parameter if type `n_hops` was chosen. Define the number of routers between two hosts"
    )

    topogen_parser.add_argument(
        '-o', '--out-file',
        type=argparse.FileType('w'),
        help="Path to the file in which the topology representation should be stored - Default is `ir.json`"
    )

    topogen_parser.add_argument(
        '-d', '--dot',
        type=argparse.FileType('w'),
        help="Create dot represenetation and store the dot file to the path given."
    )

    # Define Arguments for the env generation
    envgen_parser.add_argument(
        '-e', '--env',
        type=argparse.FileType('r'),
        help='Path to the enviroment configuration file'
    )

    envgen_parser.add_argument(
        '-ir', '--intermediate-representation',
        type=argparse.FileType('r'),
        help='Path to the intermediate representation json file'
    )

    envgen_parser.add_argument(
        '-t', '--target',
        type=str,
        choices=['bmv2', 'tofino'],
        help='Target type to deploy to'
    )

    envgen_parser.add_argument(
        '-o', '--out-file',
        type=argparse.FileType('w'),
        help='Path to the file the host-configuration should be stored'
    )

    # Define Arguments for deployment subsystem
    deploy_parser.add_argument(
        '-ir', '--intermediate-representation',
        type=argparse.FileType('r'),
        help='Path to the intermediate representation json file'
    )

    deploy_parser.add_argument(
        '-e', '--env',
        type=argparse.FileType('r'),
        help='Path to the enviroment configuration file'
    )

    deploy_parser.add_argument(
        '-t', '--target',
        type=str,
        choices=['bmv2', 'tofino'],
        help='Target type to deploy to'
    )

    deploy_parser.add_argument(
        '--hostname',
        help='fqdn/ip of the P4 Runtime target'
    )

    deploy_parser.add_argument(
        '--port',
        help='gRPC Port of the P4 Runtime target'
    )

    deploy_parser.add_argument(
        '--p4info',
        help='Path to the p4info file generated for by the target compiler'
    )

    deploy_parser.add_argument(
        '--p4binary',
        help='Path to the p4binary file generated for by the target compiler and modified by the p4-runtime-shell script'
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    logging.debug(
        "virntup_4 called with the following arguments: {}".format(args))

    if args.conf is not None:
        conf = json.load(args.conf)
        logging.debug("Using conf file {}\n{}".format(args.conf, conf))
    else:
        conf = {
            "target": "",               # bmv2 or tofino
            "env": "",              # Path to the enviroment configuratioin file
            "ir": "",                # Path where the ir should be stored
            "host": "",            # Path where the host config should be stored
            "hostname": "",
            "port": 0,
            "p4info": "",
            "p4binary": ""
        }
        logging.debug("No config file supplied, relying on CLI parameters")

    if args.command == 'topogen':
        logging.info("Generate topology of type {}".format(args.type))

        if args.type == 'minimal':
            topo = topology_generator.create_3_node_topo()

        elif args.type == 'medium':
            topo = topology_generator.create_4_node_topo()

        elif args.type == 'large':
            topo = topology_generator.create_multi_layer_topo()

        elif args.type == 'n_hops':
            if not args.hops or args.hops < 1:
                logging.error(
                    "For type `n_hops` a number of hops has to be specified using --hops <int>")
                sys.exit()(-1)

            topo = topology_generator.create_n_hop_topo(int(args.hops))

        topo.update_all_routing_tables()
        ir = topo.get_IR_representation()

        if args.dot:
            # Create and store DOT representation if CLI param was set
            dot_visit = topology.DotRepresentationVisitor(True)
            topo.apply_visitor(dot_visit)
            dot_visit.store_representation_to_file(args.dot)

        if args.out_file:
            file = args.out_file
            logging.debug("Using outfile defined via CLI: {}".format(file))
        elif conf['ir']:
            file = open(conf['ir'], mode="w+")
            logging.debug(
                "Using outfile defined in configuration file {}: {}".format(
                    conf['ir'], file
                )
            )
        else:
            logging.error(
                "Outfile is neither specified via CLI nor in configuration json")
            sys.exit()(-1)

        json.dump(ir, file, indent=4)

        logging.info("Successfully created topology")

    elif args.command == 'envgen':
        logging.info("Generate Host Enviroment")

        if args.env:
            env = args.env
            logging.debug(
                "Using CLI parameter for {} - {}".format("env", args.env))
        elif conf['env']:
            env = open(conf['env'], mode='r')
            logging.debug(
                "Using config json for {} - {}".format("env", conf['env']))
        else:
            logging.error(
                "env.json is neither specified via CLI nor in configuration json")
            sys.exit()(-1)

        if args.intermediate_representation:
            ir = args.intermediate_representation
            logging.debug(
                "Using CLI parameter for {} - {}".format("ir", args.intermediate_representation))
        elif conf['ir']:
            ir = open(conf['ir'], mode='r')
            logging.debug(
                "Using config json for {} - {}".format("ir", conf['ir']))
        else:
            logging.error(
                "ir.json is neither specified via CLI nor in configuration json")
            sys.exit()(-1)

        if args.out_file:
            file = args.out_file
            logging.debug(
                "Using CLI parameter for {} - {}".format("outfile", args.out_file))
        elif conf['host']:
            file = open(conf['host'], mode='w')
            logging.debug(
                "Using config json for {} - {}".format("outfile", conf['host']))
        else:
            logging.error(
                "Outfile is neither specified via CLI nor in configuration json")
            sys.exit()(-1)

        if args.target:
            target = args.target
            logging.debug(
                "Using CLI parameter for {} - {}".format("target", args.target))
        elif conf['target']:
            target = conf['target']
            logging.debug(
                "Using config json for {} - {}".format("target", conf['target']))
        else:
            logging.error(
                "Target is neither specified via CLI nor in configuration json")
            sys.exit()(-1)

        if target == 'bmv2':
            topo_controller = TopologyController(env, ir_fd=ir)
            topo_controller.store_host_config_json(file)
            logging.info("Successfully created host configuration")
        elif target == 'tofino':
            # TODO
            logging.error("`{}` Is not yet implemented".format(target))
        else:
            logging.error("`{}` Is not a supported Target".format(target))

    elif args.command == 'deploy':
        logging.info("Deploy stage")

        if args.env:
            env = args.env
            logging.info(
                "Using CLI parameter for {} - {}".format("env", args.env))
        elif conf['env']:
            env = open(conf['env'], mode='r')
            logging.info(
                "Using config json for {} - {}".format("env", conf['env']))
        else:
            logging.error(
                "env.json is neither specified via CLI nor in configuration json")
            sys.exit()(-1)

        if args.intermediate_representation:
            ir = args.intermediate_representation
            logging.info(
                "Using CLI parameter for {} - {}".format("ir", args.intermediate_representation))
        elif conf['ir']:
            ir = open(conf['ir'], mode='r')
            logging.info(
                "Using config json for {} - {}".format("ir", conf['ir']))
        else:
            logging.error(
                "ir.json is neither specified via CLI nor in configuration json")
            sys.exit()(-1)

        if args.target:
            target = args.target
            logging.info(
                "Using CLI parameter for {} - {}".format("target", args.target))
        elif conf['target']:
            target = conf['target']
            logging.info(
                "Using config json for {} - {}".format("target", conf['target']))
        else:
            logging.error(
                "Target is neither specified via CLI nor in configuration json")
            sys.exit()(-1)

        if args.hostname:
            hostname = args.hostname
            logging.info(
                "Using CLI parameter for {} - {}".format("hostname", args.hostname))
        elif conf['hostname']:
            hostname = conf['hostname']
            logging.info(
                "Using config json for {} - {}".format("hostname", conf['hostname']))
        else:
            logging.error(
                "hostname is neither specified via CLI nor in configuration json")
            sys.exit()(-1)

        if args.port:
            port = args.port
            logging.info(
                "Using CLI parameter for {} - {}".format("port", args.port))
        elif conf['port']:
            port = conf['port']
            logging.info(
                "Using config json for {} - {}".format("port", conf['port']))
        else:
            logging.error(
                "port is neither specified via CLI nor in configuration json")
            sys.exit()(-1)

        if args.p4info:
            p4info = args.p4info
            logging.info(
                "Using CLI parameter for {} - {}".format("p4info", args.p4info))
        elif conf['p4info']:
            p4info = conf['p4info']
            logging.info(
                "Using config json for {} - {}".format("p4info", conf['p4info']))
        else:
            logging.error(
                "p4info is neither specified via CLI nor in configuration json")
            sys.exit()(-1)

        if args.p4binary:
            p4binary = args.p4binary
            logging.info(
                "Using CLI parameter for {} - {}".format("p4binary", args.p4binary))
        elif conf['p4binary']:
            p4binary = conf['p4binary']
            logging.info(
                "Using config json for {} - {}".format("p4binary", conf['p4binary']))
        else:
            logging.error(
                "p4binary is neither specified via CLI nor in configuration json")
            sys.exit()(-1)

        topo_controller = TopologyController(env, ir_fd=ir)

        connector = target_configurator.TargetConnector(
            hostname,
            port,
            p4info_path=p4info,
            p4binary_path=p4binary
        )

        topo_controller.deploy(connector)


if __name__ == '__main__':
    main()
