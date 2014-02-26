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

"""Named Binary Tag file format converter

Read and write Named Binary Tag file format (NBT) as specified in
http://www.minecraftwiki.net/wiki/NBT

A simple way to read a NBT file:
>>> flow = open("my_file.nbt", "rb")
>>> nbt_reader = nbt.Reader()
>>> content = nbt_reader.read(flow)

File format is separated from file content, so that it is not duplicated
among various contents. But it still accessible for further use:
>>> template = nbt_reader.last_format

Later, when edition is done, file can be updated easily:
>>> nbt_writer = nbt.Writer()
>>> flow = nbt_writer.write(content, template)

This package has no known dependency with any Python 2 or 3 oddities
"""

import gzip
import re

from . import low


class Reader(object):
    """Analyzes a NBT-encoded file, and separates its content from its format.

    >>> reader = nbt.Reader()
    >>> flow = open("level.dat", "rb")
    >>> data = reader.read(flow)
    >>> fmt = reader.last_format
    """

    # Internal variable to pass along the various readers
    _flow = None

    # Format detected during the last 'read' call
    last_format = None


    def read(self, entry):
        """Parse a NBT encoded byte flow and construct a recursive dictionary
        view of it
        """
        result = None

        if type(entry) == type(str()):
            self._flow = gzip.open(entry, "rb")
        else:
            self._flow = entry
        self.last_format = Format()

        result = self._read_named_tag(self.last_format)

        if type(entry) == type(str()):
            self._flow.close()

        return result


    def _read_named_tag(self, fmt):
        """A named tag is composed as this:
        - byte tagType
        - TAG_String name
        - [payload]

        Result is a (name, value) pair
        """
        result = None

        tag = self._read_byte()
        if tag != 0:
            name = self._read_string()

            reader = self._get_reader(tag)
            value = reader(fmt)

            result = {name: value}

            fmt.tag = tag
            fmt.name = name

        return result


    def _read_byte(self, fmt = None):
        """A TAG_Byte(1) is a 1-byte long signed integer

        Result is a Python int()
        """
        result = low.read_byte(self._flow)

        return result


    def _read_short(self, fmt = None):
        """A TAG_Short(2) is a 2-byte long signed integer

        Result is a Python int()
        """
        result = low.read_short(self._flow)

        return result


    def _read_int(self, fmt = None):
        """A TAG_Int(3) is a 4-byte long signed integer

        Result is a Python int()
        """
        result = low.read_int(self._flow)

        return result


    def _read_long(self, fmt = None):
        """A TAG_Long(4) is a 8-byte long signed integer

        Result is a Python int()
        """
        result = low.read_long(self._flow)

        return result


    def _read_float(self, fmt = None):
        """A TAG_Float(5) is a 32-bit long decimal value conforming to
        IEEE 754

        Result is a Python float()
        """
        result = low.read_float(self._flow)

        return result


    def _read_double(self, fmt = None):
        """A TAG_Double(6) is a 64-bit long decimal value conforming to
        IEEE 754

        Result is a Python float()
        """
        result = low.read_double(self._flow)

        return result


    def _read_byte_array(self, fmt):
        """A TAG_Byte_Array(7) is composed as this:
        - TAG_Int length
        - [length TAG_Byte]

        Result is a Python list() of int()
        """
        result = None

        fmt.fields = Format()
        fmt.fields.tag = 1

        result = low.read_byte_array(self._flow)

        return result


    def _read_string(self, fmt = None):
        """A TAG_String(8) is composed as this:
        - TAG_Short length
        - [length TAG_Byte] representing a UTF-8 coded value

        Result is a Python str()
        """
        result = None

        result = low.read_string(self._flow)

        return result


    def _read_list(self, fmt):
        """A TAG_List(9) is composed as this:
        - TAG_Byte tag
        - TAG_Int length
        - [length elements of tag kind]

        Result is a Python list()
        """
        result = None

        tag = self._read_byte()
        length = self._read_int()

        # All inner elements share the same type. So, a single Format field is
        # enough to store their common format
        fmt.fields = Format()
        fmt.fields.tag = tag

        reader = self._get_reader(tag)
        result = []
        for i in range(length):
            value = reader(fmt.fields)
            result.append(value)

        return result


    def _read_compound(self, fmt):
        """A TAG_Compound(10) is a set of (name, value) pairs

        Result is a Python dict()
        """
        result = dict()

        # All inner elements have a specific type.
        fmt.fields = list()

        while True:
            inner_fmt = Format()
            elem = self._read_named_tag(inner_fmt)
            if elem is None:
                break
            result.update(elem)
            fmt.fields.append(inner_fmt)

        return result


    def _read_int_array(self, fmt):
        """A TAG_Int_Array(11) is composed as this:
        - TAG_Int length
        - [length TAG_Int]

        Result is a Python list() of int()
        """
        result = None

        fmt.fields = Format()
        fmt.fields.tag = 3

        result = low.read_int_array(self._flow)

        return result


    def _get_reader(self, tag):
        """Provide parsing function associated to tag's value.

        Parsing function has the following signature:

          parsing_function(fmt)

        where fmt is a Format() object
        """
        result = None

        if tag == 1:
            result = self._read_byte
        elif tag == 2:
            result = self._read_short
        elif tag == 3:
            result = self._read_int
        elif tag == 4:
            result = self._read_long
        elif tag == 5:
            result = self._read_float
        elif tag == 6:
            result = self._read_double
        elif tag == 7:
            result = self._read_byte_array
        elif tag == 8:
            result = self._read_string
        elif tag == 9:
            result = self._read_list
        elif tag == 10:
            result = self._read_compound
        elif tag == 11:
            result = self._read_int_array
        else:
            raise RuntimeError("unknown tag")

        return result



