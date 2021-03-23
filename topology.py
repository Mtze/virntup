import ipaddress
from abc import ABCMeta, abstractmethod, ABC
import logging


class V_topology:
    """V_topology.
    """

    def __init__(self):
        """__init__.
        """
        self.hosts = []
        self.routers = []
        logging.info("V_topology initialized")

    def add_router(self, router):
        """add_router.

        Parameters
        ----------
        router :
            router
        """
        assert isinstance(router, vRouter)
        self.routers.append(router)
        logging.info("Added router " + str(router) + " to topology")

    def add_host(self, host):
        """add_host.

        Parameters
        ----------
        host :
            host
        """
        self.hosts.append(host)
        logging.info("Added host " + str(host) + " to topology")

    def create_link(self, port1, port2):
        link = Link([port1, port2])
        port1.set_Link(link)
        port2.set_Link(link)
        logging.info("Added link " + str(link) + " to topology")


class Link:
    """Link.
    """

    next_id = 1

    def __init__(self, ports):
        """ Link constructor

        Parameters
        ----------
        ports
            List of exactly two ports which should be connected.
        """
        if None in ports:
            raise Exception("Port must not be None")

        if len(ports) != 2:
            raise Exception("A link must have exactly 2 ports")

        self.ports = ports
        self.id = Link.next_id
        Link.next_id += 1

    def getOtherNode(self, node):
        logging.debug(str(self.id) + " - call get other link with node" + str(node))
        assert node is not None
        assert None not in self.ports

        if self.ports[0].node.id == node.id:
            return self.ports[1].node
        elif self.ports[1].id == node.id:
            return self.ports[0].node
        else:
            raise Exception("No other node present")

    def __str__(self):
        """__str__.
        """
        return str(self.ports[0]) + "<-"+ str(self.id) +"->" + str(self.ports[1])


class _Node(ABC):
    """_Node.
    """
    
    def __init__(self, name):
        self.name = name
        self.visited = False

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

    next_id = 1

    def __init__(self, ports, name="vRouter"):
        """__init__.

        Parameters
        ----------
        ports :
            List of LogicalPorts attached to the vRouter
        """
        super().__init__(name)

        self.id = vRouter.next_id
        vRouter.next_id += 1
        self.ports=[]
        for p in ports:
            self.add_port(p)

    def add_port(self, port):
        """addPort.

        Parameters
        ----------
        port :
            LogicalPort - The Logical Port which should be added to the vRouter
        """
        self.ports.append(port)
        port.node = self

    def accept(self, visitor):
        """accept.

        Parameters
        ----------
        visitor :
            AbstractVTopologyVisitor - Visitor to be applyed on the Node
        """
        if self.visited:
            return 
        self.visited = True
        visitor.visit_vRouter(self)
        for port in self.ports:
            port.link.getOtherNode(self).accept(visitor)


class Host(_Node):
    """Host.
    """

    next_id = 1

    def __init__(self, port=None, name="Host"):
        """__init__.

        Parameters
        ----------
        port :
            LogicalPort - The Logical Port which should be assigned to the Host
        name :
            String - Hostname
        """
        super().__init__(name)

        self.id = Host.next_id
        Host.next_id += 1

        self.set_Port(port)

    def set_Port(self, port):
        """setPort.

        Parameters
        ----------
        port :
            LogicalPort - The Logical Port which should be assigned to the Host
        """
        self.port = port
        port.node = self

    def accept(self, visitor):
        """accept.

        Parameters
        ----------
        visitor :
            AbstractVTopologyVisitor - Visitor to be applyed on the Node
        """
        visitor.visit_Host(self)


class LogicalPort():
    """LogicalPort.
    """
    next_id = 1

    def __init__(self, node=None, link=None, ipv4Address=None):
        """__init__.

        Parameters
        ----------
        node :
            node
        ipv4Address :
            ipv4Address
        """
        self.node = node
        self.pv4Adress = ipv4Address
        self.link = link

        self.id = LogicalPort.next_id
        LogicalPort.next_id += 1

    def set_Link(self, link):
        self.link = link
        link.ports.append(self)
        logging.debug(str(self.id) + "Set link to " + str(link))

    def __str__(self):
        return str(self.node)


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


class PrintNodesVisitor(AbstractVTopologyVisitor):
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
