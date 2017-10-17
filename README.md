# TimeSeriesValueExtraction
Descprition: 
The tool is developed by Leta Spencer, Yiwen Hu & Zhiwen Zhu for extracting and aggregating 
cell values from time series data based on location and time of points. This tool also generates 
a map to show the extracted values and a report to show the statistics and histogram of the 
extracted values. currently the tool can only support raster data of single band. Each raster 
data reprents a variable at a certain date. Also, it is required that the raster data and point 
shapefile have the same projection. If they have different projections, please reproject the 
data to make sure they have the same projection. The tool only supports ArcGIS 10.4 or higher version. 

Instructions: 
In order to make the tool work, please follow the instruction below:

(1) Open the "TimeSeriesValueExtraction.py" with IDLE, PythonWin or text editor.

(2) In the opend python script, go to line 228 and 230, modify the bankMxdPath and 
    symbolLayer to their absolute paths. The "bankMxdPath" points to the path of 
    a blank map document created beforehand, which will be used to create a PDF map. 
    The bank map document is saved in the folder "4_Leta_Yiwen_Zhiwen\Data\MXD\blank.mxd". 
    The "symbolLayer" is a layer used to customize the symbols for the output PDF map. 
    The "symbolLayer" is saved in the folder "4_Leta_Yiwen_Zhiwen\Data\layerSymbology.lyr".
 
(3) After modify the paths of bankMxdPath and symbolLayer, save the python script and 
    close the script window.

(4) Open ArcMap, and then open ArcToolbox. Right click at "ArcToolbox", and then click 
    "Add Toolbox". Browse to folder "4_Leta_Yiwen_Zhiwen\Script", and then select 
     "TimeSeriesValueExtraction.tbx". Then click "Open".

(5) Expand the "TimeSeriesValueExtraction" toolbox. Then double click "TimeSeriesValueExtraction"
    tool. 

(6) In the "TimeSeriesValueExtraction" user interface, select or set up the following parameters:
    (a) featureClass: the point shapefile. You could choose the sample fire ignition point
        layer: "4_Leta_Yiwen_Zhiwen\Data\ignitionpts_1621.shp" or "4_Leta_Yiwen_Zhiwen\Data\ignitionpts_50.shp"
    (b) rasterFolder: the folder where the raster files are stored. You could choose the 
        sample raster folder: "U:\Commons\4_Leta_Yiwen_Zhiwen\Data\daily_min_temp_1990_2013"
    (c) MapPath: the path of the output map PDF file
    (d) dateField: the field where the date information is stored. For the ignitionpts_1621.shp
        or ignitionpts_50.shp data, the date field is "DISCOVERY_". 
    (e) namingConV: the naming convention of the raster files. An exmple of naming convention is
        "%YearDay%_tmmn_%Year%_clipped.tif_sa.tif". The users could use a pair of "%" signs 
        and the key word "YearDay", "Year", "MOnth", "Day" in between the pair of "%" signs to 
        specify where the date information can be extracted from the file names. The users 
        can add other letters outside the "%" signs to indicate other letters in the raster 
        file names, such as "_tmmm_". ""YearDay" means which day of the year, such as 1,2,...365
        "Day" means which day of the month, such as 1, 2, 3,...31.
    (f) newField: the name of the new field to store the extracted values.
    (g) aggregateLevel: the temporal level for aggregation, which could be "daily", "montly",
        "yearly". If it is daily, only the cell value of the same date of each point will be
        extracted. If it is monthly, the average of all the cell values of the same month of 
        each point will be calculated. If it is yearly, the average of all the cell values of
        the same year of each point will be calcluated. 

(7) After all the parameters are set up, click "OK" button. Then a message window will show 
    up, updating the progress of processing the value extraction. 

(8) After the processing is finished, the user will see a HTML report, a historgram picture
    and a PDF map automatically opened. And the extracted cell values will be saved in the 
    new field specified by the user. 
