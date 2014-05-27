# -*- coding: utf-8 -*-

"""Check that iterating over coordinates is always made in the most efficient
way
"""

from pycraft import iterator
import logging
import unittest


class IteratorTest(unittest.TestCase):

    def test_complete(self):
        """Iterate over all positions of 4 files, and check that :
        - a file is opened only once
        - a chunk is loaded only once
        - all positions are covered
        - no position is covered twice
        """
        nid = (-10, 2, -2)
        but = (520, 256, 538)

        chunks = list()
        regions = list()
        points = dict()

        expected_points = (but[0] - nid[0]) * (but[1] - nid[1]) * (but[2] - nid[2])
        nb_points = 0

        for x, y, z in iterator.iterate(nid, but):
            # Valid position
            self.assertTrue(nid[0] <= x < but[0])
            self.assertTrue(nid[1] <= y < but[1])
            self.assertTrue(nid[2] <= z < but[2])

            # Regions (or files)
            rx, rz = x >> 9, z >> 9
            if len(regions) == 0 or regions[-1] != (rx, rz):
                regions.append((rx, rz))
                logging.debug("New region : {}".format(regions[-1]))
                self.assertEqual(1, regions.count(regions[-1]))

            # Chunks
            cx, cy, cz = x >> 4, y >> 5, z >> 4
            if len(chunks) == 0 or chunks[-1] != (cx, cy, cz):
                nb_points += len(points)
                points.clear()

                chunks.append((cx, cy, cz))
                logging.debug("New chunk : {}".format(chunks[-1]))
                self.assertEqual(1, chunks.count(chunks[-1]))

            # New position in chunk
            self.assertTrue((x, y, z) not in points)
            points[(x, y, z)] = 1

        nb_points += len(points)
        self.assertEqual(expected_points, nb_points)



if __name__ == "__main__":
    logging.basicConfig(level = logging.WARNING)
    unittest.main()
