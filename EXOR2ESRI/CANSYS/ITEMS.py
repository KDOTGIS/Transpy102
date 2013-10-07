'''
Created on Aug 20, 2013
Join the NEID_ITEM/MEMBER/ELEMENT Chain to a the CANSYS exported spatial item 

@author: kyleg
'''

class ITEMS(object):
    '''
    classdocs
    '''

'''

'''
pointlyrlist = ["INTC", "INTR"]
linelyrlist = ["LNCL", "LANE", "FUN", "STP", "SHLD", "ACCS", "ADMO", "PMID", "MNTR", "CITY", "MED", "NHS", "RMBL","SPED", "SWID", "TOLL"]
linelyrlist_ST = ["CITY", "UAB"] 
   
fixlist = ["INTR", "INTC", "FUN", "CITY"]    
    
from arcpy import env, mapping, CalculateField_management, MakeFeatureLayer_management, MakeTableView_management, ListFields, AddJoin_management, LocateFeaturesAlongRoutes_lr, MakeRouteEventLayer_lr, FeatureClassToFeatureClass_conversion

from CONFIG import ws, tempmdb, tempgdb, nowish, MResolution, MTolerance
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

lyrlist = pointlyrlist + linelyrlist + linelyrlist_ST
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

for lyr in pointlyrlist: 
    outlyr = ws+"\\"+tempgdb+"\\"+str(lyr)+"_pt_1"
    print lyr +"_C is the layer I'm linear referencing now..."
    lyr = lyr+"_C"
    LocateFeaturesAlongRoutes_lr(lyr,"CMLRS","LRS_KEY",'0.5 feet', outlyr,"LRS_KEY POINT Cnty_Logmile", "FIRST", "DISTANCE", "ZERO", "FIELDS")
    MakeRouteEventLayer_lr("CMLRS","LRS_KEY",outlyr,"LRS_KEY POINT Cnty_Logmile",lyr+"_Events","#","ERROR_FIELD","ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
    print str(lyr) + " event table located as points "  + str(outlyr)
    
for lyr in linelyrlist: 
    print lyr+"_C is the layer I'm linear referencing now..."
    outlyr = ws+"\\"+tempgdb+"\\"+str(lyr)+"_ln_1"
    lyr = lyr+"_C"
    LocateFeaturesAlongRoutes_lr(lyr,"CMLRS","LRS_KEY",'0.5 feet', outlyr,"LRS_KEY LINE Beg_Cnty_Logmile End_Cnty_Logmile", "FIRST", "DISTANCE", "NO_ZERO", "FIELDS", "NO_M_DIRECTION")
    MakeRouteEventLayer_lr("CMLRS","LRS_KEY",outlyr,"LRS_KEY LINE Beg_Cnty_Logmile End_Cnty_Logmile",lyr+"_Events","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
    print str(lyr) + " event table located as lines " + str(outlyr)
    del lyr
       
for lyr in linelyrlist_ST: 
    print lyr+"_C is the layer I'm linear referencing now..."
    outlyr = ws+"\\"+tempgdb+"\\"+str(lyr)+"_ln_1"
    lyr = lyr+"_C"
    LocateFeaturesAlongRoutes_lr(lyr,"SMLRS","LRS_ROUTE",'0.5 feet', outlyr,"LRS_ROUTE LINE Beg_State_Logmile End_State_Logmile", "FIRST", "DISTANCE", "NO_ZERO", "FIELDS", "NO_M_DIRECTION")
    MakeRouteEventLayer_lr("SMLRS","LRS_ROUTE",outlyr,"LRS_ROUTE LINE Beg_State_Logmile End_State_Logmile",lyr+"_Events","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
    print str(lyr) + " event table located as lines " + str(outlyr)
    del lyr          
       
try:
    import DOMAINS
    DOMAINS = DOMAINS
    print "pulled Domain"
except:
    pass    
wsouttbl = ws+"\\"+tempgdb

#run individual scripts that set up domains, custom objects, etc

lyrlist = ["INTR", "LNCL", "FUN"]
for lyr in lyrlist:
    lyrin = lyr+"_ITEM"#    
    FeatureClassToFeatureClass_conversion(lyrin, ws+"\\"+tempgdb,lyr) #23 sec

mxdout = r"\\GISDATA\ArcGIS\GISDATA\MXD\GP_LNCL_INTR"+nowish+".mxd"
mxd.saveACopy(mxdout)
del mxd

print "Process Completed - Hell yeah!"
#AADT and LYRS  - lots over overlap, takes kind of a long time
#with long item list (24 items), started to run around 8 AM, ended the run around noon... took about 4 hours to do all those items

from arcpy import TableToTable_conversion, DissolveRouteEvents_lr, AddField_management, AddIndex_management, AssignDomainToField_management, DeleteField_management
def CITY ():
    itemname = "CITY"
    cantbl = itemname+"_ln_1"
    
    domname0 = 'CITY_TYPE'
    domstate = """IAL_DOMAIN = 'CITY_TYPE' AND IAL_END_DATE is NULL"""
    domfields = "CT_CITY_NBRR_INCORPORATED_CITY"
    domtbl = itemname+"_"+domfields
    disfields = domfields
    
    domname = "CT_CITY_NBR"
  
    MakeTableView_management("Database Connections/ATLASPROD.odc/V_NM_CTY",domname)
    TableToTable_conversion(domname, wsouttbl, domname+"R", "#")
    MakeTableView_management(wsouttbl+"//"+cantbl,itemname+"PD",""""NE_OWNER" IN ( 'EB' , 'NB' )""","#")
    DissolveRouteEvents_lr(itemname+"PD","LRS_ROUTE LINE Beg_State_Logmile End_State_Logmile", "CITY_NBR", wsouttbl+"//"+itemname+"_SD","LRS_ROUTE LINE Beg_State_Logmile End_State_Logmile","CONCATENATE","INDEX")
    AddIndex_management(wsouttbl+"//"+itemname+"_SD","CITY_NBR","CITY_NBR","NON_UNIQUE","NON_ASCENDING")
    AddField_management(wsouttbl+"//"+domname+"R", "CITY_NBR", "FLOAT", "#", "#", "#")
    CalculateField_management(wsouttbl+"//"+domname+"R", "CITY_NBR", "[CITY_NUMBER]", "VB")
    MakeTableView_management(wsouttbl+"//"+itemname+"_SD", itemname+"_view", "#")
    AddJoin_management(itemname+"_view", "CITY_NBR", wsouttbl+"//"+domname+"R", "CITY_NBR", "KEEP_ALL")
    TableToTable_conversion(itemname+"_view", wsouttbl, itemname+"_EVENT", "#")
    
    AssignDomainToField_management(wsouttbl+"//"+itemname+"_EVENT",domfields,domname0)
    
    DeleteField_management(wsouttbl+"//"+itemname+"_EVENT","CTYR_OBJECTID;CTYR_IIT_NE_ID;CTYR_IIT_INV_TYPE;CTYR_IIT_PRIMARY_KEY;CTYR_IIT_START_DATE;CTYR_IIT_DATE_CREATED;CTYR_IIT_DATE_MODIFIED;CTYR_IIT_CREATED_BY;CTYR_IIT_MODIFIED_BY;CTYR_IIT_ADMIN_UNIT;CTYR_IIT_NOTE;CTYR_IIT_PEO_INVENT_BY_ID;CTYR_NAU_UNIT_CODE;CTYR_IIT_END_DATE;CTYR_CITY_NBR")
    MakeRouteEventLayer_lr(wsouttbl+"//SMLRS","LRS_ROUTE",wsouttbl+"//"+itemname+"_EVENT","LRS_ROUTE LINE Beg_State_Logmile End_State_Logmile",itemname+"_ITEM","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
    FeatureClassToFeatureClass_conversion(itemname+"_ITEM", wsouttbl, itemname)
    DeleteField_management(wsouttbl+"//"+itemname,"CTYR_OBJECTID;CTYR_IIT_NE_ID;CTYR_IIT_INV_TYPE;CTYR_IIT_PRIMARY_KEY;CTYR_IIT_START_DATE;CTYR_IIT_DATE_CREATED;CTYR_IIT_DATE_MODIFIED;CTYR_IIT_CREATED_BY;CTYR_IIT_MODIFIED_BY;CTYR_IIT_ADMIN_UNIT;CTYR_IIT_NOTE;CTYR_IIT_PEO_INVENT_BY_ID;CTYR_NAU_UNIT_CODE;CTYR_IIT_END_DATE;CTYR_CITY_NBR")
    print "we have cities"

def FUN ():
    itemname = 'FUN'
    cantbl = itemname+"_ln_1"
    domname = 'FC_FUN_CLASS'
    domfields = "FUN_CLASS"
    domtbl = itemname+"_"+domfields+"_tbl"
    disfields = domfields
    
    MakeTableView_management(wsouttbl+"//"+cantbl,itemname+"PD",""""NE_OWNER" IN ( 'EB' , 'NB' )""","#")
    DissolveRouteEvents_lr(itemname+"PD","LRS_KEY LINE Beg_Cnty_Logmile End_Cnty_Logmile",disfields,wsouttbl+"//"+itemname+"_EVENT","LRS_Key LINE Beg_Cnty_Logmile End_Cnty_Logmile","CONCATENATE","INDEX")
    AssignDomainToField_management(wsouttbl+"//"+itemname+"_EVENT",domfields,domname)
    MakeRouteEventLayer_lr(wsouttbl+"//CMLRS","LRS_KEY",wsouttbl+"//"+itemname+"_EVENT","LRS_Key LINE Beg_Cnty_Logmile End_Cnty_Logmile",itemname+"_ITEM","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
    FeatureClassToFeatureClass_conversion(itemname+"_ITEM", wsouttbl, itemname)
    
    lyrlist = ["FUN"]
    for lyr in lyrlist:
        lyrin = lyr+"_ITEM"#    
        FeatureClassToFeatureClass_conversion(lyrin, ws+"\\"+tempgdb,lyr) #23 sec

def INTR ():
    TableToTable_conversion("INTR_pt_1",wsouttbl,"INTR_pt_2","#","""LRS_KEY "LRS_KEY" true true false 13 Text 0 0 ,First,#,INTR_pt_1,LRS_KEY,-1,-1;Cnty_Logmile "Cnty_Logmile" true true false 8 Double 0 0 ,First,#,INTR_pt_1,Cnty_Logmile,-1,-1;Distance "Distance" true true false 8 Double 0 0 ,First,#,INTR_pt_1,Distance,-1,-1;IIT_NE_ID "IIT_NE_ID" true false false 4 Long 0 0 ,First,#,INTR_pt_1,IIT_NE_ID,-1,-1;IIT_INV_TYPE "IIT_INV_TYPE" true false false 4 Text 0 0 ,First,#,INTR_pt_1,IIT_INV_TYPE,-1,-1;IIT_PRIMARY_KEY "IIT_PRIMARY_KEY" true false false 50 Text 0 0 ,First,#,INTR_pt_1,IIT_PRIMARY_KEY,-1,-1;IIT_START_DATE "IIT_START_DATE" true false false 8 Date 0 0 ,First,#,INTR_pt_1,IIT_START_DATE,-1,-1;IIT_DATE_CREATED "IIT_DATE_CREATED" true false false 8 Date 0 0 ,First,#,INTR_pt_1,IIT_DATE_CREATED,-1,-1;IIT_DATE_MODIFIED "IIT_DATE_MODIFIED" true false false 8 Date 0 0 ,First,#,INTR_pt_1,IIT_DATE_MODIFIED,-1,-1;IIT_CREATED_BY "IIT_CREATED_BY" true false false 30 Text 0 0 ,First,#,INTR_pt_1,IIT_CREATED_BY,-1,-1;IIT_MODIFIED_BY "IIT_MODIFIED_BY" true false false 30 Text 0 0 ,First,#,INTR_pt_1,IIT_MODIFIED_BY,-1,-1;IIT_ADMIN_UNIT "IIT_ADMIN_UNIT" true false false 4 Long 0 0 ,First,#,INTR_pt_1,IIT_ADMIN_UNIT,-1,-1;IIT_DESCR "IIT_DESCR" true true false 40 Text 0 0 ,First,#,INTR_pt_1,IIT_DESCR,-1,-1;IIT_NOTE "IIT_NOTE" true true false 40 Text 0 0 ,First,#,INTR_pt_1,IIT_NOTE,-1,-1;IIT_PEO_INVENT_BY_ID "IIT_PEO_INVENT_BY_ID" true true false 4 Long 0 0 ,First,#,INTR_pt_1,IIT_PEO_INVENT_BY_ID,-1,-1;NAU_UNIT_CODE "NAU_UNIT_CODE" true true false 10 Text 0 0 ,First,#,INTR_pt_1,NAU_UNIT_CODE,-1,-1;IIT_END_DATE "IIT_END_DATE" true true false 8 Date 0 0 ,First,#,INTR_pt_1,IIT_END_DATE,-1,-1;INTRSCTN_NAME "INTRSCTN_NAME" true true false 50 Text 0 0 ,First,#,INTR_pt_1,INTRSCTN_NAME,-1,-1;ON_STATE_NONSTATE "ON_STATE_NONSTATE" true true false 16 Text 0 0 ,First,#,INTR_pt_1,ON_STATE_NONSTATE,-1,-1;INTRSCTN_DESC "INTRSCTN_DESC" true true false 200 Text 0 0 ,First,#,INTR_pt_1,INTRSCTN_DESC,-1,-1;INTRSCTN_ID "INTRSCTN_ID" true false false 50 Text 0 0 ,First,#,INTR_pt_1,INTRSCTN_ID,-1,-1;TFO_IND "TFO_IND" true true false 1 Text 0 0 ,First,#,INTR_pt_1,TFO_IND,-1,-1;CART_NODE_ID "CART_NODE_ID" true true false 4 Long 0 0 ,First,#,INTR_pt_1,CART_NODE_ID,-1,-1;LEFT_TURN_LN "LEFT_TURN_LN" true true false 4 Long 0 0 ,First,#,INTR_pt_1,LEFT_TURN_LN,-1,-1;RIGHT_TURN_LN "RIGHT_TURN_LN" true true false 4 Long 0 0 ,First,#,INTR_pt_1,RIGHT_TURN_LN,-1,-1;INTERSECTION_CONTROL "INTERSECTION_CONTROL" true true false 4 Long 0 0 ,First,#,INTR_pt_1,INTERSECTION_CONTROL,-1,-1;PER_GREEN_TIME "PER_GREEN_TIME" true true false 4 Double 0 0 ,First,#,INTR_pt_1,PER_GREEN_TIME,-1,-1;LONGITUDE "LONGITUDE" true true false 4 Float 0 0 ,First,#,INTR_pt_1,LONGITUDE,-1,-1;LATITUDE "LATITUDE" true true false 4 Float 0 0 ,First,#,INTR_pt_1,LATITUDE,-1,-1;NM_NE_ID_IN "NM_NE_ID_IN" true false false 4 Long 0 0 ,First,#,INTR_pt_1,NM_NE_ID_IN,-1,-1;NM_NE_ID_OF "NM_NE_ID_OF" true false false 4 Long 0 0 ,First,#,INTR_pt_1,NM_NE_ID_OF,-1,-1;NM_TYPE "NM_TYPE" true false false 4 Text 0 0 ,First,#,INTR_pt_1,NM_TYPE,-1,-1;NM_OBJ_TYPE "NM_OBJ_TYPE" true false false 4 Text 0 0 ,First,#,INTR_pt_1,NM_OBJ_TYPE,-1,-1;NM_BEGIN_MP "NM_BEGIN_MP" true false false 8 Double 0 0 ,First,#,INTR_pt_1,NM_BEGIN_MP,-1,-1;NM_START_DATE "NM_START_DATE" true false false 8 Date 0 0 ,First,#,INTR_pt_1,NM_START_DATE,-1,-1;NM_END_DATE "NM_END_DATE" true true false 8 Date 0 0 ,First,#,INTR_pt_1,NM_END_DATE,-1,-1;NM_END_MP "NM_END_MP" true false false 8 Double 0 0 ,First,#,INTR_pt_1,NM_END_MP,-1,-1;NM_SLK "NM_SLK" true true false 8 Double 0 0 ,First,#,INTR_pt_1,NM_SLK,-1,-1;NM_CARDINALITY "NM_CARDINALITY" true true false 8 Double 0 0 ,First,#,INTR_pt_1,NM_CARDINALITY,-1,-1;NM_ADMIN_UNIT "NM_ADMIN_UNIT" true false false 4 Long 0 0 ,First,#,INTR_pt_1,NM_ADMIN_UNIT,-1,-1;NM_DATE_CREATED "NM_DATE_CREATED" true true false 8 Date 0 0 ,First,#,INTR_pt_1,NM_DATE_CREATED,-1,-1;NM_DATE_MODIFIED "NM_DATE_MODIFIED" true true false 8 Date 0 0 ,First,#,INTR_pt_1,NM_DATE_MODIFIED,-1,-1;NM_MODIFIED_BY "NM_MODIFIED_BY" true true false 30 Text 0 0 ,First,#,INTR_pt_1,NM_MODIFIED_BY,-1,-1;NM_CREATED_BY "NM_CREATED_BY" true true false 30 Text 0 0 ,First,#,INTR_pt_1,NM_CREATED_BY,-1,-1;NM_SEQ_NO "NM_SEQ_NO" true true false 8 Double 0 0 ,First,#,INTR_pt_1,NM_SEQ_NO,-1,-1;NM_SEG_NO "NM_SEG_NO" true true false 4 Long 0 0 ,First,#,INTR_pt_1,NM_SEG_NO,-1,-1;NM_TRUE "NM_TRUE" true true false 8 Double 0 0 ,First,#,INTR_pt_1,NM_TRUE,-1,-1;NM_END_SLK "NM_END_SLK" true true false 8 Double 0 0 ,First,#,INTR_pt_1,NM_END_SLK,-1,-1;NM_END_TRUE "NM_END_TRUE" true true false 8 Double 0 0 ,First,#,INTR_pt_1,NM_END_TRUE,-1,-1;NE_ID "NE_ID" true false false 4 Long 0 0 ,First,#,INTR_pt_1,NE_ID,-1,-1;NE_UNIQUE "NE_UNIQUE" true false false 30 Text 0 0 ,First,#,INTR_pt_1,NE_UNIQUE,-1,-1;NE_TYPE "NE_TYPE" true false false 4 Text 0 0 ,First,#,INTR_pt_1,NE_TYPE,-1,-1;NE_NT_TYPE "NE_NT_TYPE" true false false 4 Text 0 0 ,First,#,INTR_pt_1,NE_NT_TYPE,-1,-1;NE_DESCR "NE_DESCR" true false false 240 Text 0 0 ,First,#,INTR_pt_1,NE_DESCR,-1,-1;NE_LENGTH "NE_LENGTH" true true false 8 Double 0 0 ,First,#,INTR_pt_1,NE_LENGTH,-1,-1;NE_ADMIN_UNIT "NE_ADMIN_UNIT" true false false 4 Long 0 0 ,First,#,INTR_pt_1,NE_ADMIN_UNIT,-1,-1;NE_DATE_CREATED "NE_DATE_CREATED" true false false 8 Date 0 0 ,First,#,INTR_pt_1,NE_DATE_CREATED,-1,-1;NE_DATE_MODIFIED "NE_DATE_MODIFIED" true false false 8 Date 0 0 ,First,#,INTR_pt_1,NE_DATE_MODIFIED,-1,-1;NE_MODIFIED_BY "NE_MODIFIED_BY" true false false 30 Text 0 0 ,First,#,INTR_pt_1,NE_MODIFIED_BY,-1,-1;NE_CREATED_BY "NE_CREATED_BY" true false false 30 Text 0 0 ,First,#,INTR_pt_1,NE_CREATED_BY,-1,-1;NE_START_DATE "NE_START_DATE" true false false 8 Date 0 0 ,First,#,INTR_pt_1,NE_START_DATE,-1,-1;NE_END_DATE "NE_END_DATE" true true false 8 Date 0 0 ,First,#,INTR_pt_1,NE_END_DATE,-1,-1;NE_GTY_GROUP_TYPE "NE_GTY_GROUP_TYPE" true true false 4 Text 0 0 ,First,#,INTR_pt_1,NE_GTY_GROUP_TYPE,-1,-1;NE_OWNER "NE_OWNER" true true false 4 Text 0 0 ,First,#,INTR_pt_1,NE_OWNER,-1,-1;NE_NAME_1 "NE_NAME_1" true true false 80 Text 0 0 ,First,#,INTR_pt_1,NE_NAME_1,-1,-1;NE_NAME_2 "NE_NAME_2" true true false 80 Text 0 0 ,First,#,INTR_pt_1,NE_NAME_2,-1,-1;NE_PREFIX "NE_PREFIX" true true false 4 Text 0 0 ,First,#,INTR_pt_1,NE_PREFIX,-1,-1;NE_NUMBER "NE_NUMBER" true true false 8 Text 0 0 ,First,#,INTR_pt_1,NE_NUMBER,-1,-1;NE_SUB_TYPE "NE_SUB_TYPE" true true false 2 Text 0 0 ,First,#,INTR_pt_1,NE_SUB_TYPE,-1,-1;NE_GROUP "NE_GROUP" true true false 30 Text 0 0 ,First,#,INTR_pt_1,NE_GROUP,-1,-1;NE_NO_START "NE_NO_START" true true false 4 Long 0 0 ,First,#,INTR_pt_1,NE_NO_START,-1,-1;NE_NO_END "NE_NO_END" true true false 4 Long 0 0 ,First,#,INTR_pt_1,NE_NO_END,-1,-1;NE_SUB_CLASS "NE_SUB_CLASS" true true false 4 Text 0 0 ,First,#,INTR_pt_1,NE_SUB_CLASS,-1,-1;NE_NSG_REF "NE_NSG_REF" true true false 240 Text 0 0 ,First,#,INTR_pt_1,NE_NSG_REF,-1,-1;NE_VERSION_NO "NE_VERSION_NO" true true false 240 Text 0 0 ,First,#,INTR_pt_1,NE_VERSION_NO,-1,-1""","#")

#convert EXOR domains to SDE Database domains - intersection type
    itemname = 'INTR'
    itemdom = 'IN_INTRSCTN_TYPE'  #IN INTRSCTN_TYPE, TURN_LANE
    newdomname = 'INTRSCTN_TYPE'
    itemsel = """"IAL_DOMAIN" = '"""+itemdom+"'"
    itemdescr = 'Intersection Type'
    
    #convert EXOR domains to SDE Database domains - turn lanes type
    itemdom1 = 'TURN_LANE'  #IN INTRSCTN_TYPE, TURN_LANE
    newdomname1 = 'INTERSECTION_TURN_LANE'
    itemsel1 = """"IAL_DOMAIN" = '"""+itemdom1+"'"
    itemdescr1 = 'Turn Lane Type'
    
    MakeTableView_management(itemname+"_pt_2", itemname+"PD","#","#") 
    print ("Intersections are located on a directional basis in some cases, so primary and secondary directions are allowed until advised differently")
    
    DissolveRouteEvents_lr(itemname+"PD","LRS_Key POINT Cnty_Logmile","IIT_NE_ID;INTRSCTN_NAME;ON_STATE_NONSTATE;INTRSCTN_DESC;INTRSCTN_ID;TFO_IND;CART_NODE_ID;LEFT_TURN_LN;RIGHT_TURN_LN;INTERSECTION_CONTROL;PER_GREEN_TIME;NE_OWNER",wsouttbl+"//"+itemname+"_EVENT","LRS_Key POINT Cnty_Logmile","DISSOLVE","INDEX")
    AssignDomainToField_management(itemname+"_EVENT","INTERSECTION_CONTROL",itemdom)
    AssignDomainToField_management(itemname+"_EVENT","LEFT_TURN_LN",itemdom1)
    AssignDomainToField_management(itemname+"_EVENT","RIGHT_TURN_LN",itemdom1)
    MakeRouteEventLayer_lr("CMLRS","LRS_KEY",itemname+"_EVENT","LRS_Key POINT Cnty_Logmile",itemname+"_ITEM","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
    #arcpy.FeatureClassToFeatureClass_conversion(itemname+"_ITEM", wsouttbl, itemname)
    
    lyrlist = ["INTR"]
    for lyr in lyrlist:
        lyrin = lyr+"_ITEM"#    
        FeatureClassToFeatureClass_conversion(lyrin, ws+"\\"+tempgdb,lyr) #23 sec

def LNCL():
    itemname = 'LNCL'
    lncldom = 'LC_LN_CLS_ID'
    print lncldom
    
    MakeTableView_management(wsouttbl+"\\"+"LNCL_ln_1","LNCLPD",""""NE_OWNER" IN ( 'EB' , 'NB' )""","#")
    DissolveRouteEvents_lr("LNCLPD","LRS_KEY LINE Beg_Cnty_Logmile End_Cnty_Logmile","LNCL_CLS_ID;NE_OWNER",wsouttbl+"//LNCL_EVENT","LRS_Key LINE Beg_Cnty_Logmile End_Cnty_Logmile","CONCATENATE","INDEX")
    AssignDomainToField_management(wsouttbl+"\\LNCL_EVENT","LNCL_CLS_ID",lncldom)
    MakeRouteEventLayer_lr(wsouttbl+"\\CMLRS","LRS_KEY", wsouttbl+"\\LNCL_EVENT","LRS_Key LINE Beg_Cnty_Logmile End_Cnty_Logmile","LNCL_ITEM","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
    
    lyrlist = ["LNCL"]
    for lyr in lyrlist:
        lyrin = lyr+"_ITEM"#    
        FeatureClassToFeatureClass_conversion(lyrin, ws+"\\"+tempgdb,lyr) #23 sec

def UAB():
    itemname = "UAB"
    cantbl = itemname+"_ln_1"
    domname = "UABR"
    
    MakeTableView_management("Database Connections/ATLASPROD.odc/V_NM_UABR",domname)
    
    TableToTable_conversion(domname, wsouttbl, domname+"R", "#")
    MakeTableView_management(wsouttbl+"//"+cantbl,itemname+"PD",""""NE_OWNER" IN ( 'EB' , 'NB' )""","#")
    DissolveRouteEvents_lr(itemname+"PD","LRS_ROUTE LINE Beg_State_Logmile End_State_Logmile", "CITY_NBR", wsouttbl+"//"+itemname+"_SD","LRS_ROUTE LINE Beg_State_Logmile End_State_Logmile","CONCATENATE","INDEX")
    AddIndex_management(wsouttbl+"//"+itemname+"_SD","CITY_NBR","CITY_NBR","NON_UNIQUE","NON_ASCENDING")
    AddField_management(wsouttbl+"//"+domname+"R", "CITY_NBR", "FLOAT", "#", "#", "#")
    CalculateField_management(wsouttbl+"//"+domname+"R", "CITY_NBR", "[CITY_NUMBER]", "VB")
    MakeTableView_management(wsouttbl+"//"+itemname+"_SD", itemname+"_view", "#")
    AddJoin_management(itemname+"_view", "CITY_NBR", wsouttbl+"//"+domname+"R", "CITY_NBR", "KEEP_ALL")
    TableToTable_conversion(itemname+"_view", wsouttbl, domname+"J", "#")
    MakeRouteEventLayer_lr(wsouttbl+"//SMLRS","LRS_ROUTE",wsouttbl+"//"+domname+"J","LRS_ROUTE LINE Beg_State_Logmile End_State_Logmile",itemname+"_ITEM","#","ERROR_FIELD","NO_ANGLE_FIELD","NORMAL","ANGLE","LEFT","POINT")
    FeatureClassToFeatureClass_conversion(itemname+"_ITEM", wsouttbl, itemname)
    print "we have UABs"



