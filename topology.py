import ipaddress
from abc import ABCMeta, abstractmethod, ABC
import logging


class V_topology:
    """V_topology.
    """

    def __init__(self, router=None):
        """__init__.
        """
        assert isinstance(router, vRouter)
        self.router = router
        logging.info("V_topology initialized")

    def set_root_router(self, router):
        """add_router.

        Parameters
        ----------
        router :
            router
        """
        assert isinstance(router, vRouter)
        self.router = router
        logging.info("Router " + str(router) + " is new root router")
    
    def apply_visitor(self, visitor):
        self.router.accept(visitor)

class _Node(ABC):
    """_Node.
    """

    def __init__(self, name):
        self.name = name

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

    def __init__(self, name="vRouter"):
        """__init__.

        Parameters
        ----------
        ports :
            List of LogicalPorts attached to the vRouter
        """
        super().__init__(name)

        self.id = vRouter.next_id
        vRouter.next_id += 1

        self.neighours = []

    def add_link(self, other_node):
        self.neighours.append(other_node)

    def accept(self, visitor):
        """accept.

        Parameters
        ----------
        visitor :
            AbstractVTopologyVisitor - Visitor to be applyed on the Node
        """
        visitor.visit_vRouter(self)
        for n in self.neighours:
            n.accept(visitor)


class Host(_Node):
    """Host.
    """

    next_id = 1

    def __init__(self, name="Host"):
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

    def accept(self, visitor):
        """accept.

        Parameters
        ----------
        visitor :
            AbstractVTopologyVisitor - Visitor to be applyed on the Node
        """
        visitor.visit_Host(self)


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
