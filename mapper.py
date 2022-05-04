#!/usr/bin/env python

import string
import re
import sys
from mylib_save import *
from mylib_text import *
from mylib_axis import *
from mylib_grid import *
from mylib_equator import *
from mylib_boundaries import *
from mylib_continents import *
from mylib_misc import *
from mylib_lut import *
import vtk
import os.path
import numpy
import netCDF4
import pickle
license = """
Copyright Patrick Brockmann (CEA / LSCE) 
          Patrick.Brockmann@lsce.ipsl.fr

This software is a computer program whose purpose is to 
display variables from model output with regular, curvilinear 
or generic grid description. Those grid are described by respecting 
the Climate and Forecast (CF) Metadata Convention of the netCDF format.

This software is governed by the CeCILL license under French law and
abiding by the rules of distribution of free software.  You can  use, 
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
http://www.cecill.info. 

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

"""

credits = """######################################################
VTK_Mapper : A mapping application using netCDF4, NumPy, VTK, Qt
######################################################
"""
#


##################################
PATHROOT = os.path.dirname(sys.argv[0])

##################################
usage = """######################################################
Usage:  mapper.py [-h]
        [-p projection] [-a actor]
        [-n levels_nb] [-l min:max:delta]
        [--bg r,g,b] [--fg r,g,b]
        [--camera camera_object_file] [--color spectrum_color_file]
        [--kindex index] [--lindex index]
        [--continents] [--continents_file file] [--continents_color r,g,b] [--continents_width width]
        [--boundaries] [--boundaries_color r,g,b] [--boundaries_width width]
        [--equator] [--equator_color r,g,b] [--equator_width width]
        [--grid] [--grid_color r,g,b] [--grid_width width] [--grid_delta delta]
        [--label_format format]
        [--verbose] [--prefix prefixfilename] [--offscreen] [-x] [--interface]
        [--gridfile gridCF_file]
        var_file var
"""

options = """######################################################
Options:
        -h, -?, --help, -help
                Print this manual
        -x, --interface
                Run the application with the GUI interface
        -p, --projection
                Projection to choose in (linear,orthographic)
        -a, --actor
                Actor to choose in :
                        isofill,cell,cellbounds,isoline1,isoline2
                Other accepted syntax are:
                        isofilled,cells,,cellsbounds,isolines1,isolines2
        -v, --verbose
                Verbose mode
        -n, --levels_nb
                Number of levels should be in [3:100] 
        -l, --levels
                Levels expressed as minimum:maximum:delta
                Example: -l 2:32:4 from 2 to 32 by step of 4
                         -l 0:0:4 from min to max by step of 4
        --bg, --background
                Background color expressed as red, green, blue values in [0:1]
                Example: --bg 0.3,0.3,0.3
        --fg, --foreground
                Foreground color expressed as red, green, blue values in [0:1]
                Example: --fg 1.0,1.0,1.0
        --op, --operation
                Operation to apply on variable (use quote)
                Example: --op 'var*86400'
                         --op '(var*100)+273.15'
        --camera
                Camera object file
        --color
                Spectrum color file
                This file follows the coding of the ferret percent method which
                defines points along an abstract path in RGB color space that runs
                from 0 to 100 percent. Search Palette/by_percent in
                http://ferret.wrc.noaa.gov/Ferret/Documentation
        --kindex
                Index for the 3th dimension (vertical axis)
                of the variable to plot [1:n]
        --lindex
                Index for the 4th dimension (time axis)
                of the variable to plot [1:n]
        --boundaries, --continents, --equator, --grid
                Drawn if this option is present
        --boundaries_color, --continents_color, --equator_color, --grid_color
                Color expressed as red, green, blue values in [0:1]
                Example: --boundaries_color 0.,0.,0.3
        --boundaries_width, --continents_width, --equator_width, --grid_width
                Lines width expressed in [1:5]
        --continents_file
                NetCDF continents file (CONT_LON,CONT_LAT variables)
        --grid_delta
                Delta for grid lines (default=30)
        --label_format 
                format (default="%6.2g")
        --prefix
                Filename prefix used when PNG and PDF file
                are saved (default=picture)
        --gridfile
                NetCDF file at the CF convention from where the grid is read.
                If present, the "mask" variable is read and used in combinaison
                with the mask deduced from the variable.
                If gridfile not present, use only self descriptions of the variable.
        --ratioxy
                Set the ratio between height and width
                for linear projection (default=1.0)
        --offscreen
                Produce a PNG and a PDF file in a offscreen mode
"""

interactions = """######################################################
Interactions:
        ---------------------
        * Press e to quit
        ---------------------
        * Press u to save the renderwindow as a PNG image
        ---------------------
        * Press p to pick a cell and get its indices and its value
          (available only with actors cell or cellbounds)
        ---------------------
        * Press c to capture camera position and save a camera.sty file
        ---------------------
        * Press , to move backward on k dimension
        * Press ; to move forward on k dimension
        ---------------------
        * Press - or : to move backward on l dimension
        * Press + or ! to move forward on l dimension
        ---------------------
        * Press v to save the renderwindow as a PDF file
        ---------------------
        * Press c to init or re-init size of the renderwindow
        ---------------------
        * Press o to save the object as a VTK object
          (explore use of Paraview by loading this object file)
        ---------------------
        * Press 1 to switch between different actors
          isolines1-->isolines2-->cells-->cellbounds-->isofill-->isolines1
        ---------------------
        * Press 2 to activate/inactivate display of boundaries
        ---------------------
        * Press 4 to activate/inactivate display of continents
        ---------------------
        * Press 5 to activate/inactivate display of equator
        ---------------------
        * Press 6 to activate/inactivate display of grid
        ---------------------
        * Press 7 to load the camera file
        ---------------------
        * Press ? to get this help
######################################################
"""

##################################
command = {}
command['argprogram'] = "mapper.py"

