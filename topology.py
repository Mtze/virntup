import ipaddress


class v_topology:
    def __init__(self):
        pass


class Link:
    next_id = 1

    def __init__(self, ports):
        """ Link constructor

        Parameters
        """
        self.id = Link.next_id
        if None in ports:
            raise Exception("Port must not be None")

        self.ports = ports
        Link.next_id += 1

    def __str__(self):
        return "Link: " + str(self.ports[0]) + "<-->" + str(self.ports[1])


class _Node:
    def __init__(self):
        self.id = 0
        self.name = ""

    def __str__(self):
        return "(" + self.name + " - id: " + str(self.id) + ")"


class vRouter(_Node):
    next_id = 1

    def __init__(self, ports=[]):
        super().__init__()
        self.id = vRouter.next_id
        vRouter.next_id += 1

        self.name = "vRouter"
        self.ports = ports

    def addPort(self, port):
        self.ports.add(port)


class Host(_Node):
    next_id = 1

    def __init__(self, port=None):
        super().__init__()
        self.id = Host.next_id
        Link.next_id += 1

        self.name = "Host"
        self.port = port

    def setPort(self, port):
        self.port = port


class LogicalPort():
    def __init__(self, node=None, ipv4Address=None):
        self.node = node
        self.pv4Adress = ipv4Address
