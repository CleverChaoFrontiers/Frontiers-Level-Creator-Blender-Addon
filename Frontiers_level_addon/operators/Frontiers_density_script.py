import bpy
import os
from bpy.types import WindowManager
from bpy.props import (
    StringProperty,
    EnumProperty,
    IntProperty
)
import mathutils
import json
import random
import copy
import bmesh
from math import radians
from math import degrees

def enum_previews_from_directory_items(self, context): #Function that finds the thumbnails
    """EnumProperty callback"""
    enum_items = []
    if context is None:
        return enum_items
    World_check = context.scene.FrontiersDensityProperties.Frontiers_Density_World
    wm = context.window_manager
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Finds path to the folder this script is in [DO NOT TOUCH]
    blend_file_path = bpy.data.filepath # Finds file path of Blender file
    blend_dir = os.path.dirname(blend_file_path) # Gets the name of the directory the Blender file is in
    path_dir = os.path.join(blend_dir,script_dir)
    #Set up compatible objects depending on the files in template file
    directories = {
        "density_Kronos": r"density\Frontiers density pack\Thumbnails\kronos",
        "density_Aries": r"density\Frontiers density pack\Thumbnails\aries",
        "density_Chaos": r"density\Frontiers density pack\Thumbnails\chaos",
        "density_SkySanctuary": r"density\Frontiers density pack\Thumbnails\skysanctuary",
        "density_GreenHill": r"density\Frontiers density pack\Thumbnails\greenhill",
        "density_ChemicalPlant": r"density\Frontiers density pack\Thumbnails\chemicalplant",
        "density_Highway": r"density\Frontiers density pack\Thumbnails\highway"
    }
    Thumbnail_pathname = directories.get(World_check, "")
    directory = os.path.join(path_dir, Thumbnail_pathname) #sets the file path to the thumbnails

    # Get the preview collection (defined in register func).
    pcoll = preview_collections["main"]

    if directory == pcoll.Frontiers_Density_thumbnail_dir:
        return pcoll.Frontiers_Density_thumbnail

    print("Scanning directory: %s" % directory)

    if directory:
        print("found density thumbnails directory")
        # Scan the directory for png files
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".jpg"):
                image_paths.append(fn)
        
        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.Frontiers_Density_thumbnail = enum_items
    pcoll.Frontiers_Density_thumbnail_dir = directory
    return pcoll.Frontiers_Density_thumbnail

def load_mesh_object(filepath, object_name):
    try:
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            data_to.objects = [object_name]
    except ValueError as e:
        return str(e)
    return False

