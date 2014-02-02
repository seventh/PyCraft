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

from . import low


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
        result = isinstance(value, str)

    elif kind == TAG_LIST:
        result = isinstance(value, List)

    elif kind == TAG_COMPOUND:
        result = isinstance(value, Dict)

    else:
        raise ValueError("Unknown kind {}".format(kind))

    return result


def default_value(kind):
    """Default value for any instance of the corresponding kind
    """
    result = None

    if kind in (TAG_BYTE,
                TAG_SHORT,
                TAG_INT,
                TAG_LONG):
        result = int()

    elif kind in (TAG_FLOAT,
                  TAG_DOUBLE):
        result = float()

    elif kind == TAG_STRING:
        result = str()

    elif kind == TAG_COMPOUND:
        result = Dict()

    elif kind == TAG_LIST:
        result = List()

    return result


def default_kind(value):
    """When no precision is given, the largest one is preferred
    """
    result = None

    if isinstance(value, int):
        result = TAG_LONG
    elif isinstance(value, float):
        result = TAG_DOUBLE
    elif isinstance(value, str):
        result = TAG_STRING
    elif isinstance(value, list, List):
        result = TAG_LIST
    elif isinstance(value, dict, Dict):
        result = TAG_COMPOUND

    return result


def convert(value):
    """Convert a plain dict/list container into a NBT equivalent one
    """
    result = None

    if isinstance(value, int):
        result = (TAG_LONG, value)
    elif isinstance(value, float):
        result = (TAG_DOUBLE, value)
    elif isinstance(value, str):
        result = (TAG_STRING, value)
    elif isinstance(value, List):
        result = (TAG_LIST, value)
    elif isinstance(value, Dict):
        result = (TAG_COMPOUND, value)
    elif isinstance(value, list):
        result = (TAG_LIST, List())
        for elem in value:
            result[1].append(convert(elem)[1])
    elif isinstance(value, dict):
        result = (TAG_COMPOUND, Dict())
        for key in value:
            result[1][key] = convert(value[key])[1]

    return result


