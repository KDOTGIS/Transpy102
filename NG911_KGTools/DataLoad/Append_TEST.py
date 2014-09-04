'''
Created on Aug 25, 2014
Use to delete and compress the databases
@author: kyleg
'''
#source = r'//gisdata/arcgis/GISdata/DASC/NG911/KDOTReview/RSDigital_PR_NG911.gdb/'  #Pratt County  - Final QC/Approved
source = r'\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview\RSDigital_SF_NG911.gdb/' #Stafford County - Final QC Approved
#source = r'\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview\RSDigital_KW_NG911.gdb/' #Kiowa county - Final QC Approved
#source = r'\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview\RSDigital_GT_NG911.gdb/' #Grant County - Final QC Approved
#source = r'\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview\RSDigital_SV_NG911.gdb/' #Stevens County - Final QC Approved
#source = r'\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview\KSNG911S_PN.gdb/'

fd = 'NG911/'

final = r'Database Connections\SQL61_NG911_Final_QC.sde\NG911_TEST.FINAL.'
shared = r'Database Connections\SQL61_NG911_Shared_QC.sde\NG911_TEST.SHARED.'
temp = r'Database Connections\SQL61_NG911_TEST.sde\NG911_TEST.TEST.Kansas'

fd2 = 'NG911'

#Steward to Delete
deletesteward = "485054"
#deletesteward = "null"
from arcpy import Exists, Compress_management, Delete_management, FeatureClassToFeatureClass_conversion, Append_management, MakeFeatureLayer_management, DeleteRows_management, MakeTableView_management

KSdb_fc_list = ['RoadCenterline','AddressPoints','AuthoritativeBoundary', 'CountyBoundary', 'EMS', 'ESZ','FIRE','LAW','MunicipalBoundary','PSAP']
KSdb_Tbl_list = ['RoadAlias']

def SchemaChange():
    pass            

def AppendIt():
    for fc in KSdb_fc_list:
        fcappendfrom = source +fd+r'/'+ fc
        fcappendto = final+fd2 +r'/' + fc
        tempfc = temp+r'/'+fc
        if Exists(tempfc):
            Delete_management(tempfc)
        else:
            pass
        FeatureClassToFeatureClass_conversion(fcappendfrom, temp, fc)
        Append_management(tempfc,fcappendto,"NO_TEST","#","#") 

        print "appended "+ str(fc)
    
    for tbl in KSdb_Tbl_list:
        tblappendfrom = source +r'/'+ tbl
        tblappendto = final + tbl
        Append_management(tblappendfrom,tblappendto,"NO_TEST","#","#") 
        print "appended "+ str(tbl)
        
def DeleteIt():
    for fc in KSdb_fc_list:
        print "deleting "+str(fc)+" for rows with steward = "+ deletesteward
        deletefrom = final+fd2 +r'/' + fc
        lyrname = fc+"del"
        selection = "STEWARD = "+deletesteward +"OR STEWARD IS NULL"
        MakeFeatureLayer_management(deletefrom, lyrname, selection)
        DeleteRows_management(lyrname)
        del lyrname
    
    for tbl in KSdb_Tbl_list:
        print "deleting "+str(tbl)+" for rows with steward = "+ deletesteward
        deletefrom = final + tbl
        selection = "STEWARD = "+deletesteward +"OR STEWARD IS NULL"
        lyrname = tbl+"del"
        MakeTableView_management(deletefrom, lyrname, selection)
        DeleteRows_management(lyrname)
        
def compress():
    Compress_management(r'Database Connections\SQL61_NG911_Final_QC.sde')
  
    
if __name__ == '__main__':
    pass
    DeleteIt()
    AppendIt()
    compress()
