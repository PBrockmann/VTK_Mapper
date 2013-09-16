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

def CreateTextActor(text,textprop,xpos,ypos,
			justification="left",
			verticaljustification="bottom") :	

	textactor = vtk.vtkTextActor()

	textactor.SetInput(text)
	textactor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
	textactor.SetPosition(xpos,ypos)

	textactor.GetTextProperty().SetFontFamily(textprop.GetFontFamily())
	textactor.GetTextProperty().SetColor(textprop.GetColor())

	if justification in (-1,"left") :
		textactor.GetTextProperty().SetJustificationToLeft()
	elif justification in (0,"center","middle") :
		textactor.GetTextProperty().SetJustificationToCentered()
	elif justification in (1,"right") :
		textactor.GetTextProperty().SetJustificationToRight()

	if verticaljustification in (-1,"bottom") :
		textactor.GetTextProperty().SetVerticalJustificationToBottom()
	elif verticaljustification in (0,"center","middle") :
		textactor.GetTextProperty().SetVerticalJustificationToCentered()
	elif verticaljustification in (1,"top") :
		textactor.GetTextProperty().SetVerticalJustificationToTop()

	return textactor
