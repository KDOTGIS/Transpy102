'''
Created on Jul 23, 2014

@author: kyleg
'''
#wspath=r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\ATCi\Larned Police Department Geodatabase\Final QA Pawnee County"
#wspath= r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\ATCi\Larned Police Department Geodatabase\Final QA Pawnee County"
#wspath= r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_II\RS_Stevens_county\QA_Corrections"# - 2nd review
#wspath= r"\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_II\RS_Grant_county\QA_Corrections"
#wspath=r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Kiowa_county\QA_Corrections" #2nd review - final
#wspath=r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Kiowa_county"  #first rreviewnd 
wspath=r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Stafford_county\QA_Corrections" #2nd review - final
#wspath=r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Pratt_county\QA_Corrections" #final review
#wspath=r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_II\RS_Grant_county"
#wspath=r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_II\RS_Stevens_county"  #first review
#wspath=r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Pratt_county"  #first review
#wspath=r"\\gisdata\arcgis\GISdata\DASC\NG911\DataRemediation_NG911\RSDigital\Region_I\RS_Stafford_county"  #first review


reviewpath = r"\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview"

kdotdb = 'KDOT_Roads.gdb'

Kdotdbfp = reviewpath+'/'+kdotdb

KdotRd = Kdotdbfp+"/HPMS2013"

final = r'Database Connections\SQL61_NG911_Final_QC.sde\NG911_TEST.FINAL.'