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
    
from arcpy import Exists, Delete_management, CreateFileGDB_management, CreateRoutes_lr, FeatureClassToFeatureClass_conversion, SearchCursor, MakeFeatureLayer_management, FeatureClassToGeodatabase_conversion
from arcpy import CalculateField_management, MakeRouteEventLayer_lr, FeatureVerticesToPoints_management, LocateFeaturesAlongRoutes_lr, DeleteIdentical_management, Statistics_analysis, AddJoin_management, Append_management, CalibrateRoutes_lr
from CONFIG import ws, tempgdb
inws = ws+"/"+tempgdb
inws = r'\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST\CANSYSNet2013_7_29.gdb'
#mxd = arcpy.mapping.MapDocument(r"\\GISDATA\ArcGIS\GISDATA\MXD\NewGISNetworkSeed.mxd")
#df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]

outws = r'\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST\AASHTOPROC.gdb'
outfinal = r'\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST\AASHTORoutes.gdb'
route = "SRND"
routelyr = inws+"/"+route
IDfield = "NE_UNIQUE"

if Exists(outws):
    Delete_management(outws)


CreateFileGDB_management(r"\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST", "AASHTOPROC.gdb" )

if Exists(outfinal):
    Delete_management(outfinal)

CreateFileGDB_management(r"\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST", "AASHTOROUTES.gdb" )
    
FeatureClassToFeatureClass_conversion(routelyr, outws, "USRoutes", "NE_UNIQUE LIKE 'U%'", "#")

routelyr = outws + "/USroutes"
rows = SearchCursor(routelyr)

for row in rows:
    print(row.getValue(IDfield))
    idc = str(row.getValue(IDfield)).replace("-", "_")
    print idc
    rfcx = str(row.getValue(IDfield))+"_SRND"
    rfc = str(rfcx).replace("-", "_")
    print str(rfc)
    MakeFeatureLayer_management(routelyr, rfc, IDfield+" LIKE '"+ row.getValue(IDfield)+"'")
    FeatureClassToGeodatabase_conversion(rfc, outws)        
    FeatureVerticesToPoints_management(rfc,outws+"/"+idc+"_VP","ALL")
    LocateFeaturesAlongRoutes_lr(outws+"/"+idc+"_VP",rfc, IDfield,"0 DecimalDegrees",outws+"/"+idc+"_CPT","NE_UNIQUE POINT AASHTO_MEAS","FIRST","DISTANCE","ZERO","FIELDS","M_DIRECTON")
    DeleteIdentical_management(outws+"/"+idc+"_CPT","NE_UNIQUE;AASHTO_MEAS","#","0")
    Statistics_analysis(outws+"/"+idc+"_CPT",outws+"/"+idc+"_ENDS","AASHTO_MEAS MIN;AASHTO_MEAS MAX","NE_UNIQUE")
    AddJoin_management(idc+"_SRND",IDfield,outws+"/"+idc+"_ENDS",IDfield,"KEEP_ALL")
    CreateRoutes_lr(idc+"_SRND",IDfield,outws+"/"+idc,"TWO_FIELDS",idc+"_ENDS.MAX_AASHTO_MEAS",idc+"_ENDS.MIN_AASHTO_MEAS","UPPER_LEFT","1","0","IGNORE","INDEX")
    MakeRouteEventLayer_lr(outws+"/"+idc+"_SRND",IDfield,outws+"/"+idc+"_CPT","NE_UNIQUE POINT AASHTO_MEAS",idc+"_CP","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
    FeatureClassToGeodatabase_conversion(idc+"_CP",outws)
    MakeFeatureLayer_management(outws+"/"+idc+"_CP", idc+"_CP", IDfield+" LIKE '"+ row.getValue(IDfield)+"'")
    AddJoin_management(idc+"_CP",IDfield,outws+"/"+idc+"_ENDS",IDfield,"KEEP_ALL")
    CalculateField_management(idc+"_CP",idc+"_CP.AASHTO_MEAS",'['+idc+'_ENDS.MAX_AASHTO_MEAS] - ['+idc+'_CP.AASHTO_MEAS]',"VB","#")
    CalibrateRoutes_lr(outws+"/"+idc,IDfield,idc+"_CP",IDfield,"AASHTO_MEAS",outws+"/"+idc+"Calibrated","DISTANCE","0 DecimalDegrees","BETWEEN","NO_BEFORE","NO_AFTER","IGNORE","KEEP","INDEX")
    if Exists(outfinal+"/AASHTO_US"):
        Append_management(outws+"/"+idc+"Calibrated", outfinal+"/AASHTO_US", "NO_TEST", "#")
        Append_management(outws+"/"+idc+"_CP", outfinal+"/AASHTO_US_CP", "NO_TEST", "#")
    else:
        FeatureClassToFeatureClass_conversion(outws+"/"+idc+"Calibrated", outfinal, "AASHTO_US", "#")
        FeatureClassToFeatureClass_conversion(outws+"/"+idc+"_CP", outfinal, "AASHTO_US_CP", "#")