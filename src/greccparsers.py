#!/usr/bin/env python
## A collection of parsing functions used at the Johnson laboratory.
# These are collected in one place so they can be used by multiple other pieces of code.

import sys
sys.path.append("/Data/vtrak1/SysAdmin/production/python")

## Parses a protocol info file and returns a dictionary of applicable variables.
def protocol_parse(filename, protocol):
    """Parses a protocol info file and returns a list of dictionaries of these
    variables sorted by run number.
    """
    
    f = file(filename, 'r')
    varnames = f.readline().strip().split(",")
    targetline = [l.strip().split(",") for l in f if l.startswith(protocol)][0]
    f.close()
    return dict( zip(varnames,targetline) )

## Parses a subject info file, returns a dictionary of visit variables.
def subject_parse(filename, subid):
    """Parses a subject info file, returns a dictionary of visit variables."""
    
    varnames = [ 'subid', 'runs', 'pfiles', 'tasks', 'hasfmap', 'refdat_files' ]
    f = file(filename, 'r')
    matches = []
    for line in f:
        row = [ i.strip() for i in line.split(',') ]
        if row[0] == subid:
            matches.append( row )    
    f.close()
    if not matches:
        raise IOError('No matching subject found in subject info csv file')
    matches.sort(lambda x, y: cmp(x[1],y[1]))
    return dict( zip(varnames,zip(*matches)) )


if __name__ == '__main__':
    import grecc_parsers
    help(grecc_parsers)
