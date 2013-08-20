'''
Created on Aug 20, 2013

@author: kyleg
'''

class MyClass(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
import arcpy

from ENV import ws, tempgdb, tempmdb

wsouttbl = ws+"\\"+tempgdb
wsindb = ws+"\\"+tempmdb

fldName = 'IAL_DOMAIN'
fcName = wsindb+"\NM3_NM_INV_ATTRI_LOOKUP_ALL"
arcpy.TableToGeodatabase_conversion("Database Connections\ATLASPROD.odc\NM3.NM_INV_ATTRI_LOOKUP_ALL", wsindb) #change the DBConnection to use ENV class variable
print wsouttbl
myList = set([row.getValue(fldName) for row in arcpy.SearchCursor(fcName, fields=fldName)]) 
print myList

for attrib in myList:
    #[IAL_DOMAIN] = 'STRAHNET' AND [IAL_END_DATE] IS NULL
    sels = "["+fldName+"] = '"+ attrib+"' AND [IAL_END_DATE] IS NULL"
    outname = attrib.replace(" ", "_")
    outname = outname.replace("-", "_")
    print outname
    print '"""'+fldName+'"'+" = '"+ attrib+"'"+'""'
    arcpy.TableToTable_conversion(fcName,wsindb,outname,sels)
    arcpy.TableToDomain_management(wsindb+"/"+outname,"IAL_VALUE","IAL_MEANING",wsouttbl, outname, attrib, "REPLACE")
print "All Cansys Domains copied to temp mdb as coded text values"        