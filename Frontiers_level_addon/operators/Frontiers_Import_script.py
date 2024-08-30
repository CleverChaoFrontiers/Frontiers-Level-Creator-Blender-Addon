import json
import os
import bpy
import mathutils

class HSONImportOperator(bpy.types.Operator):
    bl_idname = "object.hson_import"
    bl_label = "Import HSON"

    def execute(self, context):


        directory = context.scene.hson_directory

        
        assets_library_path = context.scene.hson_assets_library_path

 
        frontiers_collection = None
        collection_name = context.scene.hson_collection_name
        
        if collection_name:
            frontiers_collection = bpy.data.collections.get(collection_name)
            if frontiers_collection is None:
                frontiers_collection = bpy.data.collections.new(collection_name)
                bpy.context.scene.collection.children.link(frontiers_collection)
                
        else:
            # Check if the collection "Imported Objects" already exists
            frontiers_collection = bpy.data.collections.get("Imported Objects")
            
            if frontiers_collection is None:
                # Create a new collection if it doesn't exist
                frontiers_collection = bpy.data.collections.new("Imported Objects")
                bpy.context.scene.collection.children.link(frontiers_collection)
            
        #Line 72-73Added by cleverchao:this part sets the active collection as frontiers_collection. This will lead to
        #all objects added automatically being added to the correct collection without linking.
        layer_collection = bpy.context.view_layer.layer_collection.children[frontiers_collection.name]
        bpy.context.view_layer.active_layer_collection = layer_collection
        
        # Create a new collection named "Unsupported"
        unsupported_collection_name = "Unsupported"
        unsupported_collection = bpy.data.collections.get(unsupported_collection_name)
        if not unsupported_collection:
            unsupported_collection = bpy.data.collections.new(unsupported_collection_name)
            bpy.context.scene.collection.children.link(unsupported_collection)          
        
        # Create a list to store imported objects
        imported_objects_list = []

        # Function to import an object into Blender
        def import_object(object_name, position, rotation, object_parameters=None):
            #Line 88-91 added by cleverchao: In order to look in all files for the asset pack I took the already
            #created code for HSON importer that looked for all files with .HSON and switched it for .blend
            #However to iterate through the files I had to make the condition for empty creation different:
            Object_exists = False # This becomes true when the object has been found
            for filename in os.listdir(assets_library_path):#this iterates through the files in the Asset pack directory
                if filename.endswith(".blend"): #only look at the blend files
                    assets_library_file = os.path.join(assets_library_path, filename) #puts together a path to the specific blend file
                    
                    
                    with bpy.data.libraries.load(assets_library_file, link=False) as (data_from, data_to):
                        if object_name in data_from.objects:
                            Object_exists = True
                            # Import mesh data along with the object
                            bpy.ops.wm.append(directory=assets_library_file + "\\Object\\", filename=object_name)
                            # Get the imported object
                            imported_object = bpy.context.selected_objects[0]

                            # Set the location based on the HSON position values
                            # Adjust Y and Z values to match Blender's coordinate system
                            imported_object.location = (position[0], -position[2], position[1])

                            # Rearrange HSON quaternion components (0X, 1Z, 2Y, 3W) to match Blender's order (W, X, Y, Z)
                            rearranged_rotation = [rotation[3], rotation[0], -rotation[2], rotation[1]]

                            # Convert rearranged quaternion to Euler
                            rotation_quaternion = mathutils.Quaternion(rearranged_rotation)
                            rotation_euler = rotation_quaternion.to_euler('XYZ')

                            # Set the rotation of the imported object
                            imported_object.rotation_euler = rotation_euler

                            # OBJECT PARAMETER IMPORTING

                            # Check object type

                            if hson_object_type == "DashPanel" and object_parameters:
                                # Set DASHPAD_ATTR_OCTIME
                                imported_object.modifiers["GeometryNodes"]["Input_2"] = object_parameters.get("ocTime", 0.25)

                                # Set DASHPAD_ATTR_SPEED as an integer value
                                imported_object.modifiers["GeometryNodes"]["Input_3"] = int(object_parameters.get("speed", 80))

                            elif hson_object_type == "Spring" and object_parameters:
                                # Map HSON visual parameter to Blender values
                                visual_param = object_parameters.get("visual", "Normal")
                                blender_visual_value = True if visual_param == "Sky" else False
                                
                                # Set SPRING_ATTR_VISUAL
                                imported_object.modifiers["GeometryNodes"]["Input_6"] = blender_visual_value
                                # Set SPRING_ATTR_FIRST_SPEED
                                imported_object.modifiers["GeometryNodes"]["Input_2"] = object_parameters.get("firstSpeed", 30.0)
                                # Set SPRING_ATTR_KEEP_VELOCITY_DISTANCE
                                imported_object.modifiers["GeometryNodes"]["Input_8"] = object_parameters.get("keepVelocityDistance", 5.0)

                            elif hson_object_type == "WideSpring" and object_parameters:
                                # Set SPRING_ATTR_FIRST_SPEED
                                imported_object.modifiers["GeometryNodes"]["Input_5"] = object_parameters.get("firstSpeed", 17.0)
                                # Set SPRING_ATTR_KEEP_VELOCITY_DISTANCE
                                imported_object.modifiers["GeometryNodes"]["Input_2"] = object_parameters.get("keepVelocityDistance", 5.0) 

                            elif hson_object_type == "JumpBoard" and object_parameters:
                                # Set distance
                                imported_object.modifiers["GeometryNodes"]["Input_2"] = object_parameters.get("distance", 110.0)
                                # Set height
                                imported_object.modifiers["GeometryNodes"]["Input_3"] = object_parameters.get("height", 10.0)

                            elif hson_object_type == "BoardingJumpBoard" and object_parameters:
                                # Set distance
                                imported_object.modifiers["GeometryNodes"]["Input_4"] = object_parameters.get("distance", 20.0)
                                # Set height
                                imported_object.modifiers["GeometryNodes"]["Input_5"] = object_parameters.get("height", 0.0)   

                            elif hson_object_type == "PointMarker" and object_parameters:
                                # Set width
                                imported_object.modifiers["GeometryNodes"]["Input_2"] = object_parameters.get("Width", 3.0)

                            elif hson_object_type == "DashRing" and object_parameters:
                                # Map HSON visual parameter to Blender values
                                visual_param = object_parameters.get("visual", "DashRing")
                                blender_visual_value = True if visual_param == "RainbowRing" else False
                                # Set Visual
                                imported_object.modifiers["GeometryNodes"]["Input_2"] = blender_visual_value
                                # Set speed
                                imported_object.modifiers["GeometryNodes"]["Input_9"] = object_parameters.get("Speed", 100.0)
                                # Set No Control Time
                                imported_object.modifiers["GeometryNodes"]["Input_3"] = object_parameters.get("OutOfControl", 0.0)
                                # Set Keep Velocity Time 
                                imported_object.modifiers["GeometryNodes"]["Input_6"] = object_parameters.get("KeepVelocity", 0.25)

                            elif hson_object_type == "StartPosition" and object_parameters:
                                # Map HSON start parameter to Blender values
                                start_param = object_parameters.get("m_startType", "FALL")
                                blender_start_value = True if start_param == "RUNNING" else False
                                # Set Start Position
                                imported_object.modifiers["GeometryNodes"]["Input_2"] = blender_start_value
                                # Set Out Of Control Time
                                imported_object.modifiers["GeometryNodes"]["Input_5"] = object_parameters.get("m_outOfControlTime", 4.0)

                            elif hson_object_type == "EggRobo" and object_parameters:
                                # Map HSON weapon parameter to Blender values
                                weapon_param = object_parameters.get("attackParam", {}).get("weaponType", "Laser")
                                blender_weapon_value = True if weapon_param == "Missile" else False
                                # Set Weapon
                                imported_object.modifiers["GeometryNodes"]["Input_2"] = blender_weapon_value

                            elif hson_object_type == "PortalGate" and object_parameters:
                                # Map HSON isGoal parameter to Blender values
                                is_goal_param = object_parameters.get("isGoal", False)
                                # Set Goal
                                imported_object.modifiers["GeometryNodes"]["Input_2"] = is_goal_param

                            elif hson_object_type == "RedRing" and object_parameters:
                                # Map HSON ItemId parameter to Blender values
                                hson_item_id = object_parameters.get("ItemId", 0)
                                # Adjust ItemId value if needed (adding 1 to convert from 0-4 to 1-5)
                                blender_item_id = hson_item_id + 1
                                # Set the corresponding Blender property
                                imported_object.modifiers["GeometryNodes"]["Input_2"] = blender_item_id

                            elif hson_object_type == "Balloon" and object_parameters:
                                # Map HSON balloonColor parameter to Blender values
                                hson_balloon_color = object_parameters.get("balloonColor", "COLOR_RED")
                                
                                # Create a mapping from HSON values to Blender values
                                color_mapping = {"COLOR_RED": 1, "COLOR_BLUE": 2, "COLOR_YELLOW": 3, "COLOR_GREEN": 4}
                                
                                # Use the mapping to get the corresponding Blender value
                                blender_balloon_color = color_mapping.get(hson_balloon_color, 1)  # Default to 1 if not found
                                
                                # Set the corresponding Blender property
                                imported_object.modifiers["GeometryNodes"]["Input_2"] = blender_balloon_color 


                            elif hson_object_type == "Motora" and object_parameters:
                                # Set destination values
                                destination_values = object_parameters.get("destination", [0.0, 0.0, 3.0])
                                imported_object.modifiers["GeometryNodes"]["Input_2"][0] = destination_values[0]
                                imported_object.modifiers["GeometryNodes"]["Input_2"][1] = -destination_values[2]
                                imported_object.modifiers["GeometryNodes"]["Input_2"][2] = destination_values[1]     

                            elif hson_object_type == "UpReel" and object_parameters:
                                # Set Height
                                imported_object.modifiers["GeometryNodes"]["Input_8"] = object_parameters.get("length", 0.5)     

                            elif hson_object_type == "NormalFloor" and object_parameters:
                                # Map HSON isFall parameter to Blender values
                                fall_param = object_parameters.get("isFall", False)
                                imported_object.modifiers["GeometryNodes"]["Input_2"] = fall_param
                                # Set Fall Wait Time
                                imported_object.modifiers["GeometryNodes"]["Input_4"] = object_parameters.get("waitFallTime", 3.0)
                                # Map HSON Move
                                move_param = object_parameters.get("moveType", "MOVE_NONE")
                                blender_move_value = True if move_param == "MOVE_POINT" else False
                                # Set is Move
                                imported_object.modifiers["GeometryNodes"]["Input_6"] = blender_move_value
                                # Set Move Vector
                                destination_values = object_parameters.get("moveVector", [5.0, 0.0, 0.0])
                                imported_object.modifiers["GeometryNodes"]["Input_8"][0] = destination_values[0]
                                imported_object.modifiers["GeometryNodes"]["Input_8"][1] = -destination_values[2]
                                imported_object.modifiers["GeometryNodes"]["Input_8"][2] = destination_values[1]  
                                # Set MoveSpeed
                                imported_object.modifiers["GeometryNodes"]["Input_13"] = object_parameters.get("speed", 10.0)
                                # Set Move Wait Time
                                imported_object.modifiers["GeometryNodes"]["Input_12"] = object_parameters.get("waitTime", 3.0) 
                                # Set phase
                                imported_object.modifiers["GeometryNodes"]["Input_14"] = object_parameters.get("phase", 0.0)
                            
                            # MORE OBJECT PARAMETERS GO HERE
                                
                                
                            # If 'hson_create_collections' is True, place the imported object in the corresponding collection
                            if context.scene.hson_create_collections:
                                hson_collection.objects.link(imported_object) 
                            
                            #added by CleverChao "Since the asset is imported with asset data, this line tries to remove it.
                            try:
                                bpy.ops.asset.clear(set_fake_user=False)
                            except:
                                pass
                            
                            return imported_object
            if Object_exists is False: #CleverChao change: Condition is now an if statement that checks if the object was found or not.
                print(f"Warning: Object '{object_name}' not found in '{assets_library_path}'. Creating Empty Mesh Object.")
                
                # Create an Empty Mesh Object
                empty_object = bpy.data.objects.new(object_name, None)
                empty_object.location = (position[0], -position[2], position[1])

                # Set the rotation of the empty object based on HSON rotation values
                rearranged_rotation = [rotation[3], rotation[0], -rotation[2], rotation[1]]
                rotation_quaternion = mathutils.Quaternion(rearranged_rotation)
                rotation_euler = rotation_quaternion.to_euler('XYZ')
                empty_object.rotation_euler = rotation_euler

                # Place empty objects in the "Unsupported" collection
                unsupported_collection.objects.link(empty_object)

                return empty_object

        # Iterate through HSON files in the specified directory
        for filename in os.listdir(directory):
            if filename.endswith(".hson"):
                with open(os.path.join(directory, filename), "r") as file:
                    data = json.load(file)
                    objects = data.get("objects", [])

                    # Create a collection based on HSON file name
                    if context.scene.hson_create_collections:
                        collection_name = os.path.splitext(filename)[0]
                        hson_collection = bpy.data.collections.get(collection_name)
                        if not hson_collection:
                            hson_collection = bpy.data.collections.new(collection_name)
                            bpy.context.scene.collection.children.link(hson_collection)

                    # Create a dictionary to store imported objects by their "id"
                    imported_objects_by_id = {}

                    # Iterate through objects in HSON
                    for obj in objects:
                        hson_object_type = obj.get("type")
                        hson_position = obj.get("position", [0, 0, 0])
                        hson_rotation = obj.get("rotation", [0, 0, 0, 1])
                        hson_id = obj.get("id")
                        hson_parent_id = obj.get("parentId")
                        hson_object_name = obj.get("name")
                        hson_parameters = obj.get("parameters")

                        if hson_object_type:
                            imported_object = import_object(hson_object_type + ".001", hson_position, hson_rotation, object_parameters=hson_parameters)

                            if imported_object and hson_id:
                                # Store imported objects by their "id"
                                imported_objects_by_id[hson_id] = imported_object

                                # Store imported objects in list
                                imported_objects_list.append(imported_object)

                            # If it's a child object with "parentId," set its position to the parent's position
                            # and move it on its local axes based on the "position" value
                            if imported_object and hson_parent_id:
                                parent_object = imported_objects_by_id.get(hson_parent_id)
                                if parent_object:
                                    # Set child's position and rotation to the parent's position
                                    imported_object.location = parent_object.location
                                    imported_object.rotation_euler = parent_object.rotation_euler
                                    # Move the child on its local axes based on the "position" value
                                    bpy.context.view_layer.objects.active = imported_object
                                    bpy.ops.transform.translate(value=(hson_position[0], -hson_position[2], hson_position[1]), orient_type='LOCAL')

                        else:
                            print(f"No Blender asset found for HSON object type: {hson_object_type}")

        # DUPLICATING ALL IMPORTED OBJECTS - This is needed for imported modifier values to reflect correctly in blender and gedit
        # Select all imported objects
        bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects first

        for imported_object in imported_objects_list:
            imported_object.select_set(True)

        # Duplicate all selected objects
        bpy.ops.object.duplicate(linked=False)
        # Delete Duplicates
        bpy.ops.object.delete()

        # Delete the frontiers_collection if 'hson_create_collections' is True
        if context.scene.hson_create_collections:
            bpy.data.collections.remove(frontiers_collection)

        print("Done.")

        return {'FINISHED'}
#creates a name window and saves the name when called
class FrontiersImportProperties(bpy.types.PropertyGroup):
    bpy.types.Scene.hson_directory = bpy.props.StringProperty(
        name="Directory",
        subtype='DIR_PATH',
        default="",
        description="Directory path for HSON files"
    )

    bpy.types.Scene.hson_assets_library_path = bpy.props.StringProperty(
        name="Assets Library Path",
        subtype='DIR_PATH', #Changed to DIR PATH so that all asset pack files are supported
        default="",
        description="File path for the assets library"
    )

    bpy.types.Scene.hson_collection_name = bpy.props.StringProperty(
        name="Collection Name",
        default="Frontiers Objects",
        description="Name of the collection for imported objects"
    )
    
    bpy.types.Scene.hson_create_collections = bpy.props.BoolProperty(
        name="Create Collections",
        default=False,
        description="Create collections based on HSON file names"
    )