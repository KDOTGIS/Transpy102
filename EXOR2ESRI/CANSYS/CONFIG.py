'''
Created on Aug 20, 2013

@author: kyleg
'''

import datetime 
from arcpy import env
now = datetime.datetime.now()

class CONFIG(object): 
    '''
    classdocs
    '''    
now = datetime.datetime.now()

nowish = str(now.year)+"_"+str(now.month)+"_"+str(now.day)
    
ws = r'\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST'
'''
tempgdb = "CANSYSNet"+str(now.year)+"_"+str(now.month)+"_"+str(now.day)+".gdb"
tempmdb = "CANSYSNet"+str(now.year)+"_"+str(now.month)+"_"+str(now.day)+".mdb"
'''

tempmdb = "CANSYSNet2013_10_7.mdb"
tempgdb = "CANSYSNet2013_10_7.gdb"


EXOR_PROD =  "Database Connections\ATLASPROD.odc\:"

   
MResolution = 0.0005 
MTolerance = 0.001 
    
XYResolution = '0.000000000899322 Degrees'
XYTolerance = '0.000000001798644 Degrees'
    

           