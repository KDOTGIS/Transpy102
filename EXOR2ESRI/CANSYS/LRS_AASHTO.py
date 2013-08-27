'''
Created on Aug 26, 2013

@author: kyleg
'''
class LRS_CRND_SRND(object):
    '''
    classdocs
    '''

def __init__(self):
        '''
        Constructor
        '''  
    
import arcpy
from ENV import ws, tempgdb
inws = ws+"/"+tempgdb
inws = r'\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST\CANSYSNet2013_7_29.gdb'
#mxd = arcpy.mapping.MapDocument(r"\\GISDATA\ArcGIS\GISDATA\MXD\NewGISNetworkSeed.mxd")
#df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]

outws = r'\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST\AASHTOPROC.gdb'
outfinal = r'\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST\AASHTORoutes.gdb'
route = "SRND"
routelyr = inws+"/"+route
IDfield = "NE_UNIQUE"

if arcpy.Exists(outws):
    arcpy.Delete_management(outws)
    arcpy.CreateFileGDB_management(r"\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST", "AASHTOPROC.gdb" )
else:
    arcpy.CreateFileGDB_management(r"\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST", "AASHTOPROC.gdb" )

if arcpy.Exists(outfinal):
    arcpy.Delete_management(outfinal)
    arcpy.CreateFileGDB_management(r"\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST", "AASHTOROUTES.gdb" )
else:
    arcpy.CreateFileGDB_management(r"\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST", "AASHTOROUTES.gdb" )
    
arcpy.FeatureClassToFeatureClass_conversion(routelyr, outws, "USRoutes", "NE_UNIQUE LIKE 'U%'", "#")

routelyr = outws + "/USroutes"
rows = arcpy.SearchCursor(routelyr)

for row in rows:
    print(row.getValue(IDfield))
    idc = str(row.getValue(IDfield)).replace("-", "_")
    print idc
    rfcx = str(row.getValue(IDfield))+"_SRND"
    rfc = str(rfcx).replace("-", "_")
    print str(rfc)
    arcpy.MakeFeatureLayer_management(routelyr, rfc, IDfield+" LIKE '"+ row.getValue(IDfield)+"'")
    arcpy.FeatureClassToGeodatabase_conversion(rfc, outws)        
    arcpy.FeatureVerticesToPoints_management(rfc,outws+"/"+idc+"_VP","ALL")
    arcpy.LocateFeaturesAlongRoutes_lr(outws+"/"+idc+"_VP",rfc, IDfield,"0 DecimalDegrees",outws+"/"+idc+"_CPT","NE_UNIQUE POINT AASHTO_MEAS","FIRST","DISTANCE","ZERO","FIELDS","M_DIRECTON")
    arcpy.DeleteIdentical_management(outws+"/"+idc+"_CPT","NE_UNIQUE;AASHTO_MEAS","#","0")
    arcpy.Statistics_analysis(outws+"/"+idc+"_CPT",outws+"/"+idc+"_ENDS","AASHTO_MEAS MIN;AASHTO_MEAS MAX","NE_UNIQUE")
    arcpy.AddJoin_management(idc+"_SRND",IDfield,outws+"/"+idc+"_ENDS",IDfield,"KEEP_ALL")
    arcpy.CreateRoutes_lr(idc+"_SRND",IDfield,outws+"/"+idc,"TWO_FIELDS",idc+"_ENDS.MAX_AASHTO_MEAS",idc+"_ENDS.MIN_AASHTO_MEAS","UPPER_LEFT","1","0","IGNORE","INDEX")
    arcpy.MakeRouteEventLayer_lr(outws+"/"+idc+"_SRND",IDfield,outws+"/"+idc+"_CPT","NE_UNIQUE POINT AASHTO_MEAS",idc+"_CP","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
    arcpy.FeatureClassToGeodatabase_conversion(idc+"_CP",outws)
    arcpy.MakeFeatureLayer_management(outws+"/"+idc+"_CP", idc+"_CP", IDfield+" LIKE '"+ row.getValue(IDfield)+"'")
    arcpy.AddJoin_management(idc+"_CP",IDfield,outws+"/"+idc+"_ENDS",IDfield,"KEEP_ALL")
    arcpy.CalculateField_management(idc+"_CP",idc+"_CP.AASHTO_MEAS",'['+idc+'_ENDS.MAX_AASHTO_MEAS] - ['+idc+'_CP.AASHTO_MEAS]',"VB","#")
    arcpy.CalibrateRoutes_lr(outws+"/"+idc,IDfield,idc+"_CP",IDfield,"AASHTO_MEAS",outws+"/"+idc+"Calibrated","DISTANCE","0 DecimalDegrees","BETWEEN","NO_BEFORE","NO_AFTER","IGNORE","KEEP","INDEX")
    if arcpy.Exists(outfinal+"/AASHTO_US"):
        arcpy.Append_management(outws+"/"+idc+"Calibrated", outfinal+"/AASHTO_US", "NO_TEST", "#")
        arcpy.Append_management(outws+"/"+idc+"_CP", outfinal+"/AASHTO_US_CP", "NO_TEST", "#")
    else:
        arcpy.FeatureClassToFeatureClass_conversion(outws+"/"+idc+"Calibrated", outfinal, "AASHTO_US", "#")
        arcpy.FeatureClassToFeatureClass_conversion(outws+"/"+idc+"_CP", outfinal, "AASHTO_US_CP", "#")