##################################
option_projection = 'linear'
option_actor = 'cells'
option_levels_nb = 15
option_levels_nb_specified = 1
option_verbose = 0
option_bg = [1, 1, 1]
option_fg = [0, 0, 0]
option_op = None
kindex = 0
lindex = 0
camera_filename = None
color_filename = PATHROOT+'/colors/grads.spk'
option_boundaries_active = 0
option_boundaries_color_user = [1, 0, 1]
option_boundaries_width = 2
option_continents_active = 0
option_continents_file = None
option_continents_color_user = [0, 0, 1]
option_continents_width = 1
option_grid_delta = 10
option_grid_active = 0
option_grid_color_user = [1, 0, 0]
option_grid_width = 1
option_equator_active = 0
option_equator_color_user = [0, 0, 0]
option_equator_width = 2
option_label_format = '%6.2g'
option_prefix = 'picture'
option_gridfile = 0
option_ratioxy = 1.0
option_offscreen = 0
option_interface = 0
while len(sys.argv[1:]) != 0:
    if sys.argv[1] in ('-h', '--help'):
        del(sys.argv[1])
        print(usage + options)
        sys.exit(1)
    elif sys.argv[1] in ('-p', '--projection'):
        command['--projection'] = sys.argv[2]
        option_projection = sys.argv[2]
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] in ('-a', '--actor'):
        command['--actor'] = sys.argv[2]
        option_actor = sys.argv[2]
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] in ('-v', '--verbose'):
        command['--verbose'] = ''
        option_verbose = 1
        del(sys.argv[1])
    elif sys.argv[1] in ('-x', '--interface'):
        command['--interface'] = ''
        option_interface = 1
        del(sys.argv[1])
    elif sys.argv[1] in ('-n', '--levels_nb'):
        command['--levels_nb'] = sys.argv[2]
        option_levels_nb = int(sys.argv[2])
        option_levels_nb_specified = 1
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] in ('-l', '--levels'):
        command['--levels'] = sys.argv[2]
        option_levels = sys.argv[2].split(':')
        option_levels_nb_specified = 0
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] in ('--bg', '--background'):
        command['--background'] = sys.argv[2]
        option_bg = sys.argv[2].split(',')
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] in ('--fg', '--foreground'):
        command['--foreground'] = sys.argv[2]
        option_fg = sys.argv[2].split(',')
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] in ('--op', '--operation'):
        command['--operation'] = sys.argv[2]
        option_op = sys.argv[2]
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--kindex':
        command['--kindex'] = sys.argv[2]
        kindex = int(sys.argv[2])-1
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--lindex':
        command['--lindex'] = sys.argv[2]
        lindex = int(sys.argv[2])
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--camera':
        command['--camera'] = sys.argv[2]
        camera_filename = sys.argv[2]
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--color':
        command['--color'] = sys.argv[2]
        color_filename = sys.argv[2]
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--continents':
        command['--continents'] = ''
        option_continents_active = 1
        del(sys.argv[1])
    elif sys.argv[1] == '--continents_file':
        command['--continents_file'] = sys.argv[2]
        option_continents_active = 1
        option_continents_file = sys.argv[2]
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--continents_color':
        command['--continents_color'] = sys.argv[2]
        option_continents_color_user = sys.argv[2].split(',')
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--continents_width':
        command['--continents_width'] = sys.argv[2]
        option_continents_width = int(sys.argv[2])
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--boundaries':
        command['--boundaries'] = ''
        option_boundaries_active = 1
        del(sys.argv[1])
    elif sys.argv[1] == '--boundaries_color':
        command['--boundaries_color'] = sys.argv[2]
        option_boundaries_active = 1
        option_boundaries_color_user = sys.argv[2].split(',')
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--boundaries_width':
        command['--boundaries_width'] = sys.argv[2]
        option_boundaries_active = 1
        option_boundaries_width = int(sys.argv[2])
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--equator':
        command['--equator'] = ''
        option_equator_active = 1
        del(sys.argv[1])
    elif sys.argv[1] == '--equator_color':
        command['--equator_color'] = sys.argv[2]
        option_equator_active = 1
        option_equator_color_user = sys.argv[2].split(',')
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--equator_width':
        command['--equator_width'] = sys.argv[2]
        option_equator_active = 1
        option_equator_width = int(sys.argv[2])
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--grid':
        command['--grid'] = ''
        option_grid_active = 1
        del(sys.argv[1])
    elif sys.argv[1] == '--grid_delta':
        command['--grid_delta'] = sys.argv[2]
        option_grid_active = 1
        option_grid_delta = int(sys.argv[2])
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--grid_color':
        command['--grid_color'] = sys.argv[2]
        option_grid_active = 1
        option_grid_color_user = sys.argv[2].split(',')
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--grid_width':
        command['--grid_width'] = sys.argv[2]
        option_grid_active = 1
        option_grid_width = int(sys.argv[2])
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--label_format':
        command['--label_format'] = sys.argv[2]
        option_label_format = sys.argv[2]
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--prefix':
        command['--prefix'] = sys.argv[2]
        option_prefix = sys.argv[2]
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--gridfile':
        command['--gridfile'] = sys.argv[2]
        option_gridfile = 1
        gridfilename = sys.argv[2]
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--ratioxy':
        command['--ratioxy'] = sys.argv[2]
        option_ratioxy = float(sys.argv[2])
        del(sys.argv[1])
        del(sys.argv[1])
    elif sys.argv[1] == '--offscreen':
        command['--offscreen'] = ''
        option_offscreen = 1
        option_interface = 0
        del(sys.argv[1])
    elif re.match('-', sys.argv[1]):
        print('option inconnu')
        break
    else:
        break

if len(sys.argv[1:]) != 2:
    print(usage + options)
    sys.exit(1)

command['argvarfile'] = sys.argv[1]
command['argvarname'] = sys.argv[2]

################################################################
# Transform and verify arguments
# -------------------------
if option_actor not in ('isofill', 'isofilled',
                        'cell', 'cells',
                        'cellbounds', 'cellsbounds',
                        'isoline1', 'isolines1',
                        'isoline2', 'isolines2'):
    print(usage + options)
    sys.exit(1)

# -------------------------
if option_projection not in ('linear', 'orthographic'):
    print(usage + options)
    sys.exit(1)

# -------------------------
if option_levels_nb_specified:
    if not(2 < option_levels_nb < 101):
        print(usage + options)
        sys.exit(1)
    else:
        levels_nb = option_levels_nb
else:
    if len(option_levels) != 3:
        print(usage + options)
        sys.exit(1)
    else:
        for i in range(len(option_levels)):
            option_levels[i] = float(option_levels[i])
        levels_min = option_levels[0]
        levels_max = option_levels[1]
        levels_delta = abs(option_levels[2])
    if (levels_max < levels_min) or (levels_delta == 0):
        print(usage + options)
        sys.exit(1)

# -------------------------
if len(option_bg) != 3:
    print(usage + options)
    sys.exit(1)
else:
    colorbg = []
    for i in range(len(option_bg)):
        colorbg.append(float(option_bg[i]))

# -------------------------
if len(option_fg) != 3:
    print(usage + options)
    sys.exit(1)
else:
    colorfg = []
    for i in range(len(option_fg)):
        colorfg.append(float(option_fg[i]))

# -------------------------
if len(option_continents_color_user) != 3:
    print(usage + options)
    sys.exit(1)
else:
    option_continents_color = []
    for i in range(len(option_continents_color_user)):
        option_continents_color.append(
            float(option_continents_color_user[i]))

# -------------------------
if len(option_boundaries_color_user) != 3:
    print(usage + options)
    sys.exit(1)
else:
    option_boundaries_color = []
    for i in range(len(option_boundaries_color_user)):
        option_boundaries_color.append(
            float(option_boundaries_color_user[i]))

# -------------------------
if len(option_grid_color_user) != 3:
    print(usage + options)
    sys.exit(1)
else:
    option_grid_color = []
    for i in range(len(option_grid_color_user)):
        option_grid_color.append(float(option_grid_color_user[i]))

# -------------------------
if len(option_equator_color_user) != 3:
    print(usage + options)
    sys.exit(1)
else:
    option_equator_color = []
    for i in range(len(option_grid_color_user)):
        option_equator_color.append(float(option_equator_color_user[i]))

################################################################
axisxticknb = axisyticknb = 7

################################################################
my_print(option_verbose, '----------------------------')
my_print(option_verbose, 'VTK Version', vtk.vtkVersion().GetVTKVersion())

################################################################
# Limit excursion of the vertex of the cell according to
# its center position

def limit_lon(blon, clon):
    clon = (clon+360*10) % 360
    clon = numpy.where(numpy.greater(clon, 180), clon-360, clon)
    clon = numpy.where(numpy.less(clon, -180), clon+360, clon)
    clon1 = numpy.zeros(blon.shape, numpy.float32)
    clon1 = numpy.ones(blon.shape, numpy.float32)*clon[..., None]

    blon = (blon+360*10) % 360
    blon = numpy.where(numpy.greater(blon, 180), blon-360, blon)
    blon = numpy.where(numpy.less(blon, -180), blon+360, blon)

    blon = numpy.where(numpy.greater(
        abs(blon-clon1), abs(blon+360-clon1)), blon+360, blon)
    blon = numpy.where(numpy.greater(
        abs(blon-clon1), abs(blon-360-clon1)), blon-360, blon)
    return blon

