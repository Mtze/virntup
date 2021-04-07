import ipaddress
from abc import abstractmethod, ABC
import logging

ADDRESS_SPACE = ipaddress.IPv4Network("10.42.0.0/16")
SUBNET_PREFIX = 24


class V_topology:
    """V_topology. Container-Class for a virutal topology.
    This class holds the root router and can be used to apply vsitors of type
    `AbstractPreOderVTopologyVisitor` to walk the topology tree.
    """

    _next_subnet = 0
    available_subnets = list(ADDRESS_SPACE.subnets(new_prefix=SUBNET_PREFIX))

    def __init__(self, router):

        assert isinstance(router, vRouter)
        self.router = router
        logging.info("V_topology initialized")

        logging.info("Using " + str(len(V_topology.available_subnets)) +
                     " /" + str(SUBNET_PREFIX) + " subnets in " + str(ADDRESS_SPACE))

    def get_next_free_subnet(node):
        V_topology._next_subnet += 1
        logging.info("Assigned  " +
                     str(V_topology.available_subnets[V_topology._next_subnet - 1]) +
                     " to " + str(node)
                     )
        return V_topology.available_subnets[V_topology._next_subnet - 1]

    def set_root_router(self, router):
        """set_root_router.

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

        Parameters
        ----------
        visitor :
            AbstractVTopologyVisitor
        """
        self.router.accept(visitor)


class _Node(ABC):
    """_Node.
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
    def accept(self, visitor):
        """accept.
        Abstract implementation which ensures that all _Node classes impement
        the visitor pattern.

        Parameters
        ----------
        visitor :
            AbstractVTopologyVisitor - Visitor to be applyed on the Node
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
            AbstractVTopologyVisitor - Visitor to be applyed on the Node
        """
        if isinstance(visitor, AbstractPreOderVTopologyVisitor):
            visitor.visit_vRouter(self)

        for n in self.neighours:
            n.accept(visitor)

        if isinstance(visitor, AbstractPostOrderVTopologyVisitor):
            visitor.visit_vRouter(self)

    def get_dot_representation(self):
        r = ""
        for n in self.neighours:
            r += str(self.id) + " -- " + str(n.id) + "\n"
        return r

    def set_routing_table(self):
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

        logging.info("Updated Routingtable")
        logging.debug(str(self) + " has new routing table: " + str(self.routingtable))


class Host(_Node):
    """Host.
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
            AbstractVTopologyVisitor - Visitor to be applyed on the Node
        """
        visitor.visit_Host(self)

    def get_dot_representation(self):
        return str(self.id) + "[shape=box]\n"

    def set_routing_table(self):
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
    pass


class AbstractPostOrderVTopologyVisitor(AbstractVTopologyVisitor):
    pass


class UpdateRoutingTableVisitor(AbstractPostOrderVTopologyVisitor):

    def visit_vRouter(self, vRouter):
        vRouter.set_routing_table()

    def visit_Host(self, host):
        host.set_routing_table()

class PostOrderPrintNodeVisitor(AbstractPostOrderVTopologyVisitor):
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
    """PrintNodesVisitor.
    """

    def __init__(self):
        self.prefix = "graph graphname {\n"
        self.node_rep = ""
        self.suffix = "}"

    def get_representation(self):
        return self.prefix + self.node_rep + self.suffix

    def visit_vRouter(self, vRouter):
        """visit_vRouter.

        Parameters
        ----------
        vRouter :
            vRouter
        """
        self.node_rep += vRouter.get_dot_representation()

    def visit_Host(self, host):
        """visit_Host.

        Parameters
        ----------
        host :
            host
        """
        self.node_rep += host.get_dot_representation()
