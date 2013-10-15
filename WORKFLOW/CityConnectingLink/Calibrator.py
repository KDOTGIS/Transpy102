'''
Created on Oct 10, 2013

@author: kyleg
'''

class Calibrator(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        LineFeatureClass = "SRND"
        BeginFieldName = "BeginStateMP"
        EndFieldName = "EndStateMP"
        OutFeatureClass = "StateLRS"
 
        
        def LRS_PointCalibrator(LineFeatureClass,BeginFieldName, EndFieldName, RouteKeyField, OutFeatureClass):
            from arcpy import CalculateField_management, LocateFeaturesAlongRoutes_lr, MakeTableView_management, MakeRouteEventLayer_lr, FeatureClassToFeatureClass_conversion, DeleteIdentical_management,CreateRoutes_lr,AddField_management
            LocateFeaturesAlongRoutes_lr(LineFeatureClass,ws+"\\"+tempgdb+"/SRND","NE_UNIQUE","0.001 Feet",ws+"\\"+tempgdb+"/CP_SRND","STATE_MILE POINT SR_MEAS","ALL","DISTANCE","ZERO","FIELDS","M_DIRECTON")
            MakeTableView_management(ws+"\\"+tempgdb+"/CP_SRND","Calibration_SR",'"STATE_MILE" = "SRND"', ws+"\\"+tempgdb,"#")
            MakeRouteEventLayer_lr(routelyr,"NE_UNIQUE","Calibration_SR","STATE_MILE POINT SR_MEAS","SR_Calibration_Events","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
            FeatureClassToFeatureClass_conversion("SR_Calibration_Events",ws+"\\"+tempgdb,"Calibration_Points_SRND","#","#")
            DeleteIdentical_management(ws+"\\"+tempgdb+"/Calibration_Points_SRND","STATE_MILE;SR_MEAS","0.002 Miles","0")
            CreateRoutes_lr(ws+"\\"+tempgdb+"/State_System","LRS_ROUTE",ws+"\\"+tempgdb+"/StateSystem_State_Route_SRND","TWO_FIELDS","BEG_STATE_LOGMILE","END_STATE_LOGMILE","UPPER_LEFT","1","0","IGNORE","INDEX")
            CalibrateRoutes_lr(ws+"\\"+tempgdb+"/StateSystem_State_Route_"+route,"LRS_ROUTE",ws+"\\"+tempgdb+"/Calibration_Points_SRND","LRS_ROUTE","SR_MEAS",ws+"\\"+tempgdb+"/SMLRS","MEASURES","5 feet","BETWEEN","BEFORE","AFTER","IGNORE","KEEP","INDEX")
            AddField_management(ws+"\\"+tempgdb+"/SMLRS", "NETWORKDATE", "DATE")
            CalculateField_management(ws+"\\"+tempgdb+"/SMLRS","NETWORKDATE","datetime.datetime.now( )","PYTHON_9.3","#")