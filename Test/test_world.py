# -*- coding: utf-8 -*-

"""Verify the behaviour of the pycraft 'world' package.
"""

import io
import os
import unittest

from pycraft import world


class World(unittest.TestCase):

    def test_spot(self):
        """Going through all the existing spot is functional
        """
        w = world.World("/home/seventh/.minecraft/saves/blé")
        l = w.level(0)
        c = 0
        for spot in l.spots():
            c += 1


    def test_get_block(self):
        """Retrieving of all existing blocks is functional
        """
        w = world.World("/home/seventh/.minecraft/saves/blé")
        l = w.level(0)
        for spot in l.spots():
            print(l.get_block(spot))



if __name__ == "__main__":
    unittest.main()
