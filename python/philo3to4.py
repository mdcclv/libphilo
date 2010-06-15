#!/usr/bin/python
import re
import sys
import os

_patterns = (
    "FIELDS",
    "TYPE_LENGTH",
    "BLK_SIZE",
    "FREQ1_LENGTH",
    "FREQ2_LENGTH",
    "OFFST_LENGTH",
    "NEGATIVES",
    "DEPENDENCIES",
    "BITLENGTHS"
    )


def convertdb(dbs_path):
    results = {}
    ret = ""
    fh = open(dbs_path)
    for line in fh.readlines():
        for pattern in _patterns:
            m = re.search(pattern + r"\s+(\S+)",line)
            if m:
                results[pattern] = m.group(1)
    for pattern in _patterns:
        ret += "#define " +pattern + " " + results[pattern] + "\n" 
    return ret

if __name__ == "__main__":
    print convertdb(sys.argv[1])
