'''
Created on Aug 20, 2013

@author: kyleg
'''

if __name__ == '__main__':
    pass

import arcpy
from ENV import ws, tempgdb
   
def copyfromstaged(lyrlist, admin, fdset, fcoutpath):
    for lyr in lyrlist:
        print (fcoutpath+admin+'.'+lyr)
        if arcpy.Exists(fcoutpath+admin+'.'+lyr):
            arcpy.DeleteFeatures_management(fcoutpath+admin+'.'+ lyr)
            arcpy.Append_management(ws+"/"+tempgdb+'/'+lyr ,fcoutpath+admin+'.'+lyr,"NO_TEST","#")
            print "updated "+lyr+" in " + fcoutpath
        else:
            arcpy.FeatureClassToFeatureClass_conversion(ws+"/"+tempgdb+'/'+lyr, fcoutpath, lyr)
            print "copied new "+lyr+" feature class to " + fcoutpath
            print " Check roles and privleges on this "+lyr +" at "+fcoutpath
        try:
            arcpy.CalculateField_management(fcoutpath+admin+'.'+lyr,"NETWORKDATE","datetime.datetime.now( )","PYTHON_9.3","#")
            print "copy date field updated"
        except:
            arcpy.AddField_management(fcoutpath+admin+'.'+lyr, "NETWORKDATE", "DATE" )
            arcpy.CalculateField_management(fcoutpath+admin+'.'+lyr,"NETWORKDATE","datetime.datetime.now( )","PYTHON_9.3","#")
            print "copy date field added and updated"
            pass
    return

class SDEDEV_ROADWAY:
    lyrlist = ["SMLRS", "CMLRS","STATE_SYSTEM"] #Layers to copy
    sdedev = r'Database Connections/SDEDEV_GISDEV.sde/' #destination DB connection
    admin = 'GIS_DEV'
    fdset = r'KDOT_ROADWAY/'  #Destination DB feature Class
    fcoutpath = sdedev+admin+'.'+fdset
    print fcoutpath
    copyfromstaged (lyrlist, admin, fdset, fcoutpath)
    print "copied " + str(lyrlist) + " to "+ fcoutpath
    
class SDEDEV_CANSYS:
    lyrlist = ["CRND", "SRND"] #"LNCL", "FUN", "INTR", "CITY", 
    sdedev = r'Database Connections/SDEDEV_GISDEV.sde/'
    fdset = r'CANSYS/'
    admin = 'GIS_DEV'
    fcoutpath = sdedev+admin+'.'+fdset
    fcoutpath
    copyfromstaged (lyrlist, admin, fdset, fcoutpath)
    print "copied " + str(lyrlist) + " to "+ fcoutpath

class SDEPROD_ROADWAY:
    lyrlist = ["SMLRS", "CMLRS","STATE_SYSTEM"] #Layers to copy
    sdedev = r'Database Connections/SDEPROD_GIS.sde/' #destination DB connection
    admin = 'GIS'
    sys = 'Database Connections\SDEDEV_SDE.sde'
    arcpy.DisconnectUser(sys, "All")
    fdset = r'KDOT_ROADWAY/'  #Destination DB feature Class
    fcoutpath = sdedev+admin+'.'+fdset
    print fcoutpath
    copyfromstaged (lyrlist, admin, fdset, fcoutpath)
    print "copied " + str(lyrlist) + " to "+ fcoutpath
    
class SDEPROD_CANSYS:
    lyrlist = ["CRND", "SRND"] #"LNCL", "FUN", "INTR", "CITY",
    sdedev = r'Database Connections/SDEPROD_GIS.sde/'
    fdset = r'CANSYS/'
    admin = 'GIS'
    sys = 'Database Connections\SDEDEV_SDE.sde'
    arcpy.DisconnectUser(sys, "All")
    fcoutpath = sdedev+admin+'.'+fdset
    fcoutpath
    copyfromstaged (lyrlist, admin, fdset, fcoutpath)
    print "copied " + str(lyrlist) + " to "+ fcoutpath
'''    
class GISTEST:
    lyrlist = ["SMLRS", "CMLRS","STATE_SYSTEM", "STATE_SYSTEM_PRECISION"] #Layers to copy
    sdedev = r"Database Connections\GISTEST.sde" #destination DB connection
    admin = 'SHARED'
    fdset = r'/'  #Destination DB feature Class
    fcoutpath = sdedev+admin+'.'+fdset
    print fcoutpath
    copyfromstaged (lyrlist, admin, fdset, fcoutpath, sdedev)
    print "copied " + str(lyrlist) + " to "+ fcoutpath
   
class SQL_DEV_CANSYS:
    lyrlist = ["LNCL", "FUN", "INTR", "CITY", "CRND", "SRND"]
    sdedev = r'Database Connections/SDEPROD_GIS.sde/'
    fdset = r'CANSYS/'
    admin = 'GIS'
    fcoutpath = sdedev+admin+'.'+fdset
    fcoutpath
    copyfromstaged (lyrlist, admin, fdset, fcoutpath, sdedev)
    print "copied " + str(lyrlist) + " to "+ fcoutpath    
'''    