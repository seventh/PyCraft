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

"""Minecraft Region file format

A Region file is mainly an indexed container of NBT encoded data, structured
in sectors of 4 Kib. Its description can be found here:

  http://www.minecraftwiki.net/wiki/Region_file_format

The values of the container are "Chunks", i.e. a structure representing the
terrain and the entities of a single x=16 * y=256 * z=16 area. They are here
provided as con.Dict objects.
"""

import gzip
import io
import logging
import os
import time
import zlib

from . import low
from . import con


# Number of octets in a so-called "sector"
_SECTOR_SIZE = 4096

# Number of 4-octets integers in a single sector
_NB_OF_ENTRIES = _SECTOR_SIZE // 4


class _ChunkMetaData(object):
    """Information concerning a single chunk stored in the index table of the
    region file.
    """

    __slots__ = ('_offset', '_length', '_timestamp')

    def __init__(self, location, timestamp):
        self._offset = 0
        self._length = 0
        self._timestamp = 0

        self.location = location
        self.timestamp = timestamp


    def __str__(self):
        result = "({}, {}, {})".format(self._offset,
                                       self._length,
                                       self._timestamp)
        return result


    @property
    def location(self):
        """4-bytes integer, mixing offset and size
        """
        result = (self._offset << 8) | self._length

        return result


    @location.setter
    def location(self, location):
        assert 0 <= location < 2 ** 32

        self._offset = (location & 0xFFFFFF00) >> 8
        self._length = location & 0xFF


    @property
    def position(self):
        """Offset, in bytes, from the start of the Region file
        """
        return self._offset << 12


    @property
    def offset(self):
        """Offset, in number of sectors, from the start of the Region file
        """
        return self._offset


    @offset.setter
    def offset(self, offset):
        assert 2 <= offset < 2 ** 24

        self._offset = offset


    @property
    def length(self):
        """Number of sectors occupied by the chunk
        """
        return self._length


    @length.setter
    def length(self, length):
        assert 0 <= length < 2 ** 8

        self._length = length


    @property
    def timestamp(self):
        """Date, in number of seconds since Epoch, of the last update
        """
        return self._timestamp


    @timestamp.setter
    def timestamp(self, timestamp):
        assert 0 <= timestamp < 2 ** 32

        self._timestamp = timestamp



