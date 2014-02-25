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

import vtk 

#********************************
def boundaries_create(clean,arg_boundaries_color,arg_boundaries_width):

	boundariespolydata = vtk.vtkFeatureEdges()
	boundariespolydata.SetInputConnection(clean.GetOutputPort())
	boundariespolydata.SetBoundaryEdges(1)
	boundariespolydata.SetFeatureEdges(0)
	boundariespolydata.SetNonManifoldEdges(0)
	boundariespolydata.SetColoring(1)

	boundariesmapper = vtk.vtkPolyDataMapper()
	boundariesmapper.SetInputConnection(boundariespolydata.GetOutputPort())
	boundariesmapper.SetScalarVisibility(0)

	boundariesactor = vtk.vtkActor()
	boundariesactor.SetMapper(boundariesmapper)
	boundariesactor.GetProperty().SetLineWidth(arg_boundaries_width)
	boundariesactor.GetProperty().SetColor(arg_boundaries_color)
	boundariesactor.GetProperty().SetAmbient(1)
	boundariesactor.GetProperty().SetDiffuse(0)
	boundariesactor.PickableOff()

	return(boundariesactor,boundariespolydata)

#********************************
