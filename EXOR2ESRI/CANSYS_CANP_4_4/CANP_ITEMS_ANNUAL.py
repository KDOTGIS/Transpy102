'''
Created on Feb 17, 2014

@author: kyleg
'''

def: __main___
    #ESRI ITEM PROCESSOR
    import os, sys
    import arcpy, datetime
    
    from arcpy import mapping, env, Exists, MakeFeatureLayer_management, Copy_management, DissolveRouteEvents_lr, MakeTableView_management
    sourceConnection = r"Database Connections\CANP_Report_User.sde"
    destConnection = r"Database Connections\SQL61_GIS_CANSYS.sde"
    mxd = mapping.MapDocument(r"\\gisdata\arcgis\GISdata\MXD\2014010202_CANSYS_AADT.mxd")
    
    env.MResolution = 0.0005 
    env.MTolerance = 0.001 
    env.overwriteOutput = "True"
    
    #ITEM PROCESSOR
    lyrlist = ["ACCS", "ADMO", "AVSP", "CPMS", "CPAV", "FUN", "GPGR", "GRAD", "HCUR", "HPMS","INTC", "INTR", "LAND", "LNCL", "LANE", "MNTR", "MED", "NONA",  "NHS","PASS", "PAVC", "PMID","RMBL", "SNIC", "SMAP", "STP", "STRP","SHLD", "SWID", "SPED", "SWID", "TRAF", "TOLL", "UAB"]
    
    #ITEMS THAT ARE ANNUAL - AADT, CAPS, 
    #LYRS takes a long time
    
    #pointlyrlist = ["INTC", "CVSD", "INTR", "STRP"]
    
    for lyr in lyrlist:
        print str(datetime.datetime.now())
        srclyr = sourceConnection +r"\NM3.NM_INV_"+str(lyr)+"_SDO_V"
        destlyr = destConnection+r"\GIS_CANSYS.DBO."+str(lyr)
        try:
            if Exists srclyr:
                Copy_management(srclyr, destlyr,"FeatureClass")
                print " Copied " + str(lyr) + " to the SQL server database " + str(datetime.datetime.now())
            else: 
                print "that view don't exist dummy ..." + str(lyr)
    
if __name__ == '__main__':
    pass
