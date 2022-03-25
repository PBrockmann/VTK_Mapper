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

import __main__

import vtk

from mylib_misc import *

##################################
def SavePNG():
    png_number = __main__.png_number
    option_verbose = __main__.option_verbose
    option_prefix = __main__.option_prefix
    renwin = __main__.renwin

    rtTimer = vtk.vtkTimerLog

    my_print(option_verbose, '----------------------------')
    my_print(option_verbose, 'Saving PNG')
    rtStartCPU = rtTimer.GetCPUTime()

    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(renwin)
    w2i.Update()

    filepng = option_prefix+'_%03d.png' % png_number
    my_print(option_verbose, 'Start writing PNG file', filepng)
    pngw = vtk.vtkPNGWriter()
    pngw.SetInputConnection(w2i.GetOutputPort())
    pngw.SetFileName(filepng)
    pngw.Write()

    rtEndCPU = rtTimer.GetCPUTime()
    my_print(option_verbose, 'End writing PNG file')
    my_print(option_verbose, 'CPU time:', rtEndCPU-rtStartCPU)

    __main__.png_number = png_number+1

##################################
def SavePDF():
    pdf_number = __main__.pdf_number
    option_verbose = __main__.option_verbose
    option_prefix = __main__.option_prefix
    renwin = __main__.renwin

    rtTimer = vtk.vtkTimerLog

    my_print(option_verbose, '----------------------------')
    my_print(option_verbose, 'Saving PDF')
    rtStartCPU = rtTimer.GetCPUTime()

    filepdf = option_prefix+'_%03d' % pdf_number
    my_print(option_verbose, 'Start writing PDF file', filepdf+'.pdf')
    psw = vtk.vtkGL2PSExporter()
    psw.SetInput(renwin)
    # psw.SetFileFormatToPS()
    psw.SetFileFormatToPDF()
    # psw.SetFileFormatToEPS()
    psw.SetSortToOff()
    if __main__.option_projection == 'linear':
        psw.LandscapeOff()
    psw.SetFilePrefix(filepdf)
    psw.Write()

    rtEndCPU = rtTimer.GetCPUTime()
    my_print(option_verbose, 'End writing PDF file')
    my_print(option_verbose, 'CPU time:', rtEndCPU-rtStartCPU)

    __main__.pdf_number = pdf_number+1

##################################
def SavePoly():
    option_verbose = __main__.option_verbose

    my_print(option_verbose, '----------------------------')
    my_print(option_verbose, 'Saving VTK object')

    polywriter = vtk.vtkPolyDataWriter()
    polywriter.SetFileName('out_poly.vtk')
    # polywriter.SetInputConnection(__main__.boundariespolydata.GetOutputPort())
    # polywriter.SetInputConnection(__main__.polydata2.GetOutputPort())
    polywriter.SetInputConnection(__main__.clean.GetOutputPort())
    # polywriter.SetInputConnection(__main__.continentspolydata.GetOutputPort())
    polywriter.Write()

##################################
