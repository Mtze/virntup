import topology
import logging
import unittest

#logging.basicConfig(level=logging.INFO)


def reset_topo_id_counter():
    topology._Node.next_id = 1


def create_3_node_topo():
    reset_topo_id_counter()

    root = topology.vRouter()
    topo = topology.V_topology(root)

    root.add_link(topology.Host())
    root.add_link(topology.Host())

    return topo


def create_multi_layer_topo():
    reset_topo_id_counter()

    root = topology.vRouter()
    topo = topology.V_topology(root)

    for i in range(3):
        l1 = topology.vRouter()
        root.add_link(l1)
        for j in range(3):
            l2 = topology.vRouter()
            l1.add_link(l2)
            for j in range(2):
                l2.add_link(topology.Host())
    return topo

###########################################################
class TestVRouter(unittest.TestCase):
    pass


###########################################################
class TestDotRepresentationVisitor(unittest.TestCase):

    def test_3_node_topo(self):
        expected =r"""graph graphname {
1 -- 2
1 -- 3
2[shape=box]
3[shape=box]
}"""
        dot_v = topology.DotRepresentationVisitor()

        topo = create_3_node_topo()
        topo.apply_visitor(dot_v)

        actual = dot_v.get_representation()
        self.assertMultiLineEqual(actual, expected)

    def test_multi_layer_topo(self):
        expected = r"""graph graphname {
1 -- 2
1 -- 12
1 -- 22
2 -- 3
2 -- 6
2 -- 9
3 -- 4
3 -- 5
4[shape=box]
5[shape=box]
6 -- 7
6 -- 8
7[shape=box]
8[shape=box]
9 -- 10
9 -- 11
10[shape=box]
11[shape=box]
12 -- 13
12 -- 16
12 -- 19
13 -- 14
13 -- 15
14[shape=box]
15[shape=box]
16 -- 17
16 -- 18
17[shape=box]
18[shape=box]
19 -- 20
19 -- 21
20[shape=box]
21[shape=box]
22 -- 23
22 -- 26
22 -- 29
23 -- 24
23 -- 25
24[shape=box]
25[shape=box]
26 -- 27
26 -- 28
27[shape=box]
28[shape=box]
29 -- 30
29 -- 31
30[shape=box]
31[shape=box]
}"""

        topo = create_multi_layer_topo()
        dot_v = topology.DotRepresentationVisitor()
        topo.apply_visitor(dot_v)

        actual = dot_v.get_representation()

        self.assertMultiLineEqual(actual, expected)


################################################
if __name__ == '__main__':
    unittest.main()
