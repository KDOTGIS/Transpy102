'''
Created on Nov 5, 2013

@author: kyleg
'''

class ADMO(object):
    '''
    classdocs
    '''

    
    def __init__(self):
        '''
        Constructor
        '''
    from arcpy import DissolveRouteEvents_lr, AssignDomainToField_management, MakeTableView_management

    MakeTableView_management("ACCS_ln_1","ACCS_ln_1_PD","NE_OWNER in ( 'EB' , 'NB' )","#","#")
    DissolveRouteEvents_lr("ACCS_ln_1_PD","LRS_KEY LINE Beg_Cnty_Logmile End_Cnty_Logmile","IIT_START_DATE;ACS_CTRL_ID","//gisdata/arcgis/GISdata/KDOT/BTP/CANSYSTEST/CANSYSNet2013_10_7.gdb/ACCS_ln_1D","LRS_KEY LINE Beg_Cnty_Logmile End_Cnty_Logmile","CONCATENATE","INDEX")
    AssignDomainToField_management("ACCS_ln_1D","ACS_CTRL_ID","AC_ACS_CTRL_ID","#")
    