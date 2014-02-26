# -*- coding: utf-8 -*-

"""Check the behavior of entity wrappers
"""

import unittest
from pycraft import geometry

class Triple(unittest.TestCase):

    def test_str(self):
        triple = (0, 2, -1)
        point = geometry.Triple(*triple)

        self.assertEqual(str(triple), str(point))


    def test_unpack(self):
        point = geometry.Triple(2, -7, 11)
        x, y, z = point
        self.assertEqual(point.x, x)
        self.assertEqual(point.y, y)
        self.assertEqual(point.z, z)


    def test_update_x(self):
        point = geometry.Triple(2, -5, 11)
        point.x += 3
        self.assertEqual(5, point.x)



if __name__ == "__main__":
    unittest.main()
