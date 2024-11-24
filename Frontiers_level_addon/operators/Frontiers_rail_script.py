import bpy
import mathutils
import random
from math import radians
import pathlib
from pathlib import Path
import os
import bmesh

def Find_node_rot(curve_obj,index,path_dir):#New fixed rotation whooo! Based heavily on the density script
    beveled_curve = False
    hedgePath = False
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    if curve_obj.data.bevel_mode != 'ROUND' and curve_obj.data.bevel_depth != 0 :
        original_bevel_mode = curve_obj.data.bevel_mode
        original_bevel_size = curve_obj.data.bevel_depth
        curve_obj.data.bevel_depth = 0
        beveled_curve = True
    if "HedgehogPath" in curve_obj.modifiers:
        bpy.data.node_groups["HedgehogPath"].nodes["devOff"].inputs[0].default_value = True
        hedgePath = True
    nodetree_name = "FrontiersRailRotation"
    filepath = os.path.join(path_dir, r"Other\frontiers_rotation_solution.blend")
    # Check if the file exists and is a valid blend file
    if nodetree_name not in bpy.data.node_groups:
        try:
            with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to): #try loading the nodetree. Cancel script if failed
                data_to.node_groups = [nodetree_name]   
        except Exception as error:
            print(f"Failed to load {filepath}: {error}")
            return
    bpy.ops.mesh.primitive_plane_add(size = 1.0)
    appended_rotobject = bpy.context.view_layer.objects.active
        
    geo_node_mod = appended_rotobject.modifiers.new(name="Frontiersrotation", type='NODES')
    geo_node_mod.node_group = bpy.data.node_groups[nodetree_name]
    if appended_rotobject != None:
        appended_rotobject.modifiers["Frontiersrotation"]["Input_2"] = index
        appended_rotobject.modifiers["Frontiersrotation"]["Input_3"] = curve_obj
    else:
        return 0,False
    bpy.ops.object.select_all(action='DESELECT')
    appended_rotobject.select_set(True)
    bpy.context.view_layer.objects.active = appended_rotobject
    bpy.ops.object.modifier_apply(modifier="Frontiersrotation",single_user=True)
    bpy.ops.object.mode_set(mode='EDIT') # Switches to Edit Mode
    bm = bmesh.from_edit_mesh(appended_rotobject.data) # Gets the Blender Mesh from the rotobject
    for theface in bm.faces:
        face = theface
    appended_rotobject.rotation_mode = 'QUATERNION'
    objectRotation = face.normal.to_track_quat('Z', 'Y')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    curve_obj.select_set(True)
    bpy.context.view_layer.objects.active = curve_obj
    if beveled_curve:
        curve_obj.data.bevel_depth = original_bevel_size
        curve_obj.data.bevel_mode = original_bevel_mode
    if hedgePath == True:
        bpy.data.node_groups["HedgehogPath"].nodes["devOff"].inputs[0].default_value = False
    bpy.data.objects.remove(appended_rotobject, do_unlink=True)
    return objectRotation,True

