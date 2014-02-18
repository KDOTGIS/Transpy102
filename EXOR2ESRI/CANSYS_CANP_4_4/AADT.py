'''
Created on Aug 29, 2013

@author: kyleg
'''

class MyClass(object):
    '''
    classdocs
    '''

linelyrlist = ["AADT"]

fixlist = ["AADT"]    
    
from arcpy import mapping, env, MakeFeatureLayer_management, MakeTableView_management, ListFields, AddJoin_management, LocateFeaturesAlongRoutes_lr, MakeRouteEventLayer_lr, FeatureClassToFeatureClass_conversion

from CONFIG import ws, tempgdb, tempmdb, nowish, MResolution, MTolerance
ws = r'\\gisdata\arcgis\GISdata\KDOT\BTP\CANSYSTEST'
'''######################################################
tempmdb = "CANSYSNet2013_7_29.mdb"
tempgdb = "CANSYSNet2013_7_29.gdb"
######################################################'''

print ws
mxd = mapping.MapDocument(r"\\GISDATA\ArcGIS\GISDATA\MXD\GP_LNCL_INTR.mxd")
env.MResolution = MResolution
env.MTolerance = MTolerance  # set the M tolerance below the default 
env.overwriteOutput = True
rteCMLRS = ws+"\\"+tempgdb+"\\CMLRS"
rteSMLRS = ws+"\\"+tempgdb+"\\SMLRS"
MakeFeatureLayer_management(rteCMLRS, "CMLRS")
MakeFeatureLayer_management(rteSMLRS, "SMLRS")
MakeTableView_management(r"Database Connections\\ATLASPROD.odc\\NM3.NM_INV_ITEMS", "Items")
MakeTableView_management(r"Database Connections\\ATLASPROD.odc\\NM3.NM_MEMBERS", "Members")
MakeTableView_management(r"Database Connections\\ATLASPROD.odc\\NM3.NM_ELEMENTS", "Elements")
    
lyrlist = linelyrlist
print lyrlist

for lyr in lyrlist:
    lyrname = str(lyr)+"_C"
    addlyr = ws+"\\"+tempmdb+"\\"+lyr
    MakeFeatureLayer_management(addlyr, lyrname)
    lyr = lyr+"_C"
    IDField = ListFields(lyr, "*NE_ID*", "Integer")
    for field in IDField:
        PKfield =  "{}".format(field.name)
        AddJoin_management(lyr,PKfield,"Members","NM_NE_ID_IN","KEEP_COMMON")
        AddJoin_management(lyr,"NM_NE_ID_OF","Elements","NE_ID","KEEP_COMMON")
        print str(lyr) + " elements table joined"

for lyr in linelyrlist: 
    print lyr+"_C is the layer I'm linear referencing now..."
    outlyr = ws+"\\"+tempgdb+"\\"+str(lyr)+"_ln_1"
    lyr = lyr+"_C"
    LocateFeaturesAlongRoutes_lr(lyr,"CMLRS","LRS_KEY",'0.5 feet', outlyr,"LRS_KEY LINE Beg_Cnty_Logmile End_Cnty_Logmile", "FIRST", "DISTANCE", "NO_ZERO", "FIELDS", "NO_M_DIRECTION")
    MakeRouteEventLayer_lr("CMLRS","LRS_KEY",outlyr,"LRS_KEY LINE Beg_Cnty_Logmile End_Cnty_Logmile",lyr+"_Events","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
    print str(lyr) + " event table located as lines " + str(outlyr)
    del lyr    
    
wsouttbl = ws+"\\"+tempgdb


lyrlist = ["AADT"]

itemname = 'AADT'
cantbl = itemname+"_ln_1"
domname = 'FC_FUN_CLASS'
domfields = "FUN_CLASS"
disfields = domfields

MakeTableView_management(wsouttbl+"//"+cantbl,itemname+"PD","#","#")
MakeRouteEventLayer_lr(wsouttbl+"//CMLRS","LRS_KEY",wsouttbl+"//"+itemname+"_EVENT","LRS_Key LINE Beg_Cnty_Logmile End_Cnty_Logmile",itemname+"_ITEM","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
FeatureClassToFeatureClass_conversion(itemname+"_ITEM", wsouttbl, itemname)


for lyr in lyrlist:
    lyrin = lyr+"_ITEM"#    
    FeatureClassToFeatureClass_conversion(lyrin, ws+"\\"+tempgdb,lyr) #23 sec


mxdout = r"\\GISDATA\ArcGIS\GISDATA\MXD\GP_LNCL_INTR"+nowish+".mxd"
mxd.saveACopy(mxdout)
del mxd

print "Process Completed - Hell yeah!"   
'''
def AADT ():

'''

#    def __init__(selfparams):
