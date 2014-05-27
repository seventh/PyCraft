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

"""Wrapper of a Minecraft world (in its stored form)

A Minecraft world is organized hierachically, the top level being a Level
(the Overworld, the Nether or the End) composed of various Region files
(.mca extension) split into Chunks (column of terrain on the base of a
16x16 square) which are finally made of up to 16 Sections (a 16-block high
cube of terrain)
"""

import logging
import os
import re
from . import anvil
from . import con
from . import geometry


class World(object):
    """A Minecraft world
    """

    def __init__(self, path):
        self.path = path


    def level_ids(self):
        """Iterator over the identifiers of all the existing levels
        """
        root, dirs, files = next(os.walk(self.path))

        for directory in dirs:
            if directory == "region":
                yield 0
            else:
                matching = re.match("DIM(-?\d+)$", directory)
                if matching:
                    yield int(matching.groups()[0])


    def level(self, level_id):
        """Level of corresponding identifier
        """
        if level_id == 0:
            path = os.path.join(self.path, "region")
        else:
            path = os.path.join(self.path, "DIM{}".format(level_id))

        return Level(path)



class Level(object):
    """In Minecraft, a level can correspond to "the Overworld", "the Nether"
    or "the End", depending on the portals you may have created
    """

    def __init__(self, path):
        self.path = path


    def region_ids(self):
        root, dirs, files = next(os.walk(self.path))

        for region_name in files:
            matching = re.match("r\.(-?\d+)\.(-?\d+)\.mca$", region_name)
            if matching:
                rz = int(matching.groups()[0])
                rx = int(matching.groups()[1])

                yield (rz, rx)


    def region(self, region_id):
        rz, rx = region_id
        path = os.path.join(self.path, "r.{}.{}.mca".format(rz, rx))

        return Region(path)


    def spots(self):
        """Iterate over all the spots of already existing blocks
        """
        for region_id in self.region_ids():
            region = self.region(region_id)
            z_0 = region_id[0] << 9
            x_0 = region_id[1] << 9
            for spot in region.spots():
                yield geometry.Triple(x_0 + spot.x,
                                      spot.y,
                                      z_0 + spot.z)


    def get_block(self, spot):
        """Return a (kind, type) tuple, representing block/data values
        """
        # Determine anvil file from coordinates
        rz = spot.z >> 9
        rx = spot.x >> 9

        region = self.region((rz, rx))
        return region.get_block(spot)



class Region(object):
    """A wrapper of file formatted along Region format
    """

    def __init__(self, path):
        self.path = path
        self.content = anvil.open(path)


    def chunk_ids(self):
        for index in self.content.indexes():
            yield index


    def chunk(self, chunk_id):
        data = self.content.load_chunk(chunk_id)
        return Chunk(data)


    def spots(self):
        """Iterate over all the spots of already existing blocks
        """
        for chunk_id in self.chunk_ids():
            chunk = self.chunk(chunk_id)
            z_0 = (chunk_id // 16) << 4
            x_0 = (chunk_id  % 16) << 4
            for spot in chunk.spots():
                yield geometry.Triple(x_0 + spot.x,
                                      spot.y,
                                      z_0 + spot.z)



class Chunk(object):
    """A column of terrain of the base of a 16x16 square (an entry of a Region)
    """

    def __init__(self, data):
        self.data = data


    def section_ids(self):
        for section_id in range(len(self.data["Level"]["Sections"])):
            yield section_id


    def section(self, section_id):
        return Section(self.data["Level"]["Sections"][section_id])


    def spots(self):
        """Iterate over all the spots of already existing blocks
        """
        for section_id in self.section_ids():
            y_0 = self.data["Level"]["Sections"][section_id]["Y"] << 4
            for spot in self.section(section_id).spots():
                yield geometry.Triple(spot.x, y_0 + spot.y, spot.z)



class Section(object):
    """A square of 16x16x16 blocks
    """

    def __init__(self, data):
        self.data = data


    def get_block(self, spot):
        """Return a (kind, type) tuple, representing block/data values
        """
        index = spot.x + 16 * (spot.z + 16 * spot.y)

        # Getting the block id
        block_id = self.data["Blocks"][index]
        if "Add" in self.data:
            additional = self.data["Add"][index // 2]
            if index % 2 == 0:
                additional >>= 4
            additional &= 0x0F
            block_id += additional << 8

        # Getting the block data
        data_id = self.data["Data"][index // 2]
        if index % 2 == 0:
            data_id >>= 4
        data_id &= 0x0F

        return (block_id, data_id)


    def spots(self):
        """Iterate over all the spots of already existing blocks
        """
        for y in range(16):
            for z in range(16):
                for x in range(16):
                    yield geometry.Triple(x, y, z)



class LevelAccessor(object):
    """Manage accesses to a single level
    """
