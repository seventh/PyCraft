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

    def test_addition(self):
        p = geometry.Triple(1, 3, 2)
        q = geometry.Triple(-2, -6, -4)
        r = p + q
        self.assertEqual(1, p.x)
        self.assertEqual(3, p.y)
        self.assertEqual(2, p.z)
        self.assertEqual(-2, q.x)
        self.assertEqual(-6, q.y)
        self.assertEqual(-4, q.z)
        self.assertEqual(-1, r.x)
        self.assertEqual(-3, r.y)
        self.assertEqual(-2, r.z)

        p += q
        self.assertEqual(-2, q.x)
        self.assertEqual(-6, q.y)
        self.assertEqual(-4, q.z)
        self.assertEqual(-1, p.x)
        self.assertEqual(-3, p.y)
        self.assertEqual(-2, p.z)

    def test_difference(self):
        p = geometry.Triple(1, 3, 2)
        q = geometry.Triple(2, 6, 4)
        r = p - q
        self.assertEqual(1, p.x)
        self.assertEqual(3, p.y)
        self.assertEqual(2, p.z)
        self.assertEqual(2, q.x)
        self.assertEqual(6, q.y)
        self.assertEqual(4, q.z)
        self.assertEqual(-1, r.x)
        self.assertEqual(-3, r.y)
        self.assertEqual(-2, r.z)

        p -= q
        self.assertEqual(2, q.x)
        self.assertEqual(6, q.y)
        self.assertEqual(4, q.z)
        self.assertEqual(-1, p.x)
        self.assertEqual(-3, p.y)
        self.assertEqual(-2, p.z)

    def test_multiplication(self):
        p = geometry.Triple(12, -2345, 16)
        q = 3 * p
        self.assertEqual(3 * p.x, q.x)
        self.assertEqual(3 * p.y, q.y)
        self.assertEqual(3 * p.z, q.z)

        r = p * 3
        self.assertEqual(q.x, r.x)
        self.assertEqual(q.y, r.y)
        self.assertEqual(q.z, r.z)

        p *= 3
        self.assertEqual(q.x, p.x)
        self.assertEqual(q.y, p.y)
        self.assertEqual(q.z, p.z)

    def test_negation(self):
        p = geometry.Triple(12, -2345, 16)
        q = -p
        self.assertEqual(12, p.x)
        self.assertEqual(-2345, p.y)
        self.assertEqual(16, p.z)
        self.assertEqual(-12, q.x)
        self.assertEqual(2345, q.y)
        self.assertEqual(-16, q.z)


if __name__ == "__main__":
    unittest.main()