class Writer(object):
    """Convert a data hierarchy to a byte flow according to a specified format
    """

    _flow = None


    def write(self, output, value, fmt):
        """Parse a non-encoded byte flow and construct a recursive dictionary
        view of it
        """
        if type(output) == type(str()):
            self._flow = gzip.open(output, "wb")
        else:
            self._flow = output

        self._write_named_tag(value, fmt)

        if type(output) == type(str()):
            self._flow.close()


    def _write_named_tag(self, value, fmt):
        """A named tag is composed as this:
        - byte tagType
        - TAG_String name
        - [payload]
        """
        self._write_byte(fmt.tag)
        self._write_string(fmt.name)

        writer = self._get_writer(fmt.tag)
        writer(value[fmt.name], fmt.fields)


    def _write_byte(self, value, fmt = None):
        """A TAG_Byte(1) is a 1-byte long signed integer
        """
        low.write_byte(self._flow, value)


    def _write_short(self, value, fmt = None):
        """A TAG_Short(2) is a 2-byte long signed integer
        """
        low.write_short(self._flow, value)


    def _write_int(self, value, fmt = None):
        """A TAG_Int(3) is a 4-byte long signed integer
        """
        low.write_int(self._flow, value)


    def _write_long(self, value, fmt = None):
        """A TAG_Long(4) is a 8-byte long signed integer
        """
        low.write_long(self._flow, value)


    def _write_float(self, value, fmt = None):
        """A TAG_Float(5) is a 32-bit long decimal value conforming to
        IEEE 754
        """
        low.write_float(self._flow, value)


    def _write_double(self, value, fmt = None):
        """A TAG_Double(6) is a 64-bit long decimal value conforming to
        IEEE 754
        """
        low.write_double(self._flow, value)


    def _write_byte_array(self, value, fmt):
        """A TAG_Byte_Array(7) is composed as this:
        - TAG_Int length
        - [length TAG_Byte]
        """
        low.write_byte_array(self._flow, value)


    def _write_string(self, value, fmt = None):
        """A TAG_String(8) is composed as this:
        - TAG_Short length
        - [length TAG_Byte] representing a UTF-8 coded value
        """
        low.write_string(self._flow, value)


    def _write_list(self, value, fmt):
        """A TAG_List(9) is composed as this:
        - TAG_Byte tag
        - TAG_Int length
        - [length elements of tag kind]
        """
        length = len(value)

        self._write_byte(fmt.tag)
        self._write_int(length)

        writer = self._get_writer(fmt.tag)
        for element in value:
            writer(element, fmt.fields)


    def _write_compound(self, value, fmt):
        """A TAG_Compound(10) is a set of (name, value) pairs
        """
        for item in fmt:
            self._write_named_tag(value, item)
        self._write_byte(0)


    def _write_int_array(self, value, fmt):
        """A TAG_Int_Array(11) is composed as this:
        - TAG_Int length
        - [length TAG_Int]
        """
        low.write_int_array(self._flow, value)


    def _get_writer(self, tag):
        """Provide parsing function associated to tag's value.

        Parsing function has the following signature:

          parsing_function(value, fmt)

        where fmt is a Format() object
        """
        result = None

        if tag == 1:
            result = self._write_byte
        elif tag == 2:
            result = self._write_short
        elif tag == 3:
            result = self._write_int
        elif tag == 4:
            result = self._write_long
        elif tag == 5:
            result = self._write_float
        elif tag == 6:
            result = self._write_double
        elif tag == 7:
            result = self._write_byte_array
        elif tag == 8:
            result = self._write_string
        elif tag == 9:
            result = self._write_list
        elif tag == 10:
            result = self._write_compound
        elif tag == 11:
            result = self._write_int_array
        else:
            raise RuntimeError("unknown tag")

        return result



