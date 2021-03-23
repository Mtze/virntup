import ipaddress
from abc import ABCMeta, abstractmethod, ABC
import logging


class V_topology:
    """V_topology. Container-Class for a virutal topology. 
    This class holds the root router and can be used to apply vsitors of type
    `AbstractVTopologyVisitor` to walk the topology tree. 
    """

    def __init__(self, router):
        """__init__.
        """
        assert isinstance(router, vRouter)
        self.router = router
        logging.info("V_topology initialized")

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

    def __init__(self, name):
        """__init__.

        Parameters
        ----------
        name :
            string
        """
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
        name :
            name
        """
        super().__init__(name)

        self.id = vRouter.next_id
        vRouter.next_id += 1

        self.neighours = []

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
        name :
            string - hostname of the Host
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
