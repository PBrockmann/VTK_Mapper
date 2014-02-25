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

import numpy
import vtk 

#********************************
def equator_create(
		arg_equator_color,
		arg_equator_width,
		option_projection):

	if option_projection == 'linear' :
		n_polypoints=2
		polygonpoints=vtk.vtkPoints()
		polygonpoints.SetNumberOfPoints(n_polypoints)
		polygonpoints.InsertPoint(0,-180,0,0) 
		polygonpoints.InsertPoint(1,540,0,0) 
	else :
		n_polypoints=360
		polygonpoints=vtk.vtkPoints()
		polygonpoints.SetNumberOfPoints(n_polypoints)
		deg2rad=numpy.pi/180.
		for n in range(n_polypoints) :
			theta=2*numpy.pi*n/(n_polypoints-1)
			x=numpy.cos(theta)
			y=numpy.sin(theta)
			z=0
			polygonpoints.InsertPoint(n,x,y,z) 
	
	polygonlines=vtk.vtkCellArray()
	polygonlines.InsertNextCell(n_polypoints)
	for n in range(n_polypoints) : 
   		polygonlines.InsertCellPoint(n)
	equatorpolydata=vtk.vtkPolyData()
	equatorpolydata.SetPoints(polygonpoints)
	equatorpolydata.SetLines(polygonlines)

	equatorpolygonmapper=vtk.vtkDataSetMapper()
	equatorpolygonmapper.SetInputData(equatorpolydata)

	equatorpolygonactor=vtk.vtkActor()
	equatorpolygonactor.SetMapper(equatorpolygonmapper)
	equatorpolygonactor.GetProperty().SetColor(arg_equator_color)
	equatorpolygonactor.GetProperty().SetLineWidth(arg_equator_width)
	equatorpolygonactor.GetProperty().SetAmbient(1)
	equatorpolygonactor.GetProperty().SetDiffuse(0)
	equatorpolygonactor.PickableOff()

	return(equatorpolygonactor)

#********************************

