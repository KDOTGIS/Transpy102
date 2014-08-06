'''
Created on Jul 23, 2014

@author: kyleg
'''
import ntpath
import arcpy
from config import wspath, reviewpath, KdotRd

#set the workspace from the config file
arcpy.env.workspace = wspath
arcpy.env.overwriteOutput=1
gdb = arcpy.ListWorkspaces('*.gdb')

ng911 = gdb[0]
arcpy.env.workspace = ng911
datasets = arcpy.ListDatasets()
tables = arcpy.ListTables()
fd = datasets[0]
fcs = arcpy.ListFeatureClasses()
checkfile = reviewpath+"/"+ntpath.basename(ng911)

topo= fd+"/NG911_Topology"

def Compact():
    arcpy.Compact_management(ng911)
    
def Inventory():
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
    arcpy.env.workspace = fd
    
    print "Feature Classes"
    for fc in fcs:
        fcc = arcpy.GetCount_management(fc)
        indxs = arcpy.ListIndexes(fc)
        print"        "+(fc) +", "+ str(fcc)+" records"
        print "   INDEXES:"
        for index in indxs:
            print("              Name        : {0}".format(index.name))
            print("              IsUnique    : {0}".format(index.isUnique))
            
def TopologyCheck():
    path = ng911+"/"+fd
    print path
    #\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Kiowa_county\RSDigital_KW_NG911.gdb\NG911\NG911_Topology
    #\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Stafford_county/\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Stafford_county\RSDigital_SF_NG911.gdb/NG911/NG911_Topology
    topo= path+"/NG911_Topology"
    arcpy.ValidateTopology_management(topo)
    desc = arcpy.Describe(topo)
    print "%-27s %s" % ("ClusterTolerance:", desc.clusterTolerance)
    print "%-27s %s" % ("ZClusterTolerance:", desc.ZClusterTolerance)
    print "%-27s %s" % ("FeatureClassNames:", desc.featureClassNames)
    print "%-27s %s" % ("MaximumGeneratedErrorCount:", desc.maximumGeneratedErrorCount)

def GeometryCheck():
    dbin = ng911
    checkfile = reviewpath+"/"+ntpath.basename(ng911)
    print dbin
    print checkfile
    if arcpy.Exists(checkfile):
        print "file already exists"
        pass
    else:
        arcpy.Copy_management(dbin, checkfile)
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

def Uniquity():
    rcl = ng911+r"/RoadCenterline"
    apt = ng911+r"/AddressPoints"
    arcpy.FindIdentical_management(rcl,checkfile+r"/RCLDup","SEGID","#","0","ONLY_DUPLICATES")
    arcpy.FindIdentical_management(apt,checkfile+r"/AddressPointsDup","ADDID","#","0","ONLY_DUPLICATES")
    #streets - segid
    #addresses - addid

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
    
def LRSify():
    arcpy.MakeFeatureLayer_management(checkfile+"/AuthoritativeBoundary","AuthoritativeBoundary_Layer","#","#","#")
    arcpy.MakeFeatureLayer_management(KdotRd,"KDOT_Roads","#","#","#")
    arcpy.SelectLayerByLocation_management("KDOT_Roads","HAVE_THEIR_CENTER_IN","AuthoritativeBoundary_Layer","50 Feet","NEW_SELECTION")
    arcpy.FeatureClassToFeatureClass_conversion("KDOT_Roads",checkfile+r"/NG911","KDOT_Roads_Review","#","#","#")
    arcpy.DetectFeatureChanges_management("KDOT_Roads_Review","RoadCenterline",checkfile+r"/NG911/RoadDifference","50 Feet","#",checkfile+r"/RoadDifTbl","15 Feet","#")
    arcpy.GenerateRubbersheetLinks_edit("KDOT_Roads_Review","RoadCenterline",checkfile+r"/NG911/RoadLinks","10 Feet","ROUTE_ID LRSKEY",checkfile+r"/RoadMatchTbl")
    arcpy.RubbersheetFeatures_edit("KDOT_Roads_Review","RoadLinks","RoadLinks_pnt","LINEAR")
    arcpy.TransferAttributes_edit("KDOT_Roads_Review","RoadCenterline","YEAR_RECOR;ROUTE_ID","50 Feet","#",checkfile+r"/LRS_MATCH")
 
if __name__ == '__main__':
    pass
Compact()
Inventory()
TopologyCheck()
GeometryCheck()
Uniquity()
StreetNetworkCheck()
LRSify()
