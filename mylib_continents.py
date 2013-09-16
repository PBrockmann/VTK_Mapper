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

import netCDF4 
import numpy
import vtk 

#********************************
def continents_create(
		arg_continents_file,
		arg_continents_color,
		arg_continents_width,
		option_projection,
		option_ratioxy):

	f=netCDF4.Dataset(arg_continents_file)

	vlon=f.variables['CONT_LON'][:]
	vlat=f.variables['CONT_LAT'][:]
	vmask=numpy.ma.getmask(vlon)

	if option_projection == 'linear' :
		x=vlon
		y=vlat
		z=vlon*0
		y=y*option_ratioxy
	else:
		vlat=numpy.where(numpy.greater(vlat,90),90.,vlat)
		vlat=numpy.where(numpy.less(vlat,-90),-90.,vlat)
		deg2rad=numpy.pi/180.
		x=numpy.cos(vlat*deg2rad)*numpy.cos(vlon*deg2rad)
		y=numpy.cos(vlat*deg2rad)*numpy.sin(vlon*deg2rad)
		z=numpy.sin(vlat*deg2rad)

	continentspolydata=vtk.vtkAppendPolyData()

	n_polylines=0
	n_polypoints=0
	for i in range(numpy.size(vlon)) :
		if not(vmask[i]) :
			if n_polypoints == 0 :
				n_start=i
			n_polypoints=n_polypoints+1
		else :
			if n_polypoints > 0 :
				n_polylines=n_polylines+1
				polygonpoints=vtk.vtkPoints()
				polygonpoints.SetNumberOfPoints(n_polypoints)
				n_points=0
				for n in range(n_start,n_start+n_polypoints) :
					polygonpoints.InsertPoint(n_points,x[n],y[n],z[n]) 
					n_points=n_points+1
				polygonlines=vtk.vtkCellArray()
				polygonlines.InsertNextCell(n_polypoints)
				for n in range(n_polypoints) : 
   					polygonlines.InsertCellPoint(n)
				polydata=vtk.vtkPolyData()
				polydata.SetPoints(polygonpoints)
				polydata.SetLines(polygonlines)
				continentspolydata.AddInput(polydata)

			n_polypoints=0

	f.close()

	continentspolygonmapper=vtk.vtkDataSetMapper()
	continentspolygonmapper.SetInput(continentspolydata.GetOutput())

	continentspolygonactor=vtk.vtkActor()
	continentspolygonactor.SetMapper(continentspolygonmapper)
	continentspolygonactor.GetProperty().SetColor(arg_continents_color)
	continentspolygonactor.GetProperty().SetLineWidth(arg_continents_width)
	continentspolygonactor.GetProperty().SetAmbient(1)
	continentspolygonactor.GetProperty().SetDiffuse(0)
	continentspolygonactor.PickableOff()

	return(continentspolygonactor,continentspolydata)

#********************************