def tag_name(kind):
    result = None

    matrix = {
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

    try:
        result = matrix[kind]
    except KeyError:
        pass

    return result


def pretty(value, kind = None, name = "", level = 0):
    if kind is None:
        if isinstance(value, Dict, List):
            return value.pretty(name, level)
        else:
            raise ValueError("Values should be explicitely typed")

    elif kind in (TAG_COMPOUND, TAG_LIST):
        return value.pretty(name, level)

    elif kind == TAG_STRING:
        return "{: >{fill}}{}({}): {}".format("", tag_name(kind), repr(name), repr(value), fill = level * 2)
    elif kind in [TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG, TAG_FLOAT, TAG_DOUBLE]:
        return "{: >{fill}}{}({}): {}".format("", tag_name(kind), repr(name), value, fill = level * 2)

    else:
        raise ValueError


class Writer(object):
    """Utility class to record any int/float/str/[lL]ist/[dD]ict into NBT
    format

    Code snippet of typical usage:
    >>> buffer = io.BytesIO()
    >>> Writer.save(buffer, TAG_SHORT, "i", -15)
    >>> Writer.save(buffer, TAG_LIST, "keys", ["a", "b"])
    """

    @staticmethod
    def save(entry, kind, name, value):
        """Record (name, value) pair, considering value's kind, into binary
        flow
        """
        # Refine kind for a list
        if kind == TAG_LIST:
            if value.get_kind() == TAG_BYTE:
                kind = _TAG_BYTE_ARRAY
            elif value.get_kind() == TAG_INT:
                kind = _TAG_INT_ARRAY

        if type(entry) == type(str()):
            flow = gzip.open(entry, "wb")
        else:
            flow = entry

        # Write kind, then name, then value
        low.write_byte(flow, kind)
        low.write_string(flow, name)
        Writer.writers[kind](flow, value)

        if type(entry) == type(str()):
            flow.close()


    @staticmethod
    def _save_dict(flow, value):
        for key in value:
            Writer.save(flow, value.get_kind(key), key, value[key])
        low.write_byte(flow, _TAG_NONE)


    @staticmethod
    def _save_list(flow, value):
        # Refine elements kind in case of a list of lists
        inner_kind = value.get_kind()
        if inner_kind == TAG_LIST:
            byte_only = True
            int_only = True
            for inner_v in value:
                inner_inner_kind = inner_v.get_kind()
                if inner_inner_kind is not None:
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
    def load(entry):
        """Read (kind, name, value) triple from binary flow
        """
        result = None # (kind, name, value)

        if type(entry) == type(str()):
            flow = gzip.open(entry, "rb")
        else:
            flow = entry

        kind = low.read_byte(flow)
        if kind != _TAG_NONE:
            name = low.read_string(flow)

            value = Reader.readers[kind](flow)

            if kind in [_TAG_BYTE_ARRAY, _TAG_INT_ARRAY]:
                kind = TAG_LIST
            result = (kind, name, value)

        if type(entry) == type(str()):
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

        if kind in [_TAG_BYTE_ARRAY, _TAG_INT_ARRAY]:
            kind = TAG_LIST
        result.set_kind(kind)

        for i in range(count):
            result.append(reader(flow))

        return result


    @staticmethod
    def _load_list_byte(flow):
        result = convert(low.read_byte_array(flow))[1]
        result.set_kind(TAG_BYTE)

        return result


    @staticmethod
    def _load_list_int(flow):
        result = convert(low.read_int_array(flow))[1]
        result.set_kind(TAG_INT)

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

    def pretty(self, name = "", level = 0):
        raise NotImplementedError


    def save(self, flow):
        raise NotImplementedError



class Dict(Container, collections.MutableMapping):
    """Statically typed associative container indexed by string identifiers
    >>> D = Dict()
    >>> D.set_kind("abc", TAG_INT)
    >>> D["abc"] = 5
    >>> D["abc"] = 5.0
    ValueError : wrong type
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
        del self._pairs[key]


    def __getitem__(self, key):
        return self._pairs[key].item


    def __setitem__(self, key, value):
        if key in self:
            kind = self._pairs[key].kind
        else:
            kind, value = convert(value)

        if not is_accepted(kind, value):
            raise ValueError
        else:
            self._pairs[key] = _DictPair(kind, value)


    def __iter__(self):
        return iter(self._pairs)


    def __len__(self):
        return len(self._pairs)


    def __repr__(self):
        return self.pretty()


    def get_kind(self, key):
        """Get type of element identified by the corresponding key
        """
        result = self._pairs[key].kind

        return result


    def set_kind(self, key, kind):
        """Set type of element identified by the corresponding key. If there
        is currently no element pointed by the key, the value is set to the
        default one. Otherwise, compatibility between the current value and
        new kind is checked.
        """
        if kind not in _VALID_TAGS:
            raise ValueError("Kind {} cannot be used as an actual type".format(kind))
        elif key in self._pairs:
            pair = self._pairs[key]
            if not is_accepted(kind, pair.item):
                raise KeyError
            else:
                self._pairs[key] = _DictPair(kind, pair.item)
        else:
            self._pairs[key] = _DictPair(kind, default_value(kind))


    def pretty(self, name = "", level = 0):
        result = "{: >{fill}}TAG_Compound({}): {{\n".format("", repr(name), fill = 2 * level)

        for key in self._pairs:
            result += pretty(self._pairs[key].item, self._pairs[key].kind, key, level + 1)
            result += "\n"

        result += "{: >{fill}}}}".format("", fill = 2 * level)

        return result


    def save(self, flow):
        Writer.save(flow, TAG_COMPOUND, "", self)



class List(Container, collections.MutableSequence):
    """Indexed set of elements that share the same kind
    """

    __slots__ = ('_kind', '_items')


    def __init__(self):
        self._kind = None
        self._items = list()


    def __delitem__(self, key):
        del self._items[key]


    def __getitem__(self, key):
        return self._items[key]


    def __setitem__(self, key, value):
        if self._kind is None:
            self._kind = default_kind(value)

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
            self._kind = default_kind(value)

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


    def pretty(self, name = "", level = 0):
        result = "{: >{fill}}TAG_List({}) of {}: ".format("", repr(name), tag_name(self._kind), fill = 2 * level)

        if self._kind not in (TAG_LIST, TAG_COMPOUND):
            result += "[" + ", ".join(map(str, self._items)) + "]\n"
        else:
            result += "{\n"

            for key in range(len(self._items)):
                result += pretty(self._items[key], self._kind, key, level + 1)
                result += "\n"

            result += "{: >{fill}}}}".format("", fill = 2 * level)


        return result


    def save(self, flow):
        Writer.save(flow, TAG_LIST, "", self)


def load(flow):
    """Read NBT value from flow

    See Reader.load in order to also access name and kind of the read value.
    """
    return Reader.load(flow)[2]


save = Writer.save


if __name__ == "__main__":
    D = Dict()

    D["a"] = 15
    D.set_kind("a", TAG_BYTE)

    D.set_kind("b", TAG_COMPOUND)
    print(D)

    D.set_kind("c", TAG_LIST)
    D["c"].append(5)
    D["c"].append(7)
    D["c"].append(6)
    D["c"].set_kind(TAG_SHORT)
    print(D)

    D["d"] = List()
    D["d"].set_kind(TAG_LIST)
    D["d"].append(List())
    D["d"][0].set_kind(TAG_INT)
    D["d"].append(List())
    D["d"][1].set_kind(TAG_INT)
    print(D)

    import io
    BUFFER = io.BytesIO()
    D.save(BUFFER)

    BUFFER.seek(0)
    F = load(BUFFER)
    print(F)

    print(D == F)
