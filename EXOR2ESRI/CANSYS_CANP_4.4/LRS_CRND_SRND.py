'''
Created on Aug 20, 2013

Created on Jun 25, 2013
Script to calibrate the state system network to the CANSYS logmile system, and create GIS routes for DYNSEG in ArcGIS
Creates "Control Points" for EXOR route groups and calibrates GIS routes to these route groups using EXOR SECT Geometry and the MAP_EXTRACT MV
@author: kyleg

modified December 2013 to take advantage of CANP direct connection
'''
#import arcpy functions
from arcpy import mapping, env, MakeFeatureLayer_management, FeatureVerticesToPoints_management, LocateFeaturesAlongRoutes_lr, MakeTableView_management, MakeRouteEventLayer_lr, FeatureClassToFeatureClass_conversion, AddXY_management
from arcpy import DeleteIdentical_management, CreateRoutes_lr, CalibrateRoutes_lr, AddField_management, CalculateField_management, AddJoin_management, FeatureClassToGeodatabase_conversion, TableToTable_conversion
#from CONFIG import ws, EXOR_PROD, STAGEDB, nowish, MTolerance, MResolution    

#Set the workspace database connections
EXOR_PROD =  "Database Connections\CANP.odc\:"
STAGEDB = r"Database Connections\SQL61_GIS_CANSYS.sde"
MResolution = 0.0005 
MTolerance = 0.001 

#Control the MXD for processing
mxd = mapping.MapDocument("CURRENT") 
env.MTolerance = MTolerance
env.MResolution = MResolution

#Copy Network Layers from CANSYS to Staging Area.  SRND and CRND layers have full history 
FeatureClassToFeatureClass_conversion(r"Database Connections\CANP.sde\NM3.NM_NLT_SRND_SRND_SDO", STAGEDB, "SRND" )
FeatureClassToFeatureClass_conversion(r"Database Connections\CANP.sde\NM3.NM_NLT_CRND_CRND_SDO", STAGEDB, "CRND" )
TableToTable_conversion(r'Database Connections\CANP.sde\KDOT.MV_MAP_EXTRACT', STAGEDB, "Map_Extract")
TableToTable_conversion(r'Database Connections\CANP.sde\NM3.NM_ELEMENTS_ALL', STAGEDB, "ELEMENTS_ALL")
TableToTable_conversion(r'Database Connections\CANP.sde\NM3.NM_MEMBERS_ALL', STAGEDB, "MEMBERS_ALL") #Members takes a long time to copy


#To copy the SECT layer it must be joined to preserve RSE_HE_ID
MakeFeatureLayer_management(r"Database Connections\CANP.sde\NM3.NM3_NET_MAP_SECT_TABLE", "NM_SECT" )
MakeTableView_management(STAGEDB+r"\Elements_ALL", "ELEMENTS")
AddJoin_management("NM_SECT", "RSE_HE_ID", "ELEMENTS", "NE_ID", "KEEP_COMMON")
FeatureClassToFeatureClass_conversion("NM_SECT", STAGEDB, "SECT" )

#Remove the CANP Prod layers
for df in mapping.ListDataFrames(mxd):
    for lyr in mapping.ListLayers(mxd, "", df):
        mapping.RemoveLayer(df, lyr)
RefreshActiveView()

#Start the processing to rebuild layers

#Add the staging DB Layer for the current network
SRND_current = 'END_DATE is Null'
MakeFeatureLayer_management(STAGEDB+r"\SRND", "SRND", SRND_current)
#SRNDmem = "NM_END_DATE is null AND NM_OBJ_TYPE = 'SRND'"
#MakeTableView_management(STAGEDB+r"\Members_ALL", "SRND_MEM", SRNDmem)
SRNDelem = "NE_NT_TYPE = 'SRND' AND NE_END_DATE IS NULL AND NE_VERSION_NO in ('EB', 'NB')"
MakeTableView_management(STAGEDB+r"\ELEMENTS_ALL", "SRND_ELEM", SRNDelem)
AddJoin_management("SRND", "NE_ID", "SRND_ELEM", "NE_ID", "KEEP_COMMON")
FeatureClassToFeatureClass_conversion("SRND", STAGEDB, "SRND_PRIMARY" )

#Add map extract table
MapExtract = STAGEDB+r'\MAP_EXTRACT'
primdir = "DIRECTION < 4"
MakeTableView_management(MapExtract, "MapExtract",  primdir)

#calcualte the SRND KEY from the Map Extract Fields
AddField_management("MapExtract", "SRND_KEY", "TEXT", "", "", "24", "", "NULLABLE", "NON_REQUIRED")
CalculateField_management("MapExtract", "SRND_KEY", "!NQR_DESCRIPTION![3:]", "PYTHON", "#")