################################################################
def read_var_fromfile(file, varname, verbose=1):
    global varlongname, varunits, varshape
    global listvarname, listvarlongname, listvarunits, listvarshape, listvaraxis
    global dictvarsatt
    global kindex, lindex, lindex_max, kindex_max
    my_print(verbose, '----------------------------')
    my_print(verbose, 'Reading var: ', varname, ' from: ', file)
    my_print(verbose, 'Args: ', varname, file, kindex, lindex, option_op)
    listvarname = []
    listvarlongname = []
    listvarunits = []
    listvarshape = []
    listvaraxis = []
    dictvarsatt = {}
    try:
        f1 = netCDF4.Dataset(file)
        varobject = f1.variables[varname]
        try:
            varlongname = varobject.long_name
        except:
            varlongname = varname
        try:
            varunits = varobject.units
        except:
            varunits = ""
        try:
            varshape = str(varobject.shape)
        except:
            varshape = ""
        try:
            varaxis = str(varobject.axis)
        except:
            varaxis = ""

        listvarname = f1.variables.keys()
        for varname_item in listvarname:
            var_item = f1.variables[varname_item]
            try:
                varlongname_item = var_item.long_name
            except:
                varlongname_item = ""
            listvarlongname.append(varlongname_item)

            try:
                varunits_item = var_item.units
            except:
                varunits_item = ""
            listvarunits.append(varunits_item)
            try:
                varshape_item = str(var_item.shape)
            except:
                varshape_item = ""
            listvarshape.append(varshape_item)
            try:
                varaxis_item = str(var_item.dimension)
            except:
                varaxis_item = ""
            listvaraxis.append(varaxis_item)
            try:
                listvaratt_item = []
                for att in var_item.attributes.keys():
                    attribut_value = var_item.attributes.get(att)
                    # To get attribut presented as 1800. and not as an array [ 1800.,]
                    if str(type(attribut_value)) == "<type 'array'>":
                        listvaratt_item.append(
                            att+" : "+str(attribut_value[0]))
                    else:
                        listvaratt_item.append(att+" : "+str(attribut_value))
            except:
                listvaratt_item = []
            dictvarsatt[varname_item] = listvaratt_item

        my_print(verbose, 'var name: ', varname)
        my_print(verbose, 'var long name: ', varlongname)
        my_print(verbose, 'var units: ', varunits)
        my_print(verbose, 'var shape: ', varshape)

        vardimensions = varobject.dimensions
        my_print(verbose, 'var dimensions: ', vardimensions)
        var = varobject

        # ---------------------------------------
        vartype = ""
        for vardimension in vardimensions:
            try:
                vardimname = f1.variables[vardimension]
                if vardimname.axis == 'X':
                    vartype = vartype+"X"
                elif vardimname.axis == 'Y':
                    vartype = vartype+"Y"
                elif vardimname.axis == 'Z':
                    vartype = vartype+"Z"
                elif vardimname.axis == 'T' or re.search("since", vardimname.units.lower()):
                    vartype = vartype+"T"
                else:
                    raise
            except:
                if re.search("depth", vardimension.lower()) or re.match("^z", vardimension.lower()):
                    vartype = vartype+"Z"
                elif re.search("time", vardimension.lower()):
                    vartype = vartype+"T"
                else:
                    vartype = vartype+"-"

        my_print(verbose, 'var type: ', vartype)

        # ---------------------------------------
        if re.match("^TZ", vartype):
            kindex_max = var.shape[1]-1
            if kindex > var.shape[1]-1:
                kindex = var.shape[1]-1
            if kindex < 0:
                kindex = 0
            lindex_max = var.shape[0]-1
            if lindex > var.shape[0]-1:
                lindex = var.shape[0]-1
            if lindex < 0:
                lindex = 0
            var = var[lindex, kindex, ...]

        # ---------------------------------------
        elif re.match("^T", vartype):
            kindex = 0
            kindex_max = 0
            lindex_max = var.shape[0]-1
            if lindex > var.shape[0]-1:
                lindex = var.shape[0]-1
            if lindex < 0:
                lindex = 0
            var = var[lindex, ...]

        # ---------------------------------------
        elif re.match("^Z", vartype):
            lindex = 0
            lindex_max = 0
            kindex_max = var.shape[0]-1
            if kindex > var.shape[0]-1:
                kindex = var.shape[0]-1
            if kindex < 0:
                kindex = 0
            var = var[kindex, ...]

        # ---------------------------------------
        else:
            kindex = 0
            lindex = 0
            kindex_max = 0
            lindex_max = 0
            var = var[...]

    except:
        my_print(verbose, 'Error in var file processing')
        try:
            my_print(verbose, 'Variables available are: ', f1.variables.keys())
        except:
            my_print(verbose, 'Cannot read file', file)
        sys.exit(1)

    f1.close()

    return var

################################################################
def read_grid_fromfile(file, varname, verbose=1):
    global clon, blon, blat
    global nvertex
    my_print(verbose, '----------------------------')
    my_print(verbose, 'Reading grid')

    try:
        my_print(verbose, 'Get longitudes, latitudes from', file)
        f1 = netCDF4.Dataset(file)
        v1 = f1.variables[varname]

        # Try first non regular grid
        try:
            listcoord = v1.coordinates
            my_print(verbose, 'found', varname,
                     'coordinates attribut:', listcoord)
            for coordvarname in listcoord.split():
                var = f1.variables[coordvarname]
                varattrdict = var.__dict__
                print(varattrdict)
                # ajouter gestion attribut axis X,Y,Z,T
                if "units" in varattrdict or "UNITS" in varattrdict:
                    varunits = var.units.lower()
                    my_print(verbose, 'found units attribut for :', coordvarname)
                    if varunits == "degrees_east":
                        clon = f1.variables[coordvarname]
                        clonvarname = coordvarname
                    elif varunits == "degrees_north":
                        clat = f1.variables[coordvarname]
                        clatvarname = coordvarname
                elif "axis" in varattrdict or "AXIS" in varattrdict:
                    my_print(verbose, 'found axis attribut for :', coordvarname)
                    varaxis = var.axis.upper()
                    if varaxis == "X":
                        clon = f1.variables[coordvarname]
                        clonvarname = coordvarname
                    elif varaxis == "Y":
                        clat = f1.variables[coordvarname]
                        clatvarname = coordvarname
                else:
                    my_print(verbose, 'no units or axis attribut for',
                             coordvarname)
                    sys.exit(1)

            try:
                my_print(
                    verbose, 'found longitude coordinate variable:', clonvarname)
                my_print(
                    verbose, 'found latitude coordinate variable:', clatvarname)
            except:
                my_print(
                    verbose, 'no coordinate variables for longitude and/or latitude')
                sys.exit(1)

            try:
                blon = f1.variables[clon.bounds]
                my_print(
                    verbose, 'found longitude bounds coordinates variable:', clon.bounds)
            except:
                my_print(verbose, 'no bounds attribut for', clonvarname)
                sys.exit(1)

            try:
                blat = f1.variables[clat.bounds]
                my_print(
                    verbose, 'found latitude bounds coordinates variable:', clat.bounds)
            except:
                my_print(verbose, 'no bounds attribut for', clatvarname)
                sys.exit(1)
            nvertex = blon.shape[-1]
            clon = clon[:]
            clat = clat[:]
            blon = blon[:]
            blat = blat[:]

        # Now look to regular grid
        except:
            lon1D = f1.variables[v1.dimensions[-1]]
            lat1D = f1.variables[v1.dimensions[-2]]
            clon, clat = numpy.meshgrid(lon1D, lat1D)

            try:
                blon1D = f1.variables[lon1D.bounds]
                # shape of bounds variable is dim,2
                my_print(
                    verbose, 'found longitude bounds coordinates variable:', lon1D.bounds)
                blon1D_low = blon1D[..., 0]
                blon1D_up = blon1D[..., 1]

            except:
                my_print(verbose, 'no bounds for',
                         v1.dimensions[-1], ', create it with mid-points')
                blon1D_low = []
                blon1D_up = []
                for i in range(len(lon1D)-1):
                    d = abs(lon1D[i+1]-lon1D[i])/2.
                    if i == 0:
                        blon1D_low.append(lon1D[i]-d)
                    blon1D_low.append(lon1D[i]+d)
                    blon1D_up.append(lon1D[i]+d)
                    if i == (len(lon1D)-2):
                        blon1D_up.append(lon1D[i+1]+d)

            try:
                blat1D = f1.variables[lat1D.bounds]
                # shape of bounds variable is dim,2
                my_print(
                    verbose, 'found longitude bounds coordinates variable:', lat1D.bounds)
                blat1D_low = blat1D[..., 0]
                blat1D_up = blat1D[..., 1]

            except:
                my_print(verbose, 'no bounds for',
                         v1.dimensions[-2], ', create it with mid-points')
                blat1D_low = []
                blat1D_up = []
                for i in range(len(lat1D)-1):
                    d = abs(lat1D[i+1]-lat1D[i])/2.
                    if i == 0:
                        blat1D_low.append(lat1D[i]-d)
                    blat1D_low.append(lat1D[i]+d)
                    blat1D_up.append(lat1D[i]+d)
                    if i == (len(lat1D)-2):
                        blat1D_up.append(lat1D[i+1]+d)

            blon_LL, blat_LL = numpy.meshgrid(blon1D_low, blat1D_low)
            blon_LR, blat_LR = numpy.meshgrid(blon1D_up, blat1D_low)
            blon_UR, blat_UR = numpy.meshgrid(blon1D_up, blat1D_up)
            blon_UL, blat_UL = numpy.meshgrid(blon1D_low, blat1D_up)
            blon = numpy.dstack((blon_LL, blon_LR, blon_UR, blon_UL))
            blat = numpy.dstack((blat_LL, blat_LR, blat_UR, blat_UL))
            del blon_LL
            del blon_LR
            del blon_UR
            del blon_UL
            del blat_LL
            del blat_LR
            del blat_UR
            del blat_UL
            nvertex = 4

        my_print(verbose, 'number of vertex: ', nvertex)
        npoints = clon.size
        clon = numpy.reshape(clon, (npoints))
        clat = numpy.reshape(clat, (npoints))
        blon = numpy.reshape(blon, (npoints, nvertex))
        blat = numpy.reshape(blat, (npoints, nvertex))

    except:
        my_print(verbose, 'Error while extracting grid')
        sys.exit(1)

