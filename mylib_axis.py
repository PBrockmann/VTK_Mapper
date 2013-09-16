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

import __main__
from mylib_text import * 

#********************************
axisxoffset=0.03 ; axisxticksize=0.02
axisyoffset=0.03 ; axisyticksize=0.02
axisxwidth=720.0 ; axisxstart=-180.0
axisywidth=180.0 ; axisystart=-90.0

#**************************************
def CreateViewportBox(colorfg,linewidth=3) :
	pts = vtk.vtkPoints()
	pts.SetNumberOfPoints(4)
	pts.SetPoint(0, 0.0, 0.0, 0.0)
	pts.SetPoint(1, 0.0, 1.0, 0.0)
	pts.SetPoint(2, 1.0, 1.0, 0.0)
	pts.SetPoint(3, 1.0, 0.0, 0.0)
	lines = vtk.vtkCellArray()
	lines.InsertNextCell(5)
	lines.InsertCellPoint(0)
	lines.InsertCellPoint(1)
	lines.InsertCellPoint(2)
	lines.InsertCellPoint(3)
	lines.InsertCellPoint(0)
	box = vtk.vtkPolyData()
	box.SetPoints(pts)
	box.SetLines(lines)

	coords = vtk.vtkCoordinate()
	coords.SetCoordinateSystemToNormalizedViewport()

	boxmapper = vtk.vtkPolyDataMapper2D()
	boxmapper.SetInput(box)
	boxmapper.SetTransformCoordinate(coords)

	boxactor = vtk.vtkActor2D()
	boxactor.SetMapper(boxmapper)
	boxactor.GetProperty().SetLineWidth(linewidth)
	boxactor.GetProperty().SetColor(colorfg)

	return boxactor

#**************************************
def GetPrecision(x) :
	x=abs(x)
	fractionpart=x-int(x)
	if fractionpart != 0 :
		precision=len(str(fractionpart))-2
	else :
		precision=0
	return precision

#**************************************
def CreateAxisTickActor(xstart,ystart,xend,yend,colorfg) :
	line=vtk.vtkLineSource()
	line.SetPoint1(xstart,ystart,0.0)
	line.SetPoint2(xend,yend,0.0)
	coords = vtk.vtkCoordinate()
	coords.SetCoordinateSystemToNormalizedViewport()
	linemapper = vtk.vtkPolyDataMapper2D()
	linemapper.SetInput(line.GetOutput())
	linemapper.SetTransformCoordinate(coords)
	tick = vtk.vtkActor2D()
	tick.SetMapper(linemapper)
	tick.GetProperty().SetLineWidth(1)
	tick.GetProperty().SetColor(colorfg)
	tick.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
	return tick 

#**************************************
listlonaxistextactors=[]
listlonaxistickuactors=[]
listlonaxistickdactors=[]
listlonaxispos=[]
listlonaxisvisibility=[]

def InitLonAxisTicks() :
	del listlonaxistextactors[:]
	del listlonaxistickuactors[:]
	del listlonaxistickdactors[:]
	del listlonaxispos[:]
	del listlonaxisvisibility[:]

def CreateLonAxisTicks(axisxticknb,textprop) :
	colorfg=textprop.GetColor()
	xdelta=axisxwidth/(axisxticknb-1)
	xdeltaprecision=GetPrecision(xdelta)	
	xpostextformat='%.'+str(xdeltaprecision)+'f'	
	for i in range(int(axisxticknb)) :
		xpos=axisxstart+xdelta*i
		xpostext=xpostextformat%xpos
		listlonaxistextactors.append(CreateTextActor(xpostext,textprop,0,0,
					justification=0,verticaljustification=1))
		listlonaxistickdactors.append(CreateAxisTickActor(0,0,0,axisxticksize,colorfg))
		listlonaxistickuactors.append(CreateAxisTickActor(0,0,0,axisxticksize,colorfg))
		listlonaxispos.append(xpos)
		listlonaxisvisibility.append(1)

def DelLonAxisTicks(ren0) :
	for i in range(len(listlonaxistextactors)) :
		ren0.RemoveActor(listlonaxistextactors[i])
		ren0.RemoveActor(listlonaxistickdactors[i])
		ren0.RemoveActor(listlonaxistickuactors[i])
	InitLonAxisTicks()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
listlataxistextactors=[]
listlataxisticklactors=[]
listlataxistickractors=[]
listlataxispos=[]
listlataxisvisibility=[]

def InitLatAxisTicks() :
	del listlataxistextactors[:]
	del listlataxisticklactors[:]
	del listlataxistickractors[:]
	del listlataxispos[:]
	del listlataxisvisibility[:]

def CreateLatAxisTicks(axisyticknb,textprop) :
	colorfg=textprop.GetColor()
	ydelta=axisywidth/(axisyticknb-1)
	ydeltaprecision=GetPrecision(ydelta)	
	ypostextformat='%.'+str(ydeltaprecision)+'f'	
	for i in range(int(axisyticknb)) :
		ypos=axisystart+ydelta*i
		ypostext=ypostextformat%(ypos)
		listlataxistextactors.append(CreateTextActor(ypostext,textprop,0,0,
					justification=1,verticaljustification=0))
		listlataxistickractors.append(CreateAxisTickActor(0,0,axisyticksize,0,colorfg))
		listlataxisticklactors.append(CreateAxisTickActor(0,0,axisyticksize,0,colorfg))
		listlataxispos.append(ypos)
		listlataxisvisibility.append(1)

