# [Legacy] Accessibility Toolbox for R and ArcGIS

## Overview
This README contains the information for the legacy ArcGIS 10x and ArcGIS Pro <2.4 versions of the Accessibility Calculator tools:
- ```Accessibility_Calculator_10x``` for ArcGIS 10x
- ```Accessibility_Calculator_Pro``` for older versions of ArcGIS Pro (based on ```arcpy.na```)
- ```Accessibility_Calculator_Pro_2_4``` for ArcGIS Pro >=2.4 (based on ```arcpy.nax```)

## Calculating Accessibility in ArcGIS
The Accessibility Calculator has several inputs:  
<img align="right" width="275" height="1250" src="https://github.com/higgicd/Accessibility_Toolbox/blob/master/assets/toolbox.png">

*Network Details*
- **Input Network Dataset**: the input Network Analyst network dataset for your analysis
- **Travel Mode** (Pro): the travel mode for your analysis from your network dataset
  - **Impedance Attribute** (10x): the travel cost used in your analysis from your network dataset
- **Cutoff Value**: the travel time value at which to stop searching for destinations for a given origin
- *Departure Time* (optional): a time of departure from the origins; useful for analyses with traffic or GTFS transit scheduling
  - see the ArcGIS [Make OD Cost Matrix Analysis Layer](https://pro.arcgis.com/en/pro-app/tool-reference/network-analyst/make-od-cost-matrix-analysis-layer.htm) reference for more guidance and examples on setting a *departure time* parameter
- **Impedance Measure**: a selection of one or more impedance measures; refer to the *R Notebook* for guidance on selecting a measure

*Origins*
- **Origins**: a feature class representing origin locations *i*; can be point or polygon
- **Origins ID Field**: a unique identifier for your input origins; can be any type of field
- **Origins Network Search Tolerance**: the search tolerance for locating the input features on the network; features that are outside the search tolerance are left unlocated
- **Origins Network Search Criteria**: restricts the search to particular source feature classes in your network dataset; useful if you don't want to find features that may be unsuited for a network location
  - for example, if you have created a transit network using the [Add GTFS to Network Dataset](https://esri.github.io/public-transit-tools/AddGTFStoaNetworkDataset.html) tool and want your origins to locate on streets while avoiding other feature classes like transit lines, you could input these expressions (using default names for the GTFS tool) into the value table: ```Streets_UseThisOne``` with a snap type of ```SHAPE```; ```Stops``` and ```NONE```; ```Stops_Snapped2Streets``` and ```NONE```; ```Transit_Network_ND_Junctions``` and ```NONE```; ```Connectors_Stops2Streets``` and ```NONE```; and ```TransitLines``` and ```NONE``` (see example for [Pro](https://github.com/higgicd/Accessibility_Toolbox/blob/master/assets/search_criteria_query_pro.png) and [10x](https://github.com/higgicd/Accessibility_Toolbox/blob/master/assets/search_criteria_query_10x.png))
  - see the ArcGIS [Add Locations](https://pro.arcgis.com/en/pro-app/tool-reference/network-analyst/add-locations.htm) reference for more guidance and examples on setting a *search_criteria* parameter
- *Origins Network Search Query* (optional): specifies a query to restrict the search to a subset of the features within a network source feature class; useful if you don't want to locate on particular features
  - for example, if you do not want your input origins to locate on major highways, you could input ```Streets``` with the expression ```FREEWAY=0```
  - in the example data, if you do not want origins to locate on tunnels or bridges, you could input the expressions ```NYC_OSM_Walk``` and ```tunnel<>'yes'``` and ```NYC_OSM_Walk``` and ```bridge<>'yes'``` into the value table (see example for [Pro](https://github.com/higgicd/Accessibility_Toolbox/blob/master/assets/search_criteria_query_pro.png) and [10x](https://github.com/higgicd/Accessibility_Toolbox/blob/master/assets/search_criteria_query_10x.png))
  - see the ArcGIS [Add Locations](https://pro.arcgis.com/en/pro-app/tool-reference/network-analyst/add-locations.htm) reference for more guidance and examples on setting a *search_query* parameter

*Destinations*
- **Destinations**: a feature class representing destination locations *j*; can be point or polygon
- **Destinations ID Field**: a unique identifier for your input destinations; can be any type of field
- **Destination Opportunities Field**: a numeric field containing the opportunities *Oj* available at the destination, such as the number of jobs
- **Destinations Network Search Tolerance**: same notes as the *Origins Network Search Tolerance*
- **Destinations Network Search Criteria**: same notes as the *Origins Network Search Criteria*
- *Destinations Network Search Query* (optional): same notes as the *Origins Network Search Query*

*General Settings*
- **Output Work Folder**: the folder where the output geodatabase will be created; working files generated during large analyses can require many gigabytes of disk space
- **Name of Output Analysis Geodatabase**: name for the output geodatabase containing the scratch working files and the final tool output
- **Batch OD Matrix Size Factor** (batch calculator only): gives you some control over the target size of the OD matrix for batching; default is 10 million rows; a larger number will result in fewer batches but larger matrices
- *Delete OD lines where i = j?* (optional): if selected, the tool will delete any origin-destination lines or pairs where the origin was the same as the destination; useful if you only want to calculate access to opportunities that are external to the origins
- *Join output back to origins?* (optional, Pro only): if selected, joins the accessibility output back to the input origins (relies on the *JoinField* tool in ArcGIS, which I cannot seem to get to work reliably in 10x)

## Selecting an Impedance Function in R
Using the interactive R Notebook, users can explore 5 impedance functions: 
- inverse power
- negative exponential
- modified Gaussian
- cumulative opportunities rectangular
- cumulative opportunities linear

Each function is specified with several different impedance parameters for a total of 28 different impedance measures.

## Customizing or Adding Your Impedance Measure to the Tool
Users can add or change the impedance functions in the ArcGIS Accessibility Calculator by editing the toolbox's Python code in the *.pyt* files. This can be done by editing the code through ArcGIS (right-click on the toolbox > edit). The original Jupyter Notebooks are also included if you prefer to edit in that interface and copy the code back to the toolbox via ArcGIS or a text editor.

The impedance parameters are stored in the parameter dictionary *p* in the toolbox code, which can be found at around line 200 for the Accessibility Calculator and line 675 for the Batch Accessibility Calculator tools in each version of the toolbox. Using the examples of the ```POW0_8``` and ```CUMR10``` impedance measures, each dictionary entry contains four elements:

```
p = {
    "POW0_8": {"f": "pow", "b0": 0.8, "t_bar": None}, 
    "CUMR10": {"f": "cumr", "b0": None, "t_bar": 10}
    }
```

- ```POW0_8``` and ```CUMR10```: the names of the impedance measures; the list of names from *p* informs the list of available measures in the python toolbox
- ```"f"```: the key ```f``` indexes the value of the impedance function for the impedance measure; in the case of ```POW0_8```, the ```"pow"``` string refers to the inverse power function; for ```CUMR10``` the function is ```"cumr"```. Available functions are:
  - ```pow```: inverse power
  - ```neg_exp```: negative exponential
  - ```mgaus```: modified Gaussian
  - ```cumr```: cumulative opportunities rectangular
  - ```cuml```: cumulative opportunities linear
- ```"b0"```: the key ```b0``` indexes the value of the beta parameter for the impedance measure that will be input into the impedance function
  - in the case of the ```POW0_8``` measure, ```0.8``` refers to a beta value of 0.8
  - because ```CUMR10``` does not use this parameter it has a value of ```None```
- ```"t_bar"```: the key ```"t_bar"``` indexes the value of the travel time window for the cumulative impedance functions
  - in the case of the ```CUMR10``` measure, ```10``` refers to a travel time window of 10 minutes
  - because ```POW0_8``` does not use this parameter, it has a value of ```None```

When inputting a new measure into the dictionary, it *must* have entries for the ```f```, ```b0```, and ```t_bar``` parameters, even if they are ```None```

## References

Kwan, M. P. (1998). Space-time and integral measures of individual accessibility: A comparative analysis using a point-based framework. *Geographical Analysis*, 30(3), 191-216. https://doi.org/10.1111/j.1538-4632.1998.tb00396.x

## License
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
