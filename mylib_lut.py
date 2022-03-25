#!/usr/bin/env python
#
# Author: Patrick Brockmann
# Contact: Patrick.Brockmann@cea.fr
# $Date: $
# $Name: $
# $Revision: $
# History:
# Modification:
#

import __main__

import string
import vtk

from mylib_misc import *

################################################################
def interpolate_values(v1, v2, n):
    delta = (v2-v1)/(n+1)
    v = []
    for i in range(n+2):
        newv = v1+i*delta
        v.append(newv)
    return v

################################################################
def define_lut1(file, nbcolors):
    option_verbose = __main__.option_verbose

    my_print(option_verbose, '----------------------------')
    my_print(option_verbose, 'LookUpTable creation')
    my_print(option_verbose, "Spectrum color file : ", file)

    a = []
    r = []
    g = []
    b = []
    filespk = open(file, 'r')
    for line in filespk.readlines():
        words = line.split()
        if len(words) == 4:
            a.append(float(words[0]))
            r.append(float(words[1]))
            g.append(float(words[2]))
            b.append(float(words[3]))
    filespk.close()

    my_print(option_verbose, "Nb color defined: ", len(a))
    my_print(option_verbose, "Nb color to create: ", nbcolors)

    if nbcolors < len(a):
        my_print(option_verbose, "Warning!: Number of colors to defined lower")
        my_print(option_verbose,
                 "          than number of colors defined in the file.")

    for i in range(len(a)):
        a[i] = int((nbcolors-1)*a[i]/100+0.5)+1
        # my_print(option_verbose,"%d,%4.3f,%4.3f,%4.3f"%(a[i],r[i]/100,g[i]/100,b[i]/100))

    __main__.lut1.SetNumberOfTableValues(nbcolors)
    __main__.lut1.SetNumberOfColors(nbcolors)

    # my_print(option_verbose,"=============================")
    for i in range(len(a)-1):
        nvalues = a[i+1]-a[i]
        newr = interpolate_values(r[i], r[i+1], nvalues)
        newg = interpolate_values(g[i], g[i+1], nvalues)
        newb = interpolate_values(b[i], b[i+1], nvalues)
        for n in range(nvalues):
            # my_print(option_verbose,"%d,%4.3f,%4.3f,%4.3f"%(int(a[i]+n-1),newr[n]/100,newg[n]/100,newb[n]/100))
            __main__.lut1.SetTableValue(
                int(a[i]+n-1), newr[n]/100, newg[n]/100, newb[n]/100, 1)
    # my_print(option_verbose,"%d,%4.3f,%4.3f,%4.3f"%(int(a[-1]-1),r[-1]/100,g[-1]/100,b[-1]/100))
    __main__.lut1.SetTableValue(
        int(a[-1]-1), r[-1]/100, g[-1]/100, b[-1]/100, 1)

    __main__.lut1.Build()

################################################################