# Define the operator class
class SetBevelOperator(bpy.types.Operator):
    bl_idname = "object.set_bevel_operator"
    bl_label = "Curve to Hedgehog Path"
    bl_description = "Sets the curve to work like the path in Hedgehog games. If using Blender 3.6 this simply creates a profile around the curve without calculations"    

    def execute(self, context):
            # Get the active object
        obj = bpy.context.active_object
        
        with bpy.data.libraries.load(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/railprofile.blend') as (data_from, data_to):
            if not "[FLC] Profile" in bpy.data.objects:
                data_to.objects = data_from.objects

        # Check if the active object is a curve
        if obj and obj.type == 'CURVE':
            #Removes hedgehogpath if already on
            if "HedgehogPath" in obj.modifiers:
                obj.modifiers.remove(obj.modifiers.get("HedgehogPath"))
                return {'FINISHED'}    
            # Check if the curve already has a bevel
            if obj.data.bevel_mode == 'OBJECT':
                # Set bevel to 0.0 radius
                obj.data.bevel_mode = 'ROUND'
                if obj.data.bevel_depth != 0:
                    obj.data.bevel_depth = 0.0
                return {'FINISHED'}    
            elif (4, 1, 0) > bpy.app.version:
                # Set bevel to profile preset crown with 0.25 radius
                obj.data.bevel_mode = 'OBJECT'
                obj.data.bevel_object = bpy.data.objects["[FLC] Profile"]
            else:
                if not "HedgehogPath" in bpy.data.node_groups:
                    with bpy.data.libraries.load(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/SNS Curve.blend') as (data_from, data_to):
                            data_to.node_groups = data_from.node_groups
                geo_node_Path_mod = obj.modifiers.new(name="HedgehogPath", type='NODES')
                geo_node_Path_mod.node_group = bpy.data.node_groups["HedgehogPath"]
                obj.data.splines.active.type == "BEZIER"
                for point in obj.data.splines.active.bezier_points:
                    # Set the handle types to 'AUTO'
                    if point.handle_left_type != 'AUTO' and point.handle_left_type != 'VECTOR':  
                        point.handle_left_type = 'AUTO'
                    if point.handle_right_type != 'AUTO' and point.handle_right_type != 'VECTOR':
                        point.handle_right_type = 'AUTO'
                
        else:
            self.report({"INFO"}, f"Selected object is not a curve")
        return {'FINISHED'}
class PrintRailsOperator(bpy.types.Operator):
    bl_idname = "object.rail_script"
    bl_label = "Create grind rail Gedit code"
    bl_description = "Create grind rail gedit code from curves to copy-paste into your mod"
    def execute (self, context):
        #Get check info
        path_check = context.scene.FrontiersRails.objPath_check
        Straight_Path =context.scene.FrontiersRails.straightPath_Check
        rot_check = context.scene.FrontiersRails.RotationPath_Check
        if path_check == "obj_path":
            PathType = 'OBJ_PATH'
        elif path_check == "gr_path":
            PathType = 'GR_PATH'
        elif path_check == "sv_path":
            PathType = 'SV_PATH'
        # Get the collection
         
        collection_name = context.scene.FrontiersRails.Railcoll_name
        Node_startindex = context.scene.FrontiersRails.Railnode_startindex
        collection = collection_name
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        blend_file_path = bpy.data.filepath
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        blend_dir = os.path.dirname(blend_file_path)
        path_dir = os.path.join(blend_dir,script_dir)
        if collection is not None:
            changed_UID_list =[]
            path_text = ""
            node_text = ""
            node_ID_list =""
            hexValues = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
            gedit_text = ""
            Nodename_index = Node_startindex - 1       
            bpy.ops.object.select_all(action='DESELECT')
            # Iterate through each object in the collection
            for obj in collection.objects:
                if obj.type == 'CURVE':
                    #finish file paths

                    obj.select_set(True)
                    file_name = f"objects\Path.txt"
                    node_name = f"objects\PathNode.txt"
                    spline_path = os.path.join(path_dir, file_name)
                    node_path = os.path.join(path_dir, node_name)
                    bpy.ops.object.transform_apply(location = False, scale = True, rotation = True)
                    if "UID" in obj:
                        UID_Random = obj["UID"]
                    else:
                        UID_Random = str(random.randint(100000, 200000)) 
                        obj["UID"] = UID_Random
                    PathId = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
                    
                    for Otherobj in bpy.data.objects: #check if there is a duplicate UID in the scene
                        if "UID" in Otherobj:
                            if Otherobj["UID"] == obj["UID"] and Otherobj != obj:
                                changed_UID_list.append(Otherobj.name)
                                OtherID = str(random.randint(100000, 200000))
                                Otherobj["UID"] = OtherID
                    for i in range(32):
                        PathId = PathId.replace("X", hexValues[random.randrange(len(hexValues))], 1) # generates a random ID
                    pathcoord= f'{obj.location.x}, {obj.location.z}, {-obj.location.y}'
                    # Access the curve data
                    curve_data = obj.data
                    if curve_data.splines.active == None:
                        if len(curve_data.splines) > 0:
                            curve_data.splines.active = curve_data.splines[0]
                            if len(curve_data.splines) > 1:
                                self.report({"INFO"}, f"Curve {obj.name} has several splines. Only the one with index 0 will be considered")
                        else:
                            self.report({"WARNING"}, f"Curve {obj.name} has no splines. It has been skipped.")
                            continue
                            
                    if Straight_Path or curve_data.splines.active.type != "BEZIER":
                        curve_data.splines.active.type = 'POLY'
                        points_in_curve = curve_data.splines.active.points
                    elif curve_data.splines.active.type == "BEZIER":
                        points_in_curve = curve_data.splines.active.bezier_points
                        # Iterate through each Bezier point if not a straight path
                        for point in curve_data.splines.active.bezier_points:
                            # Set the handle types to 'AUTO'
                            if point.handle_left_type != 'AUTO' and point.handle_left_type != 'VECTOR':  
                                point.handle_left_type = 'AUTO'
                            if point.handle_right_type != 'AUTO' and point.handle_right_type != 'VECTOR':
                                point.handle_right_type = 'AUTO'
                    loop_bool = curve_data.splines.active.use_cyclic_u
                    
                    # Print the curve name
                    Pathname = obj.name
                    # Iterate through each point in the curve
                    lastLength = 0.0
                    for i, point in enumerate(points_in_curve):
                        print(i)
                        if i == 0:
                            originStr = False
                            if curve_data.splines.active.type == "BEZIER":
                                if point.handle_right_type == 'VECTOR' and point.handle_left_type == 'VECTOR':
                                    originStr = True
                            origincoord = f'{point.co.x + obj.location.x}, {point.co.z + obj.location.z}, {-(point.co.y+obj.location.y)}'
                            if rot_check == True:
                                try:
                                    RotPoint,rot_checker = Find_node_rot(obj, i, path_dir)
                                    if rot_checker == False:
                                        pass
                                    originrotation = f'{round(RotPoint.x,3)}, {round(RotPoint.z,3)}, {-round(RotPoint.y,3)}, {round(RotPoint.w,3)}'
                                    
                                except Exception as err:
                                    print(f'First rot error: {err}')
                                    originrotation = '0.0, 0.0, 0.0, 1.0'
                                    pass    
                        else:
                            Nodename_index += 1
                            if PathType == 'OBJ_PATH':
                                this_nodename = f"ObjPathNode{Nodename_index}"
                            elif PathType == 'SV_PATH':
                                this_nodename = f"SVPathNode{Nodename_index}"
                            else:
                                this_nodename = f"PathNode{Nodename_index}"
                            
                            #create ID for node
                            NodeId = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
                            for k in range(32):
                                NodeId = NodeId.replace("X", hexValues[random.randrange(len(hexValues))], 1) # generates a random ID
                            node_ID_list += '"{'+NodeId+'}",\n            '
                            # Print the index and coordinates of each point
                            nodeindex = f'{i}'
                            nodecoord = f'{point.co.x + obj.location.x}, {point.co.z + obj.location.z}, {-(point.co.y+obj.location.y)}'
                            rotation = f'{0.0}, {0.0}, {0.0}, {1.0}'
                            if rot_check == True:
                                try:
                                #     if point == points_in_curve[-1]:
                                #         rotation = lastRotation
                                #     else:
                                #         next_point = points_in_curve[i + 1]
                                #         # Call the function to spawn cube, set up constraint, print rotation, and delete cube
                                #         RotPoint,lastLength = Find_node_rot(obj, point,next_point,lastLength)
                                #         RotPoint = RotPoint.to_quaternion()
                                #         #Rotation
                                #         rotation = f'{round(RotPoint.x,3)}, {round(RotPoint.z,3)}, {-round(RotPoint.y,3)}, {round(RotPoint.w,3)}'
                                #         lastRotation = rotation
                                # except:
                                #     rotation = '0.0, 0.0, 0.0, 1.0'
                                #     pass
                                    if i ==len(points_in_curve)-1:
                                        
                                        RotPoint,rot_checker = Find_node_rot(obj, i, path_dir)
                                        if rot_checker == False:
                                            pass
                                        rotation = f'{round(RotPoint.x,3)}, {round(RotPoint.z,3)}, {-round(RotPoint.y,3)}, {round(RotPoint.w,3)}'
                                        
                                    else:
                                        next_point = points_in_curve[i + 1]
                                        # Call the function to spawn plane, set up constraint, print rotation, and delete cube
                                        RotPoint,rot_checker = Find_node_rot(obj, i, path_dir)
                                        if rot_checker == False:
                                            pass
                                        rotation = f'{round(RotPoint.x,3)}, {round(RotPoint.z,3)}, {-round(RotPoint.y,3)}, {round(RotPoint.w,3)}'
                                        
                                except Exception as err:
                                    print(f'node for {obj} failed because: {err}')
                                    rotation = '0.0, 0.0, 0.0, 1.0'
                                    pass   


                            with open(node_path, "r") as file: #with open opens the file temporarily in order to avoid memory leak
                                node_temp =  file.read()
                            node_temp = node_temp.replace('DATA_ID', NodeId)
                            node_temp = node_temp.replace('DATA_NAME', this_nodename)
                            node_temp = node_temp.replace('DATA_POSITION', nodecoord)
                            node_temp = node_temp.replace('DATA_ROTATION', rotation)
                            node_temp = node_temp.replace('DATA_INDEX', nodeindex)
                            if Straight_Path or (point.handle_right_type == 'VECTOR' and point.handle_left_type == 'VECTOR'):
                                node_temp = node_temp.replace('LINETYPE_SNS', 'LINETYPE_STRAIGHT')
                            node_text += node_temp
                            
                    if loop_bool:
                        Nodename_index += 1
                        if path_check:
                            this_nodename = f"ObjPathNode{Nodename_index}"
                        else:
                            this_nodename = f"PathNode{Nodename_index}"
                            
                        #create ID for node
                        NodeId = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
                        for k in range(32):
                            NodeId = NodeId.replace("X", hexValues[random.randrange(len(hexValues))], 1) # generates a random ID
                        node_ID_list += '"{'+NodeId+'}",\n            '
                        # Print the index and coordinates of each point
                        nodeindex = f'{i+1}'
                        nodecoord = f'{point.co.x + obj.location.x}, {point.co.z + obj.location.z}, {-(point.co.y+obj.location.y)}'
                        rotation = f'{0.0}, {0.0}, {0.0}, {1.0}'
                
                        with open(node_path, "r") as file: #with open opens the file temporarily in order to avoid memory leak
                            node_temp =  file.read()
                        node_temp = node_temp.replace('DATA_ID', NodeId)
                        node_temp = node_temp.replace('DATA_NAME', this_nodename)
                        node_temp = node_temp.replace('DATA_POSITION', origincoord)
                        node_temp = node_temp.replace('DATA_ROTATION', rotation)
                        node_temp = node_temp.replace('DATA_INDEX', nodeindex)
                        node_text += node_temp
                    node_ID_list = node_ID_list[:-14] #delete the last comma in the nodeID list
                    with open(spline_path, "r") as file: #with open opens the file temporarily in order to avoid memory leak
                        path_temp =  file.read()
                    path_temp = path_temp.replace('DATA_ID', PathId)
                    path_temp = path_temp.replace('DATA_NAME', Pathname)
                    path_temp = path_temp.replace('DATA_TYPE', PathType)
                    path_temp = path_temp.replace('DATA_POSITION', origincoord)
                    path_temp = path_temp.replace('DATA_NODES', node_ID_list)
                    path_temp = path_temp.replace('DATA_LOOP', str(loop_bool).lower())
                    path_temp = path_temp.replace('DATA_UID', UID_Random)
                    if Straight_Path or originStr:
                        path_temp = path_temp.replace('LINETYPE_SNS', 'LINETYPE_STRAIGHT')
                    path_text += path_temp
                    node_ID_list =""
                    obj.select_set(False)
            gedit_text += path_text
            gedit_text += node_text
            if changed_UID_list != []:
                self.report({"INFO"}, f"Duplicate ID's were found. Objects with changed IDs are: {changed_UID_list}")
            if gedit_text == "":
                self.report({"WARNING"}, f"Collection '{collection_name}' do not have any curve objects.")
                return {'CANCELLED'}
            else:
                bpy.ops.wm.window_new()
                GeditPrint = bpy.data.texts.new("Rail Gedit Code")
                GeditPrint.write(gedit_text)
                context.area.type = 'TEXT_EDITOR'
                context.space_data.text = GeditPrint
                return {'FINISHED'}
        else:
            self.report({"WARNING"}, f"Collection{collection_name} not found")
            return {'CANCELLED'}
        
class FrontiersRails(bpy.types.PropertyGroup):
    objPath_check: bpy.props.EnumProperty(
        items=[("gr_path", "Grind Rail", "Creates code for a grindrail"),
               ("obj_path", "Object path", "Creates an object path (TECHNICAL: USE FOR AUTORUN AND MANUAL GEDIT EDITING. WILL ALSO CHANGE THE NAME OF THE PATHS.)"),
               ("sv_path", "Sideview(2D) path", "Creates a sideview path (HIGHLY RECOMMENDED FOR 2D SECTIONS. WILL ALSO CHANGE THE NAME OF THE PATHS.)") ],
        name="Type",
        description="Set the type of path that will be converted to code",
        default = "gr_path")
    Railcoll_name: bpy.props.PointerProperty(
        name="Rail Collection",
        description = "Choose Rail Collection",
        type=bpy.types.Collection
    )
    straightPath_Check: bpy.props.BoolProperty(
        name="No smoothing",
        description="Make straight lines between nodes. If off, Frontiers will automatically smooth the path.",
        default = False)
    RotationPath_Check: bpy.props.BoolProperty(
        name="Rail rotation",
        description="Lets the rail rotate following it's normal, for loops and such.(Remember that each node can be tilted in edit mode with Ctrl+T)",
        default = False)
    Railnode_startindex: bpy.props.IntProperty(
        name="Node start index",
        description = "Set Start index (Only change if you are using several collections. Set this to avoid duplicate indices)",
        min = 1,
        soft_min = 1
    )