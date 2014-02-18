'''
Created on Aug 20, 2013
create a begin - end attribute network using segments for Precision Linear referencing by GeoMedia users 

@author: kyleg
'''

from arcpy import env, SplitLine_management, LocateFeaturesAlongRoutes_lr, CalculateField_management, TransformRouteEvents_lr, MakeRouteEventLayer_lr, FeatureClassToFeatureClass_conversion
from CONFIG import ws, tempgdb, XYResolution, XYTolerance, MResolution, MTolerance
operws = ws+"\\"+tempgdb+"\\"

env.XYResolution = XYResolution
env.XYTolerance = XYTolerance
env.MResolution = MResolution
env.MTolerance = MTolerance

print "tolerances  set, now proceeding to split the lines"

SplitLine_management(operws+"STATE_SYSTEM", operws+"STATE_SYSTEM_PREC") # 15 sec

output = ws+"\\"+tempgdb+'\LRM_CR_PART'
LocateFeaturesAlongRoutes_lr(operws+"STATE_SYSTEM_PREC",operws+"CMLRS","LRS_KEY","0 miles",output,"LRS_KEY LINE BEG_CNTY_LOGMILE2 END_CNTY_LOGMILE2","FIRST","DISTANCE","ZERO","FIELDS","M_DIRECTON")
print 'tried' + output + ' successfully' #4 minutes; 06/17/01 removed the 1 ft tolerance
CalculateField_management(operws+"LRM_CR_PART","BEG_CNTY_LOGMILE","[BEG_CNTY_LOGMILE2]","VB","#")
CalculateField_management(operws+"LRM_CR_PART","END_CNTY_LOGMILE","[END_CNTY_LOGMILE2]","VB","#")
TransformRouteEvents_lr(operws+"LRM_CR_PART","LRS_KEY LINE BEG_CNTY_LOGMILE2 END_CNTY_LOGMILE2",operws+"CMLRS","LRS_KEY",operws+"SMLRS","LRS_ROUTE",operws+"LRM_SR_PART","LRS_ROUTE LINE BEG_STATE_LOGMILE2 END_STATE_LOGMILE2","0 DecimalDegrees","FIELDS")
CalculateField_management(operws+"LRM_SR_PART","BEG_STATE_LOGMILE","[BEG_STATE_LOGMILE2]","VB","#")
CalculateField_management(operws+"LRM_SR_PART","END_STATE_LOGMILE","[END_STATE_LOGMILE2]","VB","#")
MakeRouteEventLayer_lr(operws+"SMLRS","LRS_ROUTE",operws+"LRM_SR_PART","LRS_ROUTE LINE BEG_STATE_LOGMILE END_STATE_LOGMILE","STATE_SYSTEM_PRECISION_SDO","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
FeatureClassToFeatureClass_conversion("STATE_SYSTEM_PRECISION_SDO", ws+"\\"+tempgdb,"STATE_SYSTEM_PRECISION") #23 sec
print "completed Precision Network for SDO"
        