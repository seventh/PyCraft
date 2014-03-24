# -*- coding: utf-8 -*-

# Copyright or © or Copr. Guillaume Lemaître (2014)
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

"""Container-Oriented NBT format

The original description of the NBT format does not correspond to the way it
is actually used in Minecraft. A TAG_COMPOUND is always the top-most level
of any data hierarchy. Even a TAG_COMPOUND is always wrapped in a first
level, anonymous TAG_COMPOUND! TAG names can disappear in TAG_LIST (and its
derivatives), so they are not as mandatory as it seems.

So, this package provides a realistic usage of NBT format, by using python
standard types for scalar values (int, float or str), and providing with
two specific containers to mimic constraints of TAG_LIST and TAG_COMPOUND.

TAG_BYTE_ARRAY and TAG_INT_ARRAY are considered to be storage optimizations,
which constraints are difficult enough to manage to authorize their usage
only by package implementation, and not by package user.
"""

# - Type of the elements is known from the container only
# - If no precision is given, the largest one is provided

import collections
import gzip
import sys

from . import low

if sys.version_info < (3,):
    str_type = unicode
else:
    str_type = str


_TAG_NONE = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
_TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
_TAG_INT_ARRAY = 11

_VALID_TAGS = (
    TAG_BYTE,
    TAG_SHORT,
    TAG_INT,
    TAG_LONG,
    TAG_FLOAT,
    TAG_DOUBLE,
    TAG_STRING,
    TAG_LIST,
    TAG_COMPOUND
    );


def is_accepted(kind, value):
    """Does the value corresponds to the specificities of the kind?
    """
    result = False

    if kind == TAG_BYTE:
        result = isinstance(value, int) \
            and -128 <= value < 128

    elif kind == TAG_SHORT:
        result = isinstance(value, int) \
            and -32768 <= value < 32768

    elif kind == TAG_INT:
        result = isinstance(value, int) \
            and -2147483648 <= value < 2147483648

    elif kind == TAG_LONG:
        result = isinstance(value, int) \
            and -9223372036854775808 <= value < 9223372036854775808

    elif kind == TAG_FLOAT or kind == TAG_DOUBLE:
        result = isinstance(value, float)

    elif kind == TAG_STRING:
        result = isinstance(value, str_type)

    elif kind == TAG_LIST:
        result = isinstance(value, List)

    elif kind == TAG_COMPOUND:
        result = isinstance(value, Dict)

    else:
        raise ValueError("Unknown kind {}".format(kind))

    return result


TAG_NAME = {
    TAG_BYTE : "TAG_Byte",
    TAG_SHORT : "TAG_Short",
    TAG_INT : "TAG_Int",
    TAG_LONG : "TAG_Long",
    TAG_FLOAT : "TAG_Float",
    TAG_DOUBLE : "TAG_Double",
    TAG_STRING : "TAG_String",
    TAG_LIST : "TAG_List",
    TAG_COMPOUND : "TAG_Compound",
}


def pretty(value, kind = None, name = None, level = 0):
    def_kind, value = Oracle.suit(value)

    if kind is None:
        pretty(value, def_kind, name, level)

    elif kind in [TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG, TAG_FLOAT, TAG_DOUBLE]:
        if name is None:
            return "{: >{fill}}{}: {}".format("", TAG_NAME[kind], value, fill = level * 2)
        else:
            return "{: >{fill}}{}({}): {}".format("", TAG_NAME[kind], repr(name), value, fill = level * 2)

    elif kind == TAG_STRING:
        if name is None:
            return "{: >{fill}}{}: {}".format("", TAG_NAME[kind], repr(value), fill = level * 2)
        else:
            return "{: >{fill}}{}({}): {}".format("", TAG_NAME[kind], repr(name), repr(value), fill = level * 2)

    elif kind in (TAG_LIST, TAG_COMPOUND):
        return value.pretty(name, level)

    else:
        raise ValueError


