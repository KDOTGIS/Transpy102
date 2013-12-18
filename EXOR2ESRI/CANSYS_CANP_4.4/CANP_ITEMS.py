'''
Created on Dec 11, 2013

@author: kyleg
'''
#ESRI ROUTE PROCESSOR
env.MResolution = 0.0005 
env.MTolerance = 0.001 


from arcpy import mapping, env, MakeTableView_management, MakeFeatureLayer_management, AddJoin_management, LocateFeaturesAlongRoutes_lr, MakeRouteEventLayer_lr
mxd = mapping.MapDocument("CURRENT")

MakeTableView_management(r"Database Connections\\CANP.sde\\NM3.NM_INV_ITEMS", "Items")
MakeTableView_management(r"Database Connections\\CANP.sde\\NM3.NM_MEMBERS", "Members")
sselements = "NE_NT_TYPE = 'SECT'"
MakeTableView_management(r"Database Connections\\CANP.sde\\NM3.NM_ELEMENTS", "Elements", sselements)
#MakeFeatureLayer_management(r"Database Connections\CANP.sde\NM3.NM_NLT_SRND_SRND_SDO", "SRND" )

#ITEM PROCESSOR
linelyrlist = ["AADT", "ACCS", "ADMO", "ACCX", "AVSP", "CAPS", "CITY", "CONC", "CPMS", "CPAV", "FUN", "GPGR", "GRAD", "HCUR", "HPMS", "LAND", "LNCL", "LANE", "LYRS", "MNTR", "MED", "NONA",  "NHS","PASS", "PAVC", "PMID","RMBL", "SNIC", "SMAP", "STP", "SHLD", "SWID", "SPED", "SWID", "TRAF", "TOLL", "UAB"]
pointlyrlist = ["INTC", "CVSD", "INTR", "STRP"]
ITEMSDO = r"Database Connections\\CANP.sde\\NM3.NM_NIT_"

for lyr in linelyrlist:
    addlyr = ITEMSDO+lyr+"_SDO"
    lyrname = str(addlyr[36:])
    MakeFeatureLayer_management(addlyr, lyrname)
    AddJoin_management(lyrname, "NE_ID","Members","NM_NE_ID_IN","KEEP_COMMON")
    AddJoin_management(lyrname,"NE_ID_OF","Elements","NE_ID","KEEP_COMMON")
    print str(addlyr) + " elements table joined"
      
    #LocateFeaturesAlongRoutes_lr(lyr,"SRND","LRS_ROUTE",'0.5 feet', outlyr,"LRS_ROUTE LINE Beg_State_Logmile End_State_Logmile", "FIRST", "DISTANCE", "NO_ZERO", "FIELDS", "NO_M_DIRECTION")
    #MakeRouteEventLayer_lr("SRND","LRS_ROUTE",outlyr,"LRS_ROUTE LINE Beg_State_Logmile End_State_Logmile",lyr+"_Events","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")



        
        #Add definition query for element NE_NT_TYPE = SECT in order to pull only state netowrk and separate the Network types


