# Accessibility Toolbox for R and ArcGIS

## Overview
This repository contains the tools, code, and data to support the paper *Accessibility Toolbox for R and ArcGIS*.

<img width="900" alt="fig_2" src="https://github.com/higgicd/Accessibility_Toolbox/blob/master/assets/fig_2.jpg">

The Accessibility Toolbox contains two tools. The first is the **Accessibility Calculator** python toolbox for ArcGIS Pro and 10x simplifies the steps involved in a place-based accessibility workflow. Two versions of the tool are included in the toolbox: the first outputs a single origin-destination matrix while the second segments origins into smaller batches and overwrites the origin-destination matrix across iterations to save memory and disk space for large analyses.

The second is an interactive **Accessibility Toolbox** R Notebook that visualizes the 5 impedance functions from Kwan (1998) and 28 impedance measures to aid in the selection and customization of accessibility cost functions. Customized parameters can be implemented in the ArcGIS tool's python code.

## Calculating Accessibility in ArcGIS
The Accessibility Calculator has several inputs:  
<img align="right" width="300" height="1000" src="https://github.com/higgicd/Accessibility_Toolbox/blob/master/assets/toolbox_fig.png">

*Network Details*
- **Input Network Dataset**: the input Network Analyst network dataset for your analysis
- **Travel Mode** (Pro): the travel mode for your analysis from your network dataset
  - **Impedance Attribute** (10x): the travel cost used in your analysis from your network dataset
- **Cutoff Value**: the travel time value at which to stop searching for destinations for a given origin
- *Departure Time* (optional): a time of departure from the origins; useful for analyses with traffic or GTFS transit scheduling
  - a specific date and time can be specified as *3/19/2018 10:30 AM*
  - to specify that travel should begin at 5:00 PM on a typical Tuesday, use the parameter value *1/2/1900 5:00 PM*
  - see the ArcGIS [Make OD Cost Matrix Analysis Layer](https://pro.arcgis.com/en/pro-app/tool-reference/network-analyst/make-od-cost-matrix-analysis-layer.htm) reference for more guidance and examples on setting a *departure time* parameter
- **Impedance Measure**: a selection of one or more impedance measures; refer to the *R Notebook* for guidance on selecting a measure

*Origins*
- **Origins**: a feature class representing origin locations *i*; can be point or polygon
- **Origins ID Field**: a unique identifier for your input origins; can be any type of field
- *Origins Network Search Tolerance* (optional): the search tolerance for locating the input features on the network; features that are outside the search tolerance are left unlocated
- *Origins Network Search Query* (optional): specifies a query to restrict the search to a subset of the features within a source feature class; useful if you don't want to find features that may be unsuited for a network location
  - for example, if you do not want your input origins to locate on major highways, you could input the SQL expression *["Streets", ""FREEWAY" = 0"]*
  - in the example data, if you do not want origins to locate on tunnels or bridges, you could input the SQL expression *[["NYC_OSM_Walk", ""tunnel" <> 'yes'"], ["NYC_OSM_Walk", ""bridge" <> 'yes'"]]*
  - see the ArcGIS [Add Locations](https://pro.arcgis.com/en/pro-app/tool-reference/network-analyst/add-locations.htm) reference for more guidance and examples on setting a *search_criteria* parameter

*Destinations*
- **Destinations**: a feature class representing destination locations *j*; can be point or polygon
- **Destinations ID Field**: a unique identifier for your input destinations; can be any type of field
- **Destination Opportunities Field**: a numeric field containing the opportunities *Oj* available at the destination, such as the number of jobs
- *Destinations Network Search Tolerance* (optional): same notes as the *Origins Network Search Tolerance*
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
- modified gaussian
- cumulative opportunities rectangular
- cumulative opportunities linear

Each function is specified with several different impedance parameters for a total of 28 different impedance measures.

## Customizing or Adding Your Impedance Measure to the Tool
Users can add or change the impedance functions in the ArcGIS Accessibility Calculator by editing the toolbox's Python code in the *.pyt* files. This can be done by editing the code through ArcGIS (right-click on the toolbox > edit). The original Jupyter Notebooks are also included if you prefer to edit in that interface and copy the code back to the toolbox via ArcGIS or a text editor.

The impedance parameters are stored in the parameter dictionary *p* in the toolbox code, which can be found at around line 200 for the Accessibility Calculator and line 675 for the Batch Accessibility Calculator tools in each version of the toolbox. Using the examples of the *POW0_8* and *CUMR10* impedance measures, each dictionary entry contains four elements:

```
p = {
    "POW0_8": {"f": "pow", "b0": 0.8, "t_bar": None}, 
    "CUMR10": {"f": "cumr", "b0": None, "t_bar": 10}
    }
```

- *POW0_8* and *CUMR10*: the names of the impedance measures; the list of names from *p* informs the list of available measures in the python toolbox
- *"f"*: the key *f* indexes the value of the impedance function for the impedance measure; in the case of *POW0_8*, the *"pow"* string refers to the inverse power function; for *CUMR10* the function is *"cumr"*. Available functions are:
  - *pow*: inverse power
  - *neg_exp*: negative exponential
  - *mgaus*: modified gaussian
  - *cumr*: cumulative opportunities rectangular
  - *cuml*: cumulative opportunities linear
- *"b0"*: the key *b0* indexes the value of the beta parameter for the impedance measure that will be input into the impedance function
  - in the case of the *POW0_8* measure, *0.8* refers to a beta value of 0.8
  - because *CUMR10* does not use this parameter it has a value of *None*
- *"t_bar"*: the key *"t_bar"* indexes the value of the travel time window for the cumulative impedance functions
  - in the case of the *CUMR10* measure, *10* refers to a travel time window of 10 minutes
  - because *POW0_8* does not use this parameter, it has a value of *None*

When inputting a new measure into the dictionary, it must have entries for the *f*, *b0*, and *t_bar* parameters, even if they are *None*

## References

Kwan, M. P. (1998). Space-time and integral measures of individual accessibility: A comparative analysis using a point-based framework. *Geographical Analysis*, 30(3), 191-216. https://doi.org/10.1111/j.1538-4632.1998.tb00396.x

## License
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
