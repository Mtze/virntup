import ipaddress
from abc import abstractmethod, ABC
import logging


"""
The ADDRESS_SPACE variable holds the IP Address space used for topology
generation. The Each _Node gets a  portion from this ADDRESS_SPACE
during initialization.
"""
ADDRESS_SPACE = ipaddress.IPv4Network("10.42.0.0/16")

"""
The SUBNET_PREFIX allows to configure the desired network size each _Node
gets assinged during initialization.
"""
SUBNET_PREFIX = 24


class V_topology:
    """V_topology. Container-Class for a virtual topology.
    This class holds the root router and can be used to apply visitors of type
    `AbstractPreOderVTopologyVisitor` to walk the topology tree.
    """

    _next_subnet = 0
    available_subnets = list(ADDRESS_SPACE.subnets(new_prefix=SUBNET_PREFIX))

    def __init__(self, router):
        """__init__.

        Parameters
        ----------
        router :
            router
        """

        assert isinstance(router, vRouter)
        self.router = router
        logging.info("V_topology initialized")

        logging.info("Using " + str(len(V_topology.available_subnets)) +
                     " /" + str(SUBNET_PREFIX) + " subnets in " + str(ADDRESS_SPACE))

    def get_next_free_subnet(node):
        """get_next_free_subnet.

        This class-method manages the sub-net assignment.

        Parameters
        ----------
        node :
            node

        Returns:
        ---------
        IPv4Network : An Network inside of ADDRESS_SPACE of size SUBNET_PREFIX
        """

        V_topology._next_subnet += 1
        logging.info("Assigned  " +
                     str(V_topology.available_subnets[V_topology._next_subnet - 1]) +
                     " to " + str(node)
                     )
        return V_topology.available_subnets[V_topology._next_subnet - 1]

    def set_root_router(self, router):
        """set_root_router.

        This method allows to set the root vRouter of the topology.
        Only necessary if the topology was initialized without a vRouter.

        Parameters
        ----------
        router :
            vRouter
        """
        assert isinstance(router, vRouter)
        self.router = router
        logging.info("Router " + str(router) + " is new root router")

    def apply_visitor(self, visitor):
        """apply_visitor.

        This meta-function applies a AbstractVTopologyVisitor to the topology.
        The visitor has to be a subclass of AbstractVTopologyVisitor!

        Parameters
        ----------
        visitor :
            AbstractVTopologyVisitor
        """
        self.router.accept(visitor)

    def update_all_routing_tables(self):
        """update_all_routing_tables.

        After a topology was generated (or updated) the routing-tables of each
        _Node have to be updated. This method updates all routing-tales of all
        _Nodes in the topology.

        """
        rt_visitor = UpdateRoutingTableVisitor()
        self.apply_visitor(rt_visitor)

    def get_IR_representation(self):
        """get_IR_representation.

        This method return the Intermediate Representation of the topology as a
        dict with the following structure:

        ```
        {
            "vRouter": {
                "1": {
                    "name" : "example",
                    "uplink_network" : "10.0.0.0/24",
                    "neighbour": [
                        [0,"5"]         #  [Port, Neighbor _Node.id]
                    ],
                    "routing_table" : [
                        [0,"10.0.1.0/24"],
                        [1,"10.0.2.0/24"]
                    ]
                },
                ...
            },
            "Host" : {
                "5" :{
                    "name" : "string",
                    "uplink_network" : "10.0.5.0/24",
                },
                ...
            }
        }
        ```
        """
        ir_visit = IntermediateRepresentationVisitor()
        self.apply_visitor(ir_visit)
        return ir_visit.builder


class _Node(ABC):
    """_Node.

    Abstract _Node implementation. This class specifies how a topology node has
    to look like. This class must not be initialized!
    """
    next_id = 1

    def __init__(self, name):
        """__init__.

        Parameters
        ----------
        name :
            string
        """
        self.name = name
        self.uplink_network = V_topology.get_next_free_subnet(self)
        self.ipv4Adress = self.uplink_network.network_address + 1
        self.routingtable = []

    @abstractmethod
    def get_IR_representation(self, dict_builder):
        """get_IR_representation.

        Generates the IR of the _Node and inserts it into the IR builder
        dict.

        Parameters
        ----------
        dict_builder :
            dict of dicts, with structure: `{"vRouter": {}, "Host":{}}`
        """

        raise NotImplementedError("This is an abstract class")

    @abstractmethod
    def accept(self, visitor):
        """accept.
        Abstract implementation which ensures that all _Node classes implement
        the visitor pattern.

        Parameters
        ----------
        visitor :
            AbstractVTopologyVisitor - Visitor to be applied  on the Node
        """
        raise NotImplementedError("This is an abstract class")

    def __str__(self):
        """__str__.
        """
        return "(" + self.name + "_" + str(self.id) + ")"


