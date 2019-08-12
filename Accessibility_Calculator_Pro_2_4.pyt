# Accessibility Calculator for ArcGIS v1.1
# Christopher D. Higgins
# Department of Human Geography
# University of Toronto Scarborough
# https://higgicd.github.io
# tool help can be found at https://github.com/higgicd/Accessibility_Toolbox
    
import arcpy
from arcpy import env
env.overwriteOutput = True
import os

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Accessibility Calculator for Pro 2.4"
        self.alias = "AccessibilityCalculatorforPro24"

        # List of tool classes associated with this toolbox
        self.tools = [AccessCalcPro2_4, AccessBatchPro2_4]

############### START OF ACCESS CALC TOOL ###############

class AccessCalcPro2_4(object):
    def __init__(self):
        self.label = "Accessibility Calculator for Pro 2.4"
        self.description = "Calculate place-based accessibility for origins"
        self.canRunInBackground = True
        self.category = "Accessibility Calculator"

    def getParameterInfo(self):
        global p
        p = None
        
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
            displayName="Delete OD lines where i equals j?",
            name="del_i_eq_j",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        param18.value = False
        
        param19 = arcpy.Parameter(
            displayName="Join output back to origins?",
            name="join_back_i",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        param19.value = False
        
        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8,\
                  param9, param10, param11, param12, param13, param14, param15, param16,\
                  param17, param18, param19]
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
        
        fields4 = list(p)
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
        arcpy.CheckOutExtension("Network")
        
        input_network = parameters[0].valueAsText
        travel_mode = parameters[1].valueAsText
        cutoff = parameters[2].valueAsText
        time_of_day = parameters[3].value
        impedance_list = parameters[4].valueAsText
        origins_i_input = parameters[5].valueAsText
        i_id = parameters[6].valueAsText
        search_tolerance_i = parameters[7].value
        search_criteria_i = parameters[8].value
        search_query_i = parameters[9].value
        destinations_j_input = parameters[10].valueAsText
        j_id = parameters[11].valueAsText
        opportunities_j = parameters[12].valueAsText
        search_tolerance_j = parameters[13].value
        search_criteria_j = parameters[14].value
        search_query_j = parameters[15].value
        output_dir = parameters[16].valueAsText
        output_gdb = parameters[17].valueAsText
        del_i_eq_j = parameters[18].valueAsText
        join_back_i = parameters[19].valueAsText
        layer_name = "Accessibility OD Matrix"
        
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
        
        # create input features and convert to points if required
        # field mappings for i_input
        field_mappings_i_input = arcpy.FieldMappings()

        # field maps for i_id
        field_map_i_id = arcpy.FieldMap()
        field_map_i_id.addInputField(origins_i_input, i_id)
        field_i_id_output = field_map_i_id.outputField
        field_i_id_output.name = "i_id"
        field_map_i_id.outputField = field_i_id_output
        field_mappings_i_input.addFieldMap(field_map_i_id)
        
        # convert i to points if input is polygon
        describe_i = arcpy.Describe(origins_i_input)
        if describe_i.ShapeType == "Polygon":
            arcpy.AddMessage("Converting Origins to points...")
            arcpy.management.FeatureToPoint(origins_i_input, r"in_memory/origins_i_point", "INSIDE")
            origins_i_point = r"in_memory/origins_i_point"
            arcpy.conversion.FeatureClassToFeatureClass(origins_i_point, arcpy.env.workspace, 
                                                        "origins_i", field_mapping = field_mappings_i_input)
        else:
            arcpy.conversion.FeatureClassToFeatureClass(origins_i_input, arcpy.env.workspace, 
                                                        "origins_i", field_mapping = field_mappings_i_input)
        
        origins_i = os.path.join(arcpy.env.workspace+"/origins_i")
        
        # add i_id_text to join with OriginsName in nax
        arcpy.management.AddField(origins_i, "i_id_text", "TEXT")
        arcpy.management.CalculateField(origins_i, "i_id_text", "!i_id!", "PYTHON3")
        
        # save attributes in memory for joining
        arcpy.conversion.FeatureClassToFeatureClass(origins_i, r"in_memory", "origins_i_attr")
        origins_i_attr = r"in_memory/origins_i_attr"
        
        # field mappings for j_input
        field_mappings_j_input = arcpy.FieldMappings()

        # field maps for j_id
        field_map_j_id = arcpy.FieldMap()
        field_map_j_id.addInputField(destinations_j_input, j_id)
        field_j_id_output = field_map_j_id.outputField
        field_j_id_output.name = "j_id"
        field_map_j_id.outputField = field_j_id_output
        field_mappings_j_input.addFieldMap(field_map_j_id)

        # field maps for o_j
        field_map_o_j = arcpy.FieldMap()
        field_map_o_j.addInputField(destinations_j_input, opportunities_j)
        field_o_j_output = field_map_o_j.outputField
        field_o_j_output.name = "o_j"
        field_map_o_j.outputField = field_o_j_output
        field_mappings_j_input.addFieldMap(field_map_o_j)
        
        # convert j to points if input is polygon
        describe_j = arcpy.Describe(destinations_j_input)
        if describe_j.ShapeType == "Polygon":
            arcpy.AddMessage("Converting Destinations to points...")
            arcpy.management.FeatureToPoint(destinations_j_input, r"in_memory/destinations_j_point", "INSIDE")
            destinations_j_point = r"in_memory/destinations_j_point"
            arcpy.conversion.FeatureClassToFeatureClass(destinations_j_point, arcpy.env.workspace, 
                                                        "destinations_j", field_mapping = field_mappings_j_input)
        else:
            arcpy.conversion.FeatureClassToFeatureClass(destinations_j_input, arcpy.env.workspace, 
                                                        "destinations_j", field_mapping = field_mappings_j_input)
        
        destinations_j = os.path.join(arcpy.env.workspace+"/destinations_j")
        
        # add j_id_text to join with DestinationsName in nax
        arcpy.management.AddField(destinations_j, "j_id_text", "TEXT")
        arcpy.management.CalculateField(destinations_j, "j_id_text", "!j_id!", "PYTHON3")
        
        # save attributes in memory for joining
        arcpy.conversion.FeatureClassToFeatureClass(destinations_j, r"in_memory", "destinations_j_attr")
        destinations_j_attr = r"in_memory/destinations_j_attr"
        
        # create od matrix with nax
        network_layer = "network_layer"
        arcpy.AddMessage("Creating Accessibility OD Cost Matrix...")
        arcpy.nax.MakeNetworkDatasetLayer(input_network, network_layer)
        odcm = arcpy.nax.OriginDestinationCostMatrix(network_layer)
        
        if time_of_day != None:
            arcpy.AddMessage("Departure time is "+str(time_of_day))
            # set nax network_layer properties
            odcm.travelMode = travel_mode
            odcm.timeUnits = arcpy.nax.TimeUnits.Minutes
            odcm.defaultImpedanceCutoff = cutoff
            odcm.lineShapeType = arcpy.nax.LineShapeType.NoLine
            odcm.timeOfDay = time_of_day
        
        else:
            # set nax network_layer properties
            odcm.travelMode = travel_mode
            odcm.timeUnits = arcpy.nax.TimeUnits.Minutes
            odcm.defaultImpedanceCutoff = cutoff
            odcm.lineShapeType = arcpy.nax.LineShapeType.NoLine
            odcm.timeOfDay = None
        
        # add origins
        arcpy.AddMessage("Adding Origins...")
        
        # 1: calculate origin locations
        arcpy.nax.CalculateLocations(origins_i, input_network, 
                                     search_tolerance = search_tolerance_i, 
                                     search_criteria = search_criteria_i, 
                                     search_query = search_query_i,
                                     travel_mode = travel_mode,
                                     exclude_restricted_elements = "EXCLUDE")
        
        # 2: map i_id field
        candidate_fields_i = arcpy.ListFields(origins_i)
        field_mappings_i = odcm.fieldMappings(arcpy.nax.OriginDestinationCostMatrixInputDataType.Origins, 
                                              True, candidate_fields_i)
        field_mappings_i["Name"].mappedFieldName = "i_id"
        
        # 3: load origins
        odcm.load(arcpy.nax.OriginDestinationCostMatrixInputDataType.Origins, 
                  features = origins_i, 
                  field_mappings = field_mappings_i,
                  append = False)
        
        # add destinations
        arcpy.AddMessage("Adding Destinations...")
        
        # 1: calculate origin locations
        arcpy.nax.CalculateLocations(destinations_j, input_network, 
                                     search_tolerance = search_tolerance_j, 
                                     search_criteria = search_criteria_j, 
                                     search_query = search_query_i,
                                     travel_mode = travel_mode,
                                     exclude_restricted_elements = "EXCLUDE")
        
        # 2: map j_id field
        candidate_fields_j = arcpy.ListFields(destinations_j)
        field_mappings_j_nax = odcm.fieldMappings(arcpy.nax.OriginDestinationCostMatrixInputDataType.Destinations,
                                                  True, candidate_fields_j)
        field_mappings_j_nax["Name"].mappedFieldName = "j_id"
        
        # 3: load destinations
        odcm.load(arcpy.nax.OriginDestinationCostMatrixInputDataType.Destinations, 
                  features = destinations_j, 
                  field_mappings = field_mappings_j_nax,
                  append = False)
        
        # solve
        arcpy.AddMessage("Solving OD Matrix...")
        result = odcm.solve()
        
        # Export the results to a feature class
        if result.solveSucceeded:
            result.export(arcpy.nax.OriginDestinationCostMatrixOutputDataType.Lines, r"in_memory/od_lines")
        else:
            print("Solved failed")
            print(result.solverMessages(arcpy.nax.MessageSeverity.All))
        
        od_lines = arcpy.management.MakeFeatureLayer(r"in_memory/od_lines", "od_lines")
        
        # add join to transfer origin and destination IDs from the OD Cost Matrix to the lines sublayer
        arcpy.AddMessage("Joining attributes...")
        arcpy.management.AddJoin(od_lines, "OriginName", origins_i_attr, "i_id_text")
        arcpy.management.AddJoin(od_lines, "DestinationName", destinations_j_attr, "j_id_text")
        od_lines_joined = arcpy.conversion.FeatureClassToFeatureClass(od_lines, r"in_memory", "od_lines_joined")
        arcpy.management.RemoveJoin(od_lines)
        arcpy.management.RemoveJoin(od_lines)
        
        # delete rows where i = j
        if del_i_eq_j == "true":
            if origins_i_input == destinations_j_input:
                if i_id == j_id:
                    #arcpy.AddMessage("Deleting lines where i = j...")
                    #od_lines_view = arcpy.management.MakeTableView(od_lines_joined, "od_lines_joined_view")
                    arcpy.management.MakeFeatureLayer(od_lines_joined, "od_lines_view")
                    arcpy.management.SelectLayerByAttribute("od_lines_view", "NEW_SELECTION", "i_id <> j_id")
                    arcpy.management.SelectLayerByAttribute("od_lines_view", "SWITCH_SELECTION")
                    #arcpy.management.SelectLayerByAttribute(od_lines_view, "NEW_SELECTION", "OriginName = DestinationName")
                    if int(arcpy.management.GetCount("od_lines_view").getOutput(0)) > 0:
                        arcpy.AddMessage("Deleting "+str(int(arcpy.management.GetCount("od_lines_view")[0]))+" lines where i = j...")
                        arcpy.management.DeleteRows("od_lines_view")
                else:
                    arcpy.AddMessage("Can't delete where i = j: inputs don't match")
            else:
                arcpy.AddMessage("Can't delete where i = j: inputs don't match")
        
        # impedance functions
        o_j = '!o_j!'
        total_impedance_fieldname = "Total_Time"
        t_ij = '!'+total_impedance_fieldname+'!'
        
        # loop over selected impedance functions list
        for i in selected_impedance_function:
            f_name = i
            arcpy.AddMessage("Calculating accessibility using impedance function "+f_name+"...")
            arcpy.management.AddField(od_lines_joined, "Ai_"+f_name, "DOUBLE")
            # define dictionary of functions with calls to parameters dictionary p
            func = {
                "pow": "(1 if {}<1 else ({}**-{}))".format(t_ij, t_ij, p[f_name]["b0"]),
                "neg_exp": "(math.exp(-{}*{}))".format(t_ij, p[f_name]["b0"]),
                "mgaus": "(math.exp(-{}**2/{}))".format(t_ij, p[f_name]["b0"]),
                "cumr": "(1 if {}<={} else 0)".format(t_ij, p[f_name]["t_bar"]),
                "cuml": "(1-{}/{} if {}<={} else 0)".format(t_ij, p[f_name]["t_bar"], t_ij, p[f_name]["t_bar"])
            }
            
            impedance_f = func[p[f_name]["f"]]
            arcpy.management.CalculateField(od_lines_joined, "Ai_"+f_name, "{}*{}".format(o_j, impedance_f), "PYTHON3", None)
        
        # calcualte summary statistics
        arcpy.AddMessage("Summarizing accessibility...")
        sum_fields = ["Ai_"+f_field+" SUM" for f_field in selected_impedance_function]
        sum_fields_str = ";".join(sum_fields)
        output_table = arcpy.analysis.Statistics(od_lines_joined, arcpy.env.workspace+"\\output_"+output_gdb, sum_fields_str, "i_id")
        
        if join_back_i == "true":
            # join accessibility output back to origins input
            join_fields = ["SUM_Ai_"+f_field for f_field in selected_impedance_function]
            join_fields.insert(0, "FREQUENCY")
            arcpy.AddMessage("Joining accessibility output to input i...")
            arcpy.management.JoinField(origins_i_input, i_id, output_table, "i_id", join_fields)
        
        # clean up
        arcpy.management.Delete(r"in_memory/origins_i_point")
        arcpy.management.Delete(r"in_memory/origins_i")
        arcpy.management.Delete(r"in_memory/origins_i_attr")
        arcpy.management.Delete(r"in_memory/destinations_j_point")
        arcpy.management.Delete(r"in_memory/destinations_j")
        arcpy.management.Delete(r"in_memory/destinations_j_attr")
        
        arcpy.AddMessage("Finished accessibility calculation")
        return
    
