# -*- coding: utf-8 -*-

"""Verify the behaviour of the pycraft 'con' package.
"""

import io
import os
import unittest

from pycraft import region


class ReadWrite(unittest.TestCase):

    def test_metadata(self):
        """Verify ChunkMetaData helper class correct behaviour
        """
        meta = region._ChunkMetaData(2**32 - 1, 2**32 - 1)

        for offset in range(2, 18):
            for length in range(16):
                for timestamp in range(2**31, 2**31 + 16):
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
        r_input = region.open("region.mca")
        r_output = region.open(io.BytesIO())

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
        r_output = region.open(path)
        indexes = set()

        for index in range(0, region._NB_OF_ENTRIES, 3):
            r_output.save_chunk(index, value % (index + 2))
            indexes.add(index)

        self.assertEqual(indexes, set(r_output.indexes()))

        del r_output

        # Then, read it back and check its content
        r_input = region.open(path)

        self.assertEqual(indexes, set(r_input.indexes()))

        for index in r_input.indexes():
            chunk = r_input.load_chunk(index)
            self.assertEqual(value % (index + 2), chunk)

        os.unlink(path)


    def test_wipe_file(self):
        """Totally wiped files shall be removed
        """
        path = "output_wipe.mca"
        value = 1234567890

        # First, create file
        r_output = region.open(path)

        for index in range(0, region._NB_OF_ENTRIES, 3):
            r_output.save_chunk(index, value % (index + 2))

        del r_output

        # Then, reload file
        r_output = region.open(path)

        for index in r_output.indexes():
            r_output.wipe_chunk(index)

        del r_output

        with self.assertRaises(OSError):
            os.stat(path)


if __name__ == "__main__":
    unittest.main()
