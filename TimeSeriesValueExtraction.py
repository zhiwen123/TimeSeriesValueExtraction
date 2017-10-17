"""
    Author: Zhiwen Zhu
    Date: March 6, 2017
    Decription: This script automates the process of extracting attribute values
                from time series data to point feature class
"""

import arcpy
import numpy as np
import matplotlib.pyplot as plt
import webbrowser
import datetime
import calendar
import os

def extractTimeSeriesValue(featureClass,rasterFolder,namingConv,dateField,newField,aggreLevel):
    fields = [dateField,"SHAPE@XY",newField]

    if newField not in arcpy.ListFields(featureClass):
        arcpy.AddField_management(featureClass,newField,"FLOAT")

    cursor = arcpy.da.UpdateCursor(featureClass, fields)

    #get the number of features, to calculate the process percentage later
    result = arcpy.GetCount_management(featureClass) 
    count = int(result.getOutput(0))
    step = count / 100.0 #determine the step for updating progress
    perc = 0 #current process percentage
    nextStep = 0 #the next step to update progress
    
    index = 0
    rasterFile = ""
    noDataCnt = 0
    valList = [] #this list will store the extracted values and be returned
    
    for record in cursor:
        #filename = parseFileName(record[0],namingConv)
        #filePath = rasterFolder+filename
        isNoData, val = extractPixelValue(rasterFolder,namingConv,record[0],record[1][0],record[1][1],aggreLevel)
        #val = arcpy.GetCellValue_management(filePath,record[1][0] + " " + record[1][1],"1")
        record[2] = val
        if isNoData == True:
            noDataCnt += 1
        else:
            valList.append(record[2])
    
        #update tmin value in current record         
        cursor.updateRow(record)

        if step >= 1.0:
            if index == nextStep: #update in every 1 percent
                arcpy.AddMessage("Extraction is processing: "  + str(perc) + "%")
                #print "Extraction is processing: " + str(perc) + "%"
                perc += 1
                nextStep = int(step * perc)
        else:
            #update in every increment of index
            perc = index * 100 / count
            arcpy.AddMessage("Extraction is processing: "  + str(perc) + "%")
            
        index +=1
        #print index
    arcpy.AddMessage("Extraction is processing: "  + str(100) + "%") #100 percent process finished
    
    return valList,noDataCnt

def extractPixelValue(rasterFolder,namingConv,date,x,y,aggreLevel):
    aggreLevel = aggreLevel.lower()
    res = 0.0
    cnt = 0 #valid number of days
    
    #the default aggregate level is daily
    beginDate = date
    endDate = date
    if aggreLevel == "monthly":
        beginDate = date.replace(day=1)
        numberDays = calendar.monthrange(date.year, date.month)[1] #the number of days in that month
        endDate = date.replace(day=numberDays)
    elif aggreLevel == "yearly":
        begindDate = date.replace(month=1,day=31)
        endDate = date.replace(month=12,day=31)
        
    while beginDate <= endDate:
        filename = parseFileName(beginDate,namingConv)
        filePath = rasterFolder+filename
        val = arcpy.GetCellValue_management(filePath,str(x) + " " + str(y),"1")
        if val.getOutput(0) == 'NoData':
            raster = arcpy.Raster(filePath)
            return True, raster.noDataValue #there is no data for the pixel location, then there is no need to continue search for other dates
        res += float(val.getOutput(0))
        cnt += 1
        beginDate += datetime.timedelta(days=1)
    if cnt != 0:
        res /= cnt
    return False, res

def parseFileName(date,namingConv):
    fileName = namingConv.lower()
    #check whether it is "Day" naming convetion or "Date" convention
    if fileName.find("%yearday%") != -1: #Day naming convention.
        #"yearday" means which day of the year, such as 1,2,...365
        yearday = date.timetuple().tm_yday 
        fileName = fileName.replace("%yearday%",str(yearday))
        fileName = fileName.replace("%year%",str(date.year))
    else:
        #"day" means which day of the month, such as 1, 2, 3,...31
        fileName = fileName.replace("%day%",str(date.day)) 
        fileName = fileName.replace("%month%",str(date.month))
        fileName = fileName.replace("%year%",str(date.year))
    return fileName    

# show the histo
def hist(valList,folder):
    arcpy.AddMessage("Generating histogram...")
    bins=np.arange(260,310,2)
    plt.xlim([min(valList)-2,max(valList)+2])
    plt.hist(valList,bins=bins,alpha=0.5)
    plt.xlabel('Pixel Value')
    plt.ylabel('Count')
    plt.title("Histogram")
    savePath = folder + "\\" + "histogram.png"
    plt.savefig(savePath,dpi=100)
    os.system("start " + savePath)


