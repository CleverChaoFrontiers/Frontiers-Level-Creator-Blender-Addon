import bpy
import json
import os

def read_json_parameters(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return flatten_parameters(data.get('parameters', {}))
def isfldigit(stringvalue): #isdigit but for floats instead
    try:
        variablevalue = float(stringvalue)
        return True
    except:
        return False
#-------------------------------------------------------------------------------------------------------
#Driver connecting functions
#-------------------------------------------------------------------------------------------------------    
def connect_geo_to_param(obj, param_name, parameter_type,param,param_vector = None,list_type = None):
    # Find the geometry nodes modifier
    modifier = None
    for mod in obj.modifiers:
        if mod.type == 'NODES':
            modifier = mod
            break

    if not modifier:
        print("No Geometry Nodes modifier found.")
        return

    # Get the node tree from the modifier
    node_tree = modifier.node_group
    if not node_tree:
        print("No node tree found in the Geometry Nodes modifier.")
        return
    # Find and connect corresponding input attributes
    find_corresponding_input(node_tree, modifier, param_name, parameter_type, param,param_vector,list_type)
    
def find_corresponding_input(node_tree, modifier, param_name, parameter_type, param,param_vector,list_type):
    group_input = find_node_by_type(node_tree, 'GROUP_INPUT') #gets group input node
    if parameter_type == "list_value":
        param_name = param_name + f"[{param_vector}]"
            
    if param_name in group_input.outputs:
        print(f"Found param {param_name}")
        param_input = group_input.outputs[param_name] #gets the specific output
        if parameter_type == "enum_value": #if enumerator
            menu_node = None #enum depends on the new menu switch node in blender 4.1+. Do nothing if this node is not found.
            for link in param_input.links:
                if link.to_node.type == "MENU_SWITCH":
                    menu_node = link.to_node
                    
            if menu_node != None:
                param_list = [i.name for i in menu_node.inputs] #Creates list of the geonode enumerator items
                param_dict = {k: v for v, k in enumerate(param_list,-1)} #Creates dictionary of the geonode enumerator items and their index as the value
                driver_expression_list = []
                driver_expression_items = {}
                for index,param_items in enumerate(param.enum_items):
                    if param_items.value in param_dict: #creates expression for driver in form "option1 * index + option2 * index...etc". the option expressions will be 0 if not selected.
                        driver_expression_list.append(f'{param_items.value}*{param_dict[param_items.value]}')
                        driver_expression_items[param_items.value] = index
                driver_expression = "+".join(driver_expression_list)
                #print(f'json_parameters[{param.name}].enum_items[{driver_expression_items["Laser"]}].selected')
                #creating enumerator driver
                driver = modifier.driver_add(f'["{param_input.identifier}"]').driver #add driver to param_inputs menu slot (.identifier finds it)
                driver.type = 'SCRIPTED'
                # Set up the driver variables
                for variable_item in driver_expression_items:
                    var = driver.variables.new()
                    var.name = variable_item
                    var.type = 'SINGLE_PROP'
                    target = var.targets[0]
                    target.id_type = 'OBJECT'
                    target.id = bpy.context.object
                    target.data_path = f'json_parameters["{param.name}"].enum_items[{driver_expression_items[variable_item]}].selected'
                    
                #     Set the driver expression
                driver.expression = driver_expression
        elif parameter_type == "vector_value":

            for values in range(len(param_vector)):
                driver = modifier.driver_add(f'["{param_input.identifier}"]',int(values)).driver #add driver to param_inputs menu slot (.identifier finds it)
                driver.type = 'SCRIPTED'
                # Set up the driver variables
                var = driver.variables.new()
                var.name = "var"
                var.type = 'SINGLE_PROP'
                target = var.targets[0]
                target.id_type = 'OBJECT'
                target.id = bpy.context.object
                target.data_path = f'json_parameters["{param.name}"].{parameter_type}[{values}]'
                #     Set the driver expression
                driver.expression = var.name
        #elif parameter_type == "list_value":
        elif parameter_type == "list_value":
            driver = modifier.driver_add(f'["{param_input.identifier}"]').driver #add driver to param_inputs menu slot (.identifier finds it)
            driver.type = 'SCRIPTED'
            # Set up the driver variables
            var = driver.variables.new()
            var.name = "var"
            var.type = 'SINGLE_PROP'
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = bpy.context.object
            target.data_path = f'json_parameters["{param.name}"].{parameter_type}[{param_vector}].{list_type}'
                
            #     Set the driver expression
            driver.expression = var.name
        else:
            driver = modifier.driver_add(f'["{param_input.identifier}"]').driver #add driver to param_inputs menu slot (.identifier finds it)
            driver.type = 'SCRIPTED'
            # Set up the driver variables
            var = driver.variables.new()
            var.name = "var"
            var.type = 'SINGLE_PROP'
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = bpy.context.object
            target.data_path = f'json_parameters["{param.name}"].{parameter_type}'
                
            #     Set the driver expression
            driver.expression = var.name

def find_node_by_type(node_tree, node_type):
    """Find a node by its type."""
    for node in node_tree.nodes:
        if node.type == node_type:
            return node
    return None

#-------------------------------------------------------------------------------------------------------
#parameter import
#-------------------------------------------------------------------------------------------------------
def flatten_parameters(parameters, parent_key='', separator='/'): #This is for getting the parameters and putting it into the parameter group variable in the object
    items = []
    for key, value in parameters.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key #this is in case we are in a nested layer
        if isinstance(value, dict):
            items.extend(flatten_parameters(value, new_key, separator=separator).items()) #if a nested layer, do the parameter thing in there
        elif isinstance(value, list):
            if value == []: #if empty list, output value as a string (WRONG WAY SO FAR, NEED TO FIND A SOLUTION FOR LISTS)
                items.append((new_key, str(value)))
            else:
                dictinlist =True #If nested parameters in a list, this stays true
                for listitem in value:
                    if isinstance(listitem, dict) == False or value == []: #goes through list. Nested parameters in lists are dictionaries. if one of the values aren't a dictionary, it is not a nested parameter
                        dictinlist = False
                        break
                if dictinlist == True: #if list nested, create parameters for the gruop per object in the dictionaries
                    listindex = -1
                    for v in value:
                        listindex += 1
                        items.extend(flatten_parameters(v, f'{new_key}[{listindex}]', separator=separator).items())
                elif dictinlist == False: #if not nested. Same strategy for dict, but checks for three numbers. if three numbers, it's a vector and outputs as such
                    vectorlist = True         
                    if len(value) == 3:
                        for listitem in value:
                            
                            if isinstance(listitem, (float,int)) == False:
                                vectorlist = False
                    elif len(value) != 0:
                        vectorlist = False
                    if vectorlist == True:
                        
                        items.append((new_key, value))
                    else: #Prints list as string, which again is incorrect.
                        items.append((new_key, str(value)))
        else:
            items.append((new_key, value))
    return dict(items)
def get_rfl_filepath(obj_name):
    enumerator_list = {}
    file_name = "Other\\rangers-rfl.json"
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Finds path to the folder this script is in [DO NOT TOUCH]
    blend_file_path = bpy.data.filepath # Finds file path of Blender file
    blend_dir = os.path.dirname(blend_file_path) # Gets the name of the directory the Blender file is in
    path_dir = os.path.join(blend_dir,script_dir) # Joins the paths from the blender file to the script file
    rfl_path = os.path.join(path_dir, file_name)
    with open(rfl_path, 'r') as f:
        data = json.load(f)
    objName_list = [f"Obj{obj_name}Spawner",f"Enemy{obj_name}Spawner",f"Boss{obj_name}Spawner",f"MiniBoss{obj_name}Spawner"]
    #print(obj_name)
    #-------------------------------------------------------------------------------------------------------
    #Some objects are named differently in the rfl and should be added here
    #-------------------------------------------------------------------------------------------------------
    if obj_name == "EventCondition" or obj_name == "EventTrigger":
        objName_list.append("ObjEventSetterSpawner")
    elif obj_name == "SoundSourcePoint":
        objName_list.append("ObjPointSoundSourceSpawner")
    elif obj_name == "CarVan" or obj_name == "CarHatchback" or obj_name == "CarMinivan":
        objName_list.append("ObjCarSpawner")
    elif obj_name == "NormalFloor2m" or obj_name == "NormalFloor10m":
        objName_list.append("ObjNormalFloorSpawner")
    elif obj_name == "JumpBoard":
        objName_list.append("ObjJumpBoardPathSpawner")
    
    #print(objName_list)
    for full_obj_name in objName_list:
        if full_obj_name in data:
            obj = data[full_obj_name]
            # Iterate through the members of the object
            for member in obj['members']:
                if member['type'] == 'enum':
                    # Get the name of the enum used by this member
                    enum_name = member['enum']
                    top_name = member['name']
                    # Check if the enum is defined in the enums dictionary of the object
                    if enum_name in obj['enums']:
                        # Fetch the enum dictionary
                        enum_dict = obj['enums'][enum_name]
        
                        # Store the keys (names of the enum values) along with their numerical values
                        enumerator_list[top_name] = list(enum_dict.keys())
                elif member['type'] == 'struct':
                    # Get the name of the enum used by this member
                    top_struct_name = member['name']
                    struct_name = member['struct']
                    if struct_name in data:
                        struct_obj = data[struct_name]
                        # Iterate through the members of the object
                        for struct_member in struct_obj['members']:
                            if struct_member['type'] == 'enum':
                                # Get the name of the enum used by this member
                                struct_enum_name = struct_member['enum']
                                struct_name = struct_member['name']
                                nested_struct_name = f"{top_struct_name}/{struct_name}"
                                # Check if the enum is defined in the enums dictionary of the object
                                if struct_enum_name in struct_obj['enums']:
                                    # Fetch the enum dictionary
                                    enum_dict = struct_obj['enums'][struct_enum_name]
                    
                                    # Store the keys (names of the enum values) along with their numerical values
                                    enumerator_list[nested_struct_name] = list(enum_dict.keys())
                    
                                    # Store the keys (names of the enum values) along with their numerical values
                                    enumerator_list[nested_struct_name] = list(enum_dict.keys())
    return enumerator_list
def get_json_filepath(obj_name,obj): #gets the path to the templates
    volume_objects = ["CameraFollow", "CameraPan","CameraFix","CameraRailSideView","CameraRailForwardView"] #Only volumes with double code/ this was for stopping the code if it is any of these... but it will already output an error anyway. leave it for now
    
    Customdir = False
    txt_file_names = [] #set custom template list
    addonName = __package__
    addonName = addonName.split(".") #package gives the name of the add-on plus operator folder but we want the name of the add-on only. Split package to take only the name
    preference = bpy.context.preferences
    addon_prefs = preference.addons[addonName[0]].preferences #get the preference
        
    if addon_prefs.CustomTemplatePath != '': #if there is a custom directory defined
            
        CustomDirectory_path = addon_prefs.CustomTemplatePath #get path from preferenses
        try:
                
            txt_files = [file for file in os.listdir(CustomDirectory_path) if file.endswith('.json')]
            if not txt_files:
                pass
            else:    
                Customdir = True
                for file in txt_files:
                    txt_file_names.append((file.split("."))[0])
                
        except Exception as direcerror:
            print(f'Custom directory gave this error: {direcerror}')
        pass
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Finds path to the folder this script is in [DO NOT TOUCH]
    blend_file_path = bpy.data.filepath # Finds file path of Blender file
    blend_dir = os.path.dirname(blend_file_path) # Gets the name of the directory the Blender file is in
    path_dir = os.path.join(blend_dir,script_dir) # 
    if Customdir == True and obj_name in txt_file_names: #Check if the object is one of the custom ones.
        file_name = f"{obj_name}.json"
        filepath = os.path.join(CustomDirectory_path, file_name)
    elif obj_name not in volume_objects or "FrontiersCamera" in obj:
        file_name = f"objects\{obj_name}.json" 
        filepath = os.path.join(path_dir, file_name)
    return filepath

def update_parameters(self, context):
    obj = context.object
    if obj.use_display_json_parameters == False:
        if obj.animation_data is not None and obj.animation_data.drivers:
            for driver in obj.animation_data.drivers:
                obj.animation_data.drivers.remove(driver)
    obj_name = obj.name.split('.', 1)[0]
    
    json_filepath = get_json_filepath(obj_name,obj)
    rfl_enum = get_rfl_filepath(obj_name)
    if os.path.exists(json_filepath):
        parameters = read_json_parameters(json_filepath)
        obj.json_parameters.clear()
        #add the parameter to the objects custom property
        for key, value in parameters.items():
            sepkey = key
            row = obj.json_parameters.add()
            if "[" in key:
                sepkey = key.split("[")[0] + key.split("]")[1]
            if sepkey in rfl_enum and "[" not in value :
                row.name = f"{key}/enum"
                # Clear existing items and add new ones based on rfl_enum
                row.enum_items.clear()
                for enum_option in rfl_enum[sepkey]:
                    enum_item = row.enum_items.add()
                    enum_item.value = enum_option
                    if value == enum_option:
                        enum_item.selected = True
                if obj.use_display_json_parameters and (4,1,0) <= bpy.app.version: #Only enum for blender 4.1 or higher
                    connect_geo_to_param(obj,key,"enum_value",row)
            elif isinstance(value, float):
                row.name = f"{key}/float"
                row.float_value = value
                if obj.use_display_json_parameters:
                    connect_geo_to_param(obj,key,"float_value",row)
            elif isinstance(value, bool):
                row.name = f"{key}/bool"
                row.bool_value = value
                if obj.use_display_json_parameters:
                    connect_geo_to_param(obj,key,"bool_value",row)
            elif isinstance(value, int):
                row.name = f"{key}/int"
                row.int_value = value
                if obj.use_display_json_parameters:
                    connect_geo_to_param(obj,key,"int_value",row)
            elif isinstance(value, list) and len(value) == 3 and (isfldigit(value[0])):
                
                row.name = f"{key}/vector"
                row.vector_value = value
                if obj.use_display_json_parameters:
                    connect_geo_to_param(obj,key,"vector_value",row,row.vector_value)
            elif isinstance(value, str):
                if "[" in value:
                    row.name = f"{key}/list"
                    listfromvalue = value.strip('][').split(', ')
                    #print(listfromvalue)
                    for item_value in listfromvalue:
                        if item_value.replace("-","",1).isdigit(): #Negative sign removed for check.
                            row.name = f"{key}/listINT"
                            list_item = row.list_value.add()
                            list_item.listint = int(item_value)
                            list_index = listfromvalue.index(str(list_item.listint))
                            
                            if obj.use_display_json_parameters:
                                connect_geo_to_param(obj,key,"list_value",row,list_index,"listint")
                        elif isfldigit(item_value):
                            row.name = f"{key}/listFLOAT"
                            list_item = row.list_value.add()
                            list_item.listfloat = float(item_value)
                            list_index = listfromvalue.index(str(list_item.listfloat))
                            
                            if obj.use_display_json_parameters:
                                connect_geo_to_param(obj,key,"list_value",row,list_index,"listfloat")
                        else:
                            list_item = row.list_value.add()
                            stringitem = str(item_value)
                            while ("'" in stringitem):
                                stringitem=stringitem.replace("'", "")
                            while ('"' in stringitem):
                                stringitem=stringitem.replace('"', '')
                            list_item.liststring = stringitem
                    
                else:
                    row.name = f"{key}/string"
                    row.string_value = value
            else:
                row.name = f"{key}/ERR"
                
def update_enum_selection(self, context):
    obj = context.object
    # Identify the parent JsonParameter of the current EnumItem
    parent_param = None

    # Loop through all json parameters to find the parameter with this EnumItem
    for param in obj.json_parameters:
        if "enum" in param.name:
            for item in param.enum_items:
                if item == self:
                    parent_param = param
                    break
        if parent_param is not None:
            break

    # Update only the enum items within the same JsonParameter
    if parent_param:
        for item in parent_param.enum_items:
            if item != self and self.selected:
                item.selected = False
class JsonParameterListItem(bpy.types.PropertyGroup):
    selected: bpy.props.BoolProperty(name="Selected",update=update_enum_selection)
    value: bpy.props.StringProperty(name="Value")

class parametersListvalues(bpy.types.PropertyGroup):
    liststring: bpy.props.StringProperty()
    listint: bpy.props.IntProperty()
    listfloat: bpy.props.FloatProperty()
    listobject: bpy.props.PointerProperty(
        name="ObjectID",
        description = "Choose Object to take ID from (will override text)",
        type=bpy.types.Object
    )
class JsonParametersPropertyGroup(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    float_value: bpy.props.FloatProperty(name="Float Value")
    int_value: bpy.props.IntProperty(name="Integer Value")
    bool_value: bpy.props.BoolProperty(name="Integer Value")
    vector_value: bpy.props.FloatVectorProperty(name="Vector Value", size=3)
    list_value: bpy.props.CollectionProperty(type=parametersListvalues)
    expanded: bpy.props.BoolProperty(name="Expanded", default=False)
    string_value: bpy.props.StringProperty(name="String Value")
    object_value: bpy.props.PointerProperty(
        name="ObjectID",
        description ="Choose Object to take ID from (will override text)",
        type=bpy.types.Object
    )
    enum_items: bpy.props.CollectionProperty(type=JsonParameterListItem)


class OBJECT_PT_JsonParameters(bpy.types.Panel):
    bl_label = "Frontiers Level creator: Gedit/Hson parameters from template"
    bl_idname = "OBJECT_PT_json_parameters"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        if obj:
            row = layout.row()
            row.prop(obj, "use_display_json_parameters", text="Set Gedit/JSON Parameters Manually")
            
            if obj.use_display_json_parameters:
                if obj.type == 'LIGHT':
                    layout.label(text="Warning: Blender light settings will take priority. Only options not covered by blender will be changed")
                else:
                    layout.label(text="Warning: this will override parameters set by Geometry Nodes.")
                for item in obj.json_parameters:
                    name = item.name
                    
                    data_type = item.name.split('/')
                    menuName = str(data_type[:-1])
                    if data_type[-1] == "enum":
                        selected_value = None
                        for enum_item in item.enum_items:
                            if enum_item.selected:
                                selected_value = enum_item.value
                                break
                        display_name = f"{menuName}: {selected_value}" if selected_value else menuName
                        box = layout.box()
                        row = box.row()
                        icon = 'TRIA_DOWN' if item.expanded else 'TRIA_RIGHT'
                        op = row.operator("wm.context_toggle", text=display_name, emboss=False, icon=icon)
                        op.data_path = f"object.json_parameters[{obj.json_parameters.find(name)}].expanded"
    
                        if item.expanded:
                            for enum_item in item.enum_items:
                                row = box.row()
                                row.prop(enum_item, "selected", text=enum_item.value)
                    else:
                        if data_type[-1] == "ERR":
                            layout.label(text=f"{menuName}: Not compatible")
                        elif data_type[-1] == "float":
                            layout.prop(item, "float_value", text=menuName)
                        elif data_type[-1] == "int":
                            layout.prop(item, "int_value", text=menuName)
                        elif data_type[-1] == "bool":
                            layout.prop(item, "bool_value", text=menuName)
                        elif data_type[-1] == "vector":
                            layout.prop(item, "vector_value", text=menuName)
                        elif data_type[-1] == "string":
                            row = layout.row()
                            row = row.split(factor=0.6)
                            row.prop(item, "string_value", text=menuName)
                            row.prop(item, "object_value")
                        elif data_type[-1].startswith("list"):
                            box = layout.box()
                            split = box.split(factor=0.9)
                            col = split.column()
                            col.label(text=menuName)
                            
                            # Draw the list items
                            for list_item in item.list_value:
                                if data_type[-1]=="listINT":
                                    col.prop(list_item, "listint", text="")
                                elif data_type[-1]=="listFLOAT":
                                    col.prop(list_item, "listfloat", text="")
                                else:
                                    row = col.row()
                                    row = row.split(factor=0.6)
                                    row.prop(list_item, "liststring", text="")
                                    row.prop(list_item, "listobject")
                                
                            # Add and Remove buttons
                            col = split.column(align=True)
                            col.operator("object.add_list_item", text="", icon="ADD").index = obj.json_parameters.find(item.name)
                            col.operator("object.remove_list_item", text="", icon="REMOVE").index = obj.json_parameters.find(item.name)
class OBJECT_OT_AddListItem(bpy.types.Operator):
    bl_idname = "object.add_list_item"
    bl_label = "Add List Item"
    index: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.object
        if obj:
            obj.json_parameters[self.index].list_value.add()
        return {'FINISHED'}

# Operator to remove a list item
class OBJECT_OT_RemoveListItem(bpy.types.Operator):
    bl_idname = "object.remove_list_item"
    bl_label = "Remove List Item"
    index: bpy.props.IntProperty()

    def execute(self, context):
        obj = context.object
        if obj:
            obj.json_parameters[self.index].list_value.remove(len(obj.json_parameters[self.index].list_value)-1)   
        return {'FINISHED'}
bpy.types.Object.use_display_json_parameters = bpy.props.BoolProperty(
    name="Display JSON Parameters",
    default=False,
    update=update_parameters
)
