'''
Created on Aug 25, 2014

@author: kyleg
'''
#source = r'//gisdata/arcgis/GISdata/DASC/NG911/KDOTReview/RSDigital_PR_NG911.gdb/'  #Pratt County  - Final QC/Approved
source = r'\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview\RSDigital_SF_NG911.gdb/' #Stafford County - Final QC Approved
fd = 'NG911/'

final = r'Database Connections\SQL61_NG911_Final_QC.sde\NG911_TEST.FINAL.'
fd2 = 'NG911'

#Steward to Delete
deletesteward = "485039"


import arcpy

KSdb_fc_list = ['AddressPoints','AuthoritativeBoundary', 'CountyBoundary', 'EMS', 'ESZ','FIRE','LAW','MunicipalBoundary','PSAP','RoadCenterline']
KSdb_Tbl_list = ['RoadAlias']


def AppendIt():
    for fc in KSdb_fc_list:
        fcappendfrom = source +fd+r'/'+ fc
        fcappendto = final+fd2 +r'/' + fc
        arcpy.Append_management(fcappendfrom,fcappendto,"NO_TEST","#","#") 
        print "appended "+ str(fc)
    
    for tbl in KSdb_Tbl_list:
        tblappendfrom = source +r'/'+ tbl
        tblappendto = final + tbl
        arcpy.Append_management(tblappendfrom,tblappendto,"NO_TEST","#","#") 
        print "appended "+ str(tbl)
        
def DeleteIt():
    for fc in KSdb_fc_list:
        print "deleting "+str(fc)+" for rows with steward = "+ deletesteward
        deletefrom = final+fd2 +r'/' + fc
        lyrname = fc+"del"
        selection = "STEWARD = "+deletesteward
        arcpy.MakeFeatureLayer_management(deletefrom, lyrname, selection)
        arcpy.DeleteRows_management(lyrname)
        
    
if __name__ == '__main__':
    pass
    DeleteIt()
    #AppendIt()
