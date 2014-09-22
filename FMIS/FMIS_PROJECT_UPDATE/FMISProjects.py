'''
Created on Aug 25, 2014

@author: kyleg
'''
#import arcpy
from arcpy import env, DeleteRows_management, da, SelectLayerByAttribute_management, GetCount_management, Intersect_analysis, Append_management, LocateFeaturesAlongRoutes_lr, Dissolve_management, MakeFeatureLayer_management, MakeRouteEventLayer_lr, MakeTableView_management, Exists, AddJoin_management, Union_analysis, Delete_management

FMIS_PROJ = r"Database Connections\CANT_CPMS.sde\CPMS.CPMS_STAGING_TMP"
FMIS_LOAD = r"Database Connections\CANT_CPMS.sde\CPMS.CPMS_HPMS_FMIS_DATA"
deltbl = r'Database Connections\CANT_CPMS.sde\CPMS.CPMS_FMIS_GIS_DEL_ROWS'
newtbl = r'Database Connections\CANT_CPMS.sde\CPMS.CPMS_FMIS_GIS_INS_ROWS'

ProjectID = "Project_ID"

ws = r"\\gisdata\arcgis\GISdata\FHWA\HPMS2012\kansas2012\Process.gdb"

env.overwriteOutput=True
env.outputMFlag = 'Disabled'
env.MTolerance = 0.001
env.MResolution = 0.0005

CountyLyr = r'Database Connections\SDEPROD_SHARED.sde\SHARED.Counties'
MPOLyr = r'Database Connections\SDEPROD_SHARED.sde\SHARED.MPO_Boundaries'
CONGDistlyr =r'Database Connections\GATEPROD.sde\GATE.GATE_US_CONG_2012' 
CPMSlyr =r"Database Connections\SQL61_GIS_CANSYS_RO.sde\GIS_CANSYS.DBO.CPMS"
HPMSlyr = r"\\gisdata\arcgis\GISdata\FHWA\HPMS2012\kansas2012\HPMS2012.gdb\HPMS2012\Kansas2012"

#HPMSlyr = r"\\gisdata\arcgis\GISdata\FHWA\HPMS2012\kansas2012\Kansas2012.shp" Have to copy shapefile to geodatabase to control M tolerance - also helps to project

#Do this Annually
def Annually():
    #arcpy.MakeFeatureLayer_management(CPMSlyr, 'CPMS', ProjectSelect)
    MakeFeatureLayer_management(CPMSlyr, 'CPMS')
    MakeFeatureLayer_management(CountyLyr, 'County')
    MakeFeatureLayer_management(HPMSlyr, 'HPMS')
    MakeFeatureLayer_management(MPOLyr, 'MPO')
    MakeFeatureLayer_management(CONGDistlyr, 'CONG')
    
    #make the polygon analysis layer for Districts, Counties, and MPOs 
    Union_analysis("CONG #;MPO #;County #",ws+"/Polygons","ALL","1 feet","GAPS")
    
