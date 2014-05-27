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

def iterate(nid, but):
    """Efficient iterator of a bounded box, in order to limitate the number of
    files open, or chunks loaded.

    This iterator also respects the order of chunks inside a Region file.
    """
    xn, yn, zn = nid
    xb, yb, zb = but

    for rz in range(zn >> 9, (zb + 511) >> 9):
        for rx in range(xn >> 9, (xb + 511) >> 9):
            for cz in range(max(32 * rz, zn >> 4), min(32 * (rz + 1), (zb + 15) >> 4)):
                for cx in range(max(32 * rx, xn >> 4), min(32 * (rx + 1), (xb + 15) >> 4)):
                    for cy in range(yn >> 4, (yb + 15) >> 4):
                        for x in range(max(16 * cx, xn), min(16 * (cx + 1), xb)):
                            for z in range(max(16 * cz, zn), min(16 * (cz + 1), zb)):
                                for y in range(max(16 * cy, yn), min(16 * (cy + 1), yb)):
                                    yield (x, y, z)