class Oracle(object):
    """Utility class to transform any data into a pycraft one.
    The proposed transformation follows this schema:

    isinstance(value, int)          --> result = (TAG_LONG, value)
    isinstance(value, float)        --> result = (TAG_DOUBLE, value)
    isinstance(value, str)          --> result = (TAG_STRING, value)
    isinstance(value, (list, List)) --> result = (TAG_LIST, List(value))
    isinstance(value, (dict, Dict)) --> result = (TAG_COMPOUND, Dict(value))
    """

    @staticmethod
    def suit(value):
        """Recursively create a pycraft compliant data from input value.
        Result is a (kind, value) pair
        """
        result = None

        if isinstance(value, (int, float, str_type)):
            result = (Oracle.default_kind(value), value)

        elif isinstance(value, (list, List)):
            result = (TAG_LIST, List())
            if isinstance(value, List):
                result[1].set_kind(value.get_kind())
            for elem in value:
                result[1].append(Oracle.suit(elem)[1])

        elif isinstance(value, (dict, Dict)):
            result = (TAG_COMPOUND, Dict())
            if isinstance(value, Dict):
                for key in value:
                    result[1].set_kind(key, value.get_kind(key))
                    result[1][key] = Oracle.suit(value[key])[1]
            else:
                for key in value:
                    result[1][key] = Oracle.suit(value[key])[1]

        return result


    @staticmethod
    def test(value):
        """Recursively verify that value complies to both its explicit
        constraints and implicit constraints induced by the NBT format
        """
        result = True

        if isinstance(value, (int, float, str_type)):
            result = is_accepted(Oracle.default_kind(value), value)

        elif isinstance(value, list):
            kind = None
            for elem in value:
                if kind is None:
                    kind = Oracle.default_kind(elem)
                    if not Oracle.test(elem):
                        result = False
                        break
                elif kind != Oracle.default_kind(elem) or not Oracle.test(elem):
                    result = False
                    break

        elif isinstance(value, dict):
            for elem in value.items():
                if not is_accepted(Oracle.default_kind(elem), elem) \
                        or not Oracle.test(elem):
                    result = False
                    break

        return result


    @staticmethod
    def default_value(kind):
        """Default value for any instance of the corresponding kind
        """
        result = None

        if kind in (TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG):
            result = int()

        elif kind in (TAG_FLOAT, TAG_DOUBLE):
            result = float()

        elif kind == TAG_STRING:
            result = str_type()

        elif kind == TAG_LIST:
            result = List()

        elif kind == TAG_COMPOUND:
            result = Dict()

        return result


    @staticmethod
    def default_kind(value):
        """When no precision is given, the largest suitable kind is preferred
        """
        result = None

        if isinstance(value, int):
            result = TAG_LONG
        elif isinstance(value, float):
            result = TAG_DOUBLE
        elif isinstance(value, str_type):
            result = TAG_STRING
        elif isinstance(value, (list, List)):
            result = TAG_LIST
        elif isinstance(value, (dict, Dict)):
            result = TAG_COMPOUND

        return result



class Writer(object):
    """Utility class to record any int/float/str/[lL]ist/[dD]ict into NBT
    format

    Code snippet of typical usage:
    >>> buffer = io.BytesIO()
    >>> Writer.save(buffer, TAG_SHORT, "i", -15)
    >>> Writer.save(buffer, TAG_LIST, "keys", ["a", "b"])
    """

    @staticmethod
    def save(flow, kind, name, value):
        """Record (name, value) pair, considering value's kind, into binary
        flow
        """
        # Refine kind for a list
        if kind == TAG_LIST:
            if value.get_kind() == TAG_BYTE:
                kind = _TAG_BYTE_ARRAY
            elif value.get_kind() == TAG_INT:
                kind = _TAG_INT_ARRAY

        # Write kind, then name, then value
        low.write_byte(flow, kind)
        low.write_string(flow, name)
        Writer.writers[kind](flow, value)


    @staticmethod
    def save_file(path, kind, name, value):
        """Record (name, value) pair, considering value's kind, into a file
        identified by given path
        """
        flow = gzip.open(path, "wb")
        Writer.save(flow, kind, name, value)
        flow.close()


    @staticmethod
    def _save_dict(flow, value):
        for key in value:
            Writer.save(flow, value.get_kind(key), key, value[key])
        low.write_byte(flow, _TAG_NONE)


    @staticmethod
    def _save_list(flow, value):
        # Refine elements kind in case of an empty list or a list of lists
        inner_kind = value.get_kind()
        if inner_kind is None:
            inner_kind = _TAG_NONE
        elif inner_kind == TAG_LIST:
            at_least_one = False
            byte_only = True
            int_only = True
            for inner_v in value:
                inner_inner_kind = inner_v.get_kind()
                if inner_inner_kind is not None:
                    at_least_one = True
                    if inner_inner_kind == TAG_BYTE:
                        int_only = False
                    elif inner_inner_kind == TAG_INT:
                        byte_only = False
                    else:
                        byte_only = False
                        int_only = False

                if not (byte_only or int_only):
                    break

            # In case of deuce (all inner lists are empty), always consider
            # inner lists to be byte arrays
            if at_least_one:
                if byte_only:
                    inner_kind = _TAG_BYTE_ARRAY
                elif int_only:
                    inner_kind = _TAG_INT_ARRAY

        # Write elements kind, then elements count, then elements values
        low.write_byte(flow, inner_kind)
        low.write_int(flow, len(value))
        writer = Writer.writers[inner_kind]
        for inner_v in value:
            writer(flow, inner_v)


    writers = [
        None,
        low.write_byte,
        low.write_short,
        low.write_int,
        low.write_long,
        low.write_float,
        low.write_double,
        low.write_byte_array,
        low.write_string,
        _save_list.__func__,
        _save_dict.__func__,
        low.write_int_array,
        ]



