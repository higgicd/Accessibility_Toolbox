# Accessibility Calculator for ArcGIS
# Christopher D. Higgins
# Department of Land Surveying and Geo-Informatics
# Department of Building and Real Estate
# The Hong Kong Polytechnic University
# https://higgicd.github.io
    
import arcpy
from arcpy import env
env.overwriteOutput = True
import os
import time
start_time = time.clock()

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Accessibility Calculator 10x"
        self.alias = "Accessibility_Calculator_10x"

        # List of tool classes associated with this toolbox
        self.tools = [AccessCalc, AccessBatch]

############### START OF ACCESS CALC TOOL ###############

class AccessCalc(object):
    def __init__(self):
        self.label = "Accessibility Calculator"
        self.description = "Calculate place-based accessibility for origins"
        self.canRunInBackground = True
        self.category = "Accessibility Calculator"

    def getParameterInfo(self):
        global p
        p = None
        
        param0 = arcpy.Parameter(
            displayName="Input Network Dataset",
            name="network",
            datatype="DENetworkDataset",
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
            displayName="Impedance Attribute",
            name="impedance_attribute",
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
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param3.value = "None"
        
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
            datatype="DEFeatureClass",
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
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param7.value = "5000 Meters"
        
        param8 = arcpy.Parameter(
            displayName="Origins Network Search Query",
            name="search_query_i",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param8.value = "None"
        
        param9 = arcpy.Parameter(
            displayName="Destinations",
            name="destinations_j_input",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        
        param10 = arcpy.Parameter(
            displayName="Destinations ID Field",
            name="j_id",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        param11 = arcpy.Parameter(
            displayName="Destination Opportunities Field",
            name="opportunities_j",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
 
        param12 = arcpy.Parameter(
            displayName="Destinations Network Search Tolerance",
            name="search_tolerance_j",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param12.value = "5000 Meters"
        
        param13 = arcpy.Parameter(
            displayName="Destinations Network Search Query",
            name="search_query_j",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param13.value = "None"
        
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
        param15.value = "AccessCalc"
        
        param16 = arcpy.Parameter(
            displayName="Delete OD lines where i equals j?",
            name="del_i_eq_j",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        param16.value = False
        
        # join back i does not seem to work in ArcMap - AddJoin returns general function error
        #param17 = arcpy.Parameter(
        #    displayName="Join output back to origins?",
        #    name="join_back_i",
        #    datatype="GPBoolean",
        #    parameterType="Optional",
        #    direction="Input")
        #param17.value = False
        
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
        # impedance function parameters dictionary
        global p
        
        # define dictionary of impedance parameters for batch tool
        # can define a custom measure by altering or copying the dictionary syntax below
        # each function requires parameters b0 and t_bar (even if unused) and a function f
        # available functions are pow, neg_exp, mgaus, cumr, and cuml (see r notebook)
        p = {
            "POW0_8": {"f": "pow", "b0": 0.8, "t_bar": None}, 
            "POW1_0": {"f": "pow", "b0": 1, "t_bar": None},
            "POW1_5": {"f": "pow", "b0": 1.5, "t_bar": None}, 
            "POW2_0": {"f": "pow", "b0": 2, "t_bar": None},
            "POW_CUS": {"f": "pow", "b0": 0.5, "t_bar": None},
            "EXP0_12": {"f": "neg_exp", "b0": 0.12, "t_bar": None}, 
            "EXP0_15": {"f": "neg_exp", "b0": 0.15, "t_bar": None},
            "EXP0_22": {"f": "neg_exp", "b0": 0.22, "t_bar": None}, 
            "EXP0_45": {"f": "neg_exp", "b0": 0.45, "t_bar": None},
            "EXP_CUS": {"f": "neg_exp", "b0": 0.1, "t_bar": None},
            "HN1997": {"f": "neg_exp", "b0": 0.1813, "t_bar": None},
            "MGAUS10": {"f": "mgaus", "b0": 10, "t_bar": None}, 
            "MGAUS40": {"f": "mgaus", "b0": 40, "t_bar": None}, 
            "MGAUS100": {"f": "mgaus", "b0": 100, "t_bar": None}, 
            "MGAUS180": {"f": "mgaus", "b0": 180, "t_bar": None},
            "MGAUSCUS": {"f": "mgaus", "b0": 360, "t_bar": None},
            "CUMR05": {"f": "cumr", "b0": None, "t_bar": 5},
            "CUMR10": {"f": "cumr", "b0": None, "t_bar": 10},
            "CUMR15": {"f": "cumr", "b0": None, "t_bar": 15},
            "CUMR20": {"f": "cumr", "b0": None, "t_bar": 20}, 
            "CUMR30": {"f": "cumr", "b0": None, "t_bar": 30}, 
            "CUMR40": {"f": "cumr", "b0": None, "t_bar": 40},
            "CUMR45": {"f": "cumr", "b0": None, "t_bar": 45},
            "CUMR60": {"f": "cumr", "b0": None, "t_bar": 60},
            "CUML10": {"f": "cuml", "b0": None, "t_bar": 10}, 
            "CUML20": {"f": "cuml", "b0": None, "t_bar": 20}, 
            "CUML30": {"f": "cuml", "b0": None, "t_bar": 30}, 
            "CUML40": {"f": "cuml", "b0": None, "t_bar": 40}
        }
        
        if parameters[0].altered:
            desc_nd = arcpy.Describe(parameters[0].valueAsText)
            attributes = desc_nd.attributes
            parameters[1].filter.list = list(attribute.name for attribute in attributes)
            
        fields4 = list(p)
        parameters[4].filter.list = fields4
        
        if parameters[5].altered:
            fields6 = [f.name for f in arcpy.ListFields(parameters[5].valueAsText)]
            parameters[6].filter.list = fields6
        else:
            parameters[6].filter.list = []
        
        if parameters[9].altered:
            fields10 = [f.name for f in arcpy.ListFields(parameters[9].valueAsText)]
            parameters[10].filter.list = fields10
            parameters[11].filter.list = fields10
        else:
            parameters[10].filter.list = []
            parameters[11].filter.list = []
        
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        arcpy.CheckOutExtension("Network")
        
        network = parameters[0].valueAsText
        impedance_attribute = parameters[1].valueAsText
        cutoff = parameters[2].valueAsText
        time_of_day = parameters[3].valueAsText
        impedance_list = parameters[4].valueAsText
        origins_i_input = parameters[5].valueAsText
        i_id = parameters[6].valueAsText
        search_tolerance_i = parameters[7].valueAsText
        search_query_i = parameters[8].valueAsText
        destinations_j_input = parameters[9].valueAsText
        j_id = parameters[10].valueAsText
        opportunities_j = parameters[11].valueAsText
        search_tolerance_j = parameters[12].valueAsText
        search_query_j = parameters[13].valueAsText
        output_dir = parameters[14].valueAsText
        output_gdb = parameters[15].valueAsText
        del_i_eq_j = parameters[16].valueAsText
        #join_back_i = parameters[17].valueAsText
        layer_name = "Accessibility OD Matrix"
        origins_i_desc = arcpy.Describe(origins_i_input)
        origins_i_path = origins_i_desc.path
        
        # split impedance function multivalue
        selected_impedance_function = impedance_list.split(";")
        
        # get i_id type
        i_id_field = arcpy.ListFields(origins_i_input, i_id)[0]
        if i_id_field.type == "Double":
            i_id_type = "DOUBLE"
        if i_id_field.type == "Integer":
            i_id_type = "LONG"
        if i_id_field.type == "Single":
            i_id_type = "FLOAT"
        if i_id_field.type == "SmallInteger":
            i_id_type = "SHORT"
        if i_id_field.type == "String":
            i_id_type = "TEXT"
        if i_id_field.type == "OID":
            i_id_type = "LONG"
        
        arcpy.AddMessage(str(i_id)+" field type is "+str(i_id_type))
        
        # get j_id type
        j_id_field = arcpy.ListFields(destinations_j_input, j_id)[0]
        if j_id_field.type == "Double":
            j_id_type = "DOUBLE"
        if j_id_field.type == "Integer":
            j_id_type = "LONG"
        if j_id_field.type == "Single":
            j_id_type = "FLOAT"
        if j_id_field.type == "SmallInteger":
            j_id_type = "SHORT"
        if j_id_field.type == "String":
            j_id_type = "TEXT"
        if j_id_field.type == "OID":
            j_id_type = "LONG"
        
        arcpy.AddMessage(str(j_id)+" field type is "+str(j_id_type))
        
        # get opportunities_j type
        opportunities_j_field = arcpy.ListFields(destinations_j_input, opportunities_j)[0]
        if opportunities_j_field.type == "Double":
            opportunities_j_type = "DOUBLE"
        if opportunities_j_field.type == "Integer":
            opportunities_j_type = "LONG"
        if opportunities_j_field.type == "Single":
            opportunities_j_type = "FLOAT"
        if opportunities_j_field.type == "SmallInteger":
            opportunities_j_type = "SHORT"
        if opportunities_j_field.type == "String":
            raise Exception(str(opportunities_j)+" field type is text")
        if opportunities_j_field.type == "OID":
            raise Exception(str(opportunities_j)+" field type is ObjectID")
        
        arcpy.AddMessage(str(opportunities_j)+" field type is "+str(opportunities_j_type))
        
        # setup output workspace
        if arcpy.Exists(os.path.join(output_dir, output_gdb+".gdb")):
            arcpy.management.Delete(os.path.join(output_dir, output_gdb+".gdb"))
            arcpy.management.CreateFileGDB(output_dir, output_gdb+".gdb")
        else:
            arcpy.management.CreateFileGDB(output_dir, output_gdb+".gdb")
        
        arcpy.env.workspace = os.path.join(output_dir, output_gdb+".gdb")
        
        # convert i to points if input is polyon
        describe_i = arcpy.Describe(origins_i_input)
        if describe_i.ShapeType == "Polygon":
            arcpy.AddMessage("Converting Origins to points...")
            origins_i = arcpy.management.FeatureToPoint(origins_i_input, "origins_i_point", "INSIDE")
        else:
            origins_i = origins_i_input
        
        # convert j to points if input is polygon
        describe_j = arcpy.Describe(destinations_j_input)
        if describe_j.ShapeType == "Polygon":
            arcpy.AddMessage("Converting Destinations to points...")
            destinations_j = arcpy.management.FeatureToPoint(destinations_j_input, "destinations_j_point", "INSIDE")
        else:
            destinations_j = destinations_j_input
        
        # create od matrix
        arcpy.AddMessage("Creating Accessibility OD Cost Matrix...")
        if time_of_day != "None":
            arcpy.AddMessage("Departure time is "+time_of_day)
            result_object = arcpy.na.MakeODCostMatrixLayer(network, layer_name, 
                                               impedance_attribute = impedance_attribute, 
                                               default_cutoff = cutoff, 
                                               default_number_destinations_to_find = None,
                                               accumulate_attribute_name = None,
                                               output_path_shape = "NO_LINES",
                                               time_of_day = time_of_day)
            layer_object = result_object.getOutput(0)
            
        else:
            result_object = arcpy.na.MakeODCostMatrixLayer(network, layer_name, 
                                               impedance_attribute = impedance_attribute, 
                                               default_cutoff = cutoff, 
                                               default_number_destinations_to_find = None,
                                               accumulate_attribute_name = None,
                                               output_path_shape = "NO_LINES",
                                               time_of_day = None)
            layer_object = result_object.getOutput(0)
        
        # get layer names
        sublayer_names = arcpy.na.GetNAClassNames(layer_object)
        origins_layer_name = sublayer_names["Origins"]
        destinations_layer_name = sublayer_names["Destinations"]
        
        # field mappings i
        arcpy.na.AddFieldToAnalysisLayer(layer_object, origins_layer_name, "i_id", i_id_type)
        field_mappings_i = arcpy.na.NAClassFieldMappings(layer_object, origins_layer_name)
        field_mappings_i["Name"].mappedFieldName = i_id
        field_mappings_i["i_id"].mappedFieldName = i_id
        arcpy.AddMessage("Adding Origins...")
        arcpy.na.AddLocations(layer_object, origins_layer_name, origins_i, 
                              field_mappings_i,
                              search_tolerance = search_tolerance_i,
                              append = "CLEAR",
                              exclude_restricted_elements = "EXCLUDE",
                              search_query = search_query_i)
        
        # field mappings j
        arcpy.na.AddFieldToAnalysisLayer(layer_object, destinations_layer_name, "j_id", j_id_type)
        arcpy.na.AddFieldToAnalysisLayer(layer_object, destinations_layer_name, "o_j", opportunities_j_type)
        field_mappings_j = arcpy.na.NAClassFieldMappings(layer_object, destinations_layer_name)
        field_mappings_j["Name"].mappedFieldName = j_id
        field_mappings_j["j_id"].mappedFieldName = j_id
        field_mappings_j["o_j"].mappedFieldName = opportunities_j
        arcpy.AddMessage("Adding Destinations...")
        arcpy.na.AddLocations(layer_object, destinations_layer_name, destinations_j, 
                              field_mappings_j,
                              search_tolerance = search_tolerance_j,
                              append = "CLEAR",
                              exclude_restricted_elements = "EXCLUDE",
                              search_query = search_query_j)
        
        # solve
        arcpy.AddMessage("Solving OD Matrix...")
        arcpy.na.Solve(in_network_analysis_layer = layer_object, terminate_on_solve_error = "CONTINUE")
        
        # get sublayer names
        sub_layers = dict((lyr.datasetName, lyr) for lyr in arcpy.mapping.ListLayers(layer_object)[1:])
        origins_sublayer = sub_layers["Origins"]
        destinations_sublayer = sub_layers["Destinations"]
        lines_sublayer = sub_layers["ODLines"]
        solver_props = arcpy.na.GetSolverProperties(layer_object)
        
        # get impedance and accumulator field names
        impedance = solver_props.impedance
        total_impedance_fieldname = "Total_" + impedance
        
        # add join to transfer origin and destination IDs from the OD Cost Matrix to the lines sublayer
        arcpy.AddMessage("Joining attributes...")
        arcpy.management.AddJoin(lines_sublayer, "OriginID", origins_sublayer, "ObjectID")
        arcpy.management.AddJoin(lines_sublayer, "DestinationID", destinations_sublayer, "ObjectID")
        od_lines_joined = arcpy.conversion.TableToTable(lines_sublayer, arcpy.env.workspace, "od_lines_joined")
        arcpy.management.RemoveJoin(lines_sublayer)
        
        # delete rows where i = j
        od_lines_view = arcpy.management.MakeTableView(od_lines_joined, "od_lines_joined_view")
        if del_i_eq_j == "true":
            if origins_i_input == destinations_j_input:
                if i_id == j_id:
                    arcpy.AddMessage("Deleting lines where i = j...")
                    arcpy.management.SelectLayerByAttribute(od_lines_view, "NEW_SELECTION", "Origins_i_id = Destinations_j_id")
                    if int(arcpy.management.GetCount(od_lines_view)[0]) > 0:
                        arcpy.management.DeleteRows(od_lines_view)
                else:
                    arcpy.AddMessage("Can't delete where i = j: inputs don't match")
            else:
                arcpy.AddMessage("Can't delete where i = j: inputs don't match")
        
        # impedance functions
        o_j = '!Destinations_o_j!'
        t_ij = '!'+total_impedance_fieldname+'!'
        
        # loop over selected impedance functions list
        for i in selected_impedance_function:
            f_name = i
            arcpy.AddMessage("Calculating accessibility using impedance function "+f_name+"...")
            
            # define dictionary of functions with calls to parameters dictionary p
            func = {
                "pow": "(1 if %s<1 else (%s**-%s))" % (t_ij, t_ij, p[f_name]["b0"]),
                "neg_exp": "(math.exp(-%s*%s))" % (t_ij, p[f_name]["b0"]),
                "mgaus": "(math.exp(-%s**2/%s))" % (t_ij, p[f_name]["b0"]),
                "cumr": "(1 if %s<=%s else 0)" % (t_ij, p[f_name]["t_bar"]),
                "cuml": "(1-%s/%s if %s<=%s else 0)" % (t_ij, p[f_name]["t_bar"], t_ij, p[f_name]["t_bar"])
            }
            
            impedance_f = func[p[f_name]["f"]]
            arcpy.management.AddField(od_lines_joined, "Ai_"+f_name, "DOUBLE")
            arcpy.management.CalculateField(od_lines_joined, "Ai_"+f_name, "%s*%s" % (o_j, impedance_f), "PYTHON", None)
        
        # calcualte summary statistics
        arcpy.AddMessage("Summarizing accessibility...")
        sum_fields = ["Ai_"+f_field+" SUM" for f_field in selected_impedance_function]
        sum_fields_str = ";".join(sum_fields)
        output_table = arcpy.analysis.Statistics(od_lines_joined,
                                  arcpy.env.workspace+"\\output_"+output_gdb,
                                  sum_fields_str,
                                  "Origins_i_id")
        
        # join back i does not seem to work in ArcMap - AddJoin returns general function error
        #if join_back_i == "true":
        #    # join accessibility output back to origins input
        #    join_fields = [str("SUM_Ai_"+f_field) for f_field in selected_impedance_function]
        #    join_fields.insert(0, "FREQUENCY")
        #    arcpy.AddMessage("Joining accessibility output to "+str(join_fields)+" input i...")
        #    arcpy.AddMessage(join_fields)
        #    arcpy.management.JoinField(origins_i_input, i_id, output_table, "Origins_i_id", join_fields)
        
        end_time = time.clock()
        arcpy.AddMessage("Finished accessibility calculation in "+str(round(((end_time-start_time)/60), 2))+" minutes")
        return

############### START OF ACCESS BATCH TOOL ###############

class AccessBatch(object):
    def __init__(self):
        self.label = "Batch Accessibility Calculator"
        self.description = "Batch calculate place-based accessibility for a large number of origins"
        self.canRunInBackground = True
        self.category = "Accessibility Calculator"
        
    def getParameterInfo(self):
        global p
        p = None
        
        param0 = arcpy.Parameter(
            displayName="Input Network Dataset",
            name="network",
            datatype="DENetworkDataset",
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
            displayName="Impedance Attribute",
            name="impedance_attribute",
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
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param3.value = "None"
        
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
            datatype="DEFeatureClass",
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
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param7.value = "5000 Meters"
        
        param8 = arcpy.Parameter(
            displayName="Origins Network Search Query",
            name="search_query_i",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param8.value = "None"
        
        param9 = arcpy.Parameter(
            displayName="Destinations",
            name="destinations_j_input",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        
        param10 = arcpy.Parameter(
            displayName="Destinations ID Field",
            name="j_id",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        param11 = arcpy.Parameter(
            displayName="Destination Opportunities Field",
            name="opportunities_j",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
 
        param12 = arcpy.Parameter(
            displayName="Destinations Network Search Tolerance",
            name="search_tolerance_j",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param12.value = "5000 Meters"
        
        param13 = arcpy.Parameter(
            displayName="Destinations Network Search Query",
            name="search_query_j",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param13.value = "None"
        
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
        param15.value = "AccessCalc"
        
        param16 = arcpy.Parameter(
            displayName="Batch OD Matrix Size Factor",
            name="od_size_factor",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")
        param16.value = 10000000
        
        param17 = arcpy.Parameter(
            displayName="Delete OD lines where i equals j?",
            name="del_i_eq_j",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        param17.value = False
        
        # join back i does not seem to work in ArcMap - AddJoin returns general function error
        #param18 = arcpy.Parameter(
        #    displayName="Join output back to origins?",
        #    name="join_back_i",
        #    datatype="GPBoolean",
        #    parameterType="Optional",
        #    direction="Input")
        #param18.value = False
        
        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8,\
                  param9, param10, param11, param12, param13, param14, param15, param16, param17]
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
        global p
        
        # define dictionary of impedance parameters for batch tool
        # can define a custom measure by altering or copying the dictionary syntax below
        # each function requires parameters b0 and t_bar (even if unused) and a function f
        # available functions are pow, neg_exp, mgaus, cumr, and cuml (see r notebook)
        p = {
            "POW0_8": {"f": "pow", "b0": 0.8, "t_bar": None}, 
            "POW1_0": {"f": "pow", "b0": 1, "t_bar": None},
            "POW1_5": {"f": "pow", "b0": 1.5, "t_bar": None}, 
            "POW2_0": {"f": "pow", "b0": 2, "t_bar": None},
            "POW_CUS": {"f": "pow", "b0": 0.5, "t_bar": None},
            "EXP0_12": {"f": "neg_exp", "b0": 0.12, "t_bar": None}, 
            "EXP0_15": {"f": "neg_exp", "b0": 0.15, "t_bar": None},
            "EXP0_22": {"f": "neg_exp", "b0": 0.22, "t_bar": None}, 
            "EXP0_45": {"f": "neg_exp", "b0": 0.45, "t_bar": None},
            "EXP_CUS": {"f": "neg_exp", "b0": 0.1, "t_bar": None},
            "HN1997": {"f": "neg_exp", "b0": 0.1813, "t_bar": None},
            "MGAUS10": {"f": "mgaus", "b0": 10, "t_bar": None}, 
            "MGAUS40": {"f": "mgaus", "b0": 40, "t_bar": None}, 
            "MGAUS100": {"f": "mgaus", "b0": 100, "t_bar": None}, 
            "MGAUS180": {"f": "mgaus", "b0": 180, "t_bar": None},
            "MGAUSCUS": {"f": "mgaus", "b0": 360, "t_bar": None},
            "CUMR05": {"f": "cumr", "b0": None, "t_bar": 5},
            "CUMR10": {"f": "cumr", "b0": None, "t_bar": 10},
            "CUMR15": {"f": "cumr", "b0": None, "t_bar": 15},
            "CUMR20": {"f": "cumr", "b0": None, "t_bar": 20}, 
            "CUMR30": {"f": "cumr", "b0": None, "t_bar": 30}, 
            "CUMR40": {"f": "cumr", "b0": None, "t_bar": 40},
            "CUMR45": {"f": "cumr", "b0": None, "t_bar": 45},
            "CUMR60": {"f": "cumr", "b0": None, "t_bar": 60},
            "CUML10": {"f": "cuml", "b0": None, "t_bar": 10}, 
            "CUML20": {"f": "cuml", "b0": None, "t_bar": 20}, 
            "CUML30": {"f": "cuml", "b0": None, "t_bar": 30}, 
            "CUML40": {"f": "cuml", "b0": None, "t_bar": 40}
        }
        
        fields4 = list(p)
        parameters[4].filter.list = fields4
        
        if parameters[0].altered:
        
            desc_nd = arcpy.Describe(parameters[0].valueAsText)
            attributes = desc_nd.attributes
            parameters[1].filter.list = list(attribute.name for attribute in attributes)
        
        if parameters[5].altered:
            fields6 = [f.name for f in arcpy.ListFields(parameters[5].valueAsText)]
            parameters[6].filter.list = fields6
        else:
            parameters[6].filter.list = []
        
        if parameters[9].altered:
            fields10 = [f.name for f in arcpy.ListFields(parameters[9].valueAsText)]
            parameters[10].filter.list = fields10
            parameters[11].filter.list = fields10
        else:
            parameters[10].filter.list = []
            parameters[11].filter.list = []
        
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        arcpy.CheckOutExtension("Network")
        
        global p
        network = parameters[0].valueAsText
        impedance_attribute = parameters[1].valueAsText
        cutoff = parameters[2].valueAsText
        time_of_day = parameters[3].valueAsText
        impedance_list = parameters[4].valueAsText
        origins_i_input = parameters[5].valueAsText
        i_id = parameters[6].valueAsText
        search_tolerance_i = parameters[7].valueAsText
        search_query_i = parameters[8].valueAsText
        destinations_j_input = parameters[9].valueAsText
        j_id = parameters[10].valueAsText
        opportunities_j = parameters[11].valueAsText
        search_tolerance_j = parameters[12].valueAsText
        search_query_j = parameters[13].valueAsText
        output_dir = parameters[14].valueAsText
        output_gdb = parameters[15].valueAsText
        od_size_factor = parameters[16].value
        del_i_eq_j = parameters[17].valueAsText
        #join_back_i = parameters[18].valueAsText
        layer_name = "Accessibility OD Matrix"
        origins_i_desc = arcpy.Describe(origins_i_input)
        origins_i_path = origins_i_desc.path
        
        # split impedance function multivalue
        selected_impedance_function = impedance_list.split(";")
        
        # get i_id type
        i_id_field = arcpy.ListFields(origins_i_input, i_id)[0]
        if i_id_field.type == "Double":
            i_id_type = "DOUBLE"
        if i_id_field.type == "Integer":
            i_id_type = "LONG"
        if i_id_field.type == "Single":
            i_id_type = "FLOAT"
        if i_id_field.type == "SmallInteger":
            i_id_type = "SHORT"
        if i_id_field.type == "String":
            i_id_type = "TEXT"
        if i_id_field.type == "OID":
            i_id_type = "LONG"
        
        arcpy.AddMessage(str(i_id)+" field type is "+str(i_id_type))
        
        # get j_id type
        j_id_field = arcpy.ListFields(destinations_j_input, j_id)[0]
        if j_id_field.type == "Double":
            j_id_type = "DOUBLE"
        if j_id_field.type == "Integer":
            j_id_type = "LONG"
        if j_id_field.type == "Single":
            j_id_type = "FLOAT"
        if j_id_field.type == "SmallInteger":
            j_id_type = "SHORT"
        if j_id_field.type == "String":
            j_id_type = "TEXT"
        if j_id_field.type == "OID":
            j_id_type = "LONG"
        
        arcpy.AddMessage(str(j_id)+" field type is "+str(j_id_type))
        
        # get opportunities_j type
        opportunities_j_field = arcpy.ListFields(destinations_j_input, opportunities_j)[0]
        if opportunities_j_field.type == "Double":
            opportunities_j_type = "DOUBLE"
        if opportunities_j_field.type == "Integer":
            opportunities_j_type = "LONG"
        if opportunities_j_field.type == "Single":
            opportunities_j_type = "FLOAT"
        if opportunities_j_field.type == "SmallInteger":
            opportunities_j_type = "SHORT"
        if opportunities_j_field.type == "String":
            raise Exception(str(opportunities_j)+" field type is text")
        if opportunities_j_field.type == "OID":
            raise Exception(str(opportunities_j)+" field type is ObjectID")
        
        arcpy.AddMessage(str(opportunities_j)+" field type is "+str(opportunities_j_type))
        
        # setup output workspace
        if arcpy.Exists(os.path.join(output_dir, output_gdb+".gdb")):
            arcpy.management.Delete(os.path.join(output_dir, output_gdb+".gdb"))
            arcpy.management.CreateFileGDB(output_dir, output_gdb+".gdb")
        else:
            arcpy.management.CreateFileGDB(output_dir, output_gdb+".gdb")
        
        arcpy.env.workspace = os.path.join(output_dir, output_gdb+".gdb")
        
        # convert i to points if input is polyon
        describe_i = arcpy.Describe(origins_i_input)
        if describe_i.ShapeType == "Polygon":
            arcpy.AddMessage("Converting Origins to points...")
            origins_i = arcpy.management.FeatureToPoint(origins_i_input, "origins_i_point", "INSIDE")
            arcpy.management.AddField(origins_i, "seq_id", "LONG")
            arcpy.management.CalculateField(origins_i, "seq_id", "autoIncrement()", "PYTHON", r"rec=0 \ndef autoIncrement(): \n global rec \n pStart = 1  \n pInterval = 1 \n if (rec == 0):  \n  rec = pStart  \n else:  \n  rec += pInterval  \n return rec")
        else:
            origins_i = arcpy.management.CopyFeatures(origins_i_input, "origins_i_point")
            arcpy.management.AddField(origins_i, "seq_id", "LONG")
            arcpy.management.CalculateField(origins_i, "seq_id", "autoIncrement()", "PYTHON", r"rec=0 \ndef autoIncrement(): \n global rec \n pStart = 1  \n pInterval = 1 \n if (rec == 0):  \n  rec = pStart  \n else:  \n  rec += pInterval  \n return rec")
        
        # convert j to points if input is polygon
        describe_j = arcpy.Describe(destinations_j_input)
        if describe_j.ShapeType == "Polygon":
            arcpy.AddMessage("Converting Destinations to points...")
            destinations_j = arcpy.management.FeatureToPoint(destinations_j_input, "destinations_j_point", "INSIDE")
        else:
            destinations_j = destinations_j_input
        
        # create od matrix
        arcpy.AddMessage("Creating Accessibility OD Cost Matrix...")
        if time_of_day != "None":
            arcpy.AddMessage("Departure time is "+time_of_day)
            result_object = arcpy.na.MakeODCostMatrixLayer(network, layer_name, 
                                               impedance_attribute = impedance_attribute, 
                                               default_cutoff = cutoff, 
                                               default_number_destinations_to_find = None,
                                               accumulate_attribute_name = None,
                                               output_path_shape = "NO_LINES",
                                               time_of_day = time_of_day)
            layer_object = result_object.getOutput(0)
        
        else:
            result_object = arcpy.na.MakeODCostMatrixLayer(network, layer_name, 
                                               impedance_attribute = impedance_attribute, 
                                               default_cutoff = cutoff, 
                                               default_number_destinations_to_find = None,
                                               accumulate_attribute_name = None,
                                               output_path_shape = "NO_LINES",
                                               time_of_day = None)
            layer_object = result_object.getOutput(0)
        
        # get layer names
        sublayer_names = arcpy.na.GetNAClassNames(layer_object)
        origins_layer_name = sublayer_names["Origins"]
        destinations_layer_name = sublayer_names["Destinations"]
        
        # set size of batch raster and polygon
        origins_i_count = int(arcpy.management.GetCount(origins_i).getOutput(0))
        points_per_raster_cell = od_size_factor / origins_i_count
        raster_cell_count = max(1, origins_i_count / points_per_raster_cell)
        origins_i_extent = arcpy.Describe(origins_i).Extent
        raster_cell_area = (origins_i_extent.width * origins_i_extent.height / raster_cell_count)
        raster_cell_size = int(math.sqrt(raster_cell_area))
        
        # construct raster from points
        arcpy.AddMessage("Constructing raster from input points...")
        raster = arcpy.PointToRaster_conversion(in_features = origins_i,
                                       value_field = "seq_id",
                                       out_rasterdataset = arcpy.env.workspace+"\\raster",
                                       cell_assignment = "MOST_FREQUENT",
                                       priority_field = "NONE",
                                       cellsize= raster_cell_size)
                
        # convert raster to polygon
        arcpy.AddMessage("Converting raster to batch polygon...")
        polygons = arcpy.conversion.RasterToPolygon(in_raster = raster,
                                         out_polygon_features = arcpy.env.workspace+"\\polygons",
                                         simplify = "NO_SIMPLIFY",
                                         raster_field= "Value")
        polygon_count = int(arcpy.management.GetCount(polygons).getOutput(0))
        
        # create empty table for results
        output_table = arcpy.management.CreateTable(arcpy.env.workspace, "output_"+output_gdb)
        arcpy.management.AddField(output_table, "Origins_i_id", i_id_type)
        arcpy.management.AddField(output_table, "FREQUENCY", "LONG")
        
        # add selected impedance function names to output table by
        # looping over selected impedance functions list
        for i in selected_impedance_function:
            f_name = i
            arcpy.AddMessage("Calculating accessibility using impedance function "+f_name+"...")
            arcpy.management.AddField(output_table, "SUM_Ai_"+f_name, "DOUBLE")
        
        # create empty table for od lines
        od_lines_joined = arcpy.management.CreateTable(arcpy.env.workspace, "od_lines_joined")
        
        # field mappings j
        arcpy.na.AddFieldToAnalysisLayer(layer_object, destinations_layer_name, "j_id", j_id_type)
        arcpy.na.AddFieldToAnalysisLayer(layer_object, destinations_layer_name, "o_j", opportunities_j_type)
        field_mappings_j = arcpy.na.NAClassFieldMappings(layer_object, destinations_layer_name)
        field_mappings_j["Name"].mappedFieldName = j_id
        field_mappings_j["j_id"].mappedFieldName = j_id
        field_mappings_j["o_j"].mappedFieldName = opportunities_j
        arcpy.AddMessage("Adding Destinations...")
        arcpy.na.AddLocations(layer_object, destinations_layer_name, destinations_j, 
                              field_mappings_j,
                              search_tolerance = search_tolerance_j,
                              append = "CLEAR",
                              exclude_restricted_elements = "EXCLUDE",
                              search_query = search_query_j)
        
        # field mappings i
        arcpy.na.AddFieldToAnalysisLayer(layer_object, origins_layer_name, "i_id", i_id_type)
        field_mappings_i = arcpy.na.NAClassFieldMappings(layer_object, origins_layer_name)
        field_mappings_i["Name"].mappedFieldName = i_id
        field_mappings_i["i_id"].mappedFieldName = i_id
        
        # create feature layer for input points i
        arcpy.management.MakeFeatureLayer(origins_i, "temp_origins_i")

        # iterate od matrix for input points i using polygon
        with arcpy.da.SearchCursor(polygons, ["OBJECTID", "SHAPE@"]) as cursor:
            for row in cursor:
                row_id = row[0]
                arcpy.management.SelectLayerByLocation("temp_origins_i",
                                                   "INTERSECT",
                                                   row[1],
                                                   None,
                                                   "NEW_SELECTION")
                
                # add locations i
                arcpy.AddMessage("Adding Origins for batch "+str(row_id)+" of "+str(polygon_count)+"...")
                arcpy.na.AddLocations(layer_object, origins_layer_name, "temp_origins_i", 
                              field_mappings_i,
                              search_tolerance = search_tolerance_i,
                              append = "CLEAR",
                              exclude_restricted_elements = "EXCLUDE",
                              search_query = search_query_i)
                
                # solve
                arcpy.AddMessage("Solving OD Matrix...")
                arcpy.na.Solve(in_network_analysis_layer = layer_object, terminate_on_solve_error = "CONTINUE")
                
                # get sublayer names
                sub_layers = dict((lyr.datasetName, lyr) for lyr in arcpy.mapping.ListLayers(layer_object)[1:])
                origins_sublayer = sub_layers["Origins"]
                destinations_sublayer = sub_layers["Destinations"]
                lines_sublayer = sub_layers["ODLines"]
                solver_props = arcpy.na.GetSolverProperties(layer_object)
                
                # get impedance and accumulator field names
                impedance = solver_props.impedance
                total_impedance_fieldname = "Total_" + impedance
                
                #Use the JoinField tool to transfer origin and destination IDs from the OD Cost Matrix to the lines sublayer
                arcpy.AddMessage("Joining attributes...")
                if not arcpy.TestSchemaLock(od_lines_joined):
                    # join option 1: if yes lock, append row number to lines table
                    arcpy.management.AddJoin(lines_sublayer, "OriginID", origins_sublayer, "ObjectID")
                    arcpy.management.AddJoin(lines_sublayer, "DestinationID", destinations_sublayer, "ObjectID")
                    od_lines_joined = arcpy.conversion.TableToTable(lines_sublayer, arcpy.env.workspace, "od_lines_joined_"+str(row_id))
                    arcpy.management.RemoveJoin(lines_sublayer)
                else:
                    # join option 2: no lock
                    arcpy.management.AddJoin(lines_sublayer, "OriginID", origins_sublayer, "ObjectID")
                    arcpy.management.AddJoin(lines_sublayer, "DestinationID", destinations_sublayer, "ObjectID")
                    od_lines_joined = arcpy.conversion.TableToTable(lines_sublayer, arcpy.env.workspace, "od_lines_joined")
                    arcpy.management.RemoveJoin(lines_sublayer)
                
                # delete rows where i = j
                od_lines_view = arcpy.management.MakeTableView(od_lines_joined, "od_lines_joined_view")
                if del_i_eq_j == "true":
                    if origins_i_input == destinations_j_input:
                        if i_id == j_id:
                            arcpy.AddMessage("Deleting lines where i = j...")
                            arcpy.management.SelectLayerByAttribute(od_lines_view, "NEW_SELECTION", "Origins_i_id = Destinations_j_id")
                            if int(arcpy.management.GetCount(od_lines_view)[0]) > 0:
                                arcpy.management.DeleteRows(od_lines_view)
                        else:
                            arcpy.AddMessage("Can't delete where i = j: inputs don't match")
                    else:
                        arcpy.AddMessage("Can't delete where i = j: inputs don't match")
                
                # impedance functions
                arcpy.AddMessage("Calculating Accessibility...")
                o_j = '!Destinations_o_j!'
                t_ij = '!'+total_impedance_fieldname+'!'
                
                # loop over selected impedance functions list
                for i in selected_impedance_function:
                    f_name = i
                    # define dictionary of functions with calls to parameters dictionary p
                    func = {
                        "pow": "(1 if %s<1 else (%s**-%s))" % (t_ij, t_ij, p[f_name]["b0"]),
                        "neg_exp": "(math.exp(-%s*%s))" % (t_ij, p[f_name]["b0"]),
                        "mgaus": "(math.exp(-%s**2/%s))" % (t_ij, p[f_name]["b0"]),
                        "cumr": "(1 if %s<=%s else 0)" % (t_ij, p[f_name]["t_bar"]),
                        "cuml": "(1-%s/%s if %s<=%s else 0)" % (t_ij, p[f_name]["t_bar"], t_ij, p[f_name]["t_bar"])
                    }
                    impedance_f = func[p[f_name]["f"]]
                    arcpy.management.AddField(od_lines_joined, "Ai_"+f_name, "DOUBLE")
                    arcpy.management.CalculateField(od_lines_joined, "Ai_"+f_name, "%s*%s" % (o_j, impedance_f), "PYTHON", None)
                
                # calcualte summary statistics
                arcpy.AddMessage("Summarizing Accessibility...")
                sum_fields = ["Ai_"+f_field+" SUM" for f_field in selected_impedance_function]
                sum_fields_str = ";".join(sum_fields)
                arcpy.analysis.Statistics(od_lines_joined,
                                          arcpy.env.workspace+"\\od_statistics",
                                          sum_fields_str,
                                          "Origins_i_id")
                
                arcpy.AddMessage("Appending accessibility output for batch "+str(row_id)+" of "+str(polygon_count)+"...")
                arcpy.management.Append(arcpy.env.workspace+"\\od_statistics", output_table, "NO_TEST")
        
        # join back i does not seem to work in ArcMap - AddJoin returns general function error
        #if join_back_i == "true":
        #    # join accessibility output back to origins input
        #    join_fields = ["SUM_Ai_"+f_field for f_field in selected_impedance_function]
        #    join_fields.insert(0, "FREQUENCY")
        #    arcpy.AddMessage("Joining accessibility output to input i...")
        #    arcpy.management.JoinField(origins_i_input, i_id, output_table, "Origins_i_id", join_fields)
        
        end_time = time.clock()
        arcpy.AddMessage("Finished accessibility calculation in "+str(round(((end_time-start_time)/60), 2))+" minutes")
        return