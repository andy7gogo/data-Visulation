import vtk
import vtk.util.numpy_support as VN
import numpy as np

fileName = 'pv_insitu_300x300x300_30068.vti'

daryName = 'v02'
colors = vtk.vtkNamedColors()
aRenderer = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(aRenderer)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

aRenderer.SetBackground(51/255, 77/255, 102/255)
renWin.SetSize(600, 600)

reader = vtk.vtkXMLImageDataReader()
reader.SetFileName(fileName)
reader.Update()

reader.GetOutput().GetPointData().SetActiveAttribute(daryName,0)


 

dary = VN.vtk_to_numpy(reader.GetOutput().GetPointData().GetScalars('v02'))
dMax = np.amax(dary) 
dMin = np.amin(dary) 
dRange = dMax - dMin
print("Data array max: ", np.amax(dary))
print("Data array min: ", np.amin(dary))


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
opacityT = vtk.vtkPiecewiseFunction()
opacityT.AddPoint(dMin, 0.0)
#opacityT.AddPoint(dMin + dRange/2, 0.005)
opacityT.AddPoint(dMax, 0.001) ###### very small, still


# Create transfer mapping scalar value to color.
colorT = vtk.vtkColorTransferFunction()
colorT.AddRGBPoint(dMin, 1.0, 0.0, 0.0)
colorT.AddRGBPoint(dMin + (dRange/4)*1, 1.0, 1.0, 0.0)
colorT.AddRGBPoint(dMin + (dRange/4)*2, 0.0, 1.0, 0.0)
colorT.AddRGBPoint(dMin + (dRange/4)*3, 0.0, 1.0, 1.0)
colorT.AddRGBPoint(dMin + (dRange/4)*4, 0.0, 0.0, 1.0)

# The property describes how the data will look.
volumePr = vtk.vtkVolumeProperty()
volumePr.SetColor(colorT)
volumePr.SetScalarOpacity(opacityT)
volumePr.ShadeOn()
volumePr.SetInterpolationTypeToLinear()

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
volume.SetProperty(volumePr)

aRenderer.AddVolume(volume)
aRenderer.AddActor(outline)


aCamera = vtk.vtkCamera()
aCamera.SetViewUp(0, 0, -1)
aCamera.SetPosition(0, -1, 0)
aCamera.SetFocalPoint(0, 0, 0)
aCamera.ComputeViewPlaneNormal()
aCamera.Azimuth(30.0)
aCamera.Elevation(30.0)

aRenderer.SetActiveCamera(aCamera)

renWin.Render()

aRenderer.ResetCamera()
aCamera.Dolly(1.5)

aRenderer.ResetCameraClippingRange()

# Interact with the data.
renWin.Render()
iren.Initialize()
iren.Start()

