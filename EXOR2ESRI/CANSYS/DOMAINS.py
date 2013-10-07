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
from arcpy import TableToGeodatabase_conversion,SearchCursor, TableToTable_conversion, TableToDomain_management

from CONFIG import ws, tempgdb, tempmdb

wsouttbl = ws+"\\"+tempgdb
wsindb = ws+"\\"+tempmdb

fldName = 'IAL_DOMAIN'
fcName = wsindb+"\NM3_NM_INV_ATTRI_LOOKUP_ALL"
TableToGeodatabase_conversion("Database Connections\ATLASPROD.odc\NM3.NM_INV_ATTRI_LOOKUP_ALL", wsindb) #change the DBConnection to use ENV class variable
print wsouttbl
myList = set([row.getValue(fldName) for row in SearchCursor(fcName, fields=fldName)]) 
print myList

for attrib in myList:
    #[IAL_DOMAIN] = 'STRAHNET' AND [IAL_END_DATE] IS NULL
    sels = "["+fldName+"] = '"+ attrib+"' AND [IAL_END_DATE] IS NULL"
    outname = attrib.replace(" ", "_")
    outname = outname.replace("-", "_")
    print outname
    print '"""'+fldName+'"'+" = '"+ attrib+"'"+'""'
    TableToTable_conversion(fcName,wsindb,outname,sels)
    TableToDomain_management(wsindb+"/"+outname,"IAL_VALUE","IAL_MEANING",wsouttbl, outname, attrib, "REPLACE")
print "All Cansys Domains copied to temp mdb as coded text values"        