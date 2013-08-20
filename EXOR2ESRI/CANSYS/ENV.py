'''
Created on Aug 20, 2013

@author: kyleg
'''

import datetime, arcpy
now = datetime.datetime.now()


class ENV(object):
    
    
    '''
    classdocs
    '''
    
class now(object):   
    now = datetime.datetime.now()
    
class nowish(object):
    nowish = str(now.year)+"_"+str(now.month)+"_"+str(now.day)
    
class ws(object): 
    ws = r'\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST'
    arcpy.env.overwriteOutput= True
class tempgdb(object):
    tempgdb = "CANSYSNet"+str(now.year)+"_"+str(now.month)+"_"+str(now.day)+".gdb"
    try:
        arcpy.CreateFileGDB_management(ws,tempgdb)
        print 'created temp gdb '+ ws, tempgdb
    except:
        print 'temp gdb already exists for today'
        pass
    arcpy.env.workspace = ws+"\\"+tempgdb

class tempmdb(object):
    tempmdb = "CANSYSNet"+str(now.year)+"_"+str(now.month)+"_"+str(now.day)+".gdb"
    try:
        arcpy.CreatePersonalGDB_management(ws,tempmdb,"9.1")
        print 'created temp mdb '+ ws, tempmdb
    except Exception:
        print "not creating - already there"
        pass
    arcpy.env.workspace = ws+"\\"+tempmdb  

class TempDB(object):
    tempmdb = "CANSYSNet2013_7_29.mdb"
    tempgdb = "CANSYSNet2013_7_29.gdb"
    
class LRSENV(object):
    arcpy.env.MResolution = 0.0005
    arcpy.env.MTolerance = 0.001 
    
class XYENV(object):
    arcpy.env.XYResolution = '0.000000000899322 Degrees'
    arcpy.env.XYTolerance = '0.000000001798644 Degrees'
    
class EXOR_PROD(object):    
    EXOR_PROD =  "Database Connections\ATLASPROD.odc\:"


    def __init__(self):
        '''
        Constructor
        '''



        