def FIMS_GIS():
    #arcpy.MakeFeatureLayer_management(CPMSlyr, 'CPMS', ProjectSelect)
    
    MakeFeatureLayer_management(CPMSlyr, 'CPMS')
    MakeFeatureLayer_management(CountyLyr, 'County')
    MakeFeatureLayer_management(HPMSlyr, 'HPMS')
    MakeFeatureLayer_management(MPOLyr, 'MPO')
    MakeFeatureLayer_management(CONGDistlyr, 'CONG')
    MakeFeatureLayer_management(ws+"/Polygons", 'Polygons')
    MakeTableView_management(deltbl, 'DeleteView')
    MakeTableView_management(newtbl, 'InsertView')
    #make the polygon analysis layer for Districts, Counties, and MPOs 
    #arcpy.Union_analysis("CONG #;MPO #;County #",ws+"/Polygons","ALL","1 feet","GAPS")
    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
    # The following inputs are layers or table views: "CPMS", "CPMS.CPMS_STAGING_TMP"
    MakeTableView_management(FMIS_PROJ, "CPMS_STAGING_TMP" )
    AddJoin_management("CPMS","PROJECT_ID","InsertView","PROJECT_NUMBER","KEEP_COMMON")
    
    Output_Event_Table_Properties = 'RID LINE CNTY_BEG CNTY_END'
    
    outtblH = ws+"/FIMS_EventTableLines"
    
    if Exists(outtblH):
        Delete_management(outtblH)
        
    print "locating CPMS to HPMS route"
    LocateFeaturesAlongRoutes_lr('CPMS', 'HPMS', "Route_ID", "0 miles", outtblH, Output_Event_Table_Properties, "FIRST", "DISTANCE", "NO_ZERO", "FIELDS", "M_DIRECTON")
    #the 30 foot tolerance we allowed here also created a bunch of 30' segments at project intersections.  Those should be handled.  
    #...Or the locate tolerance changed to 0
    #cleansel = "RID <> CRND_RTE" #is thisnot the right way to handle this, because it will delete the short segments crossing the GIS county boundary?  not really
    #selection statement deleted non-state highway system might be better
    #MakeTableView_management(outtblH, "cleanup", cleansel)
    #DeleteRows_management("cleanup")
    
    MakeRouteEventLayer_lr("HPMS","Route_ID",ws+"/FIMS_EventTableLines","rid LINE CNTY_BEG CNTY_END","FIMS_EventTableLineLyr","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
    
    print "Intersection routes to areas"
    Intersect_analysis("FIMS_EventTableLineLyr #;HPMS #;Polygons #",ws+"/FMIS_Data","ALL","#","LINE")
    
    if Exists(ws +"/HPMS_DataD"):
        Delete_management(ws +"/HPMS_DataD")
    
    Dissolve_management(ws+"/FMIS_Data",ws +"/HPMS_DataD","PROJECT_ID;F_SYSTEM_V;NHS_VN;DISTRICT_1;COUNTY_NUMBER;ID_1","#","MULTI_PART","UNSPLIT_LINES")
    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
    print "locating processed data to HPMS mileage"
    
    if Exists(ws+"/FIMS_EventTable"):
        Delete_management(ws+"/FIMS_EventTable")    
    
    LocateFeaturesAlongRoutes_lr(ws+"/HPMS_DataD","HPMS","Route_ID","0 miles",ws+"/FIMS_EventTable","RID LINE CNTY_BEG CNTY_END","FIRST","DISTANCE","NO_ZERO","FIELDS","M_DIRECTON")
    #MaleTableView(ws+"/FIMS_EventTable", )
    
    Append_management(ws+"/FIMS_EventTable",FMIS_LOAD,"NO_TEST","""ROUTE_ID "ROUTE_ID" true true false 14 Text 0 0 ,First,#,FIMS_EventTable,RID,-1,-1;BEG_CNTY_MP "BEG_CNTY_MP" true true false 8 Double 10 38 ,First,#,FIMS_EventTable,CNTY_BEG,-1,-1;END_CNTY_MP "END_CNTY_MP" true true false 8 Double 10 38 ,First,#,FIMS_EventTable,CNTY_END,-1,-1;CONGRESSIONAL_DISTRICT "CONGRESSIONAL_DISTRICT" true true false 50 Text 0 0 ,First,#,FIMS_EventTable,DISTRICT_1,-1,-1;URBAN_ID "URBAN_ID" true true false 10 Text 0 0 ,First,#,FIMS_EventTable,ID_1,-1,-1;FUN_CLASS "FUN_CLASS" true true false 3 Text 0 0 ,First,#,FIMS_EventTable,F_SYSTEM_V,-1,-1;SYSTEM_CODE "SYSTEM_CODE" true true false 10 Text 0 0 ,First,#,FIMS_EventTable,NHS_VN,-1,-1;PROJECT_NUMBER "PROJECT_NUMBER" true true false 15 Text 0 0 ,First,#,FIMS_EventTable,PROJECT_ID,-1,-1;COUNTY "COUNTY" true true false 3 Text 0 0 ,First,#,FIMS_EventTable,COUNTY_NUMBER,-1,-1""","#")
    
    print "Rows appended to CPMS Load Table CPMS_HPMS_FMIS_DATA"
    #Need some error handling - need to (just look for errors or place errors in testing)
    #Maybe locate routes to add begin/end or other LRS errors
    #Need to join and delete rows prior to appending, if the project exists in the output table, need to delete those rows before appending them back in
    #Consider adding a processdate, it might be helpful in the future.  (oracle side or GP?)

def ProjDelete():#delete rows from the FMIS load table that are about to be processed
    delcount = GetCount_management(r'Database Connections\CANT_CPMS.sde\CPMS.CPMS_FMIS_GIS_DEL_ROWS')
    print str(delcount)+" records to delete"
    deletelist=list()
    if delcount == 0:
        print "no records to delete, ending"
        pass
    else:
        MakeTableView_management(FMIS_LOAD, "FMIS_TABLE")
        MakeTableView_management(deltbl, "deletes")
        with da.SearchCursor(deltbl, "PROJECT_NUMBER") as delcur:  # @UndefinedVariable
            for row in delcur:
                DelXID=  ("{0}".format(row[0]))
                #print DelXID + " is being deleted from the FMIS table"
                #AddJoin_management(layer_name,"CROSSINGID", deltbl, "CROSSINGID", "KEEP_ALL")
                #delsel = "PROJECT_NUMBER LIKE '"+DelXID+"'"
                #print delsel
                deletelist.append(DelXID)
                #SelectLayerByAttribute_management("FMIS_TABLE","ADD_TO_SELECTION", delsel)
        #print str(deletelist)
        delsel = "PROJECT_NUMBER IN "+str(deletelist)
        #for ProjectNumber in deletelist:
        print delsel 
        
        SelectLayerByAttribute_management("FMIS_TABLE", "NEW_SELECTION", delsel)
        #DeleteRows_management("FMIS_TABLE")
    print "Delete function completed"
    
def newcheck():
    newcnt = GetCount_management(r'Database Connections\CANT_CPMS.sde\CPMS.CPMS_FMIS_GIS_INS_ROWS')
    print str(newcnt)+" records to process"
    if newcnt == 0:
        print "no records to load, pass"
        pass
    else: 
        print "Starting the processing now"
        FIMS_GIS()
        
#ProjDelete()
newcheck()


