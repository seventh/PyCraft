PyCraft
=======

PyCraft is a high-quality Python_ library for offline edition of Minecraft_
worlds. High-quality, because it respects the spirit of the Python programming
language (i.e. it is *pythonic*), and because it also takes care of memory
consumption, which can be a huge problem during Minecraft world edition.
PyCraft complies with Python 3.3 specifications.

.. _Minecraft: http://www.minecraft.net
.. _Python: http://www.python.org

PyCraft is governed by the CeCILL-C_ license under French law and abiding by
the rules of distribution of free software.

.. _CeCILL-C: http://www.cecill.info

Quick and dirty: edit a NBT-formatted file
------------------------------------------

Here is an example of modifications that can be operated with PyCraft on a file
stored with NBT_ encoding format. NBT encoding is widely used in Minecraft.

.. _NBT: http://minecraft.gamepedia.com/NBT

::

   from pycraft import con

   # Load our favorite TAG_COMPOUND
   W = con.load("entry.nbt")

   # Add some meaningful information :)
   W[u"author"] = "Me, myself and I"
   W[u"date"] = "2014-02-26"

   # By default, ints are of kind TAG_LONG. Nobody likes show-offs
   W[u"nb_of_followers"] = 42
   W.set_kind(u"nb_of_followers", con.TAG_BYTE)

   # Save it back
   W.save("entry.nbt")

Known limitations of using PyCraft with a Python 2.7 interpreter
----------------------------------------------------------------

The current section lists the packages of PyCraft that won't work if you use a
Python 2.7 interpreter:

* Not a single one.
