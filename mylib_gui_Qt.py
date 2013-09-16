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
        
import qt
import sys, string, os.path
import vtk
from vtk.qt.QVTKRenderWindowInteractor import *

import __main__
from mylib_misc import *
from mylib_lut import *

#**************************************
def button_ok():
	print "ok"

#**************************************
def button_cancel():
	print "cancel"

#**************************************
def button_file_selected():
	global FileSelect3 

	my_print(__main__.option_verbose,'----------------------------')
	print "New file to load: "+str(FileSelect3.selectedFile())
	print "To be implemented..."

	#__main__.varfilename=str(FileSelect3.selectedFile())
	#my_print(__main__.option_verbose,"Load file: ",__main__.varfilename)
	#FileSelect3.setSelection(__main__.varfilename)
	#FileSelect3.show()

#**************************************
def button_load_position_pressed():
	s = qt.QFileDialog.getOpenFileName(
                  ".",
                  "XML (*.xml)",
                   TabWidget,
                  "open file dialog",
                  "Choose a file to open" )
	print "Load position"
	if s.isEmpty() :
                print "Cancel pressed"
        else :
		print 'File choosed: ', s

#**************************************
def slider_xstart_grid_changed(value):
	__main__.ren1xstart=value/100.
	__main__.ren1.SetViewport(__main__.ren1xstart,__main__.ren1ystart, \
		__main__.ren1xend,__main__.ren1yend)
	__main__.renwin.Render()

#**************************************
def slider_xend_grid_changed(value):
	__main__.ren1xend=value/100.
	__main__.ren1.SetViewport(__main__.ren1xstart,__main__.ren1ystart, \
		__main__.ren1xend,__main__.ren1yend)
	__main__.renwin.Render()

#**************************************
def slider_ystart_grid_changed(value):
	__main__.ren1ystart=value/100.
	__main__.ren1.SetViewport(__main__.ren1xstart,__main__.ren1ystart, \
		__main__.ren1xend,__main__.ren1yend)
	__main__.renwin.Render()

#**************************************
def slider_yend_grid_changed(value):
	__main__.ren1yend=value/100.
	__main__.ren1.SetViewport(__main__.ren1xstart,__main__.ren1ystart, \
		__main__.ren1xend,__main__.ren1yend)
	__main__.renwin.Render()

#**************************************
def slider_ratioxy_changed(value):
	__main__.option_ratioxy=float(value)
	my_print(__main__.option_verbose,'----------------------------')
	my_print(__main__.option_verbose,"Changing ratio X/Y: ",__main__.option_ratioxy)
	__main__.command['--ratioxy']="%s" %(__main__.option_ratioxy)
	if value <> 1 :
		__main__.option_projection='linear'
		__main__.command['--projection']="%s" %(__main__.option_projection)
        	ComboBox1g.setCurrentText(__main__.option_projection)
		my_print(__main__.option_verbose,"Changing projection: ",__main__.option_projection)
	else :
		del __main__.command['--ratioxy']

#**************************************
def combobox_projection_activated(projection):
	__main__.option_projection=str(projection)
	my_print(__main__.option_verbose,'----------------------------')
	my_print(__main__.option_verbose,"Changing projection: ",__main__.option_projection)
	__main__.command['--projection']="%s" %(__main__.option_projection)
	if projection == 'orthographic' :
		__main__.option_ratioxy=1.0
		__main__.command['--ratioxy']="%s" %(__main__.option_ratioxy)
		del __main__.command['--ratioxy']
		SpinBox1f.setValue(int(__main__.option_ratioxy))	
	
#**************************************
def button_redraw_pressed():
	my_print(__main__.option_verbose,'----------------------------')
	my_print(__main__.option_verbose,'Redrawing')
	print __main__.option_projection
	__main__.compute_projection(__main__.option_projection)
	__main__.compress_pos()
	__main__.polydata_create(verbose=1)
	__main__.polydata2.RemoveAllInputs()
	__main__.polydata_transform(__main__.option_projection)
	__main__.axisxticknb,__main__.axisyticknb=__main__.DisplayAxisTextAndTicks(__main__.renwin,
			__main__.ren0,__main__.ren1,__main__.axisxticknb,__main__.axisyticknb,
			__main__.textprop,__main__.option_ratioxy)
	__main__.isoline_del()
	__main__.isoline_create()
	__main__.isofill_del()
	__main__.isofill_create()

	if __main__.option_equator_active :
		__main__.delequator()
		__main__.drawequator()
	if __main__.option_continents_active :
		__main__.delcontinents()
		__main__.drawcontinents()
	if __main__.option_grid_active :
		__main__.delgrid()
		__main__.drawgrid()

	__main__.ren1.RemoveObservers("ResetCameraEvent")
	__main__.ren1.RemoveObservers("EndEvent")
	__main__.setwindowsize()
	Win.resize(__main__.window_width+40,__main__.window_height+200+40)
	__main__.setviewport()
	__main__.setobserver(__main__.option_projection)
	__main__.camera_filename=None
	__main__.LoadCamera(__main__.camera_filename)
	__main__.renwin.Render()

