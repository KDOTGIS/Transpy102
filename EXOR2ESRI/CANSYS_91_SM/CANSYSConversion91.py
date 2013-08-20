'''
this script has to run in an ArcGIS 9.1 computer with older version of python and pywin
@kyle g


"""********************************************************************************************************************
FeatureClassConversion.py converted to work on a hard coded list of layers

Description: Converts or copies one or more feature classes to a GeoDatabase or folder.
The input feature classes can be shapefiles, coverage feature classes, VPF Coverage feature classes, or
Geodatabase featureclasses. Depending on which tool is calling this script, the output parameter will be a
SDE or a personal Geodatabase which means the output will be geodatabase feature classes, the output parameter
will be a folder, which means the output will be shapefiles.

The name of the output feature classes will be based on the name of the input feature class name.
If the input feature class is contained in a dataset (ie. feature dataset, coverage, CAD Dataset)
the name of the output feature class will be based on the name of the input feature class and the
dataset it contains (ie. input: covname/arc, output: covname_arc)

Requirements: The first argument must be a semi-colon seperated list of feature classes. The second argument
must be an existing output path like a folder, geodatabase, or feature dataset.

Python and the Python for Windows extention (win32 Extension) to be installed.

Author: ESRI, Redlands

Date: 11/18/2003
Updated: 6/02/2005 (use gp.GetParameterAsText as opposed to sys.argv)

Usage: FeatureClassToGeodatabase <in_feature_class;in_feature_class...> <out_workspace>
Usage: FeatureClassToShapefile <in_feature_class;in_feature_class...> <out_folder>
*********************************************************************************************************************"""
'''
import ConversionUtils, sys, os, time, win32com.client

#Define message constants so they may be translated easily
msgErrorTooFewParams = "Insufficient number of parameters provided"
msgErrorInvalidOutPath = "Output path does not exist"
msgErrorInvalidInput = " Input does not exist"
msgSuccess = "successfully converted to "
msgFailed = "Failed to convert"
now = time.localtime(time.time())
tempmdb = "CANSYSNet"+str(now[0])+"_"+str(now[1])+"_"+str(now[2])+".mdb"

try:

    # Argument 1 is the list of feature classes to be converted
    inFeatureClasses = ConversionUtils.gp.GetParameterAsText(0)

    # The list is split by semicolons ";"
    inFeatureClasses = ConversionUtils.SplitMultiInputs(inFeatureClasses)

    # The output workspace where the shapefiles are created
    outWorkspace = r"//GISDATA/arcgis/gisdata/KDOT/btp/CANSYSTEST/"+tempmdb
    #ConversionUtils.gp.GetParameterAsText(1)

    # Set the destination workspace parameter (which is the same value as the output workspace)
    # the purpose of this parameter is to allow connectivity in Model Builder.
    # ConversionUtils.gp.SetParameterAsText(outWorkspace)

    # Error trapping, in case the output workspace doesn't exist
    if not ConversionUtils.gp.Exists(outWorkspace):
        raise Exception, "%s: %s" % (msgErrorInvalidOutPath, outWorkspace)

    # Loop through the list of input feature classes and convert/copy each to the output geodatabase or folder
    for inFeatureClass in inFeatureClasses:
        try:
            # To start, make sure the input exists
            if not ConversionUtils.gp.Exists(inFeatureClass):
                raise Exception, msgErrorInvalidInput

            # Generate a valid output output name
            outFeatureClass = ConversionUtils.GenerateOutputName(inFeatureClass, outWorkspace)

            # Copy/Convert the inFeatureClasses to the outFeatureClasses
            ConversionUtils.CopyFeatures(inFeatureClass, outFeatureClass)

            # If the Copy/Convert was successfull add a message stating this
            ConversionUtils.gp.AddMessage("%s %s %s" % (inFeatureClass, msgSuccess, outFeatureClass))

        except Exception, ErrorDesc:
            # Except block for the loop. If the tool fails to convert one of the feature classes, it will come into this block
            #  and add warnings to the messages, then proceed to attempt to convert the next input feature class.
            WarningDesc = ("%s %s" % (msgFailed, inFeatureClass))

            if ConversionUtils.gp.GetMessages(2) != "":
                WarningDesc = WarningDesc + ". " + (ConversionUtils.gp.GetMessages(2))
            elif ErrorDesc != "":
                WarningDesc = WarningDesc + ". " + (str(ErrorDesc))

            # Add a warning that the fc did not convert
            ConversionUtils.gp.AddWarning(WarningDesc)
            print WarningDesc

except Exception, ErrorDesc:
    # Except block if the tool could not run at all.
    #  For example, not all parameters are provided, or if the output path doesn't exist.
    ConversionUtils.gp.AddError(str(ErrorDesc))
    print str(ErrorDesc)