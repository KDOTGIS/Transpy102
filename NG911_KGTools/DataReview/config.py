'''
Created on Jul 23, 2014

@author: kyleg
'''



wspath = r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Stafford_county\QA_Corrections" #2nd review - final

#r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Pratt_county\QA_Corrections" #final review




#r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_II\RS_Grant_county"
#r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_II\RS_Stevens_county"  #first review
#r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Pratt_county"  #first review
#r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Kiowa_county"  #first review
#r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Stafford_county"  #first review
reviewpath = r"\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview"

kdotdb = 'KDOT_Roads.gdb'

Kdotdbfp = reviewpath+'/'+kdotdb

KdotRd = Kdotdbfp+"/HPMS2013"