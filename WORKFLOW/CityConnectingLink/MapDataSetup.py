'''
Created on Oct 7, 2013

@author: kyleg
'''

if __name__ == '__main__':
    pass

from config import ws, connection0, connection1, citylimits, stateroutelyr, cntyroutelyr, laneclass, nonstate, interchange
from arcpy import mapping, env, Exists, AddJoin_management, RemoveJoin_management, Delete_management, CalibrateRoutes_lr, DeleteIdentical_management, FeatureClassToFeatureClass_conversion, FeatureVerticesToPoints_management, MakeFeatureLayer_management, Intersect_analysis, CreateRoutes_lr, MakeTableView_management, Dissolve_management, AddField_management, CalculateField_management, LocateFeaturesAlongRoutes_lr, MakeRouteEventLayer_lr, OverlayRouteEvents_lr
env.workspace = ws
env.overwriteOutput = True
#mxd = mapping.MapDocument(r"\\gisdata\arcgis\gisdata\MXD\2013100901_CCLProcess.mxd")
MakeTableView_management(connection1+"Maint_Segment", "Maint_tview")
MakeTableView_management(connection1+"CCL_Resolution", "CCL_Resolution_tbl")
CalculateField_management("CCL_Resolution_tbl", "CCL_LRS",  'str(!CITYNUMBER!)+str(!LRS_KEY![3:14])', "PYTHON" )
MakeTableView_management(connection1+"CCL_Resolution", "CCL_Resolution_tbl10", 'CITYNUMBER<100')
CalculateField_management("CCL_Resolution_tbl10", "CCL_LRS", '"0"+str(!CITYNUMBER!)+str(!LRS_KEY![3:14])', "PYTHON")
MakeFeatureLayer_management(citylimits, "CityLimits", "TYPE IN ( 'CS', 'ON')")
MakeFeatureLayer_management(cntyroutelyr, "clrs")
MakeFeatureLayer_management(stateroutelyr, "smlrs")
LocateFeaturesAlongRoutes_lr(citylimits,"clrs","LRS_KEY","60 Feet",connection1+"GIS_CITY","LRS_KEY LINE Beg_CMP End_CMP","FIRST","DISTANCE","NO_ZERO","FIELDS","M_DIRECTON")
MakeRouteEventLayer_lr("clrs","LRS_KEY","Maint_tview","LRSKEY LINE BEGMILEPOST END_MP","Maint_Events_ln","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
MakeRouteEventLayer_lr("clrs","LRS_KEY","CCL_Resolution_tbl","LRS_KEY LINE BEG_CNTY_LOGMILE END_CNTY_LOGMILE","City_Connecting_Links","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
MakeRouteEventLayer_lr("clrs","LRS_KEY","GIS_CITY","LRS_KEY LINE BEG_CMP END_CMP","GIS_BASED_CCL","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
OverlayRouteEvents_lr(connection1+"CCL_Resolution","LRS_KEY LINE BEG_CNTY_LOGMILE END_CNTY_LOGMILE",laneclass,"LRS_KEY LINE Beg_Cnty_Logmile End_Cnty_Logmile","INTERSECT",connection1+"CCL_LANE_CLASS_OVERLAY","LRS_KEY LINE BEG_CNTY_LOGMILE END_CNTY_LOGMILE","NO_ZERO","FIELDS","INDEX")

print "create Route Layer specific to City Connecting Link locations"
FeatureClassToFeatureClass_conversion("City_Connecting_Links", connection0, "CITY_CONNECTING_LINK_CENTERLINE")
LocateFeaturesAlongRoutes_lr(connection1+"CITY_CONNECTING_LINK_CENTERLINE",stateroutelyr,"LRS_ROUTE","0 Meters",connection1+"CCL_STATE_LRS_tbl","LRS_ROUTE LINE BEG_STATE_LOGMILE END_STATE_LOGMILE","FIRST","DISTANCE","ZERO","FIELDS","M_DIRECTON")
MakeRouteEventLayer_lr("smlrs", "LRS_ROUTE",connection1+"CCL_STATE_LRS_tbl","LRS_ROUTE LINE BEG_STATE_LOGMILE END_STATE_LOGMILE","CCL_STATE_LRS","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
FeatureClassToFeatureClass_conversion("CCL_STATE_LRS", connection0, "CITY_CONNECTING_LINK_STATEREF")
if Exists(connection1+"CITY_CONNECTING_LINK_STATE"):
    Delete_management(connection1+"CITY_CONNECTING_LINK_STATE")
Dissolve_management(connection1+"CITY_CONNECTING_LINK_STATEREF",connection1+"CITY_CONNECTING_LINK_STATE","LRS_ROUTE;CITY;CITYNUMBER;DESCRIPTION","BEG_STATE_LOGMILE MIN;END_STATE_LOGMILE MAX","MULTI_PART","DISSOLVE_LINES")

print "processes to Create the layer that will be used to create a new LRS for city connecting links"
def CCL_RestartLRS():
    CCLEnd = "!MAX_END_STATE_LOGMILE!- !MIN_BEG_STATE_LOGMILE!"
    CCLLRS = 'str(!CITYNUMBER!)+str(!LRS_ROUTE!)'
    CCLLRS10 = '"0"+str(!CITYNUMBER!)+str(!LRS_ROUTE!)'
    MakeFeatureLayer_management(connection1+"CITY_CONNECTING_LINK_STATE", "CITY_CONNECTING_LINK_RESET")
    resln = "CITY_CONNECTING_LINK_RESET"
    AddField_management(resln,"CCL_BEGIN", "DOUBLE", 12, 3)
    AddField_management(resln,"CCL_END", "DOUBLE", 12, 3)
    AddField_management(resln,"CCL_LRS", "TEXT", "#", "#", "120")
    CalculateField_management(resln, "CCL_BEGIN", "0", "PYTHON")
    CalculateField_management(resln, "CCL_END", CCLEnd, "PYTHON")
    CalculateField_management(resln, "CCL_LRS", CCLLRS, "PYTHON")
    MakeFeatureLayer_management(connection1+"CITY_CONNECTING_LINK_STATE", "CITY_CONNECTING_LINK_RESET10", 'CITYNUMBER<100')
    CalculateField_management("CITY_CONNECTING_LINK_RESET10", "CCL_LRS", CCLLRS10, "PYTHON")
CCL_RestartLRS()

def LRS_PointCalibrator(LineFeatureClass, ReferenceRoute, ReferenceRouteKey,NewRouteKey, NewRoute, NewBeg, NewEnd):
    FeatureVerticesToPoints_management(LineFeatureClass, connection1+"CALIBRATION_POINTS", "ALL")
    LocateFeaturesAlongRoutes_lr(connection1+"CALIBRATION_POINTS", ReferenceRoute,ReferenceRouteKey,"0.001 Feet",connection1+"CP_MEAS","RefKey POINT MEASURE","ALL","DISTANCE","ZERO","FIELDS","M_DIRECTON")
    querystr = str("RefKey = "+ReferenceRouteKey)
    print querystr
    MakeTableView_management(connection1+"CP_MEAS","CalibrationEvents", querystr, "#")
    delfields = NewRouteKey+";MEASURE"
    DeleteIdentical_management("CalibrationEvents", delfields)
    inprops = str(ReferenceRouteKey +" POINT MEASURE")
    MakeRouteEventLayer_lr(ReferenceRoute, ReferenceRouteKey, "CalibrationEvents",inprops,"Calibration_Event_lyr","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
    FeatureClassToFeatureClass_conversion("Calibration_Event_lyr",connection0,"Calibration_Points"+NewRoute,"#","#")
    CreateRoutes_lr(LineFeatureClass,NewRouteKey,connection1+NewRoute+"base","TWO_FIELDS",NewBeg, NewEnd,"UPPER_LEFT","1","0","IGNORE","INDEX")
    calxpr = '[MEASURE]- [MIN_BEG_STATE_LOGMILE]'
    CalculateField_management(connection1+"Calibration_Points"+NewRoute, "MEASURE", calxpr, "VB", "#")
    CalibrateRoutes_lr(connection1+NewRoute+"base", NewRouteKey,connection1+"Calibration_Points"+NewRoute,NewRouteKey,"MEASURE",connection1+NewRoute,"MEASURES","5 feet","BETWEEN","BEFORE","AFTER","IGNORE","KEEP","INDEX")
    AddField_management(connection1+NewRoute, "NETWORKDATE", "DATE")
    CalculateField_management(connection1+NewRoute,"NETWORKDATE","datetime.datetime.now( )","PYTHON_9.3","#")

LineFeatureClass = connection1+"CITY_CONNECTING_LINK_STATE"
ReferenceRoute = stateroutelyr
ReferenceRouteKey = "LRS_ROUTE"
NewRouteKey = "CCL_LRS"
NewBeg = "CCL_BEGIN"
NewEnd = "CCL_END"
NewRoute = "CCL_LRS_ROUTE"
LRS_PointCalibrator(LineFeatureClass, ReferenceRoute, ReferenceRouteKey,NewRouteKey, NewRoute, NewBeg, NewEnd)

#def NONSTATE_INT(nonstate, NewRoute, NewRouteKey, connection1):
print "intersect non-state routes"
MakeFeatureLayer_management(nonstate, 'NON_STATE_SYSTEM', "CITYNUMBER IS NOT NULL AND CITYNUMBER<999")
MakeFeatureLayer_management(connection1+NewRoute, "CCL_LRS_ROUTE")
Intersect_analysis("CCL_LRS_ROUTE #;'NON_STATE_SYSTEM' #",connection1+"Intersect_NONSTATE","ALL","5 Feet","POINT") #this doesnt reference the newroute variable, its easier that way
LocateFeaturesAlongRoutes_lr(connection1+"Intersect_NONSTATE","CCL_LRS_ROUTE",NewRouteKey,"5 Feet",connection1+"INTR_CCL_NS","CCL_LRS POINT MEASURE","ALL","DISTANCE","ZERO","FIELDS","M_DIRECTON")
MakeRouteEventLayer_lr("CCL_LRS_ROUTE",NewRouteKey,connection1+"INTR_CCL_NS","CCL_LRS POINT MEASURE","INTR_CCL_NS Events","#","ERROR_FIELD","ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")

#def STATE_INT(interchange, NewRouteKey, NewRoute,connection1)
print "add intersect intersection points that are state - state intersections"
MakeFeatureLayer_management(interchange, 'INTR', "ON_STATE_NONSTATE = 'S'")
LocateFeaturesAlongRoutes_lr("INTR","CCL_LRS_ROUTE",NewRouteKey,"5 Feet",connection1+"INTR_CCL","CCL_LRS POINT MEASURE","ALL","DISTANCE","ZERO","FIELDS","M_DIRECTON")
MakeRouteEventLayer_lr("CCL_LRS_ROUTE",NewRouteKey,connection1+"INTR_CCL","CCL_LRS POINT MEASURE","INTR_CCL_Events","#","ERROR_FIELD","ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")

print "show lane classification referenced to city connecting link LRS"
#def LaneClass(laneclass,connection1,NewRouteKey)
MakeFeatureLayer_management(laneclass, 'LNCL')
LocateFeaturesAlongRoutes_lr("LNCL","CCL_LRS_ROUTE",NewRouteKey,"#",connection1+"LANECLASS_CCL","CCL_LRS LINE CCL_BEGIN CCL_END","ALL","DISTANCE","ZERO","FIELDS","M_DIRECTON")
OverlayRouteEvents_lr(connection1+"CITY_CONNECTING_LINK_STATE","CCL_LRS LINE CCL_BEGIN CCL_END",connection1+"LANECLASS_CCL","CCL_LRS LINE CCL_BEGIN CCL_END","INTERSECT",connection1+"CCL_Report","CCL_LRS LINE CCL_BEGIN CCL_END","NO_ZERO","FIELDS","INDEX")
MakeRouteEventLayer_lr("CCL_LRS_ROUTE", "CCL_LRS",connection1+"CCL_Report","CCL_LRS LINE CCL_BEGIN CCL_END","City Connecting Links Mapping","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")

AddField_management("City Connecting Links Mapping", "CenterlineMiles", "DOUBLE")
CalculateField_management("City Connecting Links Mapping","CenterlineMiles", '[CCL_END]-[CCL_BEGIN]', "VB" )
AddField_management("City Connecting Links Mapping", "Lanes", "LONG")
AddJoin_management("City Connecting Links Mapping", "LNCL_CLS_ID", connection1+"LC_LN_CLS_ID", "IAL_VALUE")
CalculateField_management("City Connecting Links Mapping","CCL.DBO.CCL_Report_Features.Lanes", 'Left([CCL.DBO.LC_LN_CLS_ID.IAL_MEANING],1)', "VB" )
RemoveJoin_management("City Connecting Links Mapping", "CCL.DBO."+"LC_LN_CLS_ID")
AddField_management("City Connecting Links Mapping", "LaneMiles", "DOUBLE")
CalculateField_management("City Connecting Links Mapping","LaneMiles", '([CCL_END]-[CCL_BEGIN])*[Lanes]', "VB" )
