import vtk
import numpy as np
import vtk.util.numpy_support as VN

fileName = 'pv_insitu_300x300x300_30068.vti'
#download from
daryName = 'v02'
colors = vtk.vtkNamedColors()
ren1 = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren1)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

ren1.SetBackground(51/255, 77/255, 102/255)

# Create the reader for the data.
# reader = vtk.vtkStructuredPointsReader()
# reader.SetFileName(fileName)
# Create the reader for the data
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName(fileName)
reader.Update()

# specify the data array in the file to process
reader.GetOutput().GetPointData().SetActiveAttribute(daryName,0)

# convert the data array to numpy array and get the min and maximum valule

 

dary = VN.vtk_to_numpy(reader.GetOutput().GetPointData().GetScalars('v02'))
dMax = np.amax(dary) #data min value
dMin = np.amin(dary) #data max value
dRange = dMax - dMin


# An outline provides context around the data.
outlineData = vtk.vtkOutlineFilter()
outlineData.SetInputConnection(reader.GetOutputPort())
outlineData.Update()

mapOutline = vtk.vtkPolyDataMapper()
mapOutline.SetInputConnection(outlineData.GetOutputPort())

outline = vtk.vtkActor()
outline.SetMapper(mapOutline)
outline.GetProperty().SetColor(colors.GetColor3d("White"))

# Create transfer mapping scalar value to opacity.
opacityTransferFunction = vtk.vtkPiecewiseFunction()
opacityTransferFunction.AddPoint(dMin, 0.0)
#opacityTransferFunction.AddPoint(dMin + dRange/2, 0.005)
opacityTransferFunction.AddPoint(dMax, 0.001) ###### very small, still


# Create transfer mapping scalar value to color.
colorTransferFunction = vtk.vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(dMin, 1.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(dMin + (dRange/4)*1, 1.0, 1.0, 0.0)
colorTransferFunction.AddRGBPoint(dMin + (dRange/4)*2, 0.0, 1.0, 0.0)
colorTransferFunction.AddRGBPoint(dMin + (dRange/4)*3, 0.0, 1.0, 1.0)
colorTransferFunction.AddRGBPoint(dMin + (dRange/4)*4, 0.0, 0.0, 1.0)

# The property describes how the data will look.
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(colorTransferFunction)
volumeProperty.SetScalarOpacity(opacityTransferFunction)
volumeProperty.ShadeOn()
volumeProperty.SetInterpolationTypeToLinear()

# The mapper / ray cast function know how to render the data.

volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
volumeMapper.SetInputConnection(reader.GetOutputPort())

hueLut = vtk.vtkLookupTable()
hueLut.SetTableRange(dMin, dMax)
# hueLut.SetHueRange(0, 1)  #comment these three line to default color map, rainbow
# hueLut.SetSaturationRange(1, 1)
# hueLut.SetValueRange(1, 1)
hueLut.Build()  # effective built

# create the scalar_bar
scalar_bar = vtk.vtkScalarBarActor()
scalar_bar.SetOrientationToHorizontal()
scalar_bar.SetLookupTable(hueLut)
scalar_bar.SetTitle("Scalar value(v02)")
# create the scalar_bar_widget
scalar_bar_widget = vtk.vtkScalarBarWidget()
scalar_bar_widget.SetInteractor(iren)
scalar_bar_widget.SetScalarBarActor(scalar_bar)
scalar_bar_widget.On()

# The volume holds the mapper and the property and
# can be used to position/orient the volume.
volume = vtk.vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)

ren1.AddVolume(volume)
ren1.AddActor(outline)
ren1.GetActiveCamera().Azimuth(45)
ren1.GetActiveCamera().Elevation(30)
ren1.ResetCameraClippingRange()
ren1.ResetCamera()

renWin.SetSize(600, 600)
renWin.Render()

iren.Start()
