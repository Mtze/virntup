import logging
import unittest
import topology
from topology_generator import create_multi_layer_topo, create_3_node_topo

logging.basicConfig(level=logging.INFO)


###########################################################
class TestVRouter(unittest.TestCase):
    """TestVRouter.
    """


###########################################################
class TestDotRepresentationVisitor(unittest.TestCase):
    """TestDotRepresentationVisitor.
    """

    def test_3_node_topo(self):
        """test_3_node_topo.
        """
        expected = r"""graph graphname {
1[shape=box]
1 -- 2
1 -- 3
2
3
}"""
        dot_v = topology.DotRepresentationVisitor()

        topo = create_3_node_topo()
        topo.update_all_routing_tables()
        topo.apply_visitor(dot_v)

        actual = dot_v.get_representation()
        self.assertMultiLineEqual(actual, expected)

    def test_multi_layer_topo(self):
        """test_multi_layer_topo.
        """
        expected = r"""graph graphname {
1[shape=box]
1 -- 2
1 -- 12
1 -- 22
2[shape=box]
2 -- 3
2 -- 6
2 -- 9
3[shape=box]
3 -- 4
3 -- 5
4
5
6[shape=box]
6 -- 7
6 -- 8
7
8
9[shape=box]
9 -- 10
9 -- 11
10
11
12[shape=box]
12 -- 13
12 -- 16
12 -- 19
13[shape=box]
13 -- 14
13 -- 15
14
15
16[shape=box]
16 -- 17
16 -- 18
17
18
19[shape=box]
19 -- 20
19 -- 21
20
21
22[shape=box]
22 -- 23
22 -- 26
22 -- 29
23[shape=box]
23 -- 24
23 -- 25
24
25
26[shape=box]
26 -- 27
26 -- 28
27
28
29[shape=box]
29 -- 30
29 -- 31
30
31
}"""

        topo = create_multi_layer_topo()
        dot_v = topology.DotRepresentationVisitor()
        topo.apply_visitor(dot_v)

        actual = dot_v.get_representation()

        self.assertMultiLineEqual(actual, expected)


################################################
if __name__ == '__main__':
    unittest.main()
