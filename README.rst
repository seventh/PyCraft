PyCraft
=======

PyCraft is a high-quality Python_ library for Minecraft_ world offline
edition. High-quality, because it respects the spirit of the Python
programming language (*pythonic*), and because it also takes care of memory
consumption, which can be a huge problem during Minecraft world edition.

.. _Minecraft: http://www.minecraft.net
.. _Python: http://www.python.org

PyCraft respects Python 3.3 specifications; nevertheless it is currently
also compliant with Python 2.7 specifications.

PyCraft is governed by the CeCILL-C_ license under French law and abiding by
the rules of distribution of free software.

.. _CeCILL-C: http://www.cecill.info

Quick and dirty: edit a NBT file format
---------------------------------------

::
   
   from pycraft import con

   with open("input.nbt", "rb") as world:
     W = con.load(word)
