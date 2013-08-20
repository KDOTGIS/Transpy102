'''
Created on Aug 20, 2013

Created on Jun 25, 2013
Script to calibrate the state system network to the CANSYS logmile system, and create GIS routes for DYNSEG in ArcGIS
Creates "Control Points" for EXOR route groups and calibrates GIS routes to these route groups using EXOR SECT Geometry and the MAP_EXTRACT MV
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
from ENV import ws, tempgdb, nowish, LRSENV     
mxd = arcpy.mapping.MapDocument(r"\\GISDATA\ArcGIS\GISDATA\MXD\NewGISNetworkSeed.mxd")
df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]

route = "SRND"
pathloc = ws+"\\"+tempgdb
routelyr = ws+"\\"+tempgdb+"\\"+route
inlyr2 = ws+"\\"+tempgdb+"/STATE_SYSTEM"
arcpy.FeatureVerticesToPoints_management(ws+"\\"+tempgdb+"/STATE_SYSTEM", ws+"\\"+tempgdb+"/Calibration_Points","ALL")
inlyr1 = ws+"\\"+tempgdb+"/Calibration_Points"

arcpy.LocateFeaturesAlongRoutes_lr(ws+"\\"+tempgdb+"/Calibration_Points",ws+"\\"+tempgdb+"/SRND","NE_UNIQUE","0.001 Feet",ws+"\\"+tempgdb+"/CP_SRND","STATE_MILE POINT SR_MEAS","ALL","DISTANCE","ZERO","FIELDS","M_DIRECTON")
arcpy.MakeTableView_management(ws+"\\"+tempgdb+"/CP_SRND","Calibration_SR",'"STATE_MILE" = "SRND"', ws+"\\"+tempgdb,"#")
arcpy.MakeRouteEventLayer_lr(routelyr,"NE_UNIQUE","Calibration_SR","STATE_MILE POINT SR_MEAS","SR_Calibration_Events","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
arcpy.FeatureClassToFeatureClass_conversion("SR_Calibration_Events",ws+"\\"+tempgdb,"Calibration_Points_SRND","#","#")
arcpy.DeleteIdentical_management(ws+"\\"+tempgdb+"/Calibration_Points_SRND","STATE_MILE;SR_MEAS","0.002 Miles","0")
arcpy.CreateRoutes_lr(ws+"\\"+tempgdb+"/State_System","LRS_ROUTE",ws+"\\"+tempgdb+"/StateSystem_State_Route_SRND","TWO_FIELDS","BEG_STATE_LOGMILE","END_STATE_LOGMILE","UPPER_LEFT","1","0","IGNORE","INDEX")
arcpy.CalibrateRoutes_lr(ws+"\\"+tempgdb+"/StateSystem_State_Route_"+route,"LRS_ROUTE",ws+"\\"+tempgdb+"/Calibration_Points_SRND","LRS_ROUTE","SR_MEAS",ws+"\\"+tempgdb+"/SMLRS","MEASURES","5 feet","BETWEEN","BEFORE","AFTER","IGNORE","KEEP","INDEX")
arcpy.AddField_management(ws+"\\"+tempgdb+"/SMLRS", "NETWORKDATE", "DATE")
arcpy.CalculateField_management(ws+"\\"+tempgdb+"/SMLRS","NETWORKDATE","datetime.datetime.now( )","PYTHON_9.3","#")

route = "CRND"
routelyr = ws+"\\"+tempgdb+"\\"+route
arcpy.LocateFeaturesAlongRoutes_lr(ws+"\\"+tempgdb+"/Calibration_Points",ws+"\\"+tempgdb+"/CRND","NE_UNIQUE","0.001 Feet",ws+"\\"+tempgdb+"/CP_CRND","STATE_MILE POINT CR_MEAS","ALL","DISTANCE","ZERO","FIELDS","M_DIRECTON")
arcpy.MakeTableView_management(ws+"\\"+tempgdb+"/CP_CRND","Calibration_CR",'"STATE_MILE" = "CRND"', ws+"\\"+tempgdb,"#")
arcpy.MakeRouteEventLayer_lr(routelyr,"NE_UNIQUE","Calibration_CR","STATE_MILE POINT CR_MEAS","CR_Calibration_Events","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
arcpy.FeatureClassToFeatureClass_conversion("CR_Calibration_Events",ws+"\\"+tempgdb,"Calibration_Points_CRND","#","#")
arcpy.DeleteIdentical_management(ws+"\\"+tempgdb+"/Calibration_Points_CRND","STATE_MILE;CR_MEAS","0.002 Miles","0")
arcpy.CreateRoutes_lr(ws+"\\"+tempgdb+"/State_System","LRS_KEY",ws+"\\"+tempgdb+"/StateSystem_County_Route_CRND","TWO_FIELDS","BEG_CNTY_LOGMILE","END_CNTY_LOGMILE","UPPER_LEFT","1","0","IGNORE","INDEX")
arcpy.CalibrateRoutes_lr(ws+"\\"+tempgdb+"/StateSystem_County_Route_"+route,"LRS_KEY",ws+"\\"+tempgdb+"/Calibration_Points_CRND","LRS_KEY","CR_MEAS",ws+"\\"+tempgdb+"/CMLRS","MEASURES","5 feet","BETWEEN","BEFORE","AFTER","IGNORE","KEEP","INDEX")
arcpy.AddField_management(ws+"\\"+tempgdb+"/CMLRS", "NETWORKDATE", "DATE")
arcpy.CalculateField_management(ws+"\\"+tempgdb+"/CMLRS","NETWORKDATE","datetime.datetime.now( )","PYTHON_9.3","#")

mxdcopy = r"\\GISDATA\ArcGIS\GISDATA\MXD\NewGISLRS"+nowish+".mxd"
arcpy.mapping.MapDocument.saveACopy(mxd, mxdcopy) 
del mxd, mxdcopy
print "Networks calibrated with no error"


        