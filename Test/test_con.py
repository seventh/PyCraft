# -*- coding: utf-8 -*-

"""Verify the behaviour of the pycraft 'con' package.
"""

import io
import unittest

from pycraft import con


class ReadWrite(unittest.TestCase):

    def test_external_read(self):
        """Check that reading and writing back an original NBT file is
        innocuous
        """
        with open("bigtest.nbt", "rb") as input_file:
            (K, N, V) = con.Reader.load(input_file)

            with open("bigtest.out", "wb") as output_file:
                con.Writer.save(output_file, K, N, V)

            input_file.seek(0, 0)
            with open("bigtest.out", "rb") as output_file:
                expected = input_file.read()
                produced = output_file.read()
                self.assertEqual(expected, produced)


    def test_write_read(self):
        """Ensures that the reconstructed version of any stored data is
        identical to the original one
        """
        for kind, expected_value in all_values(True):
            buffer = io.BytesIO()
            con.save(buffer, kind, "", expected_value)

            buffer.seek(0)
            value = con.load(buffer)

            self.assertEqual(expected_value, value, str(kind))


    def test_read_write(self):
        """Ensures that reading and writing back of any stored data is
        innocuous
        """
        for _kind, _value in all_values(False):
            # First, write reference file
            expected = io.BytesIO()
            con.save(expected, _kind, "", _value)
            expected.seek(0)

            # Then, load and save it immediately
            produced = io.BytesIO()
            kind, name, value = con.Reader.load(expected)
            con.Writer.save(produced, kind, name, value)

            # Finally compare both binary versions
            expected.seek(0)
            produced.seek(0)
            self.assertEqual(expected.read(), produced.read(), str(_value))


    def test_pretty(self):
        """Ensures that 'pretty' is always functional
        """
        for kind, value in all_values(True):
            pretty_string = con.pretty(value, kind)



def all_scalars():
    """Utility method to iterate over all authorized scalar types
    """
    yield (con.TAG_BYTE, -2**7)
    yield (con.TAG_SHORT, -2**15)
    yield (con.TAG_INT, -2**31)
    yield (con.TAG_LONG, -2**63)

    # Current value for TAG_FLOAT actually has to be totally representable
    # within the expression range of a TAG_FLOAT. For example, 3.7 would not
    # work well
    yield (con.TAG_FLOAT, 3.5)
    # Ideally, the value for TAG_DOUBLE should not be representable within
    # the expression range of a TAG_FLOAT. This is currently the case, but it
    # may provoke issues on platform where python's float() is actually 32-bit
    # long
    yield (con.TAG_DOUBLE, 3.7)

    yield (con.TAG_STRING, "ma boîte dans ton œil")


def all_dicts(restricted = False):
    """Utility method to iterate over all authorized dictionnary types
    """
    yield (con.TAG_COMPOUND, con.Dict())
    if not restricted:
        yield (con.TAG_COMPOUND, dict())


def all_lists(restricted = False):
    """Utility method to iterate over all authorized list types
    """
    yield (con.TAG_LIST, con.List())
    if not restricted:
        yield (con.TAG_LIST, list())


def all_values(restricted = False):
    """Utility method to cover all kinds of value compositions
    """
    for kind, value in all_values_1st_level(restricted):
        yield (kind, value)

    for kind, value in all_values_2nd_level(restricted):
        yield (kind, value)

    for kind, value in all_values_3rd_level(restricted):
        yield (kind, value)


def all_values_1st_level(restricted = False):
    """Utility method to produce all terminal kinds of value (i.e. scalar
    values)
    """
    for kind, value in all_scalars():
        yield (kind, value)


def all_values_2nd_level(restricted = False):
    """Utility method to produce all possible non recursive containers
    """
    for kind, value in all_dicts(restricted):
        # Empty dict
        yield (kind, value)

        # Filled dict
        for i_kind, i_value in all_values_1st_level(restricted):
            name = str(i_kind)
            value[name] = i_value
            if isinstance(value, con.Dict):
                value.set_kind(name, i_kind)
        yield (kind, value)

    for kind, value in all_lists(restricted):
        # Empty list with no kind
        yield (kind, value)

        for i_kind, i_value in all_values_1st_level(restricted):
            # Empty list with set kind
            if isinstance(value, con.List):
                value.set_kind(i_kind)
                yield (kind, value)

            # Non-empty list
            value.append(i_value)
            yield (kind, value)
            del value[:]


def all_values_3rd_level(restricted = False):
    """Utility method to produce all possible containers of containers
    """
    i = 0

    for kind, value in all_dicts(restricted):
        for i_kind, i_value in all_values_2nd_level(restricted):
            name = str(i)
            i += 1
            value[name] = i_value
            if isinstance(value, con.Dict):
                value.set_kind(name, i_kind)
        yield (kind, value)

    for kind, value in all_lists(restricted):
        for i_kind, i_value in all_values_2nd_level(restricted):
            # Empty list with set kind
            if isinstance(value, con.List):
                value.set_kind(i_kind)
                yield (kind, value)

            # Non-empty list
            value.append(i_value)
            yield (kind, value)
            del value[:]


if __name__ == "__main__":
    unittest.main()
