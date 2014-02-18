'''
Created on Aug 20, 2013

Created on Jun 25, 2013
Script to calibrate the CURRENT state system network to the CANSYS logmile system, and create GIS routes for DYNSEG in ArcGIS
Creates "Control Points" for EXOR route groups and calibrates GIS routes to these route groups using EXOR SECT Geometry and the MAP_EXTRACT MV
@author: kyleg

modified December 2013 to take advantage of CANP direct connection
'''
#import arcpy functions
from arcpy import mapping, env, MakeFeatureLayer_management, FeatureVerticesToPoints_management, LocateFeaturesAlongRoutes_lr, MakeTableView_management, MakeRouteEventLayer_lr, FeatureClassToFeatureClass_conversion, AddXY_management
from arcpy import Delete_management, Exists, RefreshActiveView, AddIndex_management, DeleteIdentical_management, CreateRoutes_lr, CalibrateRoutes_lr, AddField_management, CalculateField_management, AddJoin_management, FeatureClassToGeodatabase_conversion, TableToTable_conversion
#from CONFIG import ws, EXOR_PROD, STAGEDB, nowish, MTolerance, MResolution    

#Set the workspace database connections
EXOR_PROD =  "Database Connections\CANP.odc\:"
SDEDEV = r"Database Connections\SDEDEV_GIS_DEV.sde\GIS_DEV.KDOT_ROADWAY"
SDEDEV_SHARED = r"Database Connections\SDEDEV_SHARED.sde"
GISTEST = r"Database Connections\GISTEST.sde"
STAGEDB = r"Database Connections\SQL61_GIS_CANSYS.sde"
MResolution = 0.0005 
MTolerance = 0.001 

#Control the MXD for processing
mxd = mapping.MapDocument("CURRENT") 
env.MTolerance = MTolerance
env.MResolution = MResolution
env.overwriteOutput = "True"

#Copy Network Layers from CANSYS to Staging Area.  SRND and CRND layers have full history 
FeatureClassToFeatureClass_conversion(r"Database Connections\CANP.sde\NM3.NM_NLT_SRND_SRND_SDO", STAGEDB, "SRND" )
FeatureClassToFeatureClass_conversion(r"Database Connections\CANP.sde\NM3.NM_NLT_CRND_CRND_SDO", STAGEDB, "CRND" )
TableToTable_conversion(r'Database Connections\CANP.sde\KDOT.MV_MAP_EXTRACT', STAGEDB, "Map_Extract")
TableToTable_conversion(r'Database Connections\CANP.sde\NM3.NM_ELEMENTS', STAGEDB, "ELEMENTS")
TableToTable_conversion(r'Database Connections\CANP.sde\NM3.NM_MEMBERS', STAGEDB, "MEMBERS") #Members takes a long time to copy
TableToTable_conversion(r'Database Connections\CANP_Report_User.sde\NM3.NM_INV_ITEMS', STAGEDB, "ITEMS_ALL")

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
AddIndex_management("SRND","NE_ID","NE_ID_INDEX","NON_UNIQUE","ASCENDING")
#SRNDmem = "NM_END_DATE is null AND NM_OBJ_TYPE = 'SRND'"
#MakeTableView_management(STAGEDB+r"\Members_ALL", "SRND_MEM", SRNDmem)
SRNDelem = "NE_NT_TYPE = 'SRND' AND NE_END_DATE IS NULL AND NE_VERSION_NO in ('EB', 'NB')"
MakeTableView_management(STAGEDB+r"\ELEMENTS", "SRND_ELEM", SRNDelem)
AddJoin_management("SRND", "NE_ID", "SRND_ELEM", "NE_ID", "KEEP_COMMON")
FeatureClassToFeatureClass_conversion("SRND",STAGEDB,"SRND_PRIMARY1","#") #error exists with field mapping date types, to export then do field mapping
FeatureClassToFeatureClass_conversion("GIS_CANSYS.DBO.SRND_PRIMARY1",STAGEDB, "SRND_PRIMARY","#","""NE_ID "NE_ID" true false false 4 Long 0 10 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,NE_ID,-1,-1;START_DATE "START_DATE" true false false 36 Date 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,START_DATE,-1,-1;END_DATE "END_DATE" true true false 36 Date 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,END_DATE,-1,-1;DATE_CREATED "DATE_CREATED" true true false 36 Date 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,DATE_CREATED,-1,-1;DATE_MODIFIED "DATE_MODIFIED" true true false 36 Date 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,DATE_MODIFIED,-1,-1;MODIFIED_BY "MODIFIED_BY" true true false 30 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,MODIFIED_BY,-1,-1;CREATED_BY "CREATED_BY" true true false 30 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,CREATED_BY,-1,-1;GEOLOC_LEN "GEOLOC_LEN" true false false 8 Double 8 38 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,GEOLOC_LEN,-1,-1;NE_UNIQUE "NE_UNIQUE" true false false 30 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,GIS_CANSYS_DBO_ELEMENTS_NE_UNIQ,-1,-1;NE_TYPE "NE_TYPE" true false false 4 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,GIS_CANSYS_DBO_ELEMENTS_NE_TYPE,-1,-1;NE_NT_TYPE "NE_NT_TYPE" true false false 4 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,GIS_CANSYS_DBO_ELEMENTS_NE_NT_T,-1,-1;NE_OWNER "NE_OWNER" true true false 4 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,GIS_CANSYS_DBO_ELEMENTS_NE_OWNE,-1,-1;NE_NAME "NE_NAME_1" true true false 80 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,GIS_CANSYS_DBO_ELEMENTS_NE_NAME,-1,-1;NE_NAME1 "NE_NAME_2" true true false 80 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,GIS_CANSYS_DBO_ELEMENTS_NE_NA_1,-1,-1;NE_PREFIX "NE_PREFIX" true true false 4 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,GIS_CANSYS_DBO_ELEMENTS_NE_PREF,-1,-1;NE_NUMBER "NE_NUMBER" true true false 8 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,GIS_CANSYS_DBO_ELEMENTS_NE_NUMB,-1,-1;NE_SUB_TYPE "NE_SUB_TYPE" true true false 2 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,GIS_CANSYS_DBO_ELEMENTS_NE_SUB_,-1,-1;NE_GROUP "NE_GROUP" true true false 30 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,GIS_CANSYS_DBO_ELEMENTS_NE_GROU,-1,-1;NE_SUB_CLASS "NE_SUB_CLASS" true true false 4 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,GIS_CANSYS_DBO_ELEMENTS_NE_SUB1,-1,-1;NE_VERSION "NE_VERSION_NO" true true false 4 Text 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,GIS_CANSYS_DBO_ELEMENTS_NE_VERS,-1,-1;Shape_STLength__ "Shape_STLength__" false false true 0 Double 0 0 ,First,#,Database Connections/SQL61_GIS_CANSYS.sde/GIS_CANSYS.DBO.SRND_PRIMARY1,Shape.STLength(),-1,-1""","#")