###
class Format(object):
    """Format of a NBT-encoded file
    """

    # Tag of the element
    tag = None

    # Name of the element
    name = None

    # Format of inner elements. Useful only for list, array and compound.
    fields = None

    def __init__(self, tag = None):
        self.tag = tag


    def __str__(self):
        result = self.to_string(0)

        return result


    def pretty(self, data, indent = 0):
        """Format out data
        """
        result = str()
        prefix = "  " * indent

        result += prefix

        result += self._get_element_type(self.tag)

        if self.name is not None:
            result += "({})".format(self._format_string(self.name))
            data = data[self.name]

        if self.tag == 9:
            result += " of {}".format(self._get_element_type(self.fields.tag))

        result += ": "

        if self.tag == 8:
            result += self._format_string(data)
        elif self.tag == 9:
            if self.fields.tag not in [8, 9, 10]:
                result += str(data)
            else:
                result += "[\n"
                for i in range(len(data)):
                    result += self.fields.pretty(data[i], indent + 1) + "\n"
                result += prefix + "]"
        elif self.tag == 10:
            result += "{\n"
            for x in self.fields:
                result += x.pretty(data, indent + 1) + "\n"
            result += prefix + "}"
        else:
            result += str(data)

        return result


    def to_string(self, indent):
        result = str()
        prefix = "  " * indent

        result += prefix

        result += self._get_element_type(self.tag)

        if self.name is not None:
            result += "({})".format(self._format_string(self.name))

        if self.tag == 9:
            result += " of {}".format(self._get_element_type(self.fields.tag))
            if self.fields.tag == 10:
                result += self._format_compound(self.fields.fields, indent)
        elif self.tag == 10:
            result += self._format_compound(self.fields, indent)

        return result


    def _format_compound(self, fields, indent):
        result = " {\n"

        for field in fields:
            result += "{}\n".format(field.to_string(indent + 1))
        result += "{}}}".format("  " * indent)

        return result


    def _format_string(self, string):
        result = "'" + re.sub("'", "\\'", string) + "'"

        return result


    def _get_element_type(self, tag):
        result = None

        if tag == 1:
            result = "TAG_Byte"
        elif tag == 2:
            result = "TAG_Short"
        elif tag == 3:
            result = "TAG_Int"
        elif tag == 4:
            result = "TAG_Long"
        elif tag == 5:
            result = "TAG_Float"
        elif tag == 6:
            result = "TAG_Double"
        elif tag == 7:
            result = "TAG_Byte_Array"
        elif tag == 8:
            result = "TAG_String"
        elif tag == 9:
            result = "TAG_List"
        elif tag == 10:
            result = "TAG_Compound"
        elif tag == 1:
            result = "TAG_Int_Array"
        else:
            raise RuntimeError("unknown tag")

        return result



def read(entry):
    result = None

    r = Reader()
    result = r.read(entry)

    return result


def write(output, data, template):
    w = Writer()
    w.write(output, data, template)
