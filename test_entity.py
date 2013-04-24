#!/usr/bin/python3

import logging
from Src import nbt, entity

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    D = nbt.read("entities.nbt")
    for ENTITY in D[""]["entities"]:
        X = nbt.convert(ENTITY)
        E = entity.read(X)
        logging.info("{1:0>32x} : {0:}".format(type(E), E.uuid))