class Reader(object):
    """Utility class to load any binary flow in NBT format into memory
    """

    @staticmethod
    def load(flow):
        """Read (kind, name, value) triple from binary flow
        """
        result = None # (kind, name, value)

        kind = low.read_byte(flow)
        if kind != _TAG_NONE:
            name = low.read_string(flow)

            value = Reader.readers[kind](flow)

            if kind in [_TAG_BYTE_ARRAY, _TAG_INT_ARRAY]:
                kind = TAG_LIST
            result = (kind, name, value)

        return result


    @staticmethod
    def load_file(path):
        """Read (kind, name, value) triple from NBT-formatted file identified
        by given path
        """
        result = None # (kind, name, value)

        flow = gzip.open(path, "rb")
        result = Reader.load(flow)
        flow.close()

        return result


    @staticmethod
    def _load_dict(flow):
        result = Dict()

        while True:
            inner_v = Reader.load(flow)
            if inner_v is None:
                break
            else:
                result.set_kind(inner_v[1], inner_v[0])
                result[inner_v[1]] = inner_v[2]

        return result


    @staticmethod
    def _load_list(flow):
        result = List()

        kind = low.read_byte(flow)
        count = low.read_int(flow)

        reader = Reader.readers[kind]

        if kind == _TAG_NONE:
            kind = None
        elif kind in [_TAG_BYTE_ARRAY, _TAG_INT_ARRAY]:
            kind = TAG_LIST
        result.set_kind(kind)

        for i in range(count):
            result.append(reader(flow))

        return result


    @staticmethod
    def _load_list_byte(flow):
        """Method to load a TAG_BYTE_ARRAY
        """
        # Rely on knowledge of List implementation in order to gain
        # performance
        result = List()
        result.set_kind(TAG_BYTE)
        result._items = low.read_byte_array(flow)

        return result


    @staticmethod
    def _load_list_int(flow):
        """Method to load a TAG_INT_ARRAY
        """
        # Rely on knowledge of List implementation in order to gain
        # performance
        result = List()
        result.set_kind(TAG_INT)
        result._items = low.read_int_array(flow)

        return result


    readers = [
        None,
        low.read_byte,
        low.read_short,
        low.read_int,
        low.read_long,
        low.read_float,
        low.read_double,
        _load_list_byte.__func__,
        low.read_string,
        _load_list.__func__,
        _load_dict.__func__,
        _load_list_int.__func__,
        ]



_DictPair = collections.namedtuple('_DictPair', ['kind', 'item'])


class Container(object):
    """Abstract base class of containers
    """

    def __repr__(self):
        return self.pretty()


    def pretty(self, name = "", level = 0):
        raise NotImplementedError



class Dict(Container, collections.MutableMapping):
    """Statically typed associative container indexed by string identifiers
    >>> D = Dict()
    >>> D.set_kind("abc", TAG_INT)
    >>> D["abc"] = 5
    >>> D["abc"] = 5.0
    ValueError : wrong type
    >>> D["def"] = 6
    >>> print(D.get_kind("def") == TAG_LONG)
    True
    """

    __slots__ = ('_pairs')


    def __init__(self):
        # object is implemented as an ordered dictionary associating strings
        # with (K, V) pairs, K being a tag identifying the type of the value I
        #
        # usage of an ordered dictonary is for repeatability of results (for
        # example, read a file and write it back)

        self._pairs = collections.OrderedDict()


    def __delitem__(self, key):
        assert isinstance(key, str_type)

        del self._pairs[key]


    def __getitem__(self, key):
        assert isinstance(key, str_type)

        return self._pairs[key].item


    def __setitem__(self, key, value):
        assert isinstance(key, str_type)

        if key in self:
            kind = self._pairs[key].kind
            if not is_accepted(kind, value):
                raise ValueError
        else:
            kind = Oracle.default_kind(value)

        self._pairs[key] = _DictPair(kind, value)


    def __iter__(self):
        return iter(self._pairs)


    def __len__(self):
        return len(self._pairs)


    def get_kind(self, key):
        """Get type of element identified by the corresponding key
        """
        assert isinstance(key, str_type)

        result = self._pairs[key].kind

        return result


    def set_kind(self, key, kind):
        """Set type of element identified by the corresponding key. If there
        is currently no element pointed by the key, the value is set to the
        default one. Otherwise, compatibility between the current value and
        new kind is checked.
        """
        assert isinstance(key, str_type)

        if kind not in _VALID_TAGS:
            raise ValueError("Kind {} cannot be used as an actual type".format(kind))
        elif key in self._pairs:
            pair = self._pairs[key]
            if not is_accepted(kind, pair.item):
                raise KeyError
            else:
                self._pairs[key] = _DictPair(kind, pair.item)
        else:
            self._pairs[key] = _DictPair(kind, Oracle.default_value(kind))


    def pretty(self, name = None, level = 0):
        result = str_type("{: >{fill}}TAG_Compound".format("",
                                                           fill = 2 * level))

        if name is not None:
            result += str_type("({})".format(repr(name)))
        result += str_type(": {\n")

        for key in self._pairs:
            result += pretty(self._pairs[key].item, self._pairs[key].kind, key, level + 1)
            result += "\n"

        result += "{: >{fill}}}}".format("", fill = 2 * level)

        return result