################################################################
def read_mask_fromgridfile(file, kindex, verbose=1):
    my_print(verbose, '----------------------------')
    my_print(verbose, 'Reading grid file: ', file)
    try:
        f2 = netCDF4.Dataset(file)
        mask = f2.variables['mask'][kindex, :]
        my_print(verbose, 'mask shape: ', mask.shape)

    except:
        my_print(verbose, 'Error in grid file processing')
        my_print(verbose, 'Trying to read variable mask')
        sys.exit(1)

    return mask

################################################################
def get_and_combine_masks():
    global var, mask
    my_print(option_verbose, '----------------------------')
    my_print(option_verbose, 'Get and combine mask(s)')
    var = numpy.ravel(var)
    mask = numpy.ravel(mask)
    selection_fromvar = numpy.ma.getmask(var)
    mask_var = numpy.ma.masked_not_equal(mask, 1)
    selection_frommask = numpy.ma.getmask(mask_var)
    selection_both = numpy.ma.mask_or(selection_frommask, selection_fromvar)

    return selection_both

################################################################
def compress_var(var, selection_both):
    my_print(option_verbose, '----------------------------')
    my_print(option_verbose, 'Mask and compress var')
    my_print(option_verbose, 'Before: ', var.shape)
    var_1 = numpy.ma.masked_array(var, selection_both)
    var_1 = var_1.compressed()
    my_print(option_verbose, 'After: ', var_1.shape)

    return var_1

################################################################
varfilename = sys.argv[1]
varname = sys.argv[2]
var = read_var_fromfile(varfilename, varname, verbose=option_verbose)

my_print(option_verbose, '----------------------------')
if option_gridfile != 0:
    my_print(option_verbose, 'Grid file specified: ', gridfilename)
    mask = read_mask_fromgridfile(gridfilename, kindex, verbose=option_verbose)
    my_print(option_verbose, 'Will read grid from grid file')
    read_grid_fromfile(gridfilename, 'mask', verbose=option_verbose)
else:
    my_print(option_verbose, 'No Grid file specified')
    my_print(option_verbose, 'Will read grid from variable file')
    read_grid_fromfile(varfilename, varname, verbose=option_verbose)
    mask = var*0+1

################################################################
if option_op != None:
    var = eval(option_op)

selection_both = get_and_combine_masks()
var_1 = compress_var(var, selection_both)

################################################################
var_scalefactor = 1.0

def scale_var(var, verbose=option_verbose):
    global var_scalefactor
    var_scalefactor = scalefactor(var)
    my_print(verbose, '----------------------------')
    my_print(verbose, 'Scaling var')
    my_print(verbose, 'min,max (initial): ', min(var), max(var))
    my_print(verbose, 'Scale factor: ', var_scalefactor)
# ym	var=var*var_scalefactor
    my_print(verbose, 'min,max (scaled): ', min(var), max(var))
    return var


################################################################
if option_op == None:
    var_1 = scale_var(var_1)

################################################################
def compute_projection(projection):
    global blon, blat, x, y, z

    my_print(option_verbose, '----------------------------')
    my_print(option_verbose, 'Projection:', projection)
    if projection == 'linear':
        my_print(option_verbose, 'Limit longitude excursion')
        blon = limit_lon(blon, clon)
        x = blon
        y = blat
        z = blon*0
        my_print(option_verbose, 'Ratio X/Y: ', option_ratioxy)
        y = y*option_ratioxy
    else:
        # Limit latitude to 90 and -90 (some model grids give some!)
        blat = numpy.where(numpy.greater(blat, 90), 90., blat)
        blat = numpy.where(numpy.less(blat, -90), -90., blat)
        deg2rad = numpy.pi/180.
        x = numpy.cos(blat*deg2rad)*numpy.cos(blon*deg2rad)
        y = numpy.cos(blat*deg2rad)*numpy.sin(blon*deg2rad)
        z = numpy.sin(blat*deg2rad)

    # Limit precision
    x = numpy.rint(x*10000)/10000
    y = numpy.rint(y*10000)/10000
    z = numpy.rint(z*10000)/10000


################################################################
compute_projection(option_projection)

################################################################
def compress_pos():
    global selection_both, x, y, z, x_1, y_1, z_1, index_i_1
    my_print(option_verbose, '----------------------------')
    my_print(option_verbose, 'Mask and compress positions')
    if selection_both.all() != None:
        selection_both1 = numpy.ones(
            x.shape, numpy.int8)*selection_both[..., None]
    else:
        selection_both1 = None

    x_0 = numpy.ma.masked_array(x, selection_both1)
    x_1 = x_0.compressed()
    x_1 = numpy.reshape(x_1, [var_1.shape[0], nvertex])
    y_0 = numpy.ma.masked_array(y, selection_both1)
    y_1 = y_0.compressed()
    y_1 = numpy.reshape(y_1, [var_1.shape[0], nvertex])
    z_0 = numpy.ma.masked_array(z, selection_both1)
    z_1 = z_0.compressed()
    z_1 = numpy.reshape(z_1, [var_1.shape[0], nvertex])

    # Create var indices (FORTRAN notations)
    var_indices = numpy.indices(var.shape)
    index_i = var_indices[0]+1
    index_i_1 = numpy.ma.masked_array(index_i, selection_both)
    index_i_1 = index_i_1.compressed()

################################################################
compress_pos()

################################################################
# ----------------------------------
polydata = vtk.vtkPolyData()

def polydata_create(verbose=1):
    global nb_cells
    my_print(verbose, '----------------------------')
    my_print(verbose, 'Polydata creation')
    points = vtk.vtkPoints()
    polys = vtk.vtkCellArray()
    n_points = 0
    for i in range(numpy.size(var_1)):
        polys.InsertNextCell(nvertex)
        for v in range(nvertex):
            points.InsertPoint(n_points, x_1[i, v], y_1[i, v], z_1[i, v])
            polys.InsertCellPoint(n_points)
            n_points = n_points+1
    polydata.SetPoints(points)
    polydata.SetPolys(polys)
    nb_cells = polydata.GetNumberOfCells()
    my_print(verbose, '----------------------------')
    my_print(verbose, 'Polydata created')
    my_print(verbose, 'Nb of cells: ', polydata.GetNumberOfCells())
    my_print(verbose, 'Nb of points: ', polydata.GetNumberOfPoints())

# ----------------------------------
def polydata_update(verbose=1):
    celldata = vtk.vtkFloatArray()
    for i in range(numpy.size(var_1)):
        celldata.InsertNextValue(var_1[i])
    polydata.GetCellData().SetScalars(celldata)
    my_print(verbose, '----------------------------')
    my_print(verbose, 'Polydata updated')
    my_print(verbose, 'Scalar range: ', polydata.GetScalarRange())