#**************************************
def button_redraw_newlevels_pressed():
	my_print(__main__.option_verbose,'----------------------------')
	my_print(__main__.option_verbose,'Redrawing with new levels')

	if ListBox6a_1.count() < 3 :
		my_print(__main__.option_verbose,'Warning!: Not enough levels defined')
		return

	new_levels_values=[]
	for i in range(ListBox6a_1.count()) :
		new_levels_values.append(string.atof(str(ListBox6a_1.item(i).text())))

	my_print(__main__.option_verbose,'Old levels values: ', __main__.levels_values[:])
	my_print(__main__.option_verbose,'Old levels nb: ', __main__.levels_nb)
	my_print(__main__.option_verbose,'Old levels range: ', __main__.levels_range)
	__main__.levels_range=[new_levels_values[0],new_levels_values[-1]]
	__main__.levels_nb=len(new_levels_values)
	__main__.levels_values=new_levels_values[1:-1]
	__main__.define_lut1(__main__.color_filename,__main__.levels_nb-1)
	my_print(__main__.option_verbose,'New levels values: ', __main__.levels_values[:])
	my_print(__main__.option_verbose,'New levels nb: ', __main__.levels_nb)
	my_print(__main__.option_verbose,'New levels range: ', __main__.levels_range)

	__main__.isoline_del()
	__main__.isoline_create()
	__main__.isofill_del()
	__main__.isofill_create()
	__main__.scalarbar.SetNumberOfLabels(__main__.levels_nb)
	__main__.scalarbar.GetLookupTable().SetTableRange(__main__.levels_range)
	__main__.cellmapper.SetScalarRange(__main__.levels_range)
	__main__.isoline1mapper.SetScalarRange(__main__.levels_range)
	__main__.isofillmapper.SetScalarRange(__main__.levels_range)
	__main__.renwin.Render()

#**************************************
def button_color_continents_pressed():
	c=qt.QColorDialog.getColor()
	#print c
	if c.isValid () :
		r=c.red() ; g=c.green(); b=c.blue()
		r=int(100.*r/255.)/100. ;  g=int(100.*g/255.)/100. ; b=int(100.*b/255.)/100.
		__main__.option_continents_color=[]
		__main__.option_continents_color.append(r)
		__main__.option_continents_color.append(g)
		__main__.option_continents_color.append(b)
		__main__.delcontinents()
		__main__.command['--continents_color']="%s,%s,%s" %(r,g,b)
		__main__.drawcontinents()
		__main__.option_continents_active=1 

#**************************************
def slider_width_continents_changed(value):
	__main__.option_continents_width=value
	__main__.delcontinents()
	__main__.command['--continents_width']=str(value)
	__main__.drawcontinents()
	__main__.option_continents_active=1 

#**************************************
def button_color_boundaries_pressed():
        c=qt.QColorDialog.getColor()
	if c.isValid () :
		r=c.red() ; g=c.green(); b=c.blue()
		r=int(100.*r/255.)/100. ;  g=int(100.*g/255.)/100. ; b=int(100.*b/255.)/100.
		__main__.option_boundaries_color=[]
		__main__.option_boundaries_color.append(r)
		__main__.option_boundaries_color.append(g)
		__main__.option_boundaries_color.append(b)
		__main__.delboundaries()
		__main__.command['--boundaries_color']="%s,%s,%s" %(r,g,b)
		__main__.drawboundaries()
		__main__.option_boundaries_active=1 

#**************************************
def slider_width_boundaries_changed(value):
	__main__.option_boundaries_width=value
	__main__.delboundaries()
	__main__.command['--boundaries_width']=str(value)
	__main__.drawboundaries()
	__main__.option_boundaries_active=1 

#**************************************
def button_color_grid_pressed():
        c=qt.QColorDialog.getColor()
	if c.isValid () :
		r=c.red() ; g=c.green(); b=c.blue()
		r=int(100.*r/255.)/100. ;  g=int(100.*g/255.)/100. ; b=int(100.*b/255.)/100.
		__main__.option_grid_color=[]
		__main__.option_grid_color.append(r)
		__main__.option_grid_color.append(g)
		__main__.option_grid_color.append(b)
		__main__.delgrid()
		__main__.command['--grid_color']="%s,%s,%s" %(r,g,b)
		__main__.drawgrid()
		__main__.option_grid_active=1 