class List(Container, collections.MutableSequence):
    """Indexed set of elements that share the same kind
    """

    __slots__ = ('_kind', '_items')


    def __init__(self, other = None):
        self._kind = None
        self._items = list()

        if other is not None:
            assert Oracle.test(other)
            for value in other:
                self.append(value)


    def __delitem__(self, key):
        del self._items[key]


    def __getitem__(self, key):
        if not isinstance(key, slice):
            result = self._items[key]
        else:
            result = List()
            result.set_kind(self.get_kind())
            result[:] = self._items[key]

        return result


    def __setitem__(self, key, value):
        if isinstance(key, slice):
            if self._kind is None:
                self._kind = Oracle.default_kind(value[0])

            if self._kind is None:
                raise KeyError
            else:
                for val in value:
                    if not is_accepted(self._kind, val):
                        raise ValueError
                else:
                    self._items[key] = value

        else:
            if self._kind is None:
                self._kind = Oracle.default_kind(value)

            if self._kind is None:
                raise KeyError
            elif not is_accepted(self._kind, value):
                raise ValueError
            else:
                self._items[key] = value


    def __len__(self):
        return len(self._items)


    def __eq__(self, other):
        return self._kind == other._kind \
            and self._items == other._items


    def __ne__(self, other):
        return not self.__eq__(other)


    def insert(self, key, value):
        if self._kind is None:
            self._kind = Oracle.default_kind(value)

        if self._kind is None:
            raise KeyError
        elif not is_accepted(self._kind, value):
            raise ValueError
        else:
            self._items.insert(key, value)


    def get_kind(self):
        return self._kind


    def set_kind(self, kind):
        if len(self._items) == 0:
            self._kind = kind
        else:
            for value in self._items:
                if not is_accepted(kind, value):
                    raise KeyError
            else:
                self._kind = kind


    def pretty(self, name = None, level = 0):
        result = str_type("{: >{fill}}TAG_List".format("", fill = 2 * level))

        if name is not None:
            result += str_type("({})".format(repr(name)))
        if self._kind is not None:
            result += str_type(" of {}".format(TAG_NAME[self._kind]))
        result += str_type(": ")

        if self._kind not in (TAG_LIST, TAG_COMPOUND):
            result += "[" + ", ".join(map(str, self._items)) + "]\n"
        else:
            result += "{\n"

            for key in range(len(self._items)):
                result += pretty(self._items[key], self._kind, key, level + 1)
                result += "\n"

            result += "{: >{fill}}}}".format("", fill = 2 * level)


        return result



def load(entry):
    """Read NBT value from entry, being it a pathname identifying a file or a
    binary flow.

    See Reader.load and Reader.load_file in order to also access name and kind
    of the read value.
    """
    content = None

    if isinstance(entry, str_type):
        content = Reader.load_file(entry)
    else:
        content = Reader.load(entry)

    return content[2]


def save(entry, value):
    """Record anonymous value into entry, being it a file or a binary flow.
    Kind of entry is automatically determined.

    See Writer.save and Writer.save_file in order to also precise name and
    kind of the written value.
    """
    name = ""
    kind = Oracle.default_kind(value)

    if isinstance(entry, str_type):
        Writer.save_file(entry, kind, name, value)
    else:
        Writer.save(entry, kind, name, value)


suit = Oracle.suit
test = Oracle.test
