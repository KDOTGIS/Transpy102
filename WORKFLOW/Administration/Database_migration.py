'''
Created on Jan 22, 2014

@author: kyleg
'''
import arcpy
import cx_Oracle
outws = r'\\Database Connections\SDEDEV_SHARED.sde\SHARED.'
mxd = arcpy.mapping.MapDocument(r"\\gisdata\arcgis\GISdata\MXD\GISPROD2SDEDEV_GIS.mxd")
for df in arcpy.mapping.ListDataFrames(mxd, "TESTPROJ") :
    for lyr in arcpy.mapping.ListLayers(df):
        print lyr.name
        destlyr = outws+lyr
        