#**************************************
def slider_width_grid_changed(value):
	__main__.option_grid_width=value
	__main__.delgrid()
	__main__.command['--grid_width']=str(value)
	__main__.drawgrid()
	__main__.option_grid_active=1 

#**************************************
def slider_delta_grid_changed(value):
	__main__.option_grid_delta=value
	__main__.delgrid()
	__main__.command['--grid_delta']=str(value)
	__main__.drawgrid()
	__main__.option_grid_active=1 

#**************************************
def button_color_equator_pressed():
        c=qt.QColorDialog.getColor()
	if c.isValid () :
		r=c.red() ; g=c.green(); b=c.blue()
		r=int(100.*r/255.)/100. ;  g=int(100.*g/255.)/100. ; b=int(100.*b/255.)/100.
		__main__.option_equator_color=[]
		__main__.option_equator_color.append(r)
		__main__.option_equator_color.append(g)
		__main__.option_equator_color.append(b)
		__main__.delequator()
		__main__.command['--equator_color']="%s,%s,%s" %(r,g,b)
		__main__.drawequator()
		__main__.option_equator_active=1 

#**************************************
def slider_width_equator_changed(value):
	__main__.option_equator_width=value
	__main__.delequator()
	__main__.command['--equator_width']=str(value)
	__main__.drawequator()
	__main__.option_equator_active=1 

#**************************************
def list_variables_expanded():
	a=List5.selectedItem()
# peindre branche ??

#**************************************
def button_load_variable_pressed():

	my_print(__main__.option_verbose,'----------------------------')
	my_print(__main__.option_verbose,"Loading variable")

	if __main__.option_op != None :
		__main__.option_op = None
		del __main__.command['--operation']

	__main__.command['argvarname']=__main__.varname

	if __main__.command.has_key('--kindex') :
		if __main__.kindex == 0 :
			del __main__.command['--kindex']
		else :
			__main__.command['--kindex']=str(__main__.kindex+1)

	if __main__.command.has_key('--lindex') :
		if __main__.lindex == 0 :
			del __main__.command['--lindex']
		else :
			__main__.command['--lindex']=str(__main__.lindex+1)

	__main__.varname=str(List5.selectedItem().text(0))
	__main__.command['argvarname']=__main__.varname
	__main__.var=__main__.read_var_fromfile(__main__.varfilename,__main__.varname,verbose=1)
	__main__.var_1=__main__.compress_var(__main__.var,__main__.selection_both)
	__main__.var_1=__main__.scale_var(__main__.var_1)
	__main__.polydata_update(verbose=1)
	__main__.option_levels_nb_specified=1
	__main__.levels_nb=15
	__main__.levels_values=__main__.define_levels()
	__main__.define_lut1(__main__.color_filename,__main__.levels_nb-1)
	__main__.isoline_del()
	__main__.isoline_create()
	__main__.isofill_del()
	__main__.isofill_create()
	__main__.scalarbar.SetNumberOfLabels(__main__.levels_nb)
	__main__.scalarbar.GetLookupTable().SetTableRange(__main__.levels_range)
	__main__.cellmapper.SetScalarRange(__main__.levels_range)
	__main__.isoline1mapper.SetScalarRange(__main__.levels_range)
	__main__.isofillmapper.SetScalarRange(__main__.levels_range)
	__main__.create_texts()
	__main__.renwin.Render()

	StatusBar.message('Loading variable...',3000)

#**************************************
def button_load_spectrumferretfile_pressed():
	s = qt.QFileDialog.getOpenFileName(
                  __main__.PATHROOT+'/colors',
                  "Ferret spectrum (*.spk)",
                   TabWidget,
                  "open file dialog",
                  "Choose a file to open" )
	if not (s.isEmpty()) :
		__main__.color_filename=str(s)
		define_lut1(__main__.color_filename,__main__.levels_nb-1)		
		__main__.renwin.Render()

		__main__.command['--color']=__main__.color_filename

#**************************************
def button_delete_level():
	ListBox6a_1.removeItem(ListBox6a_1.currentItem())

#**************************************
def button_delete_alllevels():
	ListBox6a_1.clear()

#**************************************
def button_add_level():
	found=0
	for i in range(ListBox6a_1.count()) :
		if ListBox6a_1.item(i).text() == LineEdit6b_3.text() :
			found = 1
	if not found :
		ListBox6a_1.insertItem(LineEdit6b_3.text())
	ListBox6a_1.sort()

	for i in range(ListBox6a_1.count()) :
		if ListBox6a_1.item(i).text() == LineEdit6b_3.text() :
			ListBox6a_1.setCurrentItem(i)

