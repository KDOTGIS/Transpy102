'''
Created on Jul 23, 2014

@author: kyleg
'''
import ntpath
import arcpy
try:
    from config import wspath, reviewpath, KdotRd, kdotdb, Kdotdbfp
except:
    print "copy config to command line"
    
import re
"""
This module encodes a string using Soundex, as described by
http://en.wikipedia.org/w/index.php?title=Soundex&oldid=466065377

Only strings with the letters A-Z and of length >= 2 are supported.
"""

invalid_re = re.compile("[AEHIOUWY]|[^A-Z]")
numerical_re = re.compile("[A-Z]")

charsubs = {'B': '1', 'F': '1', 'P': '1', 'V': '1',
            'C': '2', 'G': '2', 'J': '2', 'K': '2',
            'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
            'D': '3', 'T': '3', 'L': '4', 'M': '5',
            'N': '5', 'R': '6'}

#numlist = ['1','2','3','4','5','6','7','8','9','0']

def normalize(s):
    """ Returns a copy of s without invalid chars and repeated letters. """
    # remove invalid chars
    first = s[0].upper()
    s = re.sub(invalid_re, "", s.upper()[1:])
    # remove repeated chars
    char = None
    
    s_clean = first

    for c in s:
        if char != c:
            s_clean += c
        char = c

    return s_clean


def soundex(s):
#""" Encode a string using Soundex.
#Takes a string and returns its Soundex representation.
#"""
    if len(s) < 2:
        return None
    s = normalize(s)
    last = None
    enc = s[0]
    for c in s[1:]:
        if len(enc) == 4:
            break
        if charsubs[c] != last:
            enc += charsubs[c]
        last = charsubs[c]
    while len(enc) < 4:
        enc += '0'
    return enc