class OBJECT_OT_duplicate_link_with_nodes(bpy.types.Operator):
    bl_idname = "object.duplicate_link_with_nodes"
    bl_label = "Paint Density Objects on selected object"
    bl_description = "Paint density objects on the selected object with weightpaint mode (will create a scatter object in density collection)"
    def execute(self, context):
        collection_name = context.scene.FrontiersDensityProperties.Frontiers_Density_collection #sets chosen collection
        if collection_name is None: #no selected collection, warns the users to choose an object
            self.report({'ERROR'}, "No collection selected")
            return {'CANCELLED'}
        selected_object = bpy.context.view_layer.objects.active #sets object to scatter on from selected object
        selected_object.select_set(True)
        if selected_object is None: #no selected object, warns the users to choose an object
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}
        bpy.ops.object.mode_set(mode='OBJECT') #set to object mode
        bpy.ops.object.duplicate_move_linked(OBJECT_OT_duplicate={"linked":True}) #make a duplicate object for scattering
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Finds path to the folder this script is in [DO NOT TOUCH]
        blend_file_path = bpy.data.filepath # Finds file path of Blender file
        blend_dir = os.path.dirname(blend_file_path) # Gets the name of the directory the Blender file is in
        path_dir = os.path.join(blend_dir,script_dir)
        nodetree_pathname = f"density\density_settings.blend" #path to blend with node tree
        filepath = os.path.join(path_dir, nodetree_pathname)
        World_check = context.scene.FrontiersDensityProperties.Frontiers_Density_World
        
        nodetree_name = "FrontiersDensitySettings" #name of the scatter geo nodetree

        try:
            with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to): #try loading the nodetree. Cancel script if failed
                data_to.node_groups = [nodetree_name]
        except ValueError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        
        duplicated_object = context.active_object
        geo_node_mod = duplicated_object.modifiers.new(name="FrontiersDensity", type='NODES')
        geo_node_mod.node_group = bpy.data.node_groups[nodetree_name]
        
        DensityAsset_directories = {
            "density_Kronos": r"density\Frontiers density pack\Frontiers Density Pack- Kronos.blend",
            "density_Aries": r"density\Frontiers density pack\Frontiers Density Pack- Aries.blend",
            "density_Chaos": r"density\Frontiers density pack\Frontiers Density Pack- Chaos.blend",
            "density_SkySanctuary": r"density\Frontiers density pack\Frontiers Density Pack- Sky sanctuary.blend",
            "density_GreenHill": r"density\Frontiers density pack\Frontiers Density Pack- Green hill.blend",
            "density_ChemicalPlant": r"density\Frontiers density pack\Frontiers Density Pack- Chemical plant.blend",
            "density_Highway": r"density\Frontiers density pack\Frontiers Density Pack- Highway.blend"
        }
        if context.scene.FrontiersDensityProperties.UseCustomDensityObject:
                bpy.ops.object.select_all(action='DESELECT')
                density_object = context.scene.FrontiersDensityProperties.CustomDensityObject
                if density_object == None:
                    bpy.ops.mesh.primitive_cube_add(size = 1.0)
                    density_object =  bpy.context.view_layer.objects.active
                    density_object["FrontiersDensityID"] = context.scene.FrontiersDensityProperties.CustomDensityID
                    self.report({'INFO'}, f"No object was selected for advanced scatter. Created {density_object.name} as substitute, with index {context.scene.FrontiersDensityProperties.CustomDensityID}")
                density_object.select_set(True)
                bpy.context.view_layer.objects.active = density_object
                if "FrontiersDensityID" in density_object:
                    index = density_object["FrontiersDensityID"]
                else:
                    index = context.scene.FrontiersDensityProperties.CustomDensityID
                    density_object["FrontiersDensityID"] = index
                    self.report({'INFO'}, f"No Index on object. Setting scatter index to {index} from advanced menu")
                weight_map_object_name = f'DensityID{index}-{density_object.name}'
        else:
            try:
                chosen_object_index = int(bpy.data.window_managers["WinMan"].Frontiers_Density_thumbnail.split("-")[0])
            except:
                print("No valid density object index found")
                return {'CANCELLED'}
                    # New functionality to import mesh based on index
            index = chosen_object_index
            filepath_Assets = DensityAsset_directories.get(World_check, "")
            filepath_objects = os.path.join(path_dir, filepath_Assets)
            object_name = self.find_and_link_object_by_index(context, filepath_objects, index)
            if object_name:
                self.append_and_cleanup(context, filepath_objects, object_name)
                self.report({'INFO'}, f"Appended object {object_name}")
            else:
                self.report({'WARNING'}, "No object found with index: {}".format(index))

                return {'FINISHED'}
            bpy.data.collections["Imported_density_assets"].hide_viewport = False
            density_object = bpy.context.view_layer.objects.active
            bpy.data.collections["Imported_density_assets"].hide_viewport = True
            weight_map_object_name = density_object.name
        density_weight_map = f'Density-map-{weight_map_object_name}'
        bpy.ops.object.select_all(action='DESELECT')
        duplicated_object.select_set(True)
        bpy.context.view_layer.objects.active = duplicated_object
        duplicated_object.modifiers[geo_node_mod.name]["Input_2"] = density_object
        duplicated_object["FrontiersDensityID"] = density_object["FrontiersDensityID"]
        duplicated_object.name = "Frontiers_Density_scatter"
        bpy.ops.collection.objects_remove_all()
        bpy.data.collections[collection_name.name].objects.link(duplicated_object)
        bpy.ops.object.select_all(action='DESELECT')
        selected_object.select_set(True)
        bpy.context.view_layer.objects.active = selected_object
        nameindexgroup = 0
        while density_weight_map in duplicated_object.vertex_groups:
            nameindexgroup += 1
            density_weight_map = f'Density-map-{density_object.name}_{nameindexgroup}'
        duplicated_object.vertex_groups.new(name = density_weight_map)
        duplicated_object.modifiers[geo_node_mod.name]["Input_4"] = density_weight_map
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        
        return {'FINISHED'}
    def find_and_link_object_by_index(self, context, filepath, index):
        object_name = None
        with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
            data_to.objects = data_from.objects

        # Temporarily link objects to inspect properties
        for obj in data_to.objects:
            context.collection.objects.link(obj)
            if "FrontiersDensityID" in obj and obj["FrontiersDensityID"] == index:
                object_name = obj.name
            context.collection.objects.unlink(obj)
            bpy.data.objects.remove(obj)

        return object_name

    def append_and_cleanup(self, context, filepath, object_name):
        # Append the object by its name from the other blend file
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            data_to.objects = [obj for obj in data_from.objects if obj == object_name]

        # After appending, the object is available in the current data
        # Now, link this object to the desired collection
        appended_obj = bpy.data.objects.get(object_name)
        if appended_obj is not None:
            # Ensure there's a specific collection to place the object in
            collection_name = "Imported_density_assets"
            collection = bpy.data.collections.get(collection_name)
            if not collection:
                collection = bpy.data.collections.new(name=collection_name)
                context.scene.collection.children.link(collection)

            # Check if the object is already in the collection, if not, link it
            if appended_obj.name not in collection.objects:
                collection.objects.link(appended_obj)
            # Deselect all objects first to ensure only the appended object is selected
            bpy.ops.object.select_all(action='DESELECT')
            appended_obj.select_set(True)
            bpy.context.view_layer.objects.active = appended_obj
