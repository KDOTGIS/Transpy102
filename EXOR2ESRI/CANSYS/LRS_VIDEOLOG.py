'''
Created on Aug 20, 2013
Script to calibrate the VIDEOLOG Lane traces to the CANSYS logmile system using the LRS_CRND control points, and create GIS dual carriage-way routes for DYNSEG in ArcGIS
Need to decide whether to use CANSYS EB/WB/NB/SB, HPMS-Videolog (1:8) and/or both for directions

@author: kyleg
'''

class MyClass(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
        
from arcpy import mapping, env, SimplifyLine_cartography, MakeFeatureLayer_management, FeatureClassToGeodatabase_conversion, CreateRoutes_lr, CalibrateRoutes_lr, AddField_management, CalculateField_management, Append_management


mxd = mapping.MapDocument(r"\\GISDATA\ArcGIS\GISDATA\MXD\StateSysLaneCalib.mxd")
df = mapping.ListDataFrames(mxd, "Layers")[0]
from CONFIG import ws, tempgdb, XYResolution, XYTolerance, now, MResolution, MTolerance
env.XYResolution = XYResolution
env.XYTolerance = XYTolerance
env.MResolution = MResolution
env.MTolerance = MTolerance

gisprod = r'Database Connections\GISTEST.sde'
route = "STATE_SYSTEM_LANE"
pathloc = ws+"\\"+tempgdb
routelyr = ws+"/"+tempgdb+"/"+route
inlyr = gisprod+"/"+route

print routelyr
print pathloc
print inlyr

SimplifyLine_cartography(gisprod+"/SHARED.STATE_SYSTEM_LANE",routelyr,"POINT_REMOVE","1 Meters","RESOLVE_ERRORS","KEEP_COLLAPSED_POINTS","CHECK")
MakeFeatureLayer_management(inlyr,route+"_Primary",""""DIRECTION"<4""","#","#")
MakeFeatureLayer_management(inlyr,route+"_Secondary",""""DIRECTION">4""","#","#")
FeatureClassToGeodatabase_conversion("STATE_SYSTEM_LANE_Primary",pathloc)
FeatureClassToGeodatabase_conversion("STATE_SYSTEM_LANE_Secondary",pathloc)
CreateRoutes_lr(routelyr+"_Primary","LRS_KEY",routelyr+"_ROUTES1","TWO_FIELDS","BEG_CNTY_LOGMILE","END_CNTY_LOGMILE","LOWER_LEFT","1","0","IGNORE","INDEX")
CreateRoutes_lr(routelyr+"_Secondary","LRS_KEY",routelyr+"_ROUTES2","TWO_FIELDS","END_CNTY_LOGMILE","BEG_CNTY_LOGMILE","LOWER_LEFT","1","0","IGNORE","INDEX")

CalibrateRoutes_lr(routelyr+"_ROUTES1","LRS_KEY",pathloc+"\Calibration_Points_CRND","LRS_KEY","CR_MEAS",routelyr+"_LRS","MEASURES","2000 Feet","BETWEEN","BEFORE","AFTER","IGNORE","KEEP","INDEX")
CalibrateRoutes_lr(routelyr+"_ROUTES2","LRS_KEY",pathloc+"\Calibration_Points_CRND","LRS_KEY","CR_MEAS",routelyr+"_LRS_2","MEASURES","2000 Feet","BETWEEN","BEFORE","AFTER","IGNORE","KEEP","INDEX")
print "routes calibrated STATE_SYSTEM_LRS"
AddField_management(routelyr+"_LRS", "Direction", "TEXT", "#", "#", "2")
AddField_management(routelyr+"_LRS_2", "Direction", "TEXT", "#", "#", "2")
AddField_management(routelyr+"_LRS", "LRS_KEY_DIR", "TEXT", "#", "#", "18")
AddField_management(routelyr+"_LRS_2", "LRS_KEY_DIR", "TEXT", "#", "#", "18")

MakeFeatureLayer_management(routelyr+"_LRS","primary_eb","""SUBSTRING("LRS_KEY",9,1) in ('0','2','4','6','8')""")
CalculateField_management("primary_eb","Direction","'EB'","PYTHON_9.3","#")
MakeFeatureLayer_management(routelyr+"_LRS","primary_nb","""SUBSTRING("LRS_KEY",9,1) in ('1','3','5','9')""")
CalculateField_management("primary_nb","Direction","'NB'","PYTHON_9.3","#")

MakeFeatureLayer_management(routelyr+"_LRS_2","secondary_wb","""SUBSTRING("LRS_KEY",9,1) in ('0','2','4','6','8')""")
CalculateField_management("secondary_wb","Direction","'WB'","PYTHON_9.3","#")
MakeFeatureLayer_management(routelyr+"_LRS_2","secondary_sb","""SUBSTRING("LRS_KEY",9,1) in ('1','3','5','9')""")
CalculateField_management("secondary_sb","Direction","'SB'","PYTHON_9.3","#")

CalculateField_management(routelyr+"_LRS_2","LRS_KEY_DIR","""!LRS_KEY! + "-"+!Direction!""","PYTHON_9.3","#")
CalculateField_management(routelyr+"_LRS","LRS_KEY_DIR","""!LRS_KEY! + "-"+!Direction!""","PYTHON_9.3","#")
print "directional components calculated"
Append_management(routelyr+"_LRS_2",routelyr+"_LRS","NO_TEST","#", "#")
print "routes combined to dual carriageway"
mxdcopy = r"\\GISDATA\ArcGIS\GISDATA\MXD\NewGISLRS"+str(now.year)+"_"+str(now.month)+"_"+str(now.day)+".mxd"
mapping.MapDocument.saveACopy(mxd, mxdcopy) 
del mxd, mxdcopy
print "Dual Carriageway calibrated with no processing error, check for route and measure error"        

