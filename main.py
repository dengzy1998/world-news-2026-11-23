#!/usr/bin/env python3
"""Deliver the front page image to the grading folder.

The repository holds the finished page as ``entry.png`` next to this
file. The grader expects it at ``/output/entry.png``, so this script
places a copy there. Standard library only: no third-party packages,
no network, nothing to install. If the page is missing, the script
says so on stderr and exits with status 1 instead of shipping
nothing.
"""

import os
import shutil
import sys

IMAGE_NAME = "entry.png"
OUTPUT_DIR = "/output"


def source_path():
    folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, IMAGE_NAME)


def deliver(src):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    dest = os.path.join(OUTPUT_DIR, IMAGE_NAME)
    shutil.copyfile(src, dest)
    return dest, os.path.getsize(dest)


def main():
    src = source_path()
    if not os.path.isfile(src):
        print("no page image at %s" % src, file=sys.stderr)
        return 1
    dest, nbytes = deliver(src)
    print("delivered %s (%d bytes) to %s" % (IMAGE_NAME, nbytes, dest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