polydata_create(verbose=option_verbose)
polydata_update(verbose=option_verbose)

# ----------------------------------
transform = vtk.vtkTransform()
transform.Translate(360, 0, 0)

transformer = vtk.vtkTransformPolyDataFilter()
transformer.SetInputData(polydata)
transformer.SetTransform(transform)

polydata2 = vtk.vtkAppendPolyData()

def polydata_transform(projection):
    polydata2.AddInputData(polydata)
    if projection == 'linear':
        polydata2.AddInputConnection(transformer.GetOutputPort())

polydata_transform(option_projection)

# ********************************
def define_levels():
    global levels_min, levels_max, levels_delta, levels_nb, levels_range

    my_print(option_verbose, '----------------------------')
    my_print(option_verbose, 'Levels cooking')
    levels_range_var = list(polydata.GetScalarRange())
    my_print(option_verbose, 'min,max (var): ', levels_range_var)
    if option_levels_nb_specified:
        levels_min = levels_range_var[0]
        levels_max = levels_range_var[1]
        my_print(option_verbose, 'min,max (computed): ',
                 levels_min, levels_max)
        my_print(option_verbose, 'nb (user): ', levels_nb)
        levels_delta = float(abs(levels_max-levels_min))/(levels_nb-1)
        levels_max = levels_min+levels_delta*(levels_nb-1)
        my_print(option_verbose, 'delta (floor): ', levels_delta)
        my_print(option_verbose, 'max (fit to delta): ', levels_max)
    else:
        my_print(option_verbose, 'min,max (user): ', levels_min, levels_max)
        my_print(option_verbose, 'delta (user): ', levels_delta)
        levels_nb = float(abs(levels_max-levels_min))/levels_delta+1
        my_print(option_verbose, 'nb (computed): ', levels_nb)
        if levels_nb % 1 != 0:
            levels_nb = numpy.floor(levels_nb)
            levels_max = levels_min+levels_delta*(levels_nb-1)
            my_print(option_verbose, 'nb (floor): ', levels_nb)
            my_print(option_verbose, 'max (fit to nb): ', levels_max)
        levels_nb = int(levels_nb)

    levels_range = [levels_min, levels_max]
    values = []
    for i in range(levels_nb-2):
        values.append(
            levels_range[0]+(i+1)*(levels_range[1]-levels_range[0])/float(levels_nb-1))

    return values

# ********************************
levels_values = define_levels()
my_print(option_verbose, 'range (final): ', levels_range)
my_print(option_verbose, 'nb (final): ', levels_nb)
my_print(option_verbose, 'values: ', levels_values)

# ********************************
textprop = vtk.vtkTextProperty()
textprop.SetColor(colorfg)
textprop.ShadowOff()
textprop.BoldOn()
textprop.SetFontFamilyToArial()
textprop.SetFontSize(12)
textprop.SetJustificationToCentered()

# ********************************
lut1 = vtk.vtkLookupTable()
define_lut1(color_filename, levels_nb-1)

# ********************************
# Clean
clean = vtk.vtkCleanPolyData()
clean.SetInputConnection(polydata2.GetOutputPort())
clean.Update()

my_print(option_verbose, '----------------------------')
my_print(option_verbose, 'Clean updated')
my_print(option_verbose, 'Nb of cells: ', clean.GetOutput().GetNumberOfCells())
my_print(option_verbose, 'Nb of points: ',
         clean.GetOutput().GetNumberOfPoints())

# ********************************
# Cells To Points
cell2point = vtk.vtkCellDataToPointData()
cell2point.SetInputConnection(clean.GetOutputPort())
cell2point.Update()

# ********************************
# Cell
cellmapper = vtk.vtkPolyDataMapper()
cellmapper.SetInputConnection(clean.GetOutputPort())
cellmapper.SetScalarRange(levels_range)
cellmapper.SetLookupTable(lut1)

cellactor = vtk.vtkActor()
cellactor.SetMapper(cellmapper)
cellactor.GetProperty().SetAmbient(1)
cellactor.GetProperty().SetDiffuse(0)
# cellactor.SetNumberOfCloudPoints(10000)

# ********************************
# Cell bounds
cellboundsmapper = vtk.vtkPolyDataMapper()
cellboundsmapper.SetInputConnection(clean.GetOutputPort())
cellboundsmapper.ScalarVisibilityOff()
cellboundsmapper.SetResolveCoincidentTopologyToPolygonOffset()

cellboundsactor = vtk.vtkActor()
cellboundsactor.SetMapper(cellboundsmapper)
cellboundsactor.GetProperty().SetRepresentationToWireframe()
cellboundsactor.GetProperty().SetLineWidth(1)
cellboundsactor.GetProperty().SetColor(0, 0, 0)
cellboundsactor.GetProperty().SetAmbient(1)
cellboundsactor.GetProperty().SetDiffuse(0)
cellboundsactor.PickableOff()
# cellboundsactor.SetNumberOfCloudPoints(10000)

# ********************************
# Isofill
isofill = vtk.vtkBandedPolyDataContourFilter()
isofill.SetInputConnection(cell2point.GetOutputPort())
isofill.SetScalarModeToValue()
isofill.GenerateContourEdgesOn()

def isofill_del():
    isofill.SetNumberOfContours(0)


def isofill_create():
    for i in range(len(levels_values)):
        isofill.SetValue(i, levels_values[i])

isofill_create()

isofillmapper = vtk.vtkPolyDataMapper()
isofillmapper.SetInputConnection(isofill.GetOutputPort())
isofillmapper.SetResolveCoincidentTopologyToPolygonOffset()
isofillmapper.SetLookupTable(lut1)
isofillmapper.SetScalarRange(levels_range)
isofillmapper.SetScalarModeToUseCellData()

isofillactor = vtk.vtkActor()
isofillactor.SetMapper(isofillmapper)
isofillactor.GetProperty().SetAmbient(1)
isofillactor.GetProperty().SetDiffuse(0)
isofillactor.GetProperty().SetRepresentationToSurface()
# isofillactor.SetNumberOfCloudPoints(2000)
isofillactor.PickableOff()

# ********************************
# Isoline
isoline = vtk.vtkContourFilter()
isoline.SetInputConnection(cell2point.GetOutputPort())

def isoline_del():
    isoline.SetNumberOfContours(0)


def isoline_create():
    for i in range(len(levels_values)):
        isoline.SetValue(i, levels_values[i])

isoline_create()

# --------
# Isolines in color
isoline1mapper = vtk.vtkPolyDataMapper()
isoline1mapper.SetInputConnection(isoline.GetOutputPort())
isoline1mapper.SetLookupTable(lut1)
isoline1mapper.SetScalarRange(levels_range)

isoline1actor = vtk.vtkActor()
isoline1actor.SetMapper(isoline1mapper)
isoline1actor.GetProperty().SetLineWidth(1)
isoline1actor.GetProperty().SetAmbient(1)
isoline1actor.GetProperty().SetDiffuse(0)
isoline1actor.PickableOff()

# --------
# Isolines in black
isoline2mapper = vtk.vtkPolyDataMapper()
isoline2mapper.SetInputConnection(isoline.GetOutputPort())
isoline2mapper.ScalarVisibilityOff()

isoline2actor = vtk.vtkActor()
isoline2actor.SetMapper(isoline2mapper)
isoline2actor.GetProperty().SetLineWidth(1)
isoline2actor.GetProperty().SetColor(0, 0, 0)
isoline2actor.GetProperty().SetAmbient(1)
isoline2actor.GetProperty().SetDiffuse(0)
isoline2actor.PickableOff()

