"""Check the behavior of entity wrappers
"""

import unittest
from pycraft import entity

class Player(unittest.TestCase):

    def test_experience(self):
        experience_per_level = {
            0 : 0,
            1 : 17,
            2 : 34,
            3 : 51,
            4 : 68,
            5 : 85,
            6 : 102,
            7 : 119,
            8 : 136,
            9 : 153,
            10 : 170,
            11 : 187,
            12 : 204,
            13 : 221,
            14 : 238,
            15 : 255,
            16 : 272,
            17 : 292,
            18 : 315,
            19 : 341,
            20 : 370,
            21 : 402,
            22 : 437,
            23 : 475,
            24 : 516,
            25 : 560,
            26 : 607,
            27 : 657,
            28 : 710,
            29 : 766,
            30 : 825,
            31 : 887,
            32 : 956,
            33 : 1032,
            34 : 1115,
            35 : 1205,
            36 : 1302,
            37 : 1406,
            38 : 1517,
            39 : 1635,
            40 : 1760,
            }

        player = entity.Player()
        for i in experience_per_level:
            expected = experience_per_level[i]

            player.experience_level = i
            produced = player.experience

            self.assertEqual(expected, produced, "i = {}".format(i))

        with self.assertRaises(AssertionError):
            player.experience_level = -1

        with self.assertRaises(AssertionError):
            player.experience_level = 41


    def test_experience_level(self):
        experience_level_per_experience = {
            0 : 0,
            17 : 1,
            34 : 2,
            51 : 3,
            68 : 4,
            85 : 5,
            102 : 6,
            119 : 7,
            136 : 8,
            153 : 9,
            170 : 10,
            187 : 11,
            204 : 12,
            221 : 13,
            238 : 14,
            255 : 15,
            272 : 16,
            292 : 17,
            315 : 18,
            341 : 19,
            370 : 20,
            402 : 21,
            437 : 22,
            475 : 23,
            516 : 24,
            560 : 25,
            607 : 26,
            657 : 27,
            710 : 28,
            766 : 29,
            825 : 30,
            887 : 31,
            956 : 32,
            1032 : 33,
            1115 : 34,
            1205 : 35,
            1302 : 36,
            1406 : 37,
            1517 : 38,
            1635 : 39,
            1760 : 40,
            }

        player = entity.Player()
        for i in experience_level_per_experience:
            expected = experience_level_per_experience[i]

            player.experience = i
            produced = player.experience_level

            self.assertEqual(expected, produced, "i = {}".format(i))

            if i > 0:
                player.experience = i - 1
                produced = player.experience_level

                self.assertEqual(expected - 1, produced, "i = {}".format(i))

        with self.assertRaises(AssertionError):
            player.experience = -1

        with self.assertRaises(AssertionError):
            player.experience = 1761



if __name__ == "__main__":
    unittest.main()
