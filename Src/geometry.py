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
