'''
Created on Aug 21, 2013

@author: kyleg
'''

if __name__ == '__main__':
    pass
import arcpy, datetime

mxd = arcpy.mapping.MapDocument(r'\\gisdata\arcgis\GISdata\MXD\CIIMS_PROCESS_DEV.mxd')
dev = r'Database Connections\sdedev_ciims.sde\CIIMS.'
prod = r'Database Connections\SDEprod_ciims.sde\CIIMS.'

def XYFC(tbl, fc, Lat, Long, GCS):

    arcpy.MakeTableView_management(tbl, 'FCtbl', "#", "#", "")
    arcpy.MakeXYEventLayer_management("FCtbl",Long, Lat,"FC_Layer", GCS,"#")
    arcpy.DeleteFeatures_management(fc)
    arcpy.Append_management("FC_Layer",fc,"NO_TEST","#","#")
    arcpy.CalculateField_management(fc,"LOADDATE","datetime.datetime.now( )","PYTHON_9.3","#")
  
class CIIMS:
    start = datetime.datetime.now()
    view = 'CIIMS_VWCROSSINGGIS3'
    GCS = "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision"
    server = dev
    fc = server + r'CIIMS\CIIMS.Static_Crossings'
    tbl = server + view
    fields = ["CROSSINGID", "CROSSINGLATITUDE", "CROSSINGLONGITUDE", "CROSSINGTYPE", "ORIG_FID", "SHAPEXY", "LOADDATE"]
    Lat = "CROSSINGLATITUDE"
    Long = "CROSSINGLONGITUDE"
    XYFC(tbl, fc, Lat, Long, GCS)
    finish = datetime.datetime.now()
    print "ran CIIMS update in " (finish-start)
del mxd