class FrontiersDensityProperties(bpy.types.PropertyGroup):#Note that chemical plant do not have density objects
    Frontiers_Density_World: EnumProperty( 
        items=[("density_GreenHill","Green Hill","Green Hill Density objects"),("density_SkySanctuary","Sky Sanctuary","Sky Sanctuary Density objects"),("density_Highway","Highway","Highway Density objects")],
        name ="", update=lambda self, context: update_thumbnail_previews(self, context) )
    # Open-zone too big. Removed for the moment. Heres the code to copy into items, whenever the assetpack is filled: ("density_Kronos","Kronos","Kronos Density objects"),("density_Aries","Aries","Aries Density objects"),("density_Chaos","Chaos","Chaos Density objects"),
    Frontiers_Density_collection: bpy.props.PointerProperty(
        name="Density Collection",
        description = "Choose Density Collection",
        type=bpy.types.Collection
    )
    CustomDensityID: bpy.props.IntProperty(
        name="Index",
        description = "Set Density index to export to the selected object",
        min = 0,
        soft_min = 0)
    CustomDensityObject: bpy.props.PointerProperty(
        name="Custom Density Object",
        description = "Choose Object to use for density (Will not show up in game. For Open Zone, this can be used to place any density object with any ID. For custom density object you will have to export the density object yourself).",
        type=bpy.types.Object
    )
    UseCustomDensityObject: bpy.props.BoolProperty(
        name="Use object for scatter",
        description="Uses the object below for scattering instead of the density assets above.",
        default = False)
class remove_densityscatter(bpy.types.Operator):
    bl_idname = "object.frontiers_remove_densityscatter"
    bl_label = "Remove scatter from object"
    bl_description = "Remove all scatter objects and all density vertex groups associated with the selected object"
    bl_options = {'UNDO'}
    def execute(self,context):
        selected_object = bpy.context.view_layer.objects.active #sets object to scatter on from selected object
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        selected_object.select_set(True)
        if selected_object is None: #no selected object, warns the users to choose an object
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}

            
        bpy.context.view_layer.objects.active = selected_object #makes sure only one object is selected
        og_mesh = selected_object.data
        for blender_object in bpy.data.objects:
            if blender_object.data == og_mesh and blender_object.name.startswith("Frontiers_Density_scatter"):
               bpy.data.objects.remove(blender_object)
        for vertex_group in selected_object.vertex_groups:
            if vertex_group.name.startswith("Density-map-DensityID"):
                selected_object.vertex_groups.remove(vertex_group)
        return {'FINISHED'}