class vRouter(_Node):
    """vRouter.
    """

    def __init__(self, name="vRouter"):
        """__init__.

        Parameters
        ----------
        name :
            name
        """

        self.id = _Node.next_id
        _Node.next_id += 1
        self.neighours = []
        super().__init__(name)

    def add_link(self, other_node):
        """add_link.

        Parameters
        ----------
        other_node :
            _Node (So either vRouter or Host)
        """
        self.neighours.append(other_node)

    def accept(self, visitor):
        """accept.

        Parameters
        ----------
        visitor :
            AbstractVTopologyVisitor - Visitor to be applied on the Node
        """
        if isinstance(visitor, AbstractPreOderVTopologyVisitor):
            visitor.visit_vRouter(self)

        for n in self.neighours:
            n.accept(visitor)

        if isinstance(visitor, AbstractPostOrderVTopologyVisitor):
            visitor.visit_vRouter(self)

    def get_dot_representation(self, with_routingtable=False):
        """get_dot_representation.

        Parameters
        ----------
        with_routingtable :
            Bool (default: False) - Specifies if the dot representation should
            contain the routing table
        """
        edges = ""
        for n in self.neighours:
            edges += str(self.id) + " -- " + str(n.id) + "\n"

        router_box = ""
        if with_routingtable:
            router_box = str(self.id) + "[\nlabel = \"{" + str(self.id)
            for route in self.routingtable:
                router_box += "|" + str(route)
            router_box += "}\" \nshape=\"record\"]\n"
        else:
            router_box += str(self.id) + "[shape=box]\n"

        return router_box + edges

    def get_IR_representation(self, dict_builder):
        """get_IR_representation.

        Generates the IR of the _Node and inserts it into the IR builder
        dict.

        Parameters
        ----------
        dict_builder :
            dict of dicts, with structure: `{"vRouter": {}, "Host":{}}`
        """
        logging.debug("Create IR representation of " +
                      self.name + " " + str(self.id))
        ir = {
            "name": self.name,
            "uplink_network": str(self.uplink_network),
            "neighours": [[x, str(self.neighours[x].id)] for x in range(len(self.neighours))],
            "routingtable": [[x, str(self.routingtable[x][1].compressed)] for x in range(len(self.routingtable))]
            # "routingtable" : str(self.routingtable)
        }
        logging.debug(str(ir))
        dict_builder["vRouter"][str(self.id)] = ir

    def set_routing_table(self):
        """set_routing_table.
        """
        for i in range(len(self.neighours)):

            # Store the current neighbour in a varaible for easy access
            current_node = self.neighours[i]

            # Iterate over the routing table of the current node and add
            # all Networks to our routingtable with corresponding egress
            # port.
            for table_entry in current_node.routingtable:
                self.routingtable.append((i, table_entry[1]))

            # Finally add route to shared network between us and current node
            self.routingtable.append((i, current_node.uplink_network))

        logging.info("Updated routing table")
        logging.debug(str(self) + " has new routing table: " +
                      str(self.routingtable))


class Host(_Node):
    """Host.

    This class represents a Host in a topology. A host is always a
    leaf _Node.
    """

    def __init__(self, name="Host"):
        """__init__.

        Parameters
        ----------
        name :
            string - hostname of the Host
        """

        self.id = _Node.next_id
        _Node.next_id += 1

        super().__init__(name)

    def accept(self, visitor):
        """accept.

        Parameters
        ----------
        visitor :
            AbstractVTopologyVisitor - Visitor to be applied on the Node
        """
        visitor.visit_Host(self)

    def get_IR_representation(self, dict_builder):
        """get_IR_representation.

        Generates the IR of the _Node and inserts it into the IR builder
        dict.

        Parameters
        ----------
        dict_builder :
            dict of dicts, with structure: `{"vRouter": {}, "Host":{}}`

        """
        ir = {
            "name": self.name,
            "uplink_network": str(self.uplink_network),
        }
        dict_builder["Host"][str(self.id)] = ir

    def get_dot_representation(self):
        """get_dot_representation.
        """
        return str(self.id) + "\n"

    def set_routing_table(self):
        """set_routing_table.
        """
        self.routingtable = []


