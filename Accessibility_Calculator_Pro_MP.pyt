# Accessibility Calculator for ArcGIS Pro v2.1
# Christopher D. Higgins
# Department of Human Geography
# University of Toronto Scarborough
# https://higgicd.github.io
# tool help can be found at https://github.com/higgicd/Accessibility_Toolbox

import os, sys
import arcpy
from importlib import reload
import access_calc_main
reload(access_calc_main)
import odcm_main
reload(odcm_main)
import odcm_to_pq_main
reload(odcm_to_pq_main)
from arcpy import env
env.overwriteOutput = True

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Accessibility Calculator for Pro 2.4 Multiprocessing"
        self.alias = "AccessibilityCalculatorforPro24Multiprocessing"

        # List of tool classes associated with this toolbox
        self.tools = [AccessCalcProMP, ODCMProMP, ODCMProPQ]

class AccessCalcProMP(object):
    def __init__(self):
        self.label = "Accessibility Calculator for Pro 2.4 Multiprocessing"
        self.description = "Calculate place-based accessibility for origins"
        self.canRunInBackground = True
        self.category = "Accessibility Calculator"

    def getParameterInfo(self):
        param0 = arcpy.Parameter(
            displayName="Input Network Dataset",
            name="network",
            datatype="GPNetworkDatasetLayer",
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
            displayName="Travel Mode",
            name="travel_mode",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        param2 = arcpy.Parameter(
            displayName="Cutoff Value",
            name="cutoff",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        param3 = arcpy.Parameter(
            displayName="Departure Time",
            name="time_of_day",
            datatype="GPDate",
            parameterType="Optional",
            direction="Input")
        param3.value = None
        
        param4 = arcpy.Parameter(
            displayName="Impedance Measure",
            name="impedance_list",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        param4.filter.list = []
        
        param5 = arcpy.Parameter(
            displayName="Origins",
            name="origins_i_input",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        
        param6 = arcpy.Parameter(
            displayName="Origins ID Field",
            name="i_id",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        param7 = arcpy.Parameter(
            displayName="Origins Network Search Tolerance",
            name="search_tolerance_i",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input")
        param7.value = "5000 Meters"
        
        param8 = arcpy.Parameter(
            displayName="Origins Network Search Criteria",
            name="search_criteria_i",
            datatype="GPValueTable",
            parameterType="Required",
            direction="Input")
        param8.value = None
        param8.columns = [['GPString', 'Network Source'], ['GPString', 'Snap Type']]
        param8.filters[0].type = 'ValueList'
        param8.filters[1].type = 'ValueList'
        param8.filters[1].list = ['SHAPE', 'MIDDLE', 'END', 'NONE']
        
        param9 = arcpy.Parameter(
            displayName="Origins Network Search Query",
            name="search_query_i",
            datatype="GPValueTable",
            parameterType="Optional",
            direction="Input")
        param9.value = None
        param9.columns = [['GPString', 'Network Source'], ['GPString', 'Expression']]
        param9.filters[0].type = 'ValueList'
        
        param10 = arcpy.Parameter(
            displayName="Destinations",
            name="destinations_j_input",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        
        param11 = arcpy.Parameter(
            displayName="Destinations ID Field",
            name="j_id",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        param12 = arcpy.Parameter(
            displayName="Destination Opportunities Field",
            name="opportunities_j",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
 
        param13 = arcpy.Parameter(
            displayName="Destinations Network Search Tolerance",
            name="search_tolerance_j",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input")
        param13.value = "5000 Meters"
        
        param14 = arcpy.Parameter(
            displayName="Destinations Network Search Criteria",
            name="search_criteria_j",
            datatype="GPValueTable",
            parameterType="Required",
            direction="Input")
        param14.value = None
        param14.columns = [['GPString', 'Network Source'], ['GPString', 'Snap Type']]
        param14.filters[0].type = 'ValueList'
        param14.filters[1].type = 'ValueList'
        param14.filters[1].list = ['SHAPE', 'MIDDLE', 'END', 'NONE']
        
        param15 = arcpy.Parameter(
            displayName="Destinations Network Search Query",
            name="search_query_j",
            datatype="GPValueTable",
            parameterType="Optional",
            direction="Input")
        param15.value = None
        param15.columns = [['GPString', 'Network Source'], ['GPString', 'Expression']]
        param15.filters[0].type = 'ValueList'
        
        param16 = arcpy.Parameter(
            displayName="Output Work Folder",
            name="output_dir",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        param16.filter.list = ["File System"]
        
        param17 = arcpy.Parameter(
            displayName="Name of Output Analysis Geodatabase",
            name="output_gdb",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param17.value = "AccessCalc"
        
        param18 = arcpy.Parameter(
            displayName="Origins Maximum Batch Size",
            name="batch_size_factor",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")
        param18.value = 500
        
        param19 = arcpy.Parameter(
            displayName="Delete OD lines where i equals j?",
            name="del_i_eq_j",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        param19.value = False
        
        param20 = arcpy.Parameter(
            displayName="Join output back to origins?",
            name="join_back_i",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        param20.value = False
        
        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8,\
                  param9, param10, param11, param12, param13, param14, param15, param16,\
                  param17, param18, param19, param20]
        return params
    
    def isLicensed(self):
        #Set whether tool is licensed to execute
        try:
            if arcpy.CheckExtension("Network") != "Available":
                raise Exception
        except Exception:
                return False  # tool cannot be executed

        return True  # tool can be executed

    def updateParameters(self, parameters):
        # impedance function parameters list
        # ***if you add any functions to the parameters file, you will need to update this list! ***
        available_functions = [
            "POW0_8", "POW1_0", "POW1_5", "POW2_0", "POW_CUS",
            "EXP0_12", "EXP0_15", "EXP0_22", "EXP0_45", "EXP_CUS", "HN1997",
            "MGAUS10", "MGAUS40", "MGAUS100", "MGAUS180", "MGAUSCUS",
            "CUMR05", "CUMR10", "CUMR15", "CUMR20", "CUMR30", "CUMR40", "CUMR45", "CUMR60",
            "CUML10", "CUML20", "CUML30", "CUML40"
            ]
        
        if parameters[0].altered:
            network_travel_modes = arcpy.nax.GetTravelModes(parameters[0].valueAsText)
            fields1 = list(network_travel_modes)
            parameters[1].filter.list = fields1
            network_describe = arcpy.Describe(parameters[0].valueAsText)
            network_sources = network_describe.sources
            network_source_features = [source.name for source in network_sources]
            parameters[8].filters[0].list = list(network_source_features)
            parameters[9].filters[0].list = list(network_source_features)
            parameters[14].filters[0].list = list(network_source_features)
            parameters[15].filters[0].list = list(network_source_features)
        
        fields4 = available_functions
        parameters[4].filter.list = fields4
        
        if parameters[5].altered:
            fields6 = [f.name for f in arcpy.ListFields(parameters[5].valueAsText)]
            parameters[6].filter.list = fields6
        else:
            parameters[6].filter.list = []
        
        if parameters[10].altered:
            fields11 = [f.name for f in arcpy.ListFields(parameters[10].valueAsText)]
            parameters[11].filter.list = fields11
            parameters[12].filter.list = fields11
        else:
            parameters[11].filter.list = []
            parameters[12].filter.list = []
        
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        network = parameters[0].valueAsText
        travel_mode = parameters[1].valueAsText
        cutoff = parameters[2].valueAsText
        time_of_day = parameters[3].value
        impedance_list = parameters[4].valueAsText
        origins_i_input = parameters[5].valueAsText
        i_id_field = parameters[6].valueAsText
        search_tolerance_i = parameters[7].value
        search_criteria_i = parameters[8].value
        search_query_i = parameters[9].value
        destinations_j_input = parameters[10].valueAsText
        j_id_field = parameters[11].valueAsText
        o_j_field = parameters[12].valueAsText
        search_tolerance_j = parameters[13].value
        search_criteria_j = parameters[14].value
        search_query_j = parameters[15].value
        output_dir = parameters[16].valueAsText
        output_gdb = parameters[17].valueAsText
        batch_size_factor = parameters[18].value
        del_i_eq_j = parameters[19].valueAsText
        join_back_i = parameters[20].valueAsText
        
        # get network file path
        input_network_desc = arcpy.Describe(network)
        input_network = os.path.join(input_network_desc.path+"/"+input_network_desc.baseName)
        
        # split impedance function multivalue
        selected_impedance_function = impedance_list.split(";")
        
        # execute
        access_calc_main.main(input_network, travel_mode, cutoff,
                              time_of_day, selected_impedance_function,
                              origins_i_input, i_id_field,
                              search_tolerance_i, search_criteria_i, search_query_i,
                              destinations_j_input, j_id_field, o_j_field,
                              search_tolerance_j, search_criteria_j, search_query_j,
                              batch_size_factor, output_dir, output_gdb,
                              del_i_eq_j, join_back_i)
                              
        arcpy.AddMessage("Finished accessibility calculation")
        return

class ODCMProMP(object):
    def __init__(self):
        self.label = "OD Cost Matrix Calculator for Pro 2.4 Multiprocessing"
        self.description = "Calculate origin-destination cost matrix with multiprocessing"
        self.canRunInBackground = True
        self.category = "OD Cost Matrix Calculator"

    def getParameterInfo(self):
        param0 = arcpy.Parameter(
            displayName="Input Network Dataset",
            name="network",
            datatype="GPNetworkDatasetLayer",
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
            displayName="Travel Mode",
            name="travel_mode",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        param2 = arcpy.Parameter(
            displayName="Cutoff Value",
            name="cutoff",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        param3 = arcpy.Parameter(
            displayName="Departure Time",
            name="time_of_day",
            datatype="GPDate",
            parameterType="Optional",
            direction="Input")
        param3.value = None
        
        param4 = arcpy.Parameter(
            displayName="Origins",
            name="origins_i_input",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        
        param5 = arcpy.Parameter(
            displayName="Origins ID Field",
            name="i_id",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        param6 = arcpy.Parameter(
            displayName="Origins Network Search Tolerance",
            name="search_tolerance_i",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input")
        param6.value = "5000 Meters"
        
        param7 = arcpy.Parameter(
            displayName="Origins Network Search Criteria",
            name="search_criteria_i",
            datatype="GPValueTable",
            parameterType="Required",
            direction="Input")
        param7.value = None
        param7.columns = [['GPString', 'Network Source'], ['GPString', 'Snap Type']]
        param7.filters[0].type = 'ValueList'
        param7.filters[1].type = 'ValueList'
        param7.filters[1].list = ['SHAPE', 'MIDDLE', 'END', 'NONE']
        
        param8 = arcpy.Parameter(
            displayName="Origins Network Search Query",
            name="search_query_i",
            datatype="GPValueTable",
            parameterType="Optional",
            direction="Input")
        param8.value = None
        param8.columns = [['GPString', 'Network Source'], ['GPString', 'Expression']]
        param8.filters[0].type = 'ValueList'
        
        param9 = arcpy.Parameter(
            displayName="Destinations",
            name="destinations_j_input",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        
        param10 = arcpy.Parameter(
            displayName="Destinations ID Field",
            name="j_id",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
 
        param11 = arcpy.Parameter(
            displayName="Destinations Network Search Tolerance",
            name="search_tolerance_j",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input")
        param11.value = "5000 Meters"
        
        param12 = arcpy.Parameter(
            displayName="Destinations Network Search Criteria",
            name="search_criteria_j",
            datatype="GPValueTable",
            parameterType="Required",
            direction="Input")
        param12.value = None
        param12.columns = [['GPString', 'Network Source'], ['GPString', 'Snap Type']]
        param12.filters[0].type = 'ValueList'
        param12.filters[1].type = 'ValueList'
        param12.filters[1].list = ['SHAPE', 'MIDDLE', 'END', 'NONE']
        
        param13 = arcpy.Parameter(
            displayName="Destinations Network Search Query",
            name="search_query_j",
            datatype="GPValueTable",
            parameterType="Optional",
            direction="Input")
        param13.value = None
        param13.columns = [['GPString', 'Network Source'], ['GPString', 'Expression']]
        param13.filters[0].type = 'ValueList'
        
        param14 = arcpy.Parameter(
            displayName="Output Work Folder",
            name="output_dir",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        param14.filter.list = ["File System"]
        
        param15 = arcpy.Parameter(
            displayName="Name of Output Analysis Geodatabase",
            name="output_gdb",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param15.value = "ODCMCalc"
        
        param16 = arcpy.Parameter(
            displayName="Origins Maximum Batch Size",
            name="batch_size_factor",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")
        param16.value = 500
        
        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8,\
                  param9, param10, param11, param12, param13, param14, param15, param16]
        return params
    
    def isLicensed(self):
        #Set whether tool is licensed to execute
        try:
            if arcpy.CheckExtension("Network") != "Available":
                raise Exception
        except Exception:
                return False  # tool cannot be executed

        return True  # tool can be executed

    def updateParameters(self, parameters):
        
        if parameters[0].altered:
            network_travel_modes = arcpy.nax.GetTravelModes(parameters[0].valueAsText)
            fields1 = list(network_travel_modes)
            parameters[1].filter.list = fields1
            network_describe = arcpy.Describe(parameters[0].valueAsText)
            network_sources = network_describe.sources
            network_source_features = [source.name for source in network_sources]
            parameters[7].filters[0].list = list(network_source_features)
            parameters[8].filters[0].list = list(network_source_features)
            parameters[12].filters[0].list = list(network_source_features)
            parameters[13].filters[0].list = list(network_source_features)
        
        if parameters[4].altered:
            fields5 = [f.name for f in arcpy.ListFields(parameters[4].valueAsText)]
            parameters[5].filter.list = fields5
        else:
            parameters[5].filter.list = []
        
        if parameters[9].altered:
            fields10 = [f.name for f in arcpy.ListFields(parameters[9].valueAsText)]
            parameters[10].filter.list = fields10
        else:
            parameters[10].filter.list = []
        
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        network = parameters[0].valueAsText
        travel_mode = parameters[1].valueAsText
        cutoff = parameters[2].valueAsText
        time_of_day = parameters[3].value
        origins_i_input = parameters[4].valueAsText
        i_id_field = parameters[5].valueAsText
        search_tolerance_i = parameters[6].value
        search_criteria_i = parameters[7].value
        search_query_i = parameters[8].value
        destinations_j_input = parameters[9].valueAsText
        j_id_field = parameters[10].valueAsText
        search_tolerance_j = parameters[11].value
        search_criteria_j = parameters[12].value
        search_query_j = parameters[13].value
        output_dir = parameters[14].valueAsText
        output_gdb = parameters[15].valueAsText
        batch_size_factor = parameters[16].value
        
        # get network file path
        input_network_desc = arcpy.Describe(network)
        input_network = os.path.join(input_network_desc.path+"/"+input_network_desc.baseName)
        
        # execute
        odcm_main.main(input_network, travel_mode, cutoff, time_of_day,
                              origins_i_input, i_id_field,
                              search_tolerance_i, search_criteria_i, search_query_i,
                              destinations_j_input, j_id_field,
                              search_tolerance_j, search_criteria_j, search_query_j,
                              batch_size_factor, output_dir, output_gdb)
                              
        arcpy.AddMessage("Finished odcm calculation")
        return

class ODCMProPQ(object):
    def __init__(self):
        self.label = "OD Cost Matrix to Parquet Dataset"
        self.description = "Calculate origin-destination cost matrix as Parquet Dataset"
        self.canRunInBackground = True
        self.category = "OD Cost Matrix to Parquet Calculator"

    def getParameterInfo(self):
        param0 = arcpy.Parameter(
            displayName="Input Network Dataset",
            name="network",
            datatype="GPNetworkDatasetLayer",
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
            displayName="Travel Mode",
            name="travel_mode",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        param2 = arcpy.Parameter(
            displayName="Cutoff Value",
            name="cutoff",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        param3 = arcpy.Parameter(
            displayName="Departure Time",
            name="time_of_day",
            datatype="GPDate",
            parameterType="Optional",
            direction="Input")
        param3.value = None
        
        param4 = arcpy.Parameter(
            displayName="Origins",
            name="origins_i_input",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        
        param5 = arcpy.Parameter(
            displayName="Origins ID Field",
            name="i_id",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        param6 = arcpy.Parameter(
            displayName="Origins Network Search Tolerance",
            name="search_tolerance_i",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input")
        param6.value = "5000 Meters"
        
        param7 = arcpy.Parameter(
            displayName="Origins Network Search Criteria",
            name="search_criteria_i",
            datatype="GPValueTable",
            parameterType="Required",
            direction="Input")
        param7.value = None
        param7.columns = [['GPString', 'Network Source'], ['GPString', 'Snap Type']]
        param7.filters[0].type = 'ValueList'
        param7.filters[1].type = 'ValueList'
        param7.filters[1].list = ['SHAPE', 'MIDDLE', 'END', 'NONE']
        
        param8 = arcpy.Parameter(
            displayName="Origins Network Search Query",
            name="search_query_i",
            datatype="GPValueTable",
            parameterType="Optional",
            direction="Input")
        param8.value = None
        param8.columns = [['GPString', 'Network Source'], ['GPString', 'Expression']]
        param8.filters[0].type = 'ValueList'
        
        param9 = arcpy.Parameter(
            displayName="Destinations",
            name="destinations_j_input",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        
        param10 = arcpy.Parameter(
            displayName="Destinations ID Field",
            name="j_id",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
 
        param11 = arcpy.Parameter(
            displayName="Destinations Network Search Tolerance",
            name="search_tolerance_j",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input")
        param11.value = "5000 Meters"
        
        param12 = arcpy.Parameter(
            displayName="Destinations Network Search Criteria",
            name="search_criteria_j",
            datatype="GPValueTable",
            parameterType="Required",
            direction="Input")
        param12.value = None
        param12.columns = [['GPString', 'Network Source'], ['GPString', 'Snap Type']]
        param12.filters[0].type = 'ValueList'
        param12.filters[1].type = 'ValueList'
        param12.filters[1].list = ['SHAPE', 'MIDDLE', 'END', 'NONE']
        
        param13 = arcpy.Parameter(
            displayName="Destinations Network Search Query",
            name="search_query_j",
            datatype="GPValueTable",
            parameterType="Optional",
            direction="Input")
        param13.value = None
        param13.columns = [['GPString', 'Network Source'], ['GPString', 'Expression']]
        param13.filters[0].type = 'ValueList'
        
        param14 = arcpy.Parameter(
            displayName="Output Work Folder",
            name="output_dir",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        param14.filter.list = ["File System"]
        
        param15 = arcpy.Parameter(
            displayName="Name of Output Parquet Dataset",
            name="output_gdb",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param15.value = "ODCMCalc"
        
        param16 = arcpy.Parameter(
            displayName="Origins Maximum Batch Size",
            name="batch_size_factor",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")
        param16.value = 500
        
        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8,\
                  param9, param10, param11, param12, param13, param14, param15, param16]
        return params
    
    def isLicensed(self):
        #Set whether tool is licensed to execute
        try:
            if arcpy.CheckExtension("Network") != "Available":
                raise Exception
        except Exception:
                return False  # tool cannot be executed

        return True  # tool can be executed

    def updateParameters(self, parameters):
        
        if parameters[0].altered:
            network_travel_modes = arcpy.nax.GetTravelModes(parameters[0].valueAsText)
            fields1 = list(network_travel_modes)
            parameters[1].filter.list = fields1
            network_describe = arcpy.Describe(parameters[0].valueAsText)
            network_sources = network_describe.sources
            network_source_features = [source.name for source in network_sources]
            parameters[7].filters[0].list = list(network_source_features)
            parameters[8].filters[0].list = list(network_source_features)
            parameters[12].filters[0].list = list(network_source_features)
            parameters[13].filters[0].list = list(network_source_features)
        
        if parameters[4].altered:
            fields5 = [f.name for f in arcpy.ListFields(parameters[4].valueAsText)]
            parameters[5].filter.list = fields5
        else:
            parameters[5].filter.list = []
        
        if parameters[9].altered:
            fields10 = [f.name for f in arcpy.ListFields(parameters[9].valueAsText)]
            parameters[10].filter.list = fields10
        else:
            parameters[10].filter.list = []
        
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        network = parameters[0].valueAsText
        travel_mode = parameters[1].valueAsText
        cutoff = parameters[2].valueAsText
        time_of_day = parameters[3].value
        origins_i_input = parameters[4].valueAsText
        i_id_field = parameters[5].valueAsText
        search_tolerance_i = parameters[6].value
        search_criteria_i = parameters[7].value
        search_query_i = parameters[8].value
        destinations_j_input = parameters[9].valueAsText
        j_id_field = parameters[10].valueAsText
        search_tolerance_j = parameters[11].value
        search_criteria_j = parameters[12].value
        search_query_j = parameters[13].value
        output_dir = parameters[14].valueAsText
        output_gdb = parameters[15].valueAsText
        batch_size_factor = parameters[16].value
        
        # get network file path
        input_network_desc = arcpy.Describe(network)
        input_network = os.path.join(input_network_desc.path+"/"+input_network_desc.baseName)
        
        # execute
        odcm_to_pq_main.main(input_network, travel_mode, cutoff, time_of_day,
                              origins_i_input, i_id_field,
                              search_tolerance_i, search_criteria_i, search_query_i,
                              destinations_j_input, j_id_field,
                              search_tolerance_j, search_criteria_j, search_query_j,
                              batch_size_factor, output_dir, output_gdb)
                              
        arcpy.AddMessage("Finished odcm calculation")
        return