class OBJECT_OT_FrontiersPointCloudExport(bpy.types.Operator):
    bl_idname = "object.frontiers_export_pointcloud"
    bl_label = "Export Density Pointcloud"
    
    def execute(self, context):
        collection = context.scene.FrontiersDensityProperties.Frontiers_Density_collection # Name of collection that will be exported goes here
        printCode = [] # This is tha variable that will hold the code to be printed
        numObjects = len(collection.all_objects) # This counts the number of objects to go though (used for the progress meter)
        objectsDone = 0 # Starts the progress meter at 0

        # Creates the template json (It's easier in this case to create it here instead of an external file since it's easy to edit and is quite short)
        template = {"TypeIndex": 0, 
                    "UnknownUInt32_1": 16777216, 
                    "Position": {
                        "X": 0.0,
                        "Y": 0.0,
                        "Z": 0.0 },
                    "Rotation": {
                        "X": 0.0,
                        "Y": 0.0,
                        "Z": 0.0,
                        "W": 0.0,
                        "IsIdentity": False }, # Not sure what this bit does, more research required
                    "Scale": {
                        "X": 1.0,
                        "Y": 1.0,
                        "Z": 1.0 },
                    "Colour": {
                        "Red": 131,
                        "Green": 161,
                        "Blue": 127,
                        "Alpha": 255 }
                    }
        
        for obj in collection.objects: # Goes through every object in the chosen collection
            
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='OBJECT')
            if obj.type == "MESH" and "FrontiersDensityID" in obj and "FrontiersDensityAsset" in obj: # This part processes single density objects
                #print(f" No Modifier for {obj.name}")
                # This part gets all of the properties needed
                objectPosition = obj.location # Gets the object's location
                original_rotation_mode = obj.rotation_mode
                obj.rotation_mode = 'QUATERNION'
                
                
                #objectRotation = mathutils.Vector((obj.rotation_quaternion.x, obj.rotation_quaternion.z, -obj.rotation_quaternion.y, obj.rotation_quaternion.w)) # Gets the object's rotation as a quaternion (A type of Rotation) compatible with Sonic Frontiers
                objectScale = obj.scale # Gets the object's scale (yay, scale support!)
                    
                objectCode = template # Copies the template over to a new variable that will be edited
                    
                # This part sets all of the correct values in the code
                objectCode["TypeIndex"] = obj["FrontiersDensityID"] # Sets ID
                    
                objectCode["Position"]["X"] = objectPosition.x # Sets X position
                objectCode["Position"]["Y"] = objectPosition.z # Sets Y position
                objectCode["Position"]["Z"] = -objectPosition.y # Sets Z position
                    
                objectCode["Rotation"]["X"] = obj.rotation_quaternion.x # Sets X rotation
                objectCode["Rotation"]["Y"] = obj.rotation_quaternion.z # Sets Y rotation
                objectCode["Rotation"]["Z"] = -obj.rotation_quaternion.y # Sets Z rotation
                objectCode["Rotation"]["W"] = obj.rotation_quaternion.w # Sets W rotation
                    
                objectCode["Scale"]["X"] = objectScale.x # Sets X scale
                objectCode["Scale"]["Y"] = objectScale.z # Sets Y scale
                objectCode["Scale"]["Z"] = objectScale.y # Sets Z scale
                    
                objectCode["Colour"]["Red"] = 131 # Sets Red colour based on hex code in object name
                objectCode["Colour"]["Green"] = 161 # Sets Green colour based on hex code in object name
                objectCode["Colour"]["Blue"] = 127 # Sets Blue colour based on hex code in object name
                objectCode["Colour"]["Alpha"] = 255 # Sets Alpha colour based on hex code in object name
                    
                printCode.append(copy.deepcopy(objectCode)) # Adds the object's code to the full code that will be printed at the end
                obj.rotation_mode = original_rotation_mode
            elif obj.type == "MESH" and "FrontiersDensity" in obj.modifiers: # This part generates an object at every vertex in the mesh
                #print(f"Modifier for {obj.name} with {obj['FrontiersDensityID']}")
                bpy.ops.object.duplicate(linked=True, mode='TRANSLATION')
                dup_obj = bpy.context.active_object
                # Ensure we're in object mode
                if bpy.context.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')
                for modifiers in dup_obj.modifiers:
                    bpy.ops.object.modifier_apply(modifier=modifiers.name,single_user=True)
                bpy.ops.object.select_all(action='DESELECT')
                dup_obj.select_set(True)
                bpy.context.view_layer.objects.active = dup_obj
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                bpy.ops.object.mode_set(mode='EDIT') # Switches to Edit Mode
                bm = bmesh.from_edit_mesh(dup_obj.data) # Gets the Blender Mesh from the object
                
                numVerts = len(bm.verts) # This counts the number of vertices to go though (used for the progress meter)
                vertsDone = 0 # Starts the progress meter at 0
                
                for face in bm.faces:
                    original_rotation_mode = dup_obj.rotation_mode
                    #dup_obj.rotation_mode = 'QUATERNION'
                    # This part gets all of the properties needed
                    objectPosition = face.calc_center_median() + dup_obj.location # Gets the vertex's location
                    
                    objectRotation = face.normal.to_track_quat('Z', 'Y')

                    objectCode = template # Copies the template over to a new variable that will be edited
                    
                    # This part sets all of the correct values in the code
                    objectCode["TypeIndex"] = dup_obj["FrontiersDensityID"] # Sets ID
                    
                    objectCode["Position"]["X"] = objectPosition.x # Sets X position
                    objectCode["Position"]["Y"] = objectPosition.z # Sets Y position
                    objectCode["Position"]["Z"] = -objectPosition.y # Sets Z position
                    
                    objectCode["Rotation"]["X"] = objectRotation.x # Sets X rotation
                    objectCode["Rotation"]["Y"] = objectRotation.z # Sets Y rotation
                    objectCode["Rotation"]["Z"] = -objectRotation.y # Sets Z rotation
                    objectCode["Rotation"]["W"] = objectRotation.w # Sets W rotation
                    
                    objectCode["Colour"]["Red"] = 179 # Sets Red colour 
                    objectCode["Colour"]["Green"] = 223 # Sets Green colour 
                    objectCode["Colour"]["Blue"] = 127 # Sets Blue colour 
                    objectCode["Colour"]["Alpha"] = 233 # Sets Alpha colour 
                    
                    printCode.append(copy.deepcopy(objectCode)) # Adds the object's code to the full code that will be printed at the end
                    
                    vertsDone += 1
                    print(f"{obj.name}   \t{round(degrees(face.normal.x), 3)},{round(degrees(face.normal.z), 3)},{round(degrees(face.normal.y), 3)}   \t{vertsDone}/{numVerts}\t{round((vertsDone / numVerts) * 100, 2)}%\t{round((objectsDone / numObjects) * 100, 2)}%") # Debug
                    #print(f"{obj.name}   \t{vertex.index}   \t{vertsDone}/{numVerts}\t{round((vertsDone / numVerts) * 100, 2)}%\t{round((objectsDone / numObjects) * 100, 2)}%") # This prints the progress on this particular mesh to the console
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.delete(use_global=False)
            objectsDone += 1
            print(f"{obj.name}  \t{objectsDone}/{numObjects}\t{round((objectsDone / numObjects) * 100, 2)}%") # This prints the progress to the console
            
        
        bpy.ops.wm.window_new() # Opens a new window
        textWindow = bpy.data.texts.new("Density") # Creates a new text
        textWindow.write(json.dumps(printCode, indent = 2)) # Adds the code to the text
        context.area.type = 'TEXT_EDITOR'
        context.space_data.text = textWindow
        return {'FINISHED'}
