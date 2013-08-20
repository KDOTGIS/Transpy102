'''
Created on Aug 20, 2013
Exports the GIS network from CANSYS
Needs "MAP EXTRACT" materialized view refreshed in the CANSYS Environment.  
This script supports the EXOR version using the ArcGIS 9.1 Spatial Manager.  Run the python script for 9.1 that exports the spatial manager to personal geodatabase.

@author: kyleg
'''

if __name__ == '__main__':
    pass


import arcpy
from ENV import ws, tempgdb, tempmdb, nowish

mxd = arcpy.mapping.MapDocument(r"\\GISDATA\ArcGIS\GISDATA\MXD\NewGISNetworkSeed91.mxd")
arcpy.env.workspace = ws
arcpy.env.XYResolution = '0.000000000899322 Degrees'
arcpy.env.XYTolerance = '0.000000001798644 Degrees'
arcpy.env.MResolution = 0.0001
arcpy.env.MTolerance = 0.0002  # set the M tolerance to the cansys tolerance, tolerance = resx2 
arcpy.env.overwriteOutput= True
incrnd = ws+"\\"+tempmdb+"\\CRND"
insrnd = ws+"\\"+tempmdb+"\\SRND"
qclean = "NETWORK_DIRECTION in ( 'EB' , 'NB' ) AND ROUTE NOT LIKE '999%' AND UNIQUE_NUMBER NOT LIKE '9'"
arcpy.MakeFeatureLayer_management(incrnd,"CRND", qclean)
arcpy.MakeFeatureLayer_management(insrnd,"SRND", qclean)
arcpy.FeatureClassToGeodatabase_conversion("CRND",ws+"\\"+tempgdb) #10 sec
arcpy.FeatureClassToGeodatabase_conversion("SRND",ws+"\\"+tempgdb)  #9 sec
arcpy.MakeTableView_management(r"Database Connections\atlasprod.odc\KDOT.MV_map_extract","MAP_EXTRACT", "DIRECTION <=2")
arcpy.TableToGeodatabase_conversion("MAP_EXTRACT", ws+"\\"+tempgdb)
del mxd
mxd = arcpy.mapping.MapDocument(r"\\GISDATA\ArcGIS\GISDATA\MXD\NewGISNetworkSeed.mxd")
arcpy.MakeFeatureLayer_management(ws+"\\"+tempgdb+"\\CRND","CRND")
arcpy.MakeFeatureLayer_management(ws+"\\"+tempgdb+"\\SRND","SRND")
arcpy.MakeTableView_management(ws+"\\"+tempgdb+"\\MAP_EXTRACT","MAP_EXTRACT", "DIRECTION <=2")
arcpy.AddField_management(ws+"\\"+tempgdb+"/MAP_EXTRACT", "SRND", "TEXT", "#", "#", "24" )
arcpy.CalculateField_management(ws+"\\"+tempgdb+"/MAP_EXTRACT", "SRND", """Mid([NQR_DESCRIPTION],4,16)""", "VB", "#")
arcpy.AddField_management(ws+"\\"+tempgdb+"/MAP_EXTRACT", "CRND", "TEXT", "#", "#", "24" )
arcpy.CalculateField_management(ws+"\\"+tempgdb+"/MAP_EXTRACT", "CRND", """[NQR_DESCRIPTION]""", "VB", "#")
arcpy.MakeRouteEventLayer_lr("CRND","NE_UNIQUE",ws+"\\"+tempgdb+"/MAP_EXTRACT","NQR_DESCRIPTION LINE BEG_CNTY_LOGMILE END_CNTY_LOGMILE", "STATE_SYSTEM", "#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
arcpy.FeatureClassToFeatureClass_conversion("STATE_SYSTEM",ws+"\\"+tempgdb, "STATE_SYSTEM", '"DIRECTION" <3')  #9 sec
arcpy.AddField_management(ws+"\\"+tempgdb+"\\STATE_SYSTEM", "NETWORKDATE", "DATE")
arcpy.CalculateField_management(ws+"\\"+tempgdb+"\\STATE_SYSTEM","NETWORKDATE","datetime.datetime.now( )","PYTHON_9.3","#")
arcpy.MakeFeatureLayer_management(ws+"\\"+tempgdb+"\\STATE_SYSTEM","STATE_SYSTEM")

import LRS_CRND_SRND
import LRS_PRECISION_SDO
import LRS_VIDEOLOG
import CANSYS_ItemExtract

#import MoveNet2Dev
mxdcopy = r"\\GISDATA\ArcGIS\GISDATA\MXD\NewGISNetwork"+nowish+".mxd"
arcpy.mapping.MapDocument.saveACopy(mxd, mxdcopy) 
del mxd, mxdcopy
print "all done"