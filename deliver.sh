#!/bin/bash

# Identify release tag

function last_tag_minor()
{
    git tag -l $1"*" | sort -rV | head -n 1 | cut -c 7
}

function get_new_tag()
{
    MAJOR=$( date +%y%m%d )

    MINOR=$( last_tag_minor ${MAJOR} )
    MINOR=${MINOR:=-1}
    let 'MINOR=MINOR+1'

    echo ${MAJOR}${MINOR}
}

function is_index_clean()
{
    test -z "$( git status -s )"
}

function fail()
{
    echo "Aborting delivery: $1"
    exit 0
}

###

TAG=$( get_new_tag )

is_index_clean || fail "repository shall be clean before delivery"

read -p "Do you really want to create a new version (${TAG})? [y/N] " -n 1
[ ${#REPLY} -ne 0 ] && echo ""
[[ ! ${REPLY} =~ ^[yY]$ ]] && fail "exiting"

COMMIT_MSG="RELEASE ${TAG}"

echo "Releasing version ${TAG} ... "

cat > setup.py <<EOF
#-*- coding: utf-8 -*-
"""Setup script for distributing PyCraft

Typical usage scenarios can either be:
 $> python3 setup.py clean
 $> python3 setup.py sdist --format=bztar
 $> python3 setup.py register
"""

from distutils.core import setup


if __name__ == "__main__":
    setup(
        name = "PyCraft",
        version = "<VERSION>",
        license = "GPLv3",
        description = "High quality Minecraft world editor",
        author = "Guillaume Lemaître",
        author_email = "guillaume.lemaitre@gmail.com",
        url = "http://github.com/seventh/PyCraft",
        packages = ["pycraft"],
        package_dir = {"pycraft": "Src"},
        data_files = [
            ("/usr/share/doc/pycraft", [
                    "Doc/AUTHORS",
                    "Doc/CHANGELOG",
                    "Doc/COPYING",
                    "README",
                    ]),
            ],
        classifiers = [
            "Development Status :: 2 - Pre-Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            ],
        keywords = ["Minecraft"],

        )
EOF
sed -i -e 's,<VERSION>,'${TAG}',' setup.py

ln Doc/README .

python3 setup.py sdist --format=bztar || fail "invalid configuration"
git add dist/PyCraft-${TAG}.tar.bz2
git commit -q -m "${COMMIT_MSG}"
git tag ${TAG}

rm MANIFEST README setup.py
echo "done."