class Region(object):
    """Low-level Region file wrapper.

    A Region is always edited in read/write mode. Modified loaded chunks shall
    be explicitely saved for modifications to be actually taken into account.
    """

    @staticmethod
    def open(flow):
        result = Region(flow)

        return result


    @staticmethod
    def open_file(path):
        flow = None
        try:
            flow = io.open(path, "rb+")
        except IOError:
            flow = io.open(path, "wb+")

        result = Region.open(flow)
        result._path = path

        return result


    def __init__(self, flow):
        self._path = None

        # Open file and determine its current size.
        self._flow = flow
        self._flow.seek(0, 2)
        self._nb_sectors = self._flow.tell() // _SECTOR_SIZE
        self._free_sectors = set(range(2, self._nb_sectors))
        self._toc = list()

        # Initialize empty files
        if self._nb_sectors == 0:
            self._nb_sectors = 2
            self._flow.write(b"\x00" * (self._nb_sectors * _SECTOR_SIZE))
            for i in range(_NB_OF_ENTRIES):
                self._toc.append(_ChunkMetaData(0, 0))

        # Otherwise, read table of contents
        else:
            self._flow.seek(0, 0)
            locations = low.read_int(self._flow, _NB_OF_ENTRIES)
            timestamps = low.read_int(self._flow, _NB_OF_ENTRIES)
            for i in range(_NB_OF_ENTRIES):
                meta = _ChunkMetaData(locations[i], timestamps[i])
                self._toc.append(meta)
                for used_sector in range(meta.offset, meta.offset + meta.length):
                    self._free_sectors.remove(used_sector)


    def __del__(self):
        if self._path is not None:
            self._flow.close()

            # Search for any referenced chunk
            for meta in self._toc:
                if meta.length != 0:
                    break
            else:
                logging.info("Removal of file {}".format(repr(self._path)))
                os.unlink(self._path)


    def load_chunk(self, index):
        """Chunk at corresponding index, or None if it does not exist
        """
        assert 0 <= index < 1024

        result = None

        meta = self._toc[index]
        if meta.length != 0:
            self._flow.seek(meta.position, 0)
            size = low.read_int(self._flow)
            compression_type = low.read_byte(self._flow)
            if compression_type == 1:
                uncompressed_flow = gzip.GzipFile(file_obj = self._flow)
            elif compression_type == 2:
                uncompressed_flow = io.BytesIO(zlib.decompress(self._flow.read(size - 1)))
            result = con.load(uncompressed_flow)

        return result


    def save_chunk(self, index, value):
        """Update chunk at corresponding index
        """
        assert 0 <= index < 1024

        meta = self._toc[index]

        # First, free previous chunk if any
        self._free_used_sectors(meta)

        # Encode data
        uncompressed_flow = io.BytesIO()
        con.save(uncompressed_flow, value)
        uncompressed_flow.seek(0, 0)
        compressed_flow = zlib.compress(uncompressed_flow.getvalue())

        # Search for enough space
        total_length = len(compressed_flow) + 5
        nb_of_needed_sectors = (total_length + _SECTOR_SIZE - 1) // _SECTOR_SIZE

        first = None
        for i in self._free_sectors:
            for j in range(i, i + nb_of_needed_sectors):
                if j not in self._free_sectors:
                    break
            else:
                first = i

            if first is not None:
                break

        # Update metadata
        meta.length = nb_of_needed_sectors
        meta.timestamp = int(time.time())

        if first is None:
            meta.offset = self._nb_sectors
            self._nb_sectors += nb_of_needed_sectors
        else:
            meta.offset = first
            for used_sector in range(meta.offset, meta.offset + meta.length):
                self._free_sectors.remove(used_sector)

        # Update TOC
        self._write_meta(index, meta)

        # Write data
        self._flow.seek(meta.position, 0)
        low.write_int(self._flow, total_length - 4)
        low.write_byte(self._flow, 2)
        self._flow.write(compressed_flow)

        # Add some null bytes in case of newly allocated sectors
        if first is None:
            self._flow.write(b"\x00" * ((-total_length) % _SECTOR_SIZE))


    def wipe_chunk(self, index):
        """Remove chunk at corresponding index
        """
        assert 0 <= index < 1024

        meta = self._toc[index]
        if meta.length != 0:
            self._free_used_sectors(meta)
            meta.length = 0
            meta.timestamp = int(time.time())

            self._write_meta(index, meta)


    def _free_used_sectors(self, meta):
        """Add sectors identified by metadata to the set of free sectors
        """
        for freed_sector in range(meta.offset, meta.offset + meta.length):
            self._free_sectors.add(freed_sector)


    def _write_meta(self, index, meta):
        """Write MetaData for chunk at corresponding index
        """
        assert 0 <= index < _NB_OF_ENTRIES

        self._flow.seek(4 * index, 0)
        low.write_int(self._flow, meta.location)
        self._flow.seek(_SECTOR_SIZE + 4 * index, 0)
        low.write_int(self._flow, meta.timestamp)


    @property
    def path(self):
        """Pathname of the currently edited Region file
        """
        return self._path


    def __iter__(self):
        """Iterate over stored chunks
        """
        for index in self.indexes():
            yield self.load_chunk(index)


    def __len__(self):
        return len(list(self.indexes()))


    def indexes(self):
        """Iterator over the indexes of stored chunks
        """
        for index in range(_NB_OF_ENTRIES):
            if self._toc[index].length != 0:
                yield index



def open(entry):
    """Wrap entry content into a Region object. entry can either be a pathname
    or a binary flow.
    """
    result = None

    if isinstance(entry, str):
        result = Region.open_file(entry)
    else:
        result = Region.open(entry)

    return result
