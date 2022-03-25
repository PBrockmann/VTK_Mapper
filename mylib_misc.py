#!/usr/bin/env python
#
# Author: Patrick Brockmann
# Contact: Patrick.Brockmann@ipsl.jussieu.fr
# $Date: $
# $Name: $
# $Revision: $
# History:
# Modification:
#

################################################################
def my_print(verbose, *args):
    if verbose or verbose == "active":
        for i in range(len(args)):
            print("%s" % str(args[i]), end=" ")
        print()

################################################################
def scalefactor(var):
    scalefactor = 1.0
    valuerange = max(var)-min(var)
    if valuerange == 0:
        return scalefactor

    while abs(valuerange*scalefactor) < 1000.0:
        scalefactor = scalefactor*100.0
        #print("inf %f %1.0e %g"%(valuerange,scalefactor,valuerange*scalefactor))
    while abs(valuerange*scalefactor) > 1000.0:
        scalefactor = scalefactor/100.0
        #print("sup %f %1.0e %g"%(valuerange,scalefactor,valuerange*scalefactor))
    return scalefactor

################################################################