def numdex(s):
    if s[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
        numerical_re = re.compile("[A-Z]|[^0-9][^0-9][^0-9][^0-9]")
        s=re.sub(numerical_re,"", s.zfill(4))
        return s.zfill(4)
    else:
        return soundex(s)
    

#set the workspace from the config file
arcpy.env.workspace = wspath
arcpy.env.overwriteOutput=1
gdb = arcpy.ListWorkspaces('*.gdb')

ng911 = gdb[0]
arcpy.env.workspace = ng911
datasets = arcpy.ListDatasets()
tables = arcpy.ListTables()
fd = datasets[0]
fcs = arcpy.ListFeatureClasses("", "", fd)
checkfile = reviewpath+"/"+ntpath.basename(ng911)
topo= fd+"/NG911_Topology"
arcpy.Compact_management(ng911)
if arcpy.Exists(checkfile):
    print "file already exists, replacing the existing file"
    arcpy.Delete_management(checkfile)
    arcpy.Copy_management(ng911, checkfile)
    pass
else:
    arcpy.Copy_management(ng911, checkfile)
    
#arcpy.CreateTable_management(checkfile, "CheckTable", KdotRd+"/CheckTable")
   
def Inventory():
    arcpy.env.workspace = ng911
    print "Geodatabase Name"
    for db in gdb:
        print db
    print "Feature Dataset Name"
    for ds in datasets:
        print "     "+ds
    print "Tables"
    for table in tables:
        tc = arcpy.GetCount_management(table)
        print "        "+(table) +", "+ str(tc) +" records"  
    print "Feature Classes"
    for fc in fcs:
        fcc = arcpy.GetCount_management(fc)
        indxs = arcpy.ListIndexes(fc)
        print"        "+(fc) +", "+ str(fcc)+" records"
        print "   INDEXES:"
        for index in indxs:
            print("              Name        : {0}".format(index.name))
            print("              IsUnique    : {0}".format(index.isUnique))
            
            
#check tolology             
def TopologyCheck():
    path = checkfile
    print path
    topo= path+"/"+fd+"/NG911_Topology"
    arcpy.ValidateTopology_management(topo)
    desc = arcpy.Describe(topo)
    print "%-27s %s" % ("ClusterTolerance:", desc.clusterTolerance)
    print "%-27s %s" % ("ZClusterTolerance:", desc.ZClusterTolerance)
    print "%-27s %s" % ("FeatureClassNames:", desc.featureClassNames)
    print "%-27s %s" % ("MaximumGeneratedErrorCount:", desc.maximumGeneratedErrorCount)

#basic geometry check for issues that would cause errors in loading to SIF
def GeometryCheck():

    outreport = checkfile+"/GeomCheck"
    arcpy.env.workspace = checkfile
    fcs = []
 
    # List all feature classes in feature datasets
    for fds in arcpy.ListDatasets():
        print fds
        fcs += arcpy.ListFeatureClasses("*","",fds)
        print fcs
    print "Running the check geometry tool on %i feature classes" % len(fcs)
    for fc in fcs:
        print fc
        outrep = outreport+fc
        arcpy.CheckGeometry_management(fc, outrep)   
        print (str(arcpy.GetCount_management(outrep)) + " geometry problems were found.")
        print ("See " + outrep + " for full details")

#not checking all the fields - just checking address points and road centerlines for duplicates on the Segment ID and Address ID that are supposed to be unique 
def Uniquity():
    rcl = ng911+r"/RoadCenterline"
    apt = ng911+r"/AddressPoints"
    arcpy.FindIdentical_management(rcl,checkfile+r"/RCLDup","SEGID","#","0","ONLY_DUPLICATES")
    arcpy.FindIdentical_management(apt,checkfile+r"/AddressPointsDup","ADDID","#","0","ONLY_DUPLICATES")
    #streets - segid
    #addresses - addid

#removes street centerlines from the topology and creates geometric network, then checks geometric network connectivity
def StreetNetworkCheck():
    print checkfile
    arcpy.env.workspace = checkfile
    print topo
    geonet = fd+"\Street_Network"
    #print geonet
    if arcpy.Exists(geonet):
        print "Street Geometric Network Already Exists"
    else:
        arcpy.RemoveFeatureClassFromTopology_management(topo, "RoadCenterline")
        arcpy.CreateGeometricNetwork_management (fd, "Street_Network", "RoadCenterline SIMPLE_EDGE NO", "#", "#", "#", "#", "#")
    arcpy.FindDisconnectedFeaturesInGeometricNetwork_management(fd+"/RoadCenterline", "Roads_Disconnected")
    StreetLogfile = reviewpath+"/KDOTReview/"+ntpath.basename(ng911)+".log"
    arcpy.VerifyAndRepairGeometricNetworkConnectivity_management(geonet, StreetLogfile, "VERIFY_ONLY", "EXHAUSTIVE_CHECK", "0, 0, 10000000, 10000000")
    
#creates an LRS network for the street centerlines, transfers the HPMS key field from the KDOT roads, then dissolves attributes to LRS events along the routes
def LRSify():
    arcpy.MakeFeatureLayer_management(checkfile+"/AuthoritativeBoundary","AuthoritativeBoundary_Layer","#","#","#")
    arcpy.MakeFeatureLayer_management(checkfile+"/CountyBoundary","CountyBoundary_Layer","#","#","#")
    arcpy.MakeFeatureLayer_management(KdotRd,"KDOT_Roads","#","#","#")
    arcpy.MakeFeatureLayer_management(checkfile+"/RoadCenterline","RoadCenterline","#","#","#")
    arcpy.SelectLayerByLocation_management("KDOT_Roads","HAVE_THEIR_CENTER_IN","AuthoritativeBoundary_Layer","50 Feet","NEW_SELECTION")
    arcpy.FeatureClassToFeatureClass_conversion("KDOT_Roads",checkfile+r"/NG911","KDOT_Roads_Review","#","#","#")
    arcpy.GenerateRubbersheetLinks_edit("KDOT_Roads_Review","RoadCenterline",checkfile+r"/NG911/RoadLinks","12 Feet","ROUTE_ID LRSKEY",checkfile+r"/RoadMatchTbl")
    arcpy.RubbersheetFeatures_edit("KDOT_Roads_Review","RoadLinks","RoadLinks_pnt","LINEAR")
    arcpy.DetectFeatureChanges_management("KDOT_Roads_Review","RoadCenterline",checkfile+r"/NG911/RoadDifference","50 Feet","#",checkfile+r"/RoadDifTbl","12 Feet","#")
    arcpy.MakeFeatureLayer_management(checkfile+"/RoadDifference","RoadDifference","#","#","#")
    arcpy.TransferAttributes_edit("KDOT_Roads_Review","RoadCenterline","YEAR_RECOR;ROUTE_ID","50 Feet","#",checkfile+r"/LRS_MATCH")
    arcpy.AddField_management(checkfile+"/RoadCenterline", "RouteName", "TEXT")
    arcpy.AddField_management(checkfile+"/RoadCenterline", "KDOT_ADMO", "TEXT")
    arcpy.AddField_management(checkfile+"/RoadCenterline", "PREDIR", "TEXT")
    arcpy.AddField_management(checkfile+"/RoadCenterline", "KDOT_COUNTY", "TEXT")
    arcpy.AddField_management(checkfile+"/RoadCenterline", "KDOT_URBAN", "TEXT")
    arcpy.AddField_management(checkfile+"/RoadCenterline", "Soundex", "TEXT")
    arcpy.AddField_management("RoadCenterline", "SuffCode", "TEXT")
    arcpy.AddField_management("RoadCenterline", "UniqueNo", "TEXT")
    arcpy.CalculateField_management("RoadCenterline","KDOT_COUNTY","!ROUTE_ID![:3]","PYTHON_9.3","#")
    arcpy.CalculateField_management("RoadCenterline","KDOT_ADMO","!ROUTE_ID![3]","PYTHON_9.3","#")
    arcpy.CalculateField_management("RoadCenterline","PREDIR","0","PYTHON_9.3","#")
    
    arcpy.MakeTableView_management(Kdotdbfp+"\NG911_RdDir", "NG911_RdDir")
    arcpy.CalculateField_management("RoadCenterline","PREDIR","0","PYTHON_9.3","#")
    arcpy.AddJoin_management("RoadCenterline","PRD","NG911_RdDir", "RoadDir", "KEEP_COMMON")
    arcpy.CalculateField_management("RoadCenterline","PREDIR","!NG911_RdDir.RdDirCode!","PYTHON_9.3","#")
    arcpy.RemoveJoin_management("RoadCenterline")
    
    arcpy.MakeTableView_management(Kdotdbfp+"\NG911_RdTypes", "NG911_RdTypes")
    arcpy.CalculateField_management("RoadCenterline","SuffCode","0","PYTHON_9.3","#")
    arcpy.AddJoin_management("RoadCenterline","STS","NG911_RdTypes", "RoadTypes", "KEEP_COMMON")
    arcpy.CalculateField_management("RoadCenterline","SuffCode","!NG911_RdTypes.LRS_CODE_TXT!","PYTHON_9.3","#")
    arcpy.RemoveJoin_management("RoadCenterline")    
    
    arcpy.MakeTableView_management(Kdotdbfp+"\NG911_County", "NG911_County")
    arcpy.AddJoin_management("RoadCenterline","COUNTY_R","NG911_County", "CountyName", "KEEP_COMMON")
    arcpy.CalculateField_management("RoadCenterline","KDOT_COUNTY","!NG911_County.CountyNumber!","PYTHON_9.3","#")
    arcpy.RemoveJoin_management("RoadCenterline") 
    
        
    arcpy.MakeTableView_management(Kdotdbfp+"\City_Limits", "City_Limits")
    arcpy.CalculateField_management("RoadCenterline","KDOT_URBAN","999","PYTHON_9.3","#")
    arcpy.AddJoin_management("RoadCenterline","MUNI_R","City_Limits", "CITY", "KEEP_COMMON")
    arcpy.CalculateField_management("RoadCenterline","KDOT_URBAN","!City_Limits.CITY_CD!.zfill(3)","PYTHON_9.3","#")
    arcpy.RemoveJoin_management("RoadCenterline")    
  
    #arcpy.AddJoin_management("CountyBoundary","COUNTY","NG911_County", "CountyName", "KEEP_COMMON")
    #from soundexpy import numdex
    arcpy.CalculateField_management("RoadCenterline","Soundex","numdex(!RD!)","PYTHON_9.3","#")
    arcpy.CalculateField_management("RoadCenterline","RouteName","str(!KDOT_COUNTY!)+str(!KDOT_URBAN!)+str(!PREDIR!) + !Soundex! + str(!SuffCode!)+!TRAVEL!","PYTHON_9.3","#")
    arcpy.MakeTableView_management(checkfile+"\RoadAlias", "RoadAlias")
    arcpy.AddJoin_management("RoadCenterline","SEGID","RoadAlias", "SEGID")
    arcpy.SelectLayerByAttribute_management("RoadCenterline", "NEW_SELECTION", "RoadAlias.LABEL LIKE 'US %' OR RoadAlias.LABEL LIKE 'I %' OR RoadAlias.LABEL LIKE 'K %'" )
    arcpy.RemoveJoin_management("RoadCenterline")    
    arcpy.CalculateField_management("RoadCenterline","RouteName","!ROUTE_ID![:11]","PYTHON_9.3","#")
    arcpy.SelectLayerByAttribute_management("RoadCenterline", "REMOVE_FROM_SELECTION", "TRAVEL is null" )
    arcpy.CalculateField_management("RoadCenterline","RouteName","!ROUTE_ID![:11]+!TRAVEL!","PYTHON_9.3","#")
    
    #arcpy.MakeFeatureLayer_management("RoadCenterline","RoadCenterline_StateHwy","KDOT_ADMO in ('I', 'U', 'K')","#","#")
    
def LRSIt():   
    
     
    pass
    
    #arcpy.CalculateField_management("RoadCenterline_StateHwy","RouteName","!ROUTE_ID![3]+!ROUTE_ID![6:11]","PYTHON_9.3","#")
    
    
 
if __name__ == '__main__':
    pass
    Inventory()
    TopologyCheck()
    GeometryCheck()
    Uniquity()
    StreetNetworkCheck()
    LRSify()