def update_thumbnail_previews(self, context):
    wm = context.window_manager
    current_value = getattr(wm, "Frontiers_Density_thumbnail", None)
    # new_value = enum_previews_from_directory_items(self, context)
    # if current_value != new_value:
    #     wm.Frontiers_Density_thumbnail = new_value

class DensityPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Frontiers Density Panel"
    bl_idname = "OBJECT_PT_previews"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Frontiers Level Creator'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        Density_props = context.scene.FrontiersDensityProperties
        row = layout.row()
        row.label(text = "Select Collection")
        row = layout.row()
        row.label(text = "to put scattered assets in and to export:")
        row = layout.row()
        row.prop(Density_props,"Frontiers_Density_collection")
        row = layout.row()
        row.label(text = "Select world")
        row.prop(Density_props, "Frontiers_Density_World")
        row = layout.row()
        row.label(text = "Select density object to scatter:")
        row = layout.row()
        row.template_icon_view(wm, "Frontiers_Density_thumbnail")
        row = layout.row()
        row.operator("object.duplicate_link_with_nodes",icon = "MOD_VERTEX_WEIGHT")
        row.operator("object.frontiers_remove_densityscatter",icon = "REMOVE")
        row = layout.row()
        row.operator("object.frontiers_export_pointcloud", icon = "EXPORT")