# generate the html report
def genhtml(valList,noDataCnt,folder):
    arcpy.AddMessage("Generating report...")
    genhtml = folder + "\\" + "Report.html"
    f = open(genhtml,'w')
    message = """
    <html>
    <head></head>
    <body>
    <p>Time Series Value Extraction Report</p>
    <p>*************************************</p>
    <p>Statistics</p>
    <p>*************************************</p>
    <p>Min value: %s</p>
    <p>Max value: %s</p>
    <p>Mean value: %s</p>
    <p>totalRecord: %s</p>
    <p>noDataRecord: %s</p>
    </body>
    </html>"""%(str(min(valList)),str(max(valList)),str(sum(valList)/(len(valList)+1)),str(len(valList)),str(noDataCnt))
    f.write(message)
    f.close()
    return webbrowser.open(genhtml,new = 1)

def creatMap(blankMxdPath, shapefilePath,symbolLayer,PDFMapPath):
    arcpy.AddMessage("Creating map...")
    #map document
    mxd = arcpy.mapping.MapDocument(blankMxdPath)
    
    #save a copy of the blank MXD to work from
    testingMxd = os.path.dirname(blankMxdPath) + "\\" + "final_map.mxd"
    mxd.saveACopy(testingMxd)
    #print mxd.filePath
    #set the workspacearcpy.env.workspace = (r'W:\Commons\Leta_Yiwen_Zhiwen')
    #if the file already exists, overwrite it
    arcpy.env.overwriteOutput = True
    #delete blank mxd named
    del mxd
    #print "1"

    #the block of code is for inserting the shape file created for visual display
    mxd = arcpy.mapping.MapDocument(testingMxd)
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    lyr_file = shapefilePath # add the shapefile to the map document
    newLayer = arcpy.mapping.Layer(lyr_file)
    arcpy.mapping.AddLayer(df, newLayer, "TOP") #insert the new file at the top of the data frame

    #copy symbology from a source layer to the new shapefile
    updateLayer = arcpy.mapping.ListLayers(mxd, newLayer, df)[0]
    sourceLayer = arcpy.mapping.Layer(symbolLayer)
    arcpy.mapping.UpdateLayer(df, updateLayer, sourceLayer, True)
    
    #insert new shapefile in the legend
    legend = arcpy.mapping.ListLayoutElements(mxd,"LEGEND_ELEMENT")[0]
    for lyr in legend.listLegendItemLayers():
        legend.updateItem(lyr)

    #project the new layer file
    input_feature = newLayer
    output_feature = os.path.splitext(shapefilePath)[0] + "_projected.shp"
    out_coordinate_system = arcpy.SpatialReference('NAD 1983 UTM Zone 10N')
    arcpy.Project_management(input_feature, output_feature, out_coordinate_system)

    #get extent of new Layer and zoom to that layer
    ext = updateLayer.getExtent()
    df.extent = ext
    
    #changing the text of the title
    for elm in arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT"):
        if elm.text == "title":
            elm.text = "Wildfire Ignition Points in Southern California"
    
    #Move north arrow
    for north in arcpy.mapping.ListLayoutElements(mxd,'MAPSURROUND_ELEMENT'):
        if north.name == 'North Arrow':
            north.elementPositionX = 7.5
            north.elementPositionY = 0.5

    #refresh and update
    arcpy.RefreshTOC()
    arcpy.RefreshActiveView()

    #save a copy of the completed map as mxd
    mxd.save()

    #export as PDF
    arcpy.mapping.ExportToPDF(mxd,PDFMapPath)

    #open PDF map
    os.system("start " + PDFMapPath)

if __name__ == "__main__":
    #input parameters. These parameters could be customized in the user interface
    featureClass = arcpy.GetParameterAsText(0)
    rasterFolder = arcpy.GetParameterAsText(1) + "\\"
    PDFMapPath = arcpy.GetParameterAsText(2)
    dateField = arcpy.GetParameterAsText(3)
    namingConv = arcpy.GetParameterAsText(4)
    newField = arcpy.GetParameterAsText(5)
    aggregateLevel = arcpy.GetParameterAsText(6) #this could be "daily", "monthly", "yearly"
    
    #default blank mxd Path,used to create PDF map
    blankMxdPath = r"\Data\MXD\blank.mxd"
    #default symbology layer,used to update symbology for new layers
    symbolLayer = r"\Data\layerSymbology.lyr" 

    featurefolder = os.path.dirname(featureClass)
    arcpy.AddMessage("Start extraction: ")
    valList,noDataCnt = extractTimeSeriesValue(featureClass,rasterFolder,namingConv,dateField,newField,aggregateLevel)
    creatMap(blankMxdPath, featureClass, symbolLayer, PDFMapPath)
    genhtml(valList,noDataCnt,featurefolder)
    hist(valList,featurefolder)