def DelLatAxisTicks(ren0) :
	for i in range(len(listlataxistextactors)) :
		ren0.RemoveActor(listlataxistextactors[i])
		ren0.RemoveActor(listlataxisticklactors[i])
		ren0.RemoveActor(listlataxistickractors[i])
	InitLatAxisTicks()

#-----------------------
def HandleVisibilityLonAxisTextAndTicks(renwin,ren0,ren1,text,tickb,ticku,xpos) :
	xsize,ysize=renwin.GetSize()
	ren1xstart,ren1ystart,ren1xend,ren1yend=ren1.GetViewport()
	coords = vtk.vtkCoordinate()
	coords.SetCoordinateSystemToWorld()
	coords.SetValue(xpos,0.0,0.0)
	x1,y1 = coords.GetComputedDoubleViewportValue(ren1)
	renxpos=x1/xsize+ren1xstart
	if renxpos > ren1xstart and renxpos < ren1xend : 
		ren0.AddActor(text)
		text.SetPosition(renxpos,ren1ystart-axisxoffset)
		ren0.AddActor(tickb)
		tickb.SetPosition(renxpos,ren1ystart-axisxticksize)
		ren0.AddActor(ticku)
		ticku.SetPosition(renxpos,ren1yend)
		visibility=1
	else :
		ren0.RemoveActor(text)
		ren0.RemoveActor(tickb)
		ren0.RemoveActor(ticku)
		visibility=0
	return visibility

#-----------------------
def HandleVisibilityLatAxisTextAndTicks(renwin,ren0,ren1,text,tickl,tickr,ypos) :
	xsize,ysize=renwin.GetSize()
	ren1xstart,ren1ystart,ren1xend,ren1yend=ren1.GetViewport()
	coords = vtk.vtkCoordinate()
	coords.SetCoordinateSystemToWorld()
	coords.SetValue(0.0,ypos,0.0)
	x1,y1 = coords.GetComputedDoubleViewportValue(ren1)
	renypos=y1/ysize+ren1ystart
	if renypos > ren1ystart and renypos < ren1yend : 
		ren0.AddActor(text)
		text.SetPosition(ren1xstart-axisyoffset,renypos)
		ren0.AddActor(tickl)
		tickl.SetPosition(ren1xstart-axisyticksize,renypos)
		ren0.AddActor(tickr)
		tickr.SetPosition(ren1xend,renypos)
		visibility=1
	else :
		ren0.RemoveActor(text)
		ren0.RemoveActor(tickl)
		ren0.RemoveActor(tickr)
		visibility=0
	return visibility

#-----------------------
def CalculNbTicks(nbticks,axiswidth,way) :
	# to switch delta from 30 to 10 
	#                 from 5 to 2
	axisdelta_actual=axiswidth/(nbticks-1)
	if way == 'closer' :
		if axisdelta_actual == 30 :
			axisdelta_new=10
		elif axisdelta_actual == 5 :
			axisdelta_new=2
		else :
			axisdelta_new=axisdelta_actual/2
	elif way == 'wider' :
		if axisdelta_actual == 10 :
			axisdelta_new=30
		elif axisdelta_actual == 2 :
			axisdelta_new=5
		else :
			axisdelta_new=axisdelta_actual*2
	nbticks=axiswidth/axisdelta_new+1
	return nbticks

#-----------------------
def DisplayAxisTextAndTicks(renwin,ren0,ren1,
		            axisxticknb,axisyticknb,textprop,ratioxy) :

	if len(listlonaxistextactors) != axisxticknb :
		DelLonAxisTicks(ren0)
		CreateLonAxisTicks(axisxticknb,textprop)		
	for i in range(len(listlonaxistextactors)) :
		listlonaxisvisibility[i]=HandleVisibilityLonAxisTextAndTicks(
			renwin,ren0,ren1,
			listlonaxistextactors[i],
			listlonaxistickdactors[i],
			listlonaxistickuactors[i],
			listlonaxispos[i])
	if listlonaxisvisibility.count(1) < 4 :
		DelLonAxisTicks(ren0)
		axisxticknb=CalculNbTicks(axisxticknb,axisxwidth,way='closer')
		CreateLonAxisTicks(axisxticknb,textprop)
	elif listlonaxisvisibility.count(1) > 11 :
		DelLonAxisTicks(ren0)
		axisxticknb=CalculNbTicks(axisxticknb,axisxwidth,way='wider')
		CreateLonAxisTicks(axisxticknb,textprop)
	axisxticknb=len(listlonaxistextactors)

	if len(listlataxistextactors) != axisyticknb :
		DelLatAxisTicks(ren0)
		CreateLatAxisTicks(axisyticknb,textprop)		
	for i in range(len(listlataxistextactors)) :
		listlataxisvisibility[i]=HandleVisibilityLatAxisTextAndTicks(
			renwin,ren0,ren1,
			listlataxistextactors[i],
			listlataxisticklactors[i],
			listlataxistickractors[i],
			listlataxispos[i]*ratioxy)
	if listlataxisvisibility.count(1) < 4 :
		DelLatAxisTicks(ren0)
		axisyticknb=CalculNbTicks(axisyticknb,axisywidth,way='closer')
		CreateLatAxisTicks(axisyticknb,textprop)
	elif listlataxisvisibility.count(1) > 11 :
		DelLatAxisTicks(ren0)
		axisyticknb=CalculNbTicks(axisyticknb,axisywidth,way='wider')
		CreateLatAxisTicks(axisyticknb,textprop)
	axisyticknb=len(listlataxistextactors)

	return axisxticknb, axisyticknb 

