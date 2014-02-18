'''
Created on Aug 20, 2013

@author: kyleg
'''
import datetime 
now = datetime.datetime.now()
nowish = str(now.year)+"_"+str(now.month)+"_"+str(now.day)
#ws = r'\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST'
'''
#tempmdb = "CANSYSNet2013_10_7.mdb"
#tempgdb = "CANSYSNet2013_10_7.gdb"
'''
EXOR_PROD =  "Database Connections\CANP.odc\:"
STAGEDB = "SQL61_GIS_CANSYS.sde:"
MResolution = 0.0005 
MTolerance = 0.001 
XYResolution = '0.000000000899322 Degrees'
XYTolerance = '0.000000001798644 Degrees'