############### START OF ACCESS BATCH TOOL ###############

class AccessBatchPro2_4(object):
    def __init__(self):
        self.label = "Batch Accessibility Calculator for Pro 2.4"
        self.description = "Batch calculate place-based accessibility for a large number of origins"
        self.canRunInBackground = True
        self.category = "Accessibility Calculator"
        
    def getParameterInfo(self):
        global p
        p = None
        
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
            displayName="Batch OD Matrix Size Factor",
            name="od_size_factor",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")
        param18.value = 10000000
        
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
        arcpy.CheckOutExtension("Network")
        
        global p
        input_network = parameters[0].valueAsText
        travel_mode = parameters[1].valueAsText
        cutoff = parameters[2].valueAsText
        time_of_day = parameters[3].value
        impedance_list = parameters[4].valueAsText
        origins_i_input = parameters[5].valueAsText
        i_id = parameters[6].valueAsText
        search_tolerance_i = parameters[7].value
        search_criteria_i = parameters[8].value
        search_query_i = parameters[9].value
        destinations_j_input = parameters[10].valueAsText
        j_id = parameters[11].valueAsText
        opportunities_j = parameters[12].valueAsText
        search_tolerance_j = parameters[13].value
        search_criteria_j = parameters[14].value
        search_query_j = parameters[15].value
        output_dir = parameters[16].valueAsText
        output_gdb = parameters[17].valueAsText
        od_size_factor = parameters[18].value
        del_i_eq_j = parameters[19].valueAsText
        join_back_i = parameters[20].valueAsText
        layer_name = "Accessibility OD Matrix"
        
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
        
        # create input features and convert to points if required
        # field mappings for i_input
        field_mappings_i_input = arcpy.FieldMappings()

        # field maps for i_id
        field_map_i_id = arcpy.FieldMap()
        field_map_i_id.addInputField(origins_i_input, i_id)
        field_i_id_output = field_map_i_id.outputField
        field_i_id_output.name = "i_id"
        field_map_i_id.outputField = field_i_id_output
        field_mappings_i_input.addFieldMap(field_map_i_id)
        
        # convert i to points if input is polyon
        describe_i = arcpy.Describe(origins_i_input)
        if describe_i.ShapeType == "Polygon":
            arcpy.AddMessage("Converting Origins to points...")
            arcpy.management.FeatureToPoint(origins_i_input, r"in_memory/origins_i_point", "INSIDE")
            origins_i_point = r"in_memory\origins_i_point"
            arcpy.conversion.FeatureClassToFeatureClass(origins_i_point, arcpy.env.workspace, 
                                                        "origins_i", field_mapping = field_mappings_i_input)
        else:
            arcpy.conversion.FeatureClassToFeatureClass(origins_i_input, arcpy.env.workspace, 
                                                        "origins_i", field_mapping = field_mappings_i_input)
        
        # assign variable
        origins_i = os.path.join(arcpy.env.workspace+"/origins_i")
        
        # add i_id_text to join with OriginsName in nax
        arcpy.management.AddField(origins_i, "i_id_text", "TEXT")
        arcpy.management.CalculateField(origins_i, "i_id_text", "!i_id!", "PYTHON3")
        
        # save attributes in memory for joining
        arcpy.conversion.FeatureClassToFeatureClass(origins_i, r"in_memory", "origins_i_attr")
        origins_i_attr = r"in_memory/origins_i_attr"
        
        # create new sequential id for creating raster
        arcpy.management.AddField(origins_i, "seq_id", "LONG")
        arcpy.management.CalculateField(origins_i, "seq_id", "autoIncrement()", "PYTHON3", "rec=0\ndef autoIncrement():\n    global rec\n    pStart    = 1 \n    pInterval = 1 \n " +
    "   if (rec == 0): \n        rec = pStart \n    else: \n        rec += pInterval \n  " +
    "  return rec")
        
        # field mappings for j_input
        field_mappings_j_input = arcpy.FieldMappings()

        # field maps for j_id
        field_map_j_id = arcpy.FieldMap()
        field_map_j_id.addInputField(destinations_j_input, j_id)
        field_j_id_output = field_map_j_id.outputField
        field_j_id_output.name = "j_id"
        field_map_j_id.outputField = field_j_id_output
        field_mappings_j_input.addFieldMap(field_map_j_id)

        # field maps for o_j
        field_map_o_j = arcpy.FieldMap()
        field_map_o_j.addInputField(destinations_j_input, opportunities_j)
        field_o_j_output = field_map_o_j.outputField
        field_o_j_output.name = "o_j"
        field_map_o_j.outputField = field_o_j_output
        field_mappings_j_input.addFieldMap(field_map_o_j)
        
        # convert j to points if input is polygon
        describe_j = arcpy.Describe(destinations_j_input)
        if describe_j.ShapeType == "Polygon":
            arcpy.AddMessage("Converting Destinations to points...")
            arcpy.management.FeatureToPoint(destinations_j_input, r"in_memory/destinations_j_point", "INSIDE")
            destinations_j_point = r"in_memory\destinations_j_point"
            arcpy.conversion.FeatureClassToFeatureClass(destinations_j_point, arcpy.env.workspace, 
                                                        "destinations_j", field_mapping = field_mappings_j_input)
        else:
            arcpy.conversion.FeatureClassToFeatureClass(destinations_j_input, arcpy.env.workspace, 
                                                        "destinations_j", field_mapping = field_mappings_j_input)
        
        destinations_j = os.path.join(arcpy.env.workspace+"/destinations_j")
        
        # add j_id_text to join with DestinationsName in nax
        arcpy.management.AddField(destinations_j, "j_id_text", "TEXT")
        arcpy.management.CalculateField(destinations_j, "j_id_text", "!j_id!", "PYTHON3")
        
        # save attributes in memory for joining
        arcpy.conversion.FeatureClassToFeatureClass(destinations_j, r"in_memory", "destinations_j_attr")
        destinations_j_attr = r"in_memory/destinations_j_attr"
        
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
                                       out_rasterdataset = r"in_memory/raster",
                                       cell_assignment = "MOST_FREQUENT",
                                       priority_field = "NONE",
                                       cellsize= raster_cell_size)
                
        # convert raster to polygon
        arcpy.AddMessage("Converting raster to batch polygon...")
        polygons = arcpy.conversion.RasterToPolygon(in_raster = raster,
                                         out_polygon_features = r"in_memory/polygons",
                                         simplify = "NO_SIMPLIFY",
                                         raster_field= "Value")
        polygon_count = int(arcpy.management.GetCount(polygons).getOutput(0))
        
        # create empty table for results
        output_table = arcpy.management.CreateTable(arcpy.env.workspace, "output_"+output_gdb)
        arcpy.management.AddField(output_table, "i_id", i_id_type)
        arcpy.management.AddField(output_table, "FREQUENCY", "LONG")
        
        # add selected impedance function names to output table by
        # looping over selected impedance functions list
        for i in selected_impedance_function:
            f_name = i
            arcpy.AddMessage("Calculating accessibility using impedance function "+f_name+"...")
            arcpy.management.AddField(output_table, "SUM_Ai_"+f_name, "DOUBLE")
        
        # create od matrix with nax
        network_layer = "network_layer"
        arcpy.AddMessage("Creating Accessibility OD Cost Matrix...")
        arcpy.nax.MakeNetworkDatasetLayer(input_network, network_layer)
        odcm = arcpy.nax.OriginDestinationCostMatrix(network_layer)
        
        if time_of_day != None:
            arcpy.AddMessage("Departure time is "+str(time_of_day))
            # set nax network_layer properties
            odcm.travelMode = travel_mode
            odcm.timeUnits = arcpy.nax.TimeUnits.Minutes
            odcm.defaultImpedanceCutoff = cutoff
            odcm.lineShapeType = arcpy.nax.LineShapeType.NoLine
            odcm.timeOfDay = time_of_day
        
        else:
            # set nax network_layer properties
            odcm.travelMode = travel_mode
            odcm.timeUnits = arcpy.nax.TimeUnits.Minutes
            odcm.defaultImpedanceCutoff = cutoff
            odcm.lineShapeType = arcpy.nax.LineShapeType.NoLine
            odcm.timeOfDay = None
        
        # calculate origin locations
        arcpy.AddMessage("Adding Origins...")
        arcpy.nax.CalculateLocations(origins_i, input_network, 
                                     search_tolerance = search_tolerance_i, 
                                     search_criteria = search_criteria_i, 
                                     search_query = search_query_i,
                                     travel_mode = travel_mode,
                                     exclude_restricted_elements = "EXCLUDE")

        # 2: map i_id field
        candidate_fields_i = arcpy.ListFields(origins_i)
        field_mappings_i = odcm.fieldMappings(arcpy.nax.OriginDestinationCostMatrixInputDataType.Origins, 
                                              True, candidate_fields_i)
        field_mappings_i["Name"].mappedFieldName = "i_id"
        
        # add destinations
        arcpy.AddMessage("Adding Destinations...")
        
        # 1: calculate destination locations
        arcpy.nax.CalculateLocations(destinations_j, input_network, 
                                     search_tolerance = search_tolerance_j, 
                                     search_criteria = search_criteria_j, 
                                     search_query = search_query_i,
                                     travel_mode = travel_mode,
                                     exclude_restricted_elements = "EXCLUDE")
        
        # 2: map j_id field
        candidate_fields_j = arcpy.ListFields(destinations_j)
        field_mappings_j_nax = odcm.fieldMappings(arcpy.nax.OriginDestinationCostMatrixInputDataType.Destinations,
                                                  True, candidate_fields_j)
        field_mappings_j_nax["Name"].mappedFieldName = "j_id"
        
        # 3: load destinations
        odcm.load(arcpy.nax.OriginDestinationCostMatrixInputDataType.Destinations, 
                  features = destinations_j, 
                  field_mappings = field_mappings_j_nax,
                  append = False)
        
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
                arcpy.conversion.FeatureClassToFeatureClass("temp_origins_i", r"in_memory", 
                                                        "temp_origins_"+str(row_id))
                
                temp_origins_i = r"in_memory/temp_origins_"+str(row_id)
                
                # add origins
                arcpy.AddMessage("Loading Origins for batch "+str(row_id)+" of "+str(polygon_count)+"...")
                odcm.load(arcpy.nax.OriginDestinationCostMatrixInputDataType.Origins, 
                          features = temp_origins_i, 
                          field_mappings = field_mappings_i,
                          append = False)
                
                # solve
                arcpy.AddMessage("Solving OD Matrix...")
                result = odcm.solve()
                
                # Export the results to a feature class
                if result.solveSucceeded:
                    result.export(arcpy.nax.OriginDestinationCostMatrixOutputDataType.Lines, r"in_memory/od_lines_"+str(row_id))
                else:
                    print("Solved failed")
                    print(result.solverMessages(arcpy.nax.MessageSeverity.All))
                    
                od_lines = arcpy.management.MakeFeatureLayer(r"in_memory/od_lines_"+str(row_id), "od_lines")
                
                # add join to transfer origin and destination IDs from the OD Cost Matrix to the lines sublayer
                arcpy.AddMessage("Joining attributes...")
                arcpy.management.AddJoin(od_lines, "OriginName", origins_i_attr, "i_id_text")
                arcpy.management.AddJoin(od_lines, "DestinationName", destinations_j_attr, "j_id_text")
                od_lines_joined = arcpy.conversion.FeatureClassToFeatureClass(od_lines, r"in_memory", "od_lines_joined_"+str(row_id))
                arcpy.management.RemoveJoin(od_lines)
                arcpy.management.RemoveJoin(od_lines)
                
                # delete rows where i = j
                if del_i_eq_j == "true":
                    if origins_i_input == destinations_j_input:
                        if i_id == j_id:
                            arcpy.management.MakeFeatureLayer(od_lines_joined, "od_lines_view")
                            arcpy.management.SelectLayerByAttribute("od_lines_view", "NEW_SELECTION", "i_id <> j_id")
                            arcpy.management.SelectLayerByAttribute("od_lines_view", "SWITCH_SELECTION")
                            if int(arcpy.management.GetCount("od_lines_view").getOutput(0)) > 0:
                                arcpy.AddMessage("Deleting "+str(int(arcpy.management.GetCount("od_lines_view")[0]))+" lines where i = j...")
                                arcpy.management.DeleteRows("od_lines_view")
                        else:
                            arcpy.AddMessage("Can't delete where i = j: inputs don't match")
                    else:
                        arcpy.AddMessage("Can't delete where i = j: inputs don't match")
                
                # impedance functions
                o_j = '!o_j!'
                total_impedance_fieldname = "Total_Time"
                t_ij = '!'+total_impedance_fieldname+'!'
                
                # loop over selected impedance functions list
                arcpy.AddMessage("Calculating Accessibility...")
                for i in selected_impedance_function:
                    f_name = i
                    # define dictionary of functions with calls to parameters dictionary p
                    func = {
                        "pow": "(1 if {}<1 else ({}**-{}))".format(t_ij, t_ij, p[f_name]["b0"]),
                        "neg_exp": "(math.exp(-{}*{}))".format(t_ij, p[f_name]["b0"]),
                        "mgaus": "(math.exp(-{}**2/{}))".format(t_ij, p[f_name]["b0"]),
                        "cumr": "(1 if {}<={} else 0)".format(t_ij, p[f_name]["t_bar"]),
                        "cuml": "(1-{}/{} if {}<={} else 0)".format(t_ij, p[f_name]["t_bar"], t_ij, p[f_name]["t_bar"])
                    }
                    
                    impedance_f = func[p[f_name]["f"]]
                    arcpy.management.AddField(od_lines_joined, "Ai_"+f_name, "DOUBLE")
                    arcpy.management.CalculateField(od_lines_joined, "Ai_"+f_name, "{}*{}".format(o_j, impedance_f), "PYTHON3", None)
                
                # calcualte summary statistics
                arcpy.AddMessage("Summarizing Accessibility...")
                sum_fields = ["Ai_"+f_field+" SUM" for f_field in selected_impedance_function]
                sum_fields_str = ";".join(sum_fields)
                arcpy.analysis.Statistics(od_lines_joined, r"in_memory/od_statistics_"+str(row_id), sum_fields_str, "i_id")
                
                # append to master output table
                arcpy.AddMessage("Appending accessibility output for batch "+str(row_id)+" of "+str(polygon_count)+"...")
                arcpy.management.Append(r"in_memory/od_statistics_"+str(row_id), output_table, "NO_TEST")
                
                # clean up
                arcpy.management.Delete(r"in_memory/temp_origins_"+str(row_id))
                arcpy.management.Delete(r"in_memory/od_lines_"+str(row_id))
                arcpy.management.Delete(r"in_memory/od_lines_joined_"+str(row_id))
                arcpy.management.Delete(r"in_memory/od_statistics_"+str(row_id))
                
                # progress indicator
                output_progress = ((int(arcpy.management.GetCount(output_table).getOutput(0))/origins_i_count)*100)
                arcpy.AddMessage("Accessibility calculation is "+str(round(output_progress, 2))+" percent complete")
        
        if join_back_i == "true":
            # join accessibility output back to origins input
            join_fields = ["SUM_Ai_"+f_field for f_field in selected_impedance_function]
            join_fields.insert(0, "FREQUENCY")
            arcpy.AddMessage("Joining accessibility output to input i...")
            arcpy.management.JoinField(origins_i_input, i_id, output_table, "i_id", join_fields)
        
        # clean up
        arcpy.management.Delete(r"in_memory/origins_i_point")
        arcpy.management.Delete(r"in_memory/origins_i")
        arcpy.management.Delete(r"in_memory/origins_i_attr")
        arcpy.management.Delete(r"in_memory/destinations_j_point")
        arcpy.management.Delete(r"in_memory/destinations_j")
        arcpy.management.Delete(r"in_memory/destinations_j_attr")
        arcpy.management.Delete(r"in_memory/raster")
        arcpy.management.Delete(r"in_memory/polygons")
        
        arcpy.AddMessage("Finished accessibility calculation")
        return
