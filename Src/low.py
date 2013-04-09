"""Common procedures for low-level file management

Read and write primitives for simple types and specific container types
(in particular, NBT Lists Compounds are not managed here)

This package has no known dependency with any Python 2 or 3 oddities
"""

import struct


__all__ = (
    "read_byte", "write_byte",
    "read_byte_array", "write_byte_array",
    "read_double", "write_double",
    "read_float", "write_float",
    "read_int", "write_int",
    "read_int_array", "write_int_array",
    "read_long", "write_long",
    "read_short", "write_short",
    "read_string", "write_string",
    "read_struct", "write_struct",
    )


### Reading primitives

def read_struct(flow, fmt):
    """Unpack a C structure as can be read in the corresponding flow, provided
    its format

    >>> f = open("file.bin", "rb")
    >>> my_tuple = read_struct(f, "<2i4d") # reads two little-endian
                                           # integers and four doubles
    """
    result = list(struct.unpack(fmt, flow.read(struct.calcsize(fmt))))

    return result


def read_byte(flow):
    """Read a 8-bit long signed int() from flow
    """
    result = read_struct(flow, ">b")[0]

    return result


def read_short(flow):
    """Read a big-endian 16-bit long signed int() from flow
    """
    result = read_struct(flow, ">h")[0]

    return result


def read_int(flow):
    """Read a big-endian 32-bit long signed int() from flow
    """
    result = read_struct(flow, ">l")[0]

    return result


def read_long(flow):
    """Read a big-endian 64-bit long signed int() from flow
    """
    result = read_struct(flow, ">q")[0]

    return result


def read_float(flow):
    """Read a big-endian 32-bit long float() conforming to IEEE 754 from flow
    """
    result = read_struct(flow, ">f")[0]

    return result


def read_double(flow):
    """Read a big-endian 64-bit long float() conforming to IEEE 754 from flow
    """
    result = read_struct(flow, ">d")[0]

    return result


def read_byte_array(flow):
    """Read an array of bytes (see read_byte) from flow
    """
    length = read_int(flow)
    result = read_struct(flow, ">{}b".format(length))

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
    result = read_struct(flow, ">{}l".format(length))

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
    """Write a 8-bit long signed int() to flow
    """
    write_struct(flow, ">b", value)


def write_short(flow, value):
    """Write a big-endian 16-bit long signed int() to flow
    """
    write_struct(flow, ">h", value)


def write_int(flow, value):
    """Write a big-endian 32-bit long signed int() to flow
    """
    write_struct(flow, ">l", value)


def write_long(flow, value):
    """Write a big-endian 64-bit long signed int() to flow
    """
    write_struct(flow, ">q", value)


def write_float(flow, value):
    """Write a big-endian 32-bit long float() conforming to IEEE 754 to flow
    """
    write_struct(flow, ">f", value)


def write_double(flow, value):
    """Write a big-endian 64-bit long float() conforming to IEEE 754 to flow
    """
    write_struct(flow, ">d", value)


def write_byte_array(flow, values):
    """Write an array of bytes (see write_byte) to flow
    """
    length = len(values)

    write_int(flow, length)
    write_struct(flow, ">{}b".format(length), *values)


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
    write_struct(flow, ">{}l".format(length), *values)