#Make route event layer from the extract table
MakeRouteEventLayer_lr("SRND","GIS_CANSYS.DBO.ELEMENTS_ALL.NE_UNIQUE","MapExtract","SRND_KEY LINE BEG_STATE_LOGMILE END_STATE_LOGMILE","MapExtractSRNDEvents","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
FeatureClassToFeatureClass_conversion("MapExtractSRNDEvents", STAGEDB, "GIS_STATE_SYSTEM", "LOC_ERROR = 'NO ERROR'" )
#Save the Primary Route Skeleton Layer

#Create the vertices for calibration points
FeatureVerticesToPoints_management(STAGEDB+"/GIS_STATE_SYSTEM", STAGEDB+"/Calibration_Points","ALL")
DeleteIdentical_management("GIS_CANSYS.DBO.Calibration_Points_SRND","GIS_CANSYS_DBO_SRND_START_D_3;GIS_CANSYS_DBO_SRND_END_DAT_4;GIS_CANSYS_DBO_ELEMENTS_ALL_12;Shape","#","0")  #Succeeded at Tue Dec 17 17:16:10 2013 (Elapsed Time: 21 minutes 55 seconds)

'''

LocateFeaturesAlongRoutes_lr(ws+"\\"+tempgdb+"/Calibration_Points",ws+"\\"+tempgdb+"/SRND","NE_UNIQUE","0.001 Feet",ws+"\\"+tempgdb+"/CP_SRND","STATE_MILE POINT SR_MEAS","ALL","DISTANCE","ZERO","FIELDS","M_DIRECTON")
MakeTableView_management(ws+"\\"+tempgdb+"/CP_SRND","Calibration_SR",'"STATE_MILE" = "SRND"', ws+"\\"+tempgdb,"#")
MakeRouteEventLayer_lr(routelyr,"NE_UNIQUE","Calibration_SR","STATE_MILE POINT SR_MEAS","SR_Calibration_Events","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
FeatureClassToFeatureClass_conversion("SR_Calibration_Events",ws+"\\"+tempgdb,"Calibration_Points_SRND","#","#")

CreateRoutes_lr(ws+"\\"+tempgdb+"/State_System","LRS_ROUTE",ws+"\\"+tempgdb+"/StateSystem_State_Route_SRND","TWO_FIELDS","BEG_STATE_LOGMILE","END_STATE_LOGMILE","UPPER_LEFT","1","0","IGNORE","INDEX")
CalibrateRoutes_lr(ws+"\\"+tempgdb+"/StateSystem_State_Route_"+route,"LRS_ROUTE",ws+"\\"+tempgdb+"/Calibration_Points_SRND","LRS_ROUTE","SR_MEAS",ws+"\\"+tempgdb+"/SMLRS","MEASURES","5 feet","BETWEEN","BEFORE","AFTER","IGNORE","KEEP","INDEX")
AddField_management(ws+"\\"+tempgdb+"/SMLRS", "NETWORKDATE", "DATE")
CalculateField_management(ws+"\\"+tempgdb+"/SMLRS","NETWORKDATE","datetime.datetime.now( )","PYTHON_9.3","#")

route = "CRND"
routelyr = ws+"\\"+tempgdb+"\\"+route
LocateFeaturesAlongRoutes_lr(ws+"\\"+tempgdb+"/Calibration_Points",ws+"\\"+tempgdb+"/CRND","NE_UNIQUE","0.001 Feet",ws+"\\"+tempgdb+"/CP_CRND","STATE_MILE POINT CR_MEAS","ALL","DISTANCE","ZERO","FIELDS","M_DIRECTON")
MakeTableView_management(ws+"\\"+tempgdb+"/CP_CRND","Calibration_CR",'"STATE_MILE" = "CRND"', ws+"\\"+tempgdb,"#")
MakeRouteEventLayer_lr(routelyr,"NE_UNIQUE","Calibration_CR","STATE_MILE POINT CR_MEAS","CR_Calibration_Events","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
FeatureClassToFeatureClass_conversion("CR_Calibration_Events",ws+"\\"+tempgdb,"Calibration_Points_CRND","#","#")
DeleteIdentical_management(ws+"\\"+tempgdb+"/Calibration_Points_CRND","STATE_MILE;CR_MEAS","0.002 Miles","0")
CreateRoutes_lr(ws+"\\"+tempgdb+"/State_System","LRS_KEY",ws+"\\"+tempgdb+"/StateSystem_County_Route_CRND","TWO_FIELDS","BEG_CNTY_LOGMILE","END_CNTY_LOGMILE","UPPER_LEFT","1","0","IGNORE","INDEX")
CalibrateRoutes_lr(ws+"\\"+tempgdb+"/StateSystem_County_Route_"+route,"LRS_KEY",ws+"\\"+tempgdb+"/Calibration_Points_CRND","LRS_KEY","CR_MEAS",ws+"\\"+tempgdb+"/CMLRS","MEASURES","5 feet","BETWEEN","BEFORE","AFTER","IGNORE","KEEP","INDEX")
AddField_management(ws+"\\"+tempgdb+"/CMLRS", "NETWORKDATE", "DATE")
CalculateField_management(ws+"\\"+tempgdb+"/CMLRS","NETWORKDATE","datetime.datetime.now( )","PYTHON_9.3","#")

mxdcopy = r"\\GISDATA\ArcGIS\GISDATA\MXD\NewGISLRS"+nowish+".mxd"
mapping.MapDocument.saveACopy(mxd, mxdcopy) 
del mxd, mxdcopy
print "Networks calibrated with no error"



#MakeFeatureLayer_management(r"Database Connections\CANP.sde\NM3.NM3_NET_MAP_SECT_TABLE", "SECT" )
#sselements = "NE_NT_TYPE = 'SECT' AND NE_OWNER in ( 'EB' , 'NB' )"
#MakeTableView_management(r"Database Connections\\CANP.sde\\NM3.NM_ELEMENTS", "Elements", sselements)        