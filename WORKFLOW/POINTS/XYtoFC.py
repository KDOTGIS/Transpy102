'''
Created on Aug 21, 2013

@author: kyleg
'''

if __name__ == '__main__':
    pass
import arcpy, datetime, os, shutil
#mxd = arcpy.mapping.MapDocument(r'\\gisdata\arcgis\GISdata\MXD\CIIMS_PROCESS_DEV.mxd')
now = datetime.datetime.now()
apd = os.getenv('APPDATA')
conns = r'\\gisdata\arcgis\GISdata\Layers\connection_files'
ArcVersion = '10.2'
DCL = apd + r'\\ESRI\\Desktop'+ArcVersion+'\\ArcCatalog'

def XYFC(source, dst, Lat, Long, GCS, loaded):
    if arcpy.Exists("FCtbl"):
        arcpy.Delete_management("FCtbl")
    else:    
        pass
    if arcpy.Exists("FC_Layer"):
        arcpy.Delete_management("FC_Layer")
    else:
        pass
    print "start XYFC "+ str(datetime.datetime.now())
    arcpy.MakeTableView_management(source, 'FCtbl', "#", "#", "")
    arcpy.MakeXYEventLayer_management("FCtbl",Long, Lat,"FC_Layer", GCS,"#")
    arcpy.DeleteFeatures_management(dst)
    arcpy.Append_management("FC_Layer",dst,"NO_TEST","#","#")
    arcpy.CalculateField_management(dst, loaded,"datetime.datetime.now( )","PYTHON_9.3","#")
    print "XYFC complete for " +str(dst)+ " at " + str(datetime.datetime.now())


class CIIMSDev(object):
    srcdb =r'sdedev_ciims.sde'
    if arcpy.Exists(r'Database Connections/'+srcdb):
        pass 
    else:
        shutil.copy(conns+"/"+srcdb, DCL+"/"+srcdb)
    srcschema = 'CIIMS'
    srctbl ='CIIMS_VWCROSSINGGIS3'
    source = r'Database Connections/'+srcdb +'/'+srcschema+'.'+srctbl
    Lat = "CROSSINGLATITUDE"
    Long = "CROSSINGLONGITUDE"
    loaded = "LOADDATE"
    dstdb = r'sdedev_ciims.sde'
    if arcpy.Exists(r'Database Connections/'+dstdb):
        pass
    else:
        shutil.copy(conns+"/"+dstdb, DCL+"/"+dstdb)
    dstschema = 'CIIMS'
    dstfd = 'CIIMS'
    dstfc = 'Static_Crossings'
    dst = r'Database Connections/'+dstdb+'/'+dstschema+'.'+dstfd+'/'+dstschema+'.'+dstfc
      
    GCS = "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision"
    XYFC(source, dst, Lat, Long, GCS, loaded)

class ACCESSPERMDev(object):
    print "access permit points: GO "+ str(datetime.datetime.now())
    srcdb =r'ATLASPROD.odc'
    if arcpy.Exists(r'Database Connections/'+srcdb):
        print srcdb +" exists"
        pass 
    else:
        shutil.copy(conns+"/"+srcdb, DCL+"/"+srcdb)
        pass
    srcschema = 'KDOT'
    srctbl ='KGATE_ACCESSPOINTS_TEST'
    source = r'Database Connections/'+srcdb +'/'+srcschema+'.'+srctbl
    print source
    Lat = "GPS_LATITUDE"
    Long = "GPS_LONGITUDE"
    loaded = "LOAD_DATE"
    dstdb = 'GISTEST.sde'
    if arcpy.Exists(r'Database Connections/'+dstdb):
        print dstdb +" exists"
        pass
    else:
        shutil.copy(conns+"/"+dstdb, DCL+"/"+dstdb)
    dstschema = 'SHARED'
    dstfc = 'ACCESS_POINTS'
    dst = r'Database Connections/'+dstdb+'/'+dstschema+'.'+dstfc
    print source
    print dst
      
    GCS = "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision"
    XYFC(source, dst, Lat, Long, GCS, loaded)

