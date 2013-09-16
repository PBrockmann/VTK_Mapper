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
def longitude_create( 
		arg_lon,
		arg_projection,
		arg_ratioxy=1):

	if arg_projection == 'linear' :
		n_polypoints=2
        	polygonpoints=vtk.vtkPoints()
        	polygonpoints.SetNumberOfPoints(n_polypoints)
		polygonpoints.InsertPoint(0,arg_lon,-90*arg_ratioxy,0)
		polygonpoints.InsertPoint(1,arg_lon,90*arg_ratioxy,0)
	else:
        	n_polypoints=360
        	polygonpoints=vtk.vtkPoints()
        	polygonpoints.SetNumberOfPoints(n_polypoints)
        	deg2rad=numpy.pi/180.
        	for n in range(n_polypoints) :
			theta=2*numpy.pi*n/(n_polypoints-1)
			x=numpy.sin(arg_lon*deg2rad)*numpy.sin(theta)
			y=numpy.cos(arg_lon*deg2rad)*numpy.sin(theta)
			z=numpy.cos(theta)
			polygonpoints.InsertPoint(n,x,y,z)

	polygonlines=vtk.vtkCellArray()
        polygonlines.InsertNextCell(n_polypoints)
        for n in range(n_polypoints) :
               	polygonlines.InsertCellPoint(n)
        lonpolydata=vtk.vtkPolyData()
        lonpolydata.SetPoints(polygonpoints)
       	lonpolydata.SetLines(polygonlines)

	return lonpolydata

#********************************
def latitude_create(
                arg_lat,
		arg_projection):

	if arg_projection == 'linear' :
		n_polypoints=2
        	polygonpoints=vtk.vtkPoints()
        	polygonpoints.SetNumberOfPoints(n_polypoints)
		polygonpoints.InsertPoint(0,-180,arg_lat,0)
		polygonpoints.InsertPoint(1,540,arg_lat,0)
	else:
        	n_polypoints=360
        	polygonpoints=vtk.vtkPoints()
        	polygonpoints.SetNumberOfPoints(n_polypoints)
        	deg2rad=numpy.pi/180.
        	for n in range(n_polypoints) :
                	theta=2*numpy.pi*n/(n_polypoints-1)
                	x=numpy.cos(arg_lat*deg2rad)*numpy.cos(theta)
                	y=numpy.cos(arg_lat*deg2rad)*numpy.sin(theta)
                	z=numpy.sin(arg_lat*deg2rad)
                	polygonpoints.InsertPoint(n,x,y,z)

        polygonlines=vtk.vtkCellArray()
        polygonlines.InsertNextCell(n_polypoints)
        for n in range(n_polypoints) :
                polygonlines.InsertCellPoint(n)
        latpolydata=vtk.vtkPolyData()
        latpolydata.SetPoints(polygonpoints)
        latpolydata.SetLines(polygonlines)

        return latpolydata

#********************************
def grid_create(
		arg_grid_delta,
		arg_grid_color,
		arg_grid_width,
		arg_projection,
		arg_ratioxy):

	gridpolydata=vtk.vtkAppendPolyData()
	for i in range(0,int(90*arg_ratioxy),int(arg_grid_delta*arg_ratioxy)) :
		latpolydata=latitude_create(i,arg_projection)
		gridpolydata.AddInput(latpolydata)
	for i in range(0,int(-90*arg_ratioxy),int(-arg_grid_delta*arg_ratioxy)) :
		latpolydata=latitude_create(i,arg_projection)
		gridpolydata.AddInput(latpolydata)
	if arg_projection == 'linear' :
		for i in range(-180,540,arg_grid_delta) :
			lonpolydata=longitude_create(i,arg_projection,arg_ratioxy)
			gridpolydata.AddInput(lonpolydata)
	else:
		for i in range(0,180,arg_grid_delta) :
			lonpolydata=longitude_create(i,arg_projection)
			gridpolydata.AddInput(lonpolydata)

	gridpolygonmapper=vtk.vtkDataSetMapper()
	gridpolygonmapper.SetInput(gridpolydata.GetOutput())

	gridpolygonactor=vtk.vtkActor()
	gridpolygonactor.SetMapper(gridpolygonmapper)
	gridpolygonactor.GetProperty().SetColor(arg_grid_color)
	gridpolygonactor.GetProperty().SetLineWidth(arg_grid_width)
	gridpolygonactor.GetProperty().SetAmbient(1)
	gridpolygonactor.GetProperty().SetDiffuse(0)
	gridpolygonactor.PickableOff()

	return(gridpolygonactor)

#********************************