#Add map extract table
MapExtract = STAGEDB+r'\MAP_EXTRACT'
primdir = "DIRECTION < 4"
MakeTableView_management(MapExtract, "MapExtract",  primdir)

#calcualte the SRND KEY from the Map Extract Fields
AddField_management("MapExtract", "SRND_KEY", "TEXT", "", "", "24", "", "NULLABLE", "NON_REQUIRED")
CalculateField_management("MapExtract", "SRND_KEY", "!NQR_DESCRIPTION![3:]", "PYTHON", "#")

#Make route event layer from the extract table
MakeFeatureLayer_management(STAGEDB+r"\SRND_PRIMARY", "SRND_PRIMARY")
MakeRouteEventLayer_lr("SRND_PRIMARY","NE_UNIQUE","MapExtract","SRND_KEY LINE BEG_STATE_LOGMILE END_STATE_LOGMILE","MapExtractSRNDEvents","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
FeatureClassToFeatureClass_conversion("MapExtractSRNDEvents", STAGEDB, "GIS_STATE_SYSTEM", "LOC_ERROR = 'NO ERROR'" )

#Copy State System to SDEDEV... problem with Geomedia ability to connect
FeatureClassToFeatureClass_conversion("MapExtractSRNDEvents", SDEDEV_SHARED, "STATE_SYSTEM", "LOC_ERROR = 'NO ERROR'" )

#copy state systen to GISTEST
FeatureClassToFeatureClass_conversion("MapExtractSRNDEvents","Database Connections/GISTEST.sde","STATE_SYSTEM","#","#","SDO_GEOMETRY")

#Save the Primary Route Skeleton Layer

#Create the vertices for calibration points
FeatureVerticesToPoints_management(STAGEDB+"/GIS_STATE_SYSTEM", STAGEDB+"/Calibration_Points","ALL")
DeleteIdentical_management("GIS_CANSYS.DBO.Calibration_Points","LRS_KEY;POINT_X;POINT_Y;POINT_M","#","0")
CreateRoutes_lr(STAGEDB+"/GIS_STATE_SYSTEM", "LRS_ROUTE", STAGEDB+"/GIS_STATE_ROUTES","TWO_FIELDS","BEG_STATE_LOGMILE","END_STATE_LOGMILE","UPPER_LEFT","1","0","IGNORE","INDEX")
CalibrateRoutes_lr(STAGEDB+"/GIS_STATE_ROUTES","LRS_ROUTE",STAGEDB+"/Calibration_Points","LRS_ROUTE","POINT_M", STAGEDB+"/SMLRS","MEASURES","5 feet","BETWEEN","BEFORE","AFTER","IGNORE","KEEP","INDEX")

#Rider Routes
CreateRoutes_lr(STAGEDB+"/GIS_STATE_SYSTEM", "SRND_KEY", STAGEDB+"/SRND_PRIMARY_ROUTE","TWO_FIELDS","BEG_STATE_LOGMILE","END_STATE_LOGMILE","UPPER_LEFT","1","0","IGNORE","INDEX")
LocateFeaturesAlongRoutes("SRND_PRIMARY", "GIS_CANSYS.DBO.SRND_PRIMARY_ROUTE", "SRND_KEY", "0 DecimalDegrees", r"Database Connections\SQL61_GIS_CANSYS.sde\GIS_CANSYS.DBO.SRND_RIDER_ROUTES", "SRND LINE FMEAS TMEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")