# Define the panel class
class DensityPaintPanel(bpy.types.Panel):
    bl_label = "Density Options"
    bl_idname = "OBJECT_PT_weight_paint_brush_density"
    bl_parent_id = "OBJECT_PT_previews"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "weight_paint"
    def weightgroupname(self,context,obj):
        if obj != None and obj.type == "MESH":
            vertex_groups = obj.vertex_groups
            if len(vertex_groups) == 0:
                return ""
            else:
                return vertex_groups[vertex_groups.active_index].name
        else:
            return ""
    def draw(self, context):
        layout = self.layout
        Density_props = context.scene.FrontiersDensityProperties
        row = layout.row()
        row.label(text = f"WeightPaint options:")
        row = layout.row()
        row.label(text = f"Paint: {self.weightgroupname(context, bpy.context.active_object)}")
        row = layout.row()
        row.operator("paint.density_add",icon='BRUSH_CURVES_ADD', text='')
        row.operator("paint.density_subtract",icon='BRUSH_CURVES_DELETE', text='')
        row.operator("choice.density_group_forward", icon='SORT_ASC', text='')
        row.operator("choice.density_group_back", icon='SORT_DESC', text='')
        row = layout.row()
        row.label(text = f"Advanced options:")
        row = layout.row()
        row.prop(Density_props,"UseCustomDensityObject")
        row = layout.row()
        row.prop(Density_props,"CustomDensityObject", text='')
        row.prop(Density_props,"CustomDensityID")
        row = layout.row()
        row.operator("density.add_index",icon='RESTRICT_INSTANCED_OFF')
        
# Operator for toggling brush modes
class DensityAddOperator(bpy.types.Operator):
    bl_idname = "paint.density_add"
    bl_label = "Set Brush to Add"
    
    def execute(self, context):
        bpy.context.tool_settings.weight_paint.brush = bpy.data.brushes.get("Add")
        return {'FINISHED'}
class DensityAssignIndex(bpy.types.Operator):
    bl_idname = "density.add_index"
    bl_label = "Turn object into Density asset"
    bl_description = "Assigns index to the object above and makes the asset recognize it as a density asset"
    
    def execute(self, context):
        obj = context.scene.FrontiersDensityProperties.CustomDensityObject
        if obj == None:
            self.report({'INFO'}, "Select an object in the window above")
            return {'CANCELLED'}
        obj["FrontiersDensityAsset"] = True
        obj["FrontiersDensityID"] = context.scene.FrontiersDensityProperties.CustomDensityID
        return {'FINISHED'}
class DensitySubtractOperator(bpy.types.Operator):
    bl_idname = "paint.density_subtract"
    bl_label = "Set Brush to remove"
    
    def execute(self, context):
        bpy.context.tool_settings.weight_paint.brush = bpy.data.brushes.get("Subtract")
        return {'FINISHED'}
class DensityForwardGroupOperator(bpy.types.Operator):
    bl_idname = "choice.density_group_forward"
    bl_label = "Choose next density group"
    
    def execute(self, context):
        obj = bpy.context.active_object
        if obj == None:
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}
        vertex_groups = obj.vertex_groups
        if len(vertex_groups) == vertex_groups.active_index + 1:
            vertex_groups.active_index = 0
        else:
            vertex_groups.active_index = vertex_groups.active_index + 1
        return {'FINISHED'}
    
class DensityBackwardsGroupOperator(bpy.types.Operator):
    bl_idname = "choice.density_group_back"
    bl_label = "Choose previous density group"
    
    def execute(self, context):
        obj = bpy.context.active_object
        if obj == None:
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}
        vertex_groups = obj.vertex_groups
        if vertex_groups.active_index == 0:
            vertex_groups.active_index = len(vertex_groups) - 1
        else:
            vertex_groups.active_index = vertex_groups.active_index - 1
        return {'FINISHED'}
# We can store multiple preview collections here,
# however in this example we only store "main"
preview_collections = {}

def register():
    import bpy
    bpy.utils.register_class(OBJECT_OT_duplicate_link_with_nodes)
    bpy.utils.register_class(OBJECT_OT_FrontiersPointCloudExport)
    WindowManager.Frontiers_Density_thumbnail = EnumProperty(
        items=enum_previews_from_directory_items,
    )
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    pcoll.Frontiers_Density_thumbnail_dir = ""
    pcoll.Frontiers_Density_thumbnail = ()

    preview_collections["main"] = pcoll
    bpy.utils.register_class(FrontiersDensityProperties)
    bpy.types.Scene.FrontiersDensityProperties = bpy.props.PointerProperty(type=FrontiersDensityProperties)
    bpy.utils.register_class(DensityPanel)
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_duplicate_link_with_nodes)
    bpy.utils.unregister_class(OBJECT_OT_FrontiersPointCloudExport)
    from bpy.types import WindowManager

    del WindowManager.Frontiers_Density_thumbnail

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    bpy.utils.unregister_class(DensityPanel)
    bpy.utils.unregister_class(FrontiersDensityProperties)
    del bpy.types.Scene.FrontiersDensityProperties
    
if __name__ == "__main__":
    register()