# ********************************
# Create a scalar bar
scalarbar = vtk.vtkScalarBarActor()
scalarbar.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
scalarbar.GetPositionCoordinate().SetValue(0.1, 0.01)
scalarbar.SetOrientationToHorizontal()
scalarbar.SetWidth(0.8)
scalarbar.SetHeight(0.1)
scalarbar.SetMaximumHeightInPixels(40)
scalarbar.SetLabelFormat(option_label_format)
#scalarbar.SetLabelFormat("%6.2g")
#scalarbar.SetLabelFormat("%6.2e")
scalarbar.SetNumberOfLabels(min(levels_nb, 20))
scalarbar.SetLookupTable(lut1)
scalarbar.SetLabelTextProperty(textprop)
scalarbar.SetTitleTextProperty(textprop)
scalarbar.SetTitle(" ")
scalarbar.GetLabelTextProperty().SetJustificationToRight()

# ********************************
ren0 = vtk.vtkRenderer()
ren0.SetBackground(colorbg)

# ********************************
ren1 = vtk.vtkRenderer()
ren1.SetBackground(colorbg)

def setviewport():
    global ren1xstart, ren1ystart, ren1xend, ren1yend, ren1
    if option_projection == 'linear':
        ren1xstart = 0.1
        ren1xend = 0.9
        ren1ystart = 0.2
        ren1yend = 0.85
    else:
        ren1xstart = 0.0
        ren1xend = 1.0
        ren1ystart = 0.1
        ren1yend = 0.9
    ren1.SetViewport(ren1xstart, ren1ystart, ren1xend, ren1yend)


setviewport()

# ********************************
# Viewport box
boxactor = CreateViewportBox(colorfg)

# ********************************
def create_texts(init=0):
    global varfilenametextactor, varnametextactor, varindextextactor
    global varindextextkindexformat, varindextextlindexformat
    if not init:
        ren0.RemoveActor(varfilenametextactor)
        ren0.RemoveActor(varnametextactor)
        ren0.RemoveActor(varindextextactor)
        del varfilenametextactor
        del varnametextactor
        del varindextextactor

    varfilenametext = 'Filename : ' + os.path.basename(varfilename)
    varfilenametextactor = CreateTextActor(
        varfilenametext, textprop, 0.1, 0.96)
    ren0.AddActor(varfilenametextactor)

    if option_op != None:
        varunitstext = varunits+' modified by '+option_op
    elif var_scalefactor != 1.0:
        varunitstext = varunits+' scaled by '+'%1.0e' % var_scalefactor
    else:
        varunitstext = varunits
    varnametext = 'Variable : '+varlongname+' ('+varunitstext+')'
    varnametextactor = CreateTextActor(varnametext, textprop, 0.1, 0.93)
    ren0.AddActor(varnametextactor)

    varindextextkindexwidth = len(str(kindex_max+1))
    varindextextkindexformat = '%0' + \
        str(varindextextkindexwidth)+'d/%0'+str(varindextextkindexwidth)+'d'
    varindextextlindexwidth = len(str(lindex_max+1))
    varindextextkindex = varindextextkindexformat % (kindex+1, kindex_max+1)
    varindextextlindexformat = '%0' + \
        str(varindextextlindexwidth)+'d/%0'+str(varindextextlindexwidth)+'d'
    varindextextlindex = varindextextlindexformat % (lindex+1, lindex_max+1)
    varindextext = 'k= ' + varindextextkindex+' l= ' + varindextextlindex
    varindextextactor = CreateTextActor(
        varindextext, textprop, 0.9, 0.93, justification=1)
    ren0.AddActor(varindextextactor)

create_texts(init=1)

# **************************************
def setwindowsize():
    global window_width, window_height
    window_sizefactor = 2
    if option_projection == 'linear':
        window_width = 297*window_sizefactor
        window_height = 210*window_sizefactor
    else:
        window_width = 210*window_sizefactor
        window_height = 297*window_sizefactor

setwindowsize()

# **************************************
if option_interface:
    try:
        my_print(option_verbose, '----------------------------')
        my_print(option_verbose, 'Loading module qt')
        from vtk.qt.QVTKRenderWindowInteractor import *
        from PyQt5.Qt import Qt
        from PyQt5.QtCore import *
        from PyQt5.QtGui import *
        from PyQt5.QtWidgets import *

    except:
        my_print(option_verbose, '----------------------------')
        my_print(option_verbose, 'Module qt not available')
        option_interface = 0
        pass

if option_interface:
    from mylib_gui_Qt import *
    app, win, renwin, inter = launch_Qt_interface(window_width, window_height)
else:
    renwin = vtk.vtkRenderWindow()
    # Offscreen mode is available only if using Mesa GL
    if option_offscreen:
        renwin.OffScreenRenderingOn()
    renwin.SetSize(window_width, window_height)
    renwin.SetWindowName("VTK_Mapper")
    inter = vtk.vtkRenderWindowInteractor()
    inter.SetRenderWindow(renwin)

# **************************************
renwin.AddRenderer(ren0)
renwin.AddRenderer(ren1)

# ********************************
def ProjOrthoResetClippingRange(obj, event):
    camera = ren1.GetActiveCamera()
    camera.SetFocalPoint(0, 0, 0)
    camera_dist = camera.GetDistance()
    camera.SetClippingRange(0.1, camera_dist)
    camera.ParallelProjectionOn()

def ProjCylinClippingRange(obj, event):
    global axisxticknb, axisyticknb
    axisxticknb, axisyticknb = DisplayAxisTextAndTicks(
        renwin, ren0, ren1, axisxticknb, axisyticknb, textprop, option_ratioxy)

# ********************************
if option_actor in ('isolines1', 'isoline1'):
    ren1.AddActor(isoline1actor)
    ren1.AddActor(cellboundsactor)
elif option_actor in ('isolines2', 'isoline2'):
    ren1.AddActor(isoline1actor)
elif option_actor in ('cell', 'cells'):
    ren1.AddActor(cellactor)
elif option_actor in ('cellbounds', 'cellsbounds'):
    ren1.AddActor(cellactor)
    ren1.AddActor(cellboundsactor)
else:
    ren1.AddActor(isofillactor)
    ren1.AddActor(isoline2actor)

ren0.AddActor(scalarbar)

# ********************************
def setobserver(projection):
    if projection == 'linear':
        ren1.AddObserver("AnyEvent", ProjCylinClippingRange)
        ren1.AddActor(boxactor)
        imagestyle = vtk.vtkInteractorStyleImage()
        inter.SetInteractorStyle(imagestyle)
    else:
        ren1.AddObserver("AnyEvent", ProjOrthoResetClippingRange)
        ren1.RemoveActor(boxactor)
        switchstyle = vtk.vtkInteractorStyleSwitch()
        inter.SetInteractorStyle(switchstyle)

setobserver(option_projection)

# ********************************
def drawboundaries():
    global option_boundaries_active, boundariesactor
    global boundariespolydata
    boundariesactor, boundariespolydata = boundaries_create(
        clean,
        option_boundaries_color,
        option_boundaries_width)
    ren1.AddActor(boundariesactor)
    command['--boundaries'] = ''
    command['--boundaries_width'] = str(option_boundaries_width)
    command['--boundaries_color'] = "%s,%s,%s" % (
        option_boundaries_color[0], option_boundaries_color[1], option_boundaries_color[2])
    option_boundaries_active = 1

def delboundaries():
    global option_boundaries_active, boundariesactor
    if option_boundaries_active:
        ren1.RemoveActor(boundariesactor)
        del boundariesactor
        del command['--boundaries']
        del command['--boundaries_width']
        del command['--boundaries_color']
        option_boundaries_active = 0

if option_boundaries_active:
    drawboundaries()

# ********************************
def drawcontinents(file=option_continents_file):
    global option_continents_file
    global option_continents_active, continentsactor
    global continentspolydata
    if file == None:
        if option_projection == 'linear':
            option_continents_file = PATHROOT+"/polydouble_earth_continents.nc"
        else:
            option_continents_file = PATHROOT+"/polysimple_earth_continents.nc"

    continentsactor, continentspolydata = continents_create(
        option_continents_file,
        option_continents_color,
        option_continents_width,
        option_projection,
        option_ratioxy)
    ren1.AddActor(continentsactor)
    command['--continents'] = ''
    command['--continents_file'] = str(option_continents_file)
    command['--continents_width'] = str(option_continents_width)
    command['--continents_color'] = "%s,%s,%s" % (
        option_continents_color[0], option_continents_color[1], option_continents_color[2])
    option_continents_active = 1

def delcontinents():
    global option_continents_active, continentsactor
    if option_continents_active:
        ren1.RemoveActor(continentsactor)
        del continentsactor
        del command['--continents']
        del command['--continents_file']
        del command['--continents_width']
        del command['--continents_color']
        option_continents_active = 0


if option_continents_active:
    drawcontinents(option_continents_file)

# ********************************
def drawequator():
    global option_equator_active, equatoractor
    equatoractor = equator_create(
        option_equator_color,
        option_equator_width,
        option_projection)
    ren1.AddActor(equatoractor)
    command['--equator'] = ''
    command['--equator_width'] = str(option_equator_width)
    command['--equator_color'] = "%s,%s,%s" % (
        option_equator_color[0], option_equator_color[1], option_equator_color[2])
    option_equator_active = 1

def delequator():
    global option_equator_active, equatoractor
    if option_equator_active:
        ren1.RemoveActor(equatoractor)
        del equatoractor
        del command['--equator']
        del command['--equator_width']
        del command['--equator_color']
        option_equator_active = 0

if option_equator_active:
    drawequator()

# ********************************
def drawgrid():
    global option_grid_active, gridactor
    gridactor = grid_create(
        option_grid_delta,
        option_grid_color,
        option_grid_width,
        option_projection,
        option_ratioxy)
    ren1.AddActor(gridactor)
    command['--grid'] = ''
    command['--grid_delta'] = str(option_grid_delta)
    command['--grid_width'] = str(option_grid_width)
    command['--grid_color'] = "%s,%s,%s" % (
        option_grid_color[0], option_grid_color[1], option_grid_color[2])
    option_grid_active = 1

def delgrid():
    global option_grid_active, gridactor
    if option_grid_active:
        ren1.RemoveActor(gridactor)
        del gridactor
        del command['--grid']
        del command['--grid_delta']
        del command['--grid_width']
        del command['--grid_color']
        option_grid_active = 0

if option_grid_active:
    drawgrid()

# ********************************
pdf_number = 1
png_number = 1

# ********************************
def LoadCamera(file):
    global axisxticknb, axisyticknb
    if file == None:
        if option_projection == 'linear':
            file = PATHROOT+'/camera_default.sty'
        else:
            file = PATHROOT+'/camera_ortho_default.sty'
    try:
        camera_file = open(file, 'rb')
    except IOError:
        my_print(option_verbose, '----------------------------')
        my_print(option_verbose, 'Error in loading camera file: ', file)
        my_print(option_verbose, '      * check if exists')
        my_print(option_verbose, '      * if not, press "c" to create')
    else:
        camera = vtk.vtkCamera()
        camera_clip = pickle.load(camera_file)
        camera.SetClippingRange(camera_clip)
        camera_focal = pickle.load(camera_file)
        camera.SetFocalPoint(camera_focal)
        camera_pos = pickle.load(camera_file)
        camera.SetPosition(camera_pos)
        camera_view = pickle.load(camera_file)
        camera.SetViewUp(camera_view)
        ren1.SetActiveCamera(camera)
        if option_projection == 'linear':
            axisxticknb = pickle.load(camera_file)
            axisyticknb = pickle.load(camera_file)
            axisxticknb, axisyticknb = DisplayAxisTextAndTicks(
                renwin, ren0, ren1, axisxticknb, axisyticknb, textprop, option_ratioxy)
        my_print(option_verbose, '----------------------------')
        my_print(option_verbose, 'Camera loaded from', file)

def SaveCamera():
    global camera_filename
    camera_filename = 'camera.sty'
    camera = ren1.GetActiveCamera()
    camera_file = open(camera_filename, 'wb')
    pickle.dump(camera.GetClippingRange(), camera_file)
    pickle.dump(camera.GetFocalPoint(), camera_file)
    pickle.dump(camera.GetPosition(), camera_file)
    pickle.dump(camera.GetViewUp(), camera_file)
    pickle.dump(axisxticknb, camera_file)
    pickle.dump(axisyticknb, camera_file)
    camera_file.close()
    my_print(option_verbose, '----------------------------')
    my_print(option_verbose, 'Camera saved in', camera_filename)

LoadCamera(camera_filename)

