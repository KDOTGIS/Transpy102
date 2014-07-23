'''
Created on Jul 23, 2014

@author: kyleg
'''
import arcpy, os, ntpath
from config import wspath, reviewpath

#set the workspace from the config file
arcpy.env.workspace = wspath
gdb = arcpy.ListWorkspaces('*.gdb')

ng911 = gdb[0]
arcpy.env.workspace = ng911
datasets = arcpy.ListDatasets()
fd = datasets[0]

def Compact():
    arcpy.Compact_management(ng911)
    
def Inventory():
    print "Geodatabase Name"
    for db in gdb:
        print db
    print "Feature Dataset Name"
    for ds in datasets:
        print "     "+ds
    
    tables = arcpy.ListTables()
    print "Tables"
    for table in tables:
        tc = arcpy.GetCount_management(table)
        print "        "+(table) +", "+ str(tc) +" records"
    arcpy.env.workspace = fd
    fcs = arcpy.ListFeatureClasses()
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
    path = wspath+"/"+ng911+"/"+fd
    print path
    desc = arcpy.Describe(fd+"/NG911_Topology")
    print "%-27s %s" % ("ClusterTolerance:", desc.clusterTolerance)
    print "%-27s %s" % ("ZClusterTolerance:", desc.ZClusterTolerance)
    print "%-27s %s" % ("FeatureClassNames:", desc.featureClassNames)
    print "%-27s %s" % ("MaximumGeneratedErrorCount:", desc.maximumGeneratedErrorCount)

def GeometryCheck():
    dbin = ng911
    outfile = reviewpath+"/"+ntpath.basename(ng911)
    print dbin
    print outfile
    if arcpy.Exists(outfile):
        print "file already exists"
        pass
    else:
        arcpy.Copy_management(dbin, outfile)
    
    


if __name__ == '__main__':
    pass
#Compact()
#Inventory()
#TopologyCheck()
GeometryCheck()