#**************************************
def button_generate_levels():
	ListBox6a_1.clear()

#**************************************
def file_browser_clicked(link):
	print "Link clicked", link 
	TextEdit7.setSource(link)
	TextEdit7.mimeSourceFactory().setFilePath(qt.QStringList('.'))

#**************************************
def launch_Qt_interface(window_width,window_height) :
	global Win,TabWidget,List5,TextEdit7,StatusBar,SpinBox1f,ComboBox1g
	global SpinBox1f,ComboBox1g,Tab3,Tab3Layout,Point3,FileSelect3
	global ListBox6a_1, LineEdit6b_3

	#-----------------------------
	App = qt.QApplication(sys.argv)
	qt.QObject.connect(App,qt.SIGNAL("lastWindowClosed()"),
		App,qt.SLOT("quit()"))

	#-----------------------------
	Win=qt.QMainWindow()
	Win.resize(window_width+40,window_height+200+40)
	Win.setCaption("VTK_Mapper")
	Win.setCentralWidget(qt.QWidget(Win,"qt_central_widget"))

	#-----------------------------
	StatusBar=Win.statusBar()
	StatusBar.setSizeGripEnabled(1)

	#-----------------------------
	WinLayout = qt.QVBoxLayout(Win.centralWidget(),20,20,"WinLayout")
	
	#-----------------------------
        WinSplitter = qt.QSplitter(Win.centralWidget(),"WinSplitter")
	WinSplitter.setOrientation(qt.QSplitter.Vertical)
	WinSplitter.setHandleWidth(10)

	#-----------------------------
	TabWidget = qt.QTabWidget(WinSplitter,"TabWidget")

	#-----------------------------
	Tab3 = qt.QWidget(TabWidget,"Tab3")
	TabWidget.insertTab(Tab3,"Files")

	Tab3Layout = qt.QGridLayout(Tab3,1,1,20,20,"Tab3Layout")

	Point3 = qt.QPoint(0,0)

	FileSelect3 = qt.QFileDialog(Tab3,"FileSelect3",0)
	FileSelect3.setSelection("netCDF (*.nc)")
	FileSelect3.setSelection(__main__.varfilename)
	FileSelect3.setSizeGripEnabled(0)
	FileSelect3.reparent(Tab3,Point3)

	Tab3Layout.addWidget(FileSelect3,0,0)

	#-----------------------------
	Tab5 = qt.QWidget(TabWidget,"Tab5")
	TabWidget.insertTab(Tab5,"Variables")

	Tab5Layout = qt.QGridLayout(Tab5,2,2,20,20,"Tab5Layout")

	List5= qt.QListView(Tab5,"List5")
        List5.addColumn("Name",300)
        List5.addColumn("Long Name",200)
        List5.addColumn("Units",60)
        List5.addColumn("Shape",100)
        List5.addColumn("Axis",300)
        List5.setAllColumnsShowFocus(1)
	List5.setShowSortIndicator(1)
	List5.setRootIsDecorated(1)
	List5.setTreeStepSize(20)

	for i in range(len(__main__.listvarname)) :
        	List5item = qt.QListViewItem(List5)
        	List5item.setText(0,string.rstrip(__main__.listvarname[i]))
        	List5item.setText(1,string.rstrip(__main__.listvarlongname[i]))
        	List5item.setText(2,string.rstrip(__main__.listvarunits[i]))
        	List5item.setText(3,string.rstrip(__main__.listvarshape[i]))
        	List5item.setText(4,string.rstrip(__main__.listvaraxis[i]))
		if __main__.listvarname[i] == __main__.varname : 
			List5item_toselect=List5item
		listvaratt=__main__.dictvarsatt[__main__.listvarname[i]]
		for j in range(len(listvaratt)) :
			itema = qt.QListViewItem(List5item,None)
			itema.setText(0,listvaratt[j])
			itema.setSelectable(0)

	List5.setCurrentItem(List5item_toselect)
	#List5.setOpen(List5item_toselect,1)
	List5.ensureItemVisible(List5item_toselect)

        PushButton5a = qt.QPushButton(Tab5,"PushButton5a")
        PushButton5a.setGeometry(qt.QRect(20,20,150,30))
        PushButton5a.setText("Load variable")

	Spacer5b = qt.QSpacerItem(20,20,qt.QSizePolicy.Expanding,qt.QSizePolicy.Minimum)
	
	Tab5Layout.addMultiCellWidget(List5,0,0,0,1)
	Tab5Layout.addWidget(PushButton5a,1,0)
	Tab5Layout.addItem(Spacer5b,1,1)

	#-----------------------------
	Tab1 = qt.QWidget(TabWidget,"Tab1")
	TabWidget.insertTab(Tab1,"Lookmarks/Positions")

        PushButton1a = qt.QPushButton(Tab1,"PushButton1a")
        PushButton1a.setGeometry(qt.QRect(50,30,150,30))
        PushButton1a.setText("Load position")

	SpinBox1a = qt.QSpinBox(Tab1,"SpinBox1a")
        SpinBox1a.setGeometry(qt.QRect(50+0*(120+2),20+2*(30+2),120,20))
        SpinBox1a.setMaxValue(90)
        SpinBox1a.setMinValue(10)
        SpinBox1a.setLineStep(5)
        SpinBox1a.setValue(__main__.ren1xstart*100)
	qt.QToolTip.add(SpinBox1a,"Indicate xstart of viewport")

	SpinBox1b = qt.QSpinBox(Tab1,"SpinBox1b")
        SpinBox1b.setGeometry(qt.QRect(50+0*(120+2),20+3*(30+2),120,20))
        SpinBox1b.setMaxValue(90)
        SpinBox1b.setMinValue(10)
        SpinBox1b.setLineStep(5)
        SpinBox1b.setValue(__main__.ren1xend*100)
	qt.QToolTip.add(SpinBox1b,"Indicate xend of viewport")

	SpinBox1c = qt.QSpinBox(Tab1,"SpinBox1c")
        SpinBox1c.setGeometry(qt.QRect(50+1*(120+2),20+2*(30+2),120,20))
        SpinBox1c.setMaxValue(90)
        SpinBox1c.setMinValue(10)
        SpinBox1c.setLineStep(5)
        SpinBox1c.setValue(__main__.ren1ystart*100)
	qt.QToolTip.add(SpinBox1c,"Indicate ystart of viewport")

	SpinBox1d = qt.QSpinBox(Tab1,"SpinBox1d")
        SpinBox1d.setGeometry(qt.QRect(50+1*(120+2),20+3*(30+2),120,20))
        SpinBox1d.setMaxValue(90)
        SpinBox1d.setMinValue(10)
        SpinBox1d.setLineStep(5)
        SpinBox1d.setValue(__main__.ren1yend*100)
	qt.QToolTip.add(SpinBox1d,"Indicate yend of viewport")

        PushButton1e = qt.QPushButton(Tab1,"PushButton1e")
        PushButton1e.setGeometry(qt.QRect(50+2*(120+2),30,150,30))
        PushButton1e.setText("Redraw")

	SpinBox1f = qt.QSpinBox(Tab1,"SpinBox1f")
        SpinBox1f.setGeometry(qt.QRect(50+2*(120+2),20+2*(30+2),120,20))
        SpinBox1f.setMaxValue(10)
        SpinBox1f.setMinValue(1)
        SpinBox1f.setLineStep(1)
        SpinBox1f.setValue(int(__main__.option_ratioxy))
	qt.QToolTip.add(SpinBox1f,"Indicate ratio X/Y")

	ComboBox1g = qt.QComboBox(Tab1,"ComboBox1g")
        ComboBox1g.setGeometry(qt.QRect(50+2*(120+2),20+3*(30+2),120,30))
	ComboBox1g.insertItem("linear")
        ComboBox1g.insertItem("orthographic")
        ComboBox1g.setCurrentText(__main__.option_projection)

	#-----------------------------
	Tab2 = qt.QWidget(TabWidget,"Tab2")
	TabWidget.insertTab(Tab2,"Overlays")

	#oooooooooooooooooooo
        PushButton2a = qt.QPushButton(Tab2,"PushButton2a")
        PushButton2a.setGeometry(qt.QRect(50,20,120,30))
        PushButton2a.setText("Continents color")

        TextLabel2a = qt.QLabel(Tab2,"TextLabel2a")
        TextLabel2a.setGeometry(qt.QRect(10,20+1*(30+2),37,20))
        TextLabel2a.setText("Width")

        Slider2a= qt.QSlider(Tab2,"Slider2a")
	Slider2a.setGeometry(qt.QRect(50,20+1*(30+2),120,22))
	Slider2a.setMinValue(1)
	Slider2a.setMaxValue(10)
	Slider2a.setLineStep(1)
	Slider2a.setPageStep(1)
	Slider2a.setValue(__main__.option_continents_width)
	Slider2a.setOrientation(qt.QSlider.Horizontal)
	Slider2a.setTickmarks(qt.QSlider.Below)
	Slider2a.setTickInterval(1)
	qt.QToolTip.add(Slider2a,"Indicate line width of continents")

	#oooooooooooooooooooo
        PushButton2b = qt.QPushButton(Tab2,"PushButton2b")
        PushButton2b.setGeometry(qt.QRect(50+1*(120+2),20,120,30))
        PushButton2b.setText("Boundaries color")

        Slider2b= qt.QSlider(Tab2,"Slider2b")
	Slider2b.setGeometry(qt.QRect(50+1*(120+2),20+1*(30+2),120,22))
	Slider2b.setMinValue(1)
	Slider2b.setMaxValue(10)
	Slider2b.setLineStep(1)
	Slider2b.setPageStep(1)
	Slider2b.setValue(__main__.option_boundaries_width)
	Slider2b.setOrientation(qt.QSlider.Horizontal)
	Slider2b.setTickmarks(qt.QSlider.Below)
	Slider2b.setTickInterval(1)
	qt.QToolTip.add(Slider2b,"Indicate line width of boundaries")

	#oooooooooooooooooooo
        PushButton2c = qt.QPushButton(Tab2,"PushButton2c")
        PushButton2c.setGeometry(qt.QRect(50+2*(120+2),20,120,30))
        PushButton2c.setText("Grid color")

        Slider2c= qt.QSlider(Tab2,"Slider2c")
	Slider2c.setGeometry(qt.QRect(50+2*(120+2),20+1*(30+2),120,22))
	Slider2c.setMinValue(1)
	Slider2c.setMaxValue(10)
	Slider2c.setLineStep(1)
	Slider2c.setPageStep(1)
	Slider2c.setValue(__main__.option_grid_width)
	Slider2c.setOrientation(qt.QSlider.Horizontal)
	Slider2c.setTickmarks(qt.QSlider.Below)
	Slider2c.setTickInterval(1)
	qt.QToolTip.add(Slider2c,"Indicate line width of grid")

        TextLabel2c = qt.QLabel(Tab2,"TextLabel2c")
        TextLabel2c.setGeometry(qt.QRect(10+2*(120+2),20+2*(30+2),37,20))
        TextLabel2c.setText("Delta")

	SpinBox2c = qt.QSpinBox(Tab2,"SpinBox2c")
        SpinBox2c.setGeometry(qt.QRect(50+2*(120+2),20+2*(30+2),120,20))
        SpinBox2c.setMaxValue(60)
        SpinBox2c.setMinValue(1)
        SpinBox2c.setLineStep(10)
        SpinBox2c.setValue(__main__.option_grid_delta)
	qt.QToolTip.add(SpinBox2c,"Indicate delta of grid")

	#oooooooooooooooooooo
        PushButton2d = qt.QPushButton(Tab2,"PushButton2d")
        PushButton2d.setGeometry(qt.QRect(50+3*(120+2),20,120,30))
        PushButton2d.setText("Equator color")

        Slider2d= qt.QSlider(Tab2,"Slider2d")
	Slider2d.setGeometry(qt.QRect(50+3*(120+2),20+1*(30+2),120,22))
	Slider2d.setMinValue(1)
	Slider2d.setMaxValue(10)
	Slider2d.setLineStep(1)
	Slider2d.setPageStep(1)
	Slider2d.setValue(__main__.option_equator_width)
	Slider2d.setOrientation(qt.QSlider.Horizontal)
	Slider2d.setTickmarks(qt.QSlider.Below)
	Slider2d.setTickInterval(1)
	qt.QToolTip.add(Slider2d,"Indicate line width of equator")

	#-----------------------------
	Tab4 = qt.QWidget(TabWidget,"Tab4")
	TabWidget.insertTab(Tab4,"Operations")

	Tab4Layout = qt.QGridLayout(Tab4,1,1,20,20,"Tab4Layout")

	TextEdit4a = qt.QTextEdit(Tab4,"TextEdit4a")

	Tab4Layout.addWidget(TextEdit4a,0,0)

	#-----------------------------
	Tab6 = qt.QWidget(TabWidget,"Tab6")
	TabWidget.insertTab(Tab6,"Levels/Colors")

        PushButton6_1 = qt.QPushButton(Tab6,"PushButton6_1")
        PushButton6_1.setGeometry(qt.QRect(50,30,150,30))
        PushButton6_1.setText("Load colors")

        PushButton6_2 = qt.QPushButton(Tab6,"PushButton6_2")
        PushButton6_2.setGeometry(qt.QRect(210,30,150,30))
        PushButton6_2.setText("Redraw")

        GroupBox6a = qt.QGroupBox(Tab6,"GroupBox6a")
	GroupBox6a.setGeometry(qt.QRect(50,80,410,160))
	GroupBox6a.setTitle("Contour values")
	ListBox6a_1 = qt.QListBox(GroupBox6a,"ListBox6a_1")
	ListBox6a_1.setGeometry(qt.QRect(20,30,290,110))
	ListBox6a_1.setVScrollBarMode(qt.QListBox.AlwaysOn)
	ListBox6a_1.setHScrollBarMode(qt.QListBox.Auto)
	for value in __main__.levels_values :
		ListBox6a_1.insertItem(str(value))
	ListBox6a_1.sort()
	PushButton6a_2 = qt.QPushButton(GroupBox6a,"PushButton6a_2")
	PushButton6a_2.setGeometry(qt.QRect(320,30,80,30))
	PushButton6a_2.setText("delele")
	PushButton6a_3 = qt.QPushButton(GroupBox6a,"PushButton6a_3")
	PushButton6a_3.setGeometry(qt.QRect(320,60,80,30))
	PushButton6a_3.setText("delele all")

	GroupBox6b = qt.QGroupBox(Tab6,"GroupBox6b")
	GroupBox6b.setGeometry(qt.QRect(50,250,410,80))
	GroupBox6b.setTitle("Add value")
	TextLabel6b_1 = qt.QLabel(GroupBox6b,"TextLabel6b_1")
	TextLabel6b_1.setGeometry(qt.QRect(20,30,65,20))
	TextLabel6b_1.setText("New value")
	Slider6b_2 = qt.QSlider(GroupBox6b,"Slider6b_2")
	Slider6b_2.setGeometry(qt.QRect(90,30,110,20))
	Slider6b_2.setOrientation(qt.QSlider.Horizontal)
	LineEdit6b_3 = qt.QLineEdit(GroupBox6b,"LineEdit6b_3")
	LineEdit6b_3.setGeometry(qt.QRect(210,30,90,20))
	#LineEdit6b_3.setValidator(qt.QDoubleValidator())
	PushButton6b_4 = qt.QPushButton(GroupBox6b,"PushButton6b_4")
	PushButton6b_4.setGeometry(qt.QRect(320,30,80,30))
	PushButton6b_4.setText("add")

	GroupBox6c = qt.QGroupBox(Tab6,"GroupBox6c")
        GroupBox6c.setGeometry(qt.QRect(50,340,410,110))
	GroupBox6c.setTitle("Generate range of values")
        TextLabel6c_1 = qt.QLabel(GroupBox6c,"TextLabel6c_1")
	TextLabel6c_1.setGeometry(qt.QRect(30,30,110,20))
        TextLabel6c_1.setText("Number of values")
        Slider6c_2 = qt.QSlider(GroupBox6c,"Slider6c_2")
        Slider6c_2.setGeometry(qt.QRect(150,30,110,20))
        Slider6c_2.setOrientation(qt.QSlider.Horizontal)
        LineEdit6c_3 = qt.QLineEdit(GroupBox6c,"LineEdit6c_3")
        LineEdit6c_3.setGeometry(qt.QRect(270,30,30,20))
        PushButton6c_4 = qt.QPushButton(GroupBox6c,"PushButton6c_4")
        PushButton6c_4.setGeometry(qt.QRect(320,30,80,30))
	PushButton6c_4.setText("Generate")
	TextLabel6c_5 = qt.QLabel(GroupBox6c,"TextLabel6c_5")
        TextLabel6c_5.setGeometry(qt.QRect(30,70,40,20))
        TextLabel6c_5.setText("Range")
        LineEdit6c_6 = qt.QLineEdit(GroupBox6c,"LineEdit6c_6")
        LineEdit6c_6.setGeometry(qt.QRect(80,70,90,20))
        Slider6c_7 = qt.QSlider(GroupBox6c,"Slider6c_7")
        Slider6c_7.setGeometry(qt.QRect(180,70,110,20))
        Slider6c_7.setOrientation(qt.QSlider.Horizontal)
        LineEdit6c_8 = qt.QLineEdit(GroupBox6c,"LineEdit6c_8")
        LineEdit6c_8.setGeometry(qt.QRect(300,70,90,20))

	#-----------------------------
	Tab7 = qt.QWidget(TabWidget,"Tab7")
	TabWidget.insertTab(Tab7,"Texts")

	Tab7Layout = qt.QGridLayout(Tab7,1,1,20,20,"Tab7Layout")

	TextEdit7 = qt.QTextBrowser(Tab7,"TextEdit7")
	TextEdit7.setTextFormat(qt.QTextEdit.AutoText)
	TextEdit7.setReadOnly(1)
	TextEdit7.mimeSourceFactory().setExtensionType("txt", "text/plain")

	Tab7Layout.addWidget(TextEdit7,0,0)

	#-----------------------------
	Tab8 = qt.QWidget(TabWidget,"Tab8")
	TabWidget.insertTab(Tab8,"Help")

	Tab8Layout = qt.QGridLayout(Tab8,1,1,20,20,"Tab8Layout")

	TextBrowser8 = qt.QTextBrowser(Tab8,"TextBrowser1")
        TextBrowser8.setText(__main__.interactions)

	Tab8Layout.addWidget(TextBrowser8,0,0)

	#-----------------------------
	Tab9 = qt.QWidget(TabWidget,"Tab9")
	TabWidget.insertTab(Tab9,"Credits")

	Tab9Layout = qt.QGridLayout(Tab9,1,1,20,20,"Tab9Layout")

	TextBrowser9 = qt.QTextBrowser(Tab9,"TextBrowser1")
        TextBrowser9.setText(__main__.credits)

	Tab9Layout.addWidget(TextBrowser9,0,0)

	#-----------------------------
	Win.connect(FileSelect3,qt.SIGNAL("fileSelected(const QString&)"), button_file_selected)
	#Win.connect(FileSelect3,qt.SIGNAL("okClicked()"), button_ok)
	#Win.connect(FileSelect3,qt.SIGNAL("cancelClicked()"), button_cancel)
	
	Win.connect(PushButton1a,qt.SIGNAL("pressed()"), button_load_position_pressed)
	Win.connect(SpinBox1a,qt.SIGNAL("valueChanged(int)"),slider_xstart_grid_changed)
	Win.connect(SpinBox1b,qt.SIGNAL("valueChanged(int)"),slider_xend_grid_changed)
	Win.connect(SpinBox1c,qt.SIGNAL("valueChanged(int)"),slider_ystart_grid_changed)
	Win.connect(SpinBox1d,qt.SIGNAL("valueChanged(int)"),slider_yend_grid_changed)
	Win.connect(PushButton1e,qt.SIGNAL("pressed()"), button_redraw_pressed)
	Win.connect(SpinBox1f,qt.SIGNAL("valueChanged(int)"),slider_ratioxy_changed)
	Win.connect(ComboBox1g,qt.SIGNAL("activated(const QString&)"),combobox_projection_activated)
        Win.connect(PushButton2a,qt.SIGNAL("pressed()"), button_color_continents_pressed)
	Win.connect(Slider2a,qt.SIGNAL("valueChanged(int)"),slider_width_continents_changed)
        Win.connect(PushButton2b,qt.SIGNAL("pressed()"), button_color_boundaries_pressed)
	Win.connect(Slider2b,qt.SIGNAL("valueChanged(int)"),slider_width_boundaries_changed)
        Win.connect(PushButton2c,qt.SIGNAL("pressed()"), button_color_grid_pressed)
	Win.connect(Slider2c,qt.SIGNAL("valueChanged(int)"),slider_width_grid_changed)
	Win.connect(SpinBox2c,qt.SIGNAL("valueChanged(int)"),slider_delta_grid_changed)
        Win.connect(PushButton2d,qt.SIGNAL("pressed()"), button_color_equator_pressed)
	Win.connect(Slider2d,qt.SIGNAL("valueChanged(int)"),slider_width_equator_changed)
	Win.connect(List5,qt.SIGNAL("expanded(QListViewItem*)"), list_variables_expanded)
	Win.connect(PushButton5a,qt.SIGNAL("pressed()"), button_load_variable_pressed)
	Win.connect(PushButton6_1,qt.SIGNAL("pressed()"), button_load_spectrumferretfile_pressed)
	Win.connect(PushButton6_2,qt.SIGNAL("pressed()"), button_redraw_newlevels_pressed)
	Win.connect(PushButton6a_2,qt.SIGNAL("pressed()"), button_delete_level)
	Win.connect(PushButton6a_3,qt.SIGNAL("pressed()"), button_delete_alllevels)
	Win.connect(PushButton6b_4,qt.SIGNAL("pressed()"), button_add_level)
	Win.connect(PushButton6c_4,qt.SIGNAL("pressed()"), button_generate_levels)
	Win.connect(TextEdit7,qt.SIGNAL("linkClicked(const QString&)"), file_browser_clicked)

	#-----------------------------
	TabWidget.showPage(Tab5)

	#-----------------------------
	RenWinInter = QVTKRenderWindowInteractor(WinSplitter)
	RenWinInter.AddObserver("ExitEvent", lambda o, e, a=App: a.quit())
	RenWin = RenWinInter.GetRenderWindow()
	RenWin.SetSize(window_width,window_height)
	Inter = RenWin.GetInteractor()

	#-----------------------------
	WinSplitter.setSizes([200,window_height])
	
	#-----------------------------
	WinLayout.addWidget(WinSplitter)	

	return App,Win,RenWin,Inter

#**************************************
