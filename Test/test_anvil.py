# -*- coding: utf-8 -*-

"""Verify the behaviour of the pycraft 'con' package.
"""

import io
import os
import unittest

from pycraft import anvil


class ReadWrite(unittest.TestCase):

    def test_metadata(self):
        """Verify Metadata helper class correct behaviour
        """
        meta = anvil.Metadata(2 ** 32 - 1, 2 ** 32 - 1)

        for offset in range(2, 18):
            for length in range(16):
                for timestamp in range(2 ** 31, 2 ** 31 + 16):
                    meta.offset = offset
                    meta.length = length
                    meta.timestamp = timestamp

                    self.assertEqual(offset, meta.offset)
                    self.assertEqual(length, meta.length)
                    self.assertEqual(timestamp, meta.timestamp)

    def test_rewrite_file(self):
        """Check that reading and writing back an original NBT file is
        innocuous
        """
        r_input = self.create_temporary_file("anvil.mca")
        r_output = anvil.open(io.BytesIO())

        for index in r_input.indexes():
            chunk = r_input.load_chunk(index)
            r_output.save_chunk(index, chunk)

        self.assertEqual(set(r_input.indexes()), set(r_output.indexes()))

        for index in r_input.indexes():
            i_chunk = r_input.load_chunk(index)
            o_chunk = r_output.load_chunk(index)
            self.assertEqual(i_chunk, o_chunk)

    def test_new_file(self):
        """Check that writing a completely new file is working
        """
        path = "output.mca"
        value = 1234567890

        # First, create file
        r_output = anvil.open(path)
        indexes = set()

        for index in range(0, anvil._NB_OF_ENTRIES, 3):
            r_output.save_chunk(index, value % (index + 2))
            indexes.add(index)

        self.assertEqual(indexes, set(r_output.indexes()))

        del r_output

        # Then, read it back and check its content
        r_input = anvil.open(path)

        self.assertEqual(indexes, set(r_input.indexes()))

        for index in r_input.indexes():
            chunk = r_input.load_chunk(index)
            self.assertEqual(value % (index + 2), chunk)

        os.unlink(path)

    def test_wipe_file(self):
        """Totally wiped files shall be removed
        """
        path = "output_wipe.mca"

        # First, create file
        self.create_temporary_file(path)
        os.stat(path)

        # Then, reload file
        r_output = anvil.open(path)

        for index in r_output.indexes():
            r_output.wipe_chunk(index)

        del r_output

        # File shall have disappeared
        with self.assertRaises(OSError):
            os.stat(path)

    def create_temporary_file(self, path):
        result = anvil.open(path)

        value = 1234567890

        for index in range(0, anvil._NB_OF_ENTRIES, 3):
            result.save_chunk(index, value % (index + 2))

        return result


if __name__ == "__main__":
    unittest.main()