class AbstractVTopologyVisitor(ABC):
    """AbstractVTopologyVisitor.
    """

    @ abstractmethod
    def visit_vRouter(self, vRouter):
        """visit_vRouter.

        Parameters
        ----------
        vRouter :
            vRouter
        """
        raise NotImplementedError("")

    @ abstractmethod
    def visit_Host(self, host):
        """visit_Host.

        Parameters
        ----------
        host :
            host
        """
        raise NotImplementedError("")


class AbstractPreOderVTopologyVisitor(AbstractVTopologyVisitor):
    """AbstractPreOderVTopologyVisitor.

    This is just a meta class to distinguish between Pre and Post order
    visitors. Should not be instantiated.
    """

    pass


class AbstractPostOrderVTopologyVisitor(AbstractVTopologyVisitor):
    """AbstractPostOrderVTopologyVisitor.

    This is just a meta class to distinguish between Pre and Post order
    visitors. Should not be instantiated.
    """

    pass


class UpdateRoutingTableVisitor(AbstractPostOrderVTopologyVisitor):
    """UpdateRoutingTableVisitor.

    This visitor updates the routing table in each _Node in a post-order
    fashion. This is important as each parent _Node routing table depends
    on the routing tables of the child nodes.

    This routing approach assumes that each _Node (except the root _Node)
    has a default route pointing  to the parent. This route is **not**
    added by this algorithm!
    """

    def visit_vRouter(self, vRouter):
        """visit_vRouter.

        Parameters
        ----------
        vRouter :
            vRouter
        """
        vRouter.set_routing_table()

    def visit_Host(self, host):
        """visit_Host.

        Parameters
        ----------
        host :
            Host
        """
        host.set_routing_table()


class PostOrderPrintNodeVisitor(AbstractPostOrderVTopologyVisitor):
    """PostOrderPrintNodeVisitor.
    """

    def visit_vRouter(self, vRouter):
        """visit_vRouter.

        Parameters
        ----------
        vRouter :
            vRouter
        """
        print(vRouter)

    def visit_Host(self, host):
        """visit_Host.

        Parameters
        ----------
        host :
            host
        """
        print(host)


class PreOderPrintNodesVisitor(AbstractPreOderVTopologyVisitor):
    """PrintNodesVisitor.
    """

    def visit_vRouter(self, vRouter):
        """visit_vRouter.

        Parameters
        ----------
        vRouter :
            vRouter
        """
        print(vRouter)

    def visit_Host(self, host):
        """visit_Host.

        Parameters
        ----------
        host :
            host
        """
        print(host)


class DotRepresentationVisitor(AbstractPreOderVTopologyVisitor):
    """DotRepresentationVisitor.

    This Pre-Order Visitor assembles a [DOT](https://graphviz.org/doc/info/lang.html)
    compatible representation of the topology.

    It can be specified if the visualization should also contain the routing table. 
    This is switched of by default as it gets quite messy for big topologies.

    After the visitor was applied to the topology, the results can be obtained
    by calling the `get_representation()` method.
    """

    def __init__(self, with_routingtable=False):
        """__init__.

        Parameters
        ----------
        with_routingtable :
            Bool (default: False) - Specifies if the dot representation should
            contain the routing table
        """
        self.prefix = "graph graphname {\n"
        self.node_rep = ""
        self.suffix = "}"
        self.with_routingtable = with_routingtable

    def get_representation(self):
        """get_representation.
        """
        return self.prefix + self.node_rep + self.suffix

    def visit_vRouter(self, vRouter):
        """visit_vRouter.

        Parameters
        ----------
        vRouter :
            vRouter
        """
        self.node_rep += vRouter.get_dot_representation(self.with_routingtable)

    def visit_Host(self, host):
        """visit_Host.

        Parameters
        ----------
        host :
            host
        """
        self.node_rep += host.get_dot_representation()


class IntermediateRepresentationVisitor(AbstractPreOderVTopologyVisitor):
    """IntermediateRepresentationVisitor

    This visitor walks the toplogy and gathers the IR of each _Node 
    in a builder dict. For the structure of the builder see the 
    `toplogly.get_IR_representation()` method. 
    """

    def __init__(self):
        """__init__.
        """
        self.builder = {"vRouter": {}, "Host": {}}

    def visit_vRouter(self, vRouter):
        """visit_vRouter.

        Parameters
        ----------
        vRouter :
            vRouter
        """
        vRouter.get_IR_representation(self.builder)

    def visit_Host(self, host):
        """visit_Host.

        Parameters
        ----------
        host :
            host
        """
        host.get_IR_representation(self.builder)
