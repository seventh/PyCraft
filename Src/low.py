# -*- coding: utf-8 -*-

# Copyright or © or Copr. Guillaume Lemaître (2013)
#
#   guillaume.lemaitre@gmail.com
#
# This software is a computer program whose purpose is to ease offline edition
# of Minecraft save files.
#
# This software is governed by the CeCILL-C license under French law and
# abiding by the rules of distribution of free software. You can use, modify
# and/or redistribute the software under the terms of the CeCILL-C license as
# circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and rights to copy, modify
# and redistribute granted by the license, users are provided only with a
# limited warranty and the software's author, the holder of the economic
# rights, and the successive licensors have only limited liability.
#
# In this respect, the user's attention is drawn to the risks associated with
# loading, using, modifying and/or developing or reproducing the software by
# the user in light of its specific status of free software, that may mean that
# it is complicated to manipulate, and that also therefore means that it is
# reserved for developers and experienced professionals having in-depth
# computer knowledge. Users are therefore encouraged to load and test the
# software's suitability as regards their requirements in conditions enabling
# the security of their systems and/or data to be ensured and, more generally,
# to use and operate it in the same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL-C license and that you accept its terms.

"""Common procedures for low-level file management

Read and write primitives for simple types and specific container types
(in particular, NBT Lists Compounds are not managed here)

This package has no known dependency with any Python 2 or 3 oddities

For simple types, both single values and containers can be used as args:
>>>  write_short(flow, 3)
>>>  write_long(flow, [4, 5, 6, -2])
"""

import struct



### Reading primitives

def read_struct(flow, fmt):
    """Interpret a binary I/O, given its format. Result is always a tuple()

    >>> f = open("file.bin", "rb")
    >>> my_tuple = read_struct(f, "<2i4d") # reads two little-endian
                                           # integers and four doubles
    """
    result = struct.unpack(fmt, flow.read(struct.calcsize(fmt)))

    return result


def read_byte(flow, count = 1):
    """Read some 8-bit long signed int() from flow
    """
    result = read_struct(flow, ">{}b".format(count))
    if count == 1:
        result = result[0]

    return result


def read_short(flow, count = 1):
    """Read some big-endian 16-bit long signed int() from flow
    """
    result = read_struct(flow, ">{}h".format(count))
    if count == 1:
        result = result[0]

    return result


def read_int(flow, count = 1):
    """Read some big-endian 32-bit long signed int() from flow
    """
    result = read_struct(flow, ">{}l".format(count))
    if count == 1:
        result = result[0]

    return result


def read_long(flow, count = 1):
    """Read some big-endian 64-bit long signed int() from flow
    """
    result = read_struct(flow, ">{}q".format(count))
    if count == 1:
        result = result[0]

    return result


def read_float(flow, count = 1):
    """Read some big-endian 32-bit long float() conforming to IEEE 754 from
    flow
    """
    result = read_struct(flow, ">{}f".format(count))
    if count == 1:
        result = result[0]

    return result


def read_double(flow, count = 1):
    """Read some big-endian 64-bit long float() conforming to IEEE 754 from
    flow
    """
    result = read_struct(flow, ">{}d".format(count))
    if count == 1:
        result = result[0]

    return result


def read_byte_array(flow):
    """Read an array of bytes (see read_byte) from flow
    """
    length = read_int(flow)
    if length == 1:
        result = [read_byte(flow)]
    else:
        result = list(read_byte(flow, length))

    return result


def read_string(flow):
    """Read an UTF-8 encoded str() from flow
    """
    length = read_short(flow)
    result = flow.read(length).decode("utf-8")

    return result


def read_int_array(flow):
    """Read an array of ints (see read_int) from flow
    """
    length = read_int(flow)
    if length == 1:
        result = [read_int(flow)]
    else:
        result = list(read_int(flow, length))

    return result


### Writing primitives

def write_struct(flow, fmt, *values):
    """Pack a C structure to the corresponding flow, given its format

    >>> f = open("file.bin", "wb")
    >>> write_struct(f, "<2i4d", x, z, a, b, c, d)
    """
    buff = struct.pack(fmt, *values)
    flow.write(buff)


def write_byte(flow, value):
    """Write some 8-bit long signed int() to flow
    """
    try:
        count = len(value)
        write_struct(flow, ">{}b".format(count), *value)
    except TypeError:
        write_struct(flow, ">b", value)


def write_short(flow, value):
    """Write some big-endian 16-bit long signed int() to flow
    """
    try:
        count = len(value)
        write_struct(flow, ">{}h".format(count), *value)
    except TypeError:
        write_struct(flow, ">h", value)


def write_int(flow, value):
    """Write some big-endian 32-bit long signed int() to flow
    """
    try:
        count = len(value)
        write_struct(flow, ">{}l".format(count), *value)
    except TypeError:
        write_struct(flow, ">l", value)


def write_long(flow, value):
    """Write some big-endian 64-bit long signed int() to flow
    """
    try:
        count = len(value)
        write_struct(flow, ">{}q".format(count), *value)
    except TypeError:
        write_struct(flow, ">q", value)


def write_float(flow, value):
    """Write some big-endian 32-bit long float() conforming to IEEE 754 to
    flow
    """
    try:
        count = len(value)
        write_struct(flow, ">{}f".format(count), *value)
    except TypeError:
        write_struct(flow, ">f", value)


def write_double(flow, value):
    """Write some big-endian 64-bit long float() conforming to IEEE 754 to
    flow
    """
    try:
        count = len(value)
        write_struct(flow, ">{}d".format(count), *value)
    except TypeError:
        write_struct(flow, ">d", value)


def write_byte_array(flow, values):
    """Write an array of bytes (see write_byte) to flow
    """
    length = len(values)

    write_int(flow, length)
    write_byte(flow, values)


def write_string(flow, value):
    """Write an UTF-8 encoded str() to flow
    """
    raw_value = value.encode("utf-8")
    length = len(raw_value)

    write_short(flow, length)
    flow.write(raw_value)


def write_int_array(flow, values):
    """Write an array of ints (see write_int) from flow
    """
    length = len(values)

    write_int(flow, length)
    write_int(flow, values)
