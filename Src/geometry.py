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

"""Elements of 3-D geometry
"""

class Triple(object):
    """Can either be a 3-D space coordinate, speed, and so on
    """

    __slots__ = ('_x', '_y', '_z')

    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z


    def __iter__(self):
        yield self._x
        yield self._y
        yield self._z


    def __str__(self):
        result = '({}, {}, {})'.format(self._x, self._y, self._z)
        return result


    @property
    def x(self):
        """Second coordinate in plan, growing from West to East
        """
        return self._x


    @x.setter
    def x(self, x):
        self._x = x


    @property
    def y(self):
        """Height, or altitude
        """
        return self._y


    @y.setter
    def y(self, y):
        self._y = y


    @property
    def z(self):
        """First coordinate in plan, growing from North to South
        """
        return self._z


    @z.setter
    def z(self, z):
        self._z = z
