'''
Created on Oct 7, 2013

@author: kyleg
'''

from arcpy import Exists, CreatePersonalGDB_management, CreateFileGDB_management, Delete_management, env
from CONFIG import ws, tempmdb, tempgdb

mdb91 = ws+"//"+tempmdb
print mdb91
if Exists(mdb91):
    Delete_management(mdb91)
CreatePersonalGDB_management(ws,tempmdb,"9.1")   

gdb102 = ws+"//"+tempgdb
if Exists(gdb102):
    Delete_management(gdb102)
CreateFileGDB_management(ws,tempgdb)    
env.workspace = ws+"/"+tempgdb