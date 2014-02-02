"""Check that reading and writing the classic 'bigtest.nbt' file is OK
"""

import unittest
from pycraft import con


class BigTest(unittest.TestCase):

    def test_complete(self):
        with open("bigtest.nbt", "rb") as input_file:
            with open("bigtest.out", "wb") as output_file:
                (K, N, V) = con.Reader.load(input_file)

                #print(V.pretty(N))

                con.Writer.save(output_file, K, N, V)

            input_file.seek(0, 0)
            with open("bigtest.out", "rb") as output_file:
                expected = input_file.read()
                produced = output_file.read()
                self.assertEqual(expected, produced)



if __name__ == "__main__":
    unittest.main()
