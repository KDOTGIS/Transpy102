'''
Created on Oct 10, 2013

@author: kyleg
'''

from arcpy import CalibrateRoutes_lr, DeleteIdentical_management, FeatureClassToFeatureClass_conversion, FeatureVerticesToPoints_management, CreateRoutes_lr, MakeTableView_management, AddField_management, CalculateField_management, LocateFeaturesAlongRoutes_lr, MakeRouteEventLayer_lr 
from config import connection0, connection1, stateroutelyr
'''    
LineFeatureClass = connection1+"CITY_CONNECTING_LINK_STATE"
ReferenceRoute = stateroutelyr
ReferenceRouteKey = "LRS_ROUTE"
NewRouteKey = "CCL_LRS"
NewBeg = "CCL_BEGIN"
NewEnd = "CCL_END"
NewRoute = "CCL_LRS_ROUTE"
'''

def LRS_PointCalibrator(LineFeatureClass, ReferenceRoute, ReferenceRouteKey,NewRouteKey, NewRoute, NewBeg, NewEnd):
    FeatureVerticesToPoints_management(LineFeatureClass, connection1+"CALIBRATION_POINTS", "ALL")
    LocateFeaturesAlongRoutes_lr(connection1+"CALIBRATION_POINTS", ReferenceRoute,ReferenceRouteKey,"0.001 Feet",connection1+"CP_MEAS","RefKey POINT MEASURE","ALL","DISTANCE","ZERO","FIELDS","M_DIRECTON")
    querystr = str("RefKey = "+ReferenceRouteKey)
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