# ********************************
def Keypress(obj, event):
    global celldata, polydata
    global x, y, z
    global kindex, kindex_max, lindex, lindex_max
    global var, mask, selection_both
    global var_1
    global option_actor
    global option_boundaries_active
    global option_continents_active, continentsactor
    global option_equator_active
    global option_grid_active
    global levels_values

    key = obj.GetKeyCode()
    my_print(option_verbose, '----------------------------')
    # When Qt interface is launched, get only upper letter (?)
    my_print(option_verbose, 'Pressed key: ', key)

    # ----------------------------
    if key == "?":
        print("****************************")
        print("To reproduce the current plot, type: ")
        print(" ")
        command['--offscreen'] = ''
        command_dict = command.copy()
        del command_dict['argprogram']
        del command_dict['argvarfile']
        del command_dict['argvarname']
        if '--verbose' in command:
            del command_dict['--verbose']
        if '--interface' in command:
            del command_dict['--interface']
        keys = list(command_dict.keys())
        keys.sort()
        command_text = command['argprogram']
        for key in keys:
            if len(command_dict[key]) != 0:
                if key == '--operation':
                    command_text = command_text+" " + \
                        key+" "+"'%s'" % command_dict[key]
                else:
                    command_text = command_text+" " + \
                        key+" "+"%s" % command_dict[key]
            else:
                command_text = command_text+" "+key
        command_text = command_text+" "+command['argvarfile']
        command_text = command_text+" "+command['argvarname']

        print(command_text)
        print("******************************")
    # ----------------------------
    elif key == "h" or key == "H":
        print(interactions)
    # ----------------------------
    elif key == "1":
        my_print(option_verbose, '----------------------------')
        if option_actor in ('isolines1', 'isoline1'):
            ren1.RemoveActor(isoline1actor)
            ren1.RemoveActor(cellboundsactor)
            option_actor = 'isoline2'
        elif option_actor in ('isolines2', 'isoline2'):
            ren1.RemoveActor(isoline1actor)
            option_actor = 'cell'
        elif option_actor in ('cell', 'cells'):
            ren1.RemoveActor(cellactor)
            option_actor = 'cellbounds'
        elif option_actor in ('cellbounds', 'cellsbounds'):
            ren1.RemoveActor(cellactor)
            ren1.RemoveActor(cellboundsactor)
            option_actor = 'isofill'
        else:
            ren1.RemoveActor(isofillactor)
            ren1.RemoveActor(isoline2actor)
            option_actor = 'isolines1'
        if option_actor in ('isolines1', 'isoline1'):
            ren1.AddActor(cellboundsactor)
            ren1.AddActor(isoline1actor)
        elif option_actor in ('isolines2', 'isoline2'):
            ren1.AddActor(isoline1actor)
        elif option_actor in ('cell', 'cells'):
            ren1.AddActor(cellactor)
        elif option_actor in ('cellbounds', 'cellsbounds'):
            ren1.AddActor(cellactor)
            ren1.AddActor(cellboundsactor)
        else:
            ren1.AddActor(isofillactor)
            ren1.AddActor(isoline2actor)
        my_print(option_verbose, option_actor)
        command['--actor'] = option_actor
    # ----------------------------
    elif key == "2":
        if option_boundaries_active:
            delboundaries()
        else:
            drawboundaries()
    # ----------------------------
    elif key == "3":
        # set mode stereo
        # didn't success to disable this default mode
        pass
    # ----------------------------
    elif key == "4":
        if option_continents_active:
            delcontinents()
        else:
            drawcontinents()
    # ----------------------------
    elif key == "5":
        if option_equator_active:
            delequator()
        else:
            drawequator()
    # ----------------------------
    elif key == "6":
        if option_grid_active:
            delgrid()
        else:
            drawgrid()
    # ----------------------------
    elif key == "7":
        LoadCamera(camera_filename)
        command['--camera'] = camera_filename
    # ----------------------------
    elif key == " ":							# Update levels and scalarbar
        levels_values = define_levels()
        my_print(option_verbose, 'range (final): ', levels_range)
        my_print(option_verbose, 'nb (final): ', levels_nb)
        my_print(option_verbose, 'values: ', levels_values)
        isoline_del()
        isoline_create()
        isofill_del()
        isofill_create()
        cellmapper.SetScalarRange(levels_range)
        isoline1mapper.SetScalarRange(levels_range)
        isoline2mapper.SetScalarRange(levels_range)
        isofillmapper.SetScalarRange(levels_range)
        renwin.Render()
    # ----------------------------
    elif key == ",":
        if kindex > 0:
            kindex = kindex-1
            if option_gridfile != 0:
                mask = read_mask_fromgridfile(gridfilename, kindex, verbose=0)
            var = read_var_fromfile(varfilename, varname, verbose=0)
            selection_both = get_and_combine_masks()
            my_print(option_verbose, '----------------------------')
            my_print(option_verbose, "New kindex", kindex+1)
            var_1 = compress_var(var, selection_both)
            compress_pos()
            if option_op == None:
                var_1 = scale_var(var_1, verbose=0)
            polydata_create(verbose=0)
            polydata_update(verbose=0)
            varindextextkindex = varindextextkindexformat % (
                kindex+1, kindex_max+1)
            varindextextlindex = varindextextlindexformat % (
                lindex+1, lindex_max+1)
            varindextext = 'k= ' + varindextextkindex+' l= ' + varindextextlindex
            varindextextactor.SetInput(varindextext)
            if kindex == 0:
                del command['--kindex']
            else:
                command['--kindex'] = str(kindex+1)
    # ----------------------------
    elif key == ";":
        if kindex < kindex_max:
            kindex = kindex+1
            if option_gridfile != 0:
                mask = read_mask_fromgridfile(gridfilename, kindex, verbose=0)
            var = read_var_fromfile(varfilename, varname, verbose=0)
            selection_both = get_and_combine_masks()
            my_print(option_verbose, '----------------------------')
            my_print(option_verbose, "New kindex", kindex+1)
            var_1 = compress_var(var, selection_both)
            compress_pos()
            if option_op == None:
                var_1 = scale_var(var_1, verbose=0)
            polydata_create(verbose=0)
            polydata_update(verbose=0)
            varindextextkindex = varindextextkindexformat % (
                kindex+1, kindex_max+1)
            varindextextlindex = varindextextlindexformat % (
                lindex+1, lindex_max+1)
            varindextext = 'k= ' + varindextextkindex+' l= ' + varindextextlindex
            varindextextactor.SetInput(varindextext)
            command['--kindex'] = str(kindex+1)
    # ----------------------------
    if key == "!" or key == "+":
        if lindex < lindex_max:
            lindex = lindex+1
            var = read_var_fromfile(varfilename, varname, verbose=0)
            my_print(option_verbose, '----------------------------')
            my_print(option_verbose, "New lindex", lindex+1)
            var_1 = compress_var(var, selection_both)
            if option_op == None:
                var_1 = scale_var(var_1, verbose=0)
            polydata_update(verbose=0)
            varindextextkindex = varindextextkindexformat % (
                kindex+1, kindex_max+1)
            varindextextlindex = varindextextlindexformat % (
                lindex+1, lindex_max+1)
            varindextext = 'k= ' + varindextextkindex+' l= ' + varindextextlindex
            varindextextactor.SetInput(varindextext)
            command['--lindex'] = str(lindex+1)
    # ----------------------------
    elif key == ":" or key == "-":
        if lindex > 0:
            lindex = lindex-1
            var = read_var_fromfile(varfilename, varname, verbose=0)
            my_print(option_verbose, '----------------------------')
            my_print(option_verbose, "New lindex", lindex+1)
            var_1 = compress_var(var, selection_both)
            if option_op == None:
                var_1 = scale_var(var_1, verbose=0)
            polydata_update(verbose=0)
            varindextextkindex = varindextextkindexformat % (
                kindex+1, kindex_max+1)
            varindextextlindex = varindextextlindexformat % (
                lindex+1, lindex_max+1)
            varindextext = 'k= ' + varindextextkindex+' l= ' + varindextextlindex
            varindextextactor.SetInput(varindextext)
            if lindex == 0:
                del command['--lindex']
            else:
                command['--lindex'] = str(lindex+1)
    # ----------------------------
    elif key == "o" or key == "O":
        SavePoly()
    # ----------------------------
    elif key == "v" or key == "V":
        SavePDF()
    # ----------------------------
    elif key == "u" or key == "U":
        print(renwin.GetSize())
        SavePNG()
    # ----------------------------
    elif key == "c" or key == "C":
        SaveCamera()
        command['--camera'] = camera_filename
    # ----------------------------
    renwin.Render()


inter.AddObserver("KeyPressEvent", Keypress)

# ********************************
# Picker
coneglyph = vtk.vtkConeSource()
coneglyph.SetResolution(6)
coneglyph.Update()

textpickactor = vtk.vtkCaptionActor2D()
textpickactor.VisibilityOff()
textpickactor.SetPosition(50, 50)
textpickactor.SetWidth(0.2)
textpickactor.SetHeight(0.2)
textpickactor.GetProperty().SetColor(0, 0, 0)
textpickactor.GetProperty().SetLineWidth(2)
textpickactor.GetCaptionTextProperty().SetColor(0, 0, 0)
textpickactor.GetCaptionTextProperty().SetFontSize(12)
textpickactor.GetCaptionTextProperty().BoldOn()
textpickactor.GetCaptionTextProperty().ShadowOff()
textpickactor.GetCaptionTextProperty().ItalicOn()
textpickactor.GetCaptionTextProperty().SetFontFamilyToArial()
textpickactor.BorderOff()
textpickactor.ThreeDimensionalLeaderOff()
textpickactor.SetLeaderGlyphData(coneglyph.GetOutput())
textpickactor.SetMaximumLeaderGlyphSize(8)
textpickactor.SetLeaderGlyphSize(0.025)

ren1.AddActor2D(textpickactor)

def AnnotatePick(obj, event):
    actor = picker.GetActor()
    if actor != cellactor:
        textpickactor.VisibilityOff()
        return
    cellid = picker.GetCellId()
    if cellid >= nb_cells:
        cellid = cellid-nb_cells
    if cellid < 0:
        #my_print(option_verbose,'Pick outside')
        textpickactor.VisibilityOff()
    else:
        my_print(option_verbose,'Pick inside', cellid)
        posx, posy, posz = picker.GetPickPosition()
        my_print(option_verbose,'Pick position', posx, posy, posz)
        if option_projection == 'linear':
            text = 'Indice I = ' + str(index_i_1[cellid]) + '\n' \
                + 'Value = ' + '%.3f' % var_1[cellid] + '\n' \
                + 'Longitude = ' + '%.3f' % posx + '\n' \
                + 'Latitude = ' + '%.3f' % posy
        else:
            text = 'Indice I = ' + str(index_i_1[cellid]) + '\n' \
                + 'Value = ' + '%.3f' % var_1[cellid]

        my_print(option_verbose, text)
        textpickactor.SetCaption(text)
        textpickactor.SetAttachmentPoint(posx, posy, posz)
        textpickactor.VisibilityOn()
    renwin.Render()

picker = vtk.vtkCellPicker()
picker.AddObserver('EndPickEvent', AnnotatePick)
picker.SetTolerance(1E-6)

inter.SetPicker(picker)

if option_projection != 'linear':
    style = vtk.vtkInteractorStyleTrackballCamera()
    inter.SetInteractorStyle(style)

# ********************************
if option_projection == 'linear':
    axisxticknb, axisyticknb = DisplayAxisTextAndTicks(
        renwin, ren0, ren1, axisxticknb, axisyticknb, textprop, option_ratioxy)

if option_offscreen:
    SavePNG()
    SavePDF()

if option_interface:
    win.show()
    app.exec_loop()
elif not option_offscreen:
    inter.Initialize()
    renwin.Render()
    inter.Start()
