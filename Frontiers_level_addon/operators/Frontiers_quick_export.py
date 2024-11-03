import bpy # type: ignore (Supresses the warning associated with it being a Blender library)
import os
import shutil
import json
import random
import textwrap
import mathutils # type: ignore
import math
import bmesh # type: ignore
import time
from . import path_export

def pack(files, directoryHedgearcpack):
    for f in range(len(files)): # For every file that needs to be packed
        if os.path.exists(files[f]): # Check if file exists
            os.chdir(os.path.dirname(directoryHedgearcpack)) # Go to the directory that hedgearcpack is in
            print(os.popen(f'hedgearcpack "{files[f]}" -T=rangers').read()) # Run hedgearcpack to pack the file

def unpack(files, directoryHedgearcpack):
    for f in range(len(files)): # For every file that needs to be packed
        if not os.path.exists(files[f][:-4]): # Check if the folder that would be extracted to exists exists
            if os.path.exists(files[f]):
                os.chdir(os.path.dirname(directoryHedgearcpack)) # Go to the directory that hedgearcpack is in
                print(os.popen(f'hedgearcpack "{files[f]}"').read()) # Run hedgearcpack to pack the file
            else:
                print(f"Unpack cancelled, {files[f]} could not be found")

def clearFolder(filepath, keepFiles):
    if keepFiles == None:
        keepFiles = ["level", "txt", "rfl"] # Backup measure in case no file types to keep are provided
    filepath = f"{filepath}\\"
    os.chdir(filepath) # Goes to the directory to be cleared
    files = os.listdir(filepath) # Gets every file/folder in the directory
    for f in range(len(files)): # For every file/folder
        if os.path.isfile(f"{filepath}\\{files[f]}"): # Only if is file, not folder
            if not files[f].split(".")[-1] in keepFiles: # If the file extension is not in the list of extensions to be kept
                os.remove(f"{filepath}\\{files[f]}") # Removes file

def ID_generator(self):
    Id = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    hexValues = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
    for i in range(32):
        Id = Id.replace("X", hexValues[random.randrange(len(hexValues))], 1) # generates a random ID
    return Id

def updateprogress(advance):
    bpy.types.Scene.heightmapprogress =  bpy.types.Scene.heightmapprogress + advance
    bpy.types.Scene.heightmapprogresstext = f"LOADING ({round(bpy.types.Scene.heightmapprogress * 100)}%)"
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    return

# def Find_node_rot(curve_obj, current_point, next_point, LastLength = 0, Final_curve_point = False,First_curve_point = False):
#     # Get the location of the curve object

#     spline = curve_obj.data.splines[0]
#     # Add a cube at the location of the curve object
#     bpy.ops.object.empty_add(type='SINGLE_ARROW',location=[0,0,0])
#     bezier_curve = False
#     # Get the newly added cube object
#     cube_obj = bpy.context.active_object

#     # Add Follow Path constraint
#     bpy.ops.object.constraint_add(type='FOLLOW_PATH')
#     constraint = cube_obj.constraints[-1]  # Get the last constraint added, which is the Follow Path constraint
#     splinelength = 0.0
#     if spline.type == "BEZIER": # If the curve is a bezier curve
#         points_in_rotcurve = spline.bezier_points #Set the points to iterate to be bezier points instead
#     else:
#         points_in_rotcurve = spline.points
#     for i in range(len(points_in_rotcurve)-1):
#         if Final_curve_point == False:
#             segment = (points_in_rotcurve[i+1].co - points_in_rotcurve[i].co).length
#             splinelength += segment
#     # Set the target curve
#     constraint.target = curve_obj
#     constraint.use_fixed_location = True
#     constraint.use_curve_follow = True
#     if Final_curve_point:
#         constraint.forward_axis = "TRACK_NEGATIVE_Y"#'TRACK_NEGATIVE_Z'
#         constraint.up_axis = 'UP_Z'
#     else:
#         constraint.forward_axis = 'TRACK_NEGATIVE_Y'
#         constraint.up_axis = 'UP_Z'

#     # Set the offset to follow the curve until reaching the positionof the current_point
#     if Final_curve_point:
#         constraint.offset_factor = 1.0
#     else:
#         constraint.offset_factor =LastLength + (next_point.co- current_point.co).length / splinelength
#     NewFactor = constraint.offset_factor
#     # Apply the modifier
#     bpy.ops.constraint.apply(constraint= constraint.name)
#     cube_obj.rotation_mode = 'QUATERNION'
#     Rotation = cube_obj.rotation_quaternion
#     # Delete the cube
#     #bpy.data.objects.remove(cube_obj)
#     return Rotation, NewFactor


#     NewFactor = constraint.offset_factor

#     bpy.context.view_layer.update()  # Ensure the constraint is applied and updated

#     empty_obj.rotation_mode = 'QUATERNION'
#     Rotation = empty_obj.rotation_quaternion.copy()

#     #bpy.data.objects.remove(empty_obj)

#     return Rotation, NewFactor
def Find_node_rot(curve_obj,index,path_dir):#New fixed rotation whooo! Based heavily on the density script
    beveled_curve = False
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    if curve_obj.data.bevel_depth != 0:
        original_bevel_size = curve_obj.data.bevel_depth
        curve_obj.data.bevel_depth = 0
        beveled_curve = True
    object_name = "Frontiers_rotation_plane"
    nodetree_name = "FrontiersRailRotation"
    filepath = os.path.join(path_dir, r"Other\frontiers_rotation_solution.blend")
    # Check if the file exists and is a valid blend file
    if nodetree_name not in bpy.data.node_groups:
        try:
            with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to): #try loading the nodetree. Cancel script if failed
                data_to.node_groups = [nodetree_name]
            # with bpy.data.libraries.load(filepath) as (data_from, data_to):
            #     if object_name in data_from.objects:
            #         data_to.objects = [object_name]
                # else:
                #     print(f"Object '{object_name}' not found in {filepath}")
                #     return
        except Exception as error:
            print(f"Failed to load {filepath}: {error}")
            return
    bpy.ops.mesh.primitive_plane_add(size = 1.0)
    appended_rotobject = bpy.context.view_layer.objects.active
    # Link the object to the scene
    # appended_rotobject = None
    # for rot_solution in data_to.objects:
    #     if rot_solution is not None:
    #         bpy.context.collection.objects.link(rot_solution)
    #         appended_rotobject = rot_solution
    #         #print(f"Appended '{object_name}' to the current scene.")
    #     else:
    #         print(f"Failed to append '{object_name}'.")

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
    bpy.data.objects.remove(appended_rotobject, do_unlink=True)
    return objectRotation,True
def Instantiate(pcmodelname,pccolname,object):
    pcmodel = [pcmodelname.split(".")[0], (object.location.x, object.location.y, object.location.z), (object.rotation_euler.x, object.rotation_euler.y, object.rotation_euler.z), (object.scale.x, object.scale.y,object.scale.z)]
    if pccolname != "":
        pccol = [pcmodelname.split(".")[0]+"_"+ pccolname.split(".")[0], (object.location.x, object.location.y, object.location.z), (object.rotation_euler.x, object.rotation_euler.y, object.rotation_euler.z),(object.scale.x, object.scale.y,object.scale.z)]
    else:
        pccol = ""
    return pcmodel, pccol
class CompleteExport(bpy.types.Operator):
    bl_idname = "qexport.completeexport"
    bl_label = "Complete Export"
    bl_description = "Exports Terrain, Objects and Heightmap"

    def ID_generator(self):
        Id = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
        hexValues = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
        for i in range(32):
            Id = Id.replace("X", hexValues[random.randrange(len(hexValues))], 1) # generates a random ID
        return Id


    def execute(self, context):
        ExportTerrain.execute(self, context)
        ExportObjects.execute(self, context)
        ExportHeightmap.execute(self, context)
        self.report({"INFO"}, f"Quick Export Finished")
        return{"FINISHED"}

class ExportTerrain(bpy.types.Operator):
    bl_idname = "qexport.exportterrain"
    bl_label = "Terrain"
    bl_description = "Exports your level's terrain, collision, materials and textures"

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        directoryModelconverter = os.path.abspath(bpy.path.abspath(preferences.directoryModelconverter)) # Gets ModelConverter path from preferences
        directoryBtmesh = os.path.abspath(bpy.path.abspath(preferences.directoryBtmesh)) # Gets btmesh path from preferences
        directoryKnuxtools = os.path.abspath(bpy.path.abspath(preferences.directoryKnuxtools)) # Gets KnuxTools path from preferences
        directoryHedgearcpack = os.path.abspath(bpy.path.abspath(preferences.directoryHedgearcpack)) # Gets HedgeArcPack path from preferences
        directoryTexconv = os.path.abspath(bpy.path.abspath(preferences.directoryTexconv)) # Gets texconv path from preferences

        absoluteModDir = os.path.abspath(bpy.path.abspath(bpy.context.scene.modDir)) # Gets mod folder directory
        worldId = bpy.context.scene.worldId # Gets the world ID to be edited

        if preferences.directoryModelconverter == "" or preferences.directoryBtmesh == "" or preferences.directoryKnuxtools == "" or preferences.directoryHedgearcpack == "" or preferences.directoryTexconv == "": # Gives an error if a program is missing
            def missingProgramError(self, context):
                missingPrograms = [] # List of missing programs
                if preferences.directoryModelconverter == "":
                    missingPrograms.append("ModelConverter.exe")
                if preferences.directoryBtmesh == "":
                    missingPrograms.append("btmesh.exe")
                if preferences.directoryKnuxtools == "":
                    missingPrograms.append("KnuxTools.exe")
                if preferences.directoryHedgearcpack == "":
                    missingPrograms.append("HedgeArcPack.exe")
                if preferences.directoryTexconv == "":
                    missingPrograms.append("texconv.exe")
                self.layout.label(text=f"The filepath(s) for: {', '.join(missingPrograms)} are not set. \nPlease set the path(s) in Settings.") # Tells the user about the missing prorgrams

            bpy.context.window_manager.popup_menu(missingProgramError, title = "Program missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        if bpy.context.scene.modDir == "": # Gives an error if no mod directory is sent
            def missingProgramError(self, context):
                self.layout.label(text="No Mod directory is set") # Sets the popup label

            bpy.context.window_manager.popup_menu(missingProgramError, title = "Mod missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        if directoryModelconverter[-3:].lower() == "bat": # Gives an error if the user has selected the modelconverter-frontiers.bat file
            def missingProgramError(self, context):
                self.layout.label(text="The filepath set leads to a .bat file. Please make sure it leads to the main .exe for ModelConverter.") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(missingProgramError, title = ".bat file selected", icon = "ERROR") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        unpack([f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00.pac", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc.pac", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_density.pac"], directoryHedgearcpack)

        bpy.ops.object.mode_set(mode = 'OBJECT')

        #for m in bpy.data.materials:
        #    m.name = m.name.replace(".", "__") # Removes any "."s from material names, which cause crashes (broken in Blender 4.0)

        collection = bpy.context.scene.trrCollection # Gets the chosen collection
        fbxModels = [] # Initialises the list of paths to FBX models

        if os.path.exists(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp"):
            shutil.rmtree(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp")

        os.mkdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp")
        if collection == None:
            collection = bpy.context.scene.collection

        print(f"Exporting from Collection \"{collection.name}\".")

        pcmodelInstances = [] # Secret feature mainly for placing multiple animated .models (I needed it for a project)
        pccolInstances = []
        for c in collection.children:
            bpy.ops.object.select_all(action='DESELECT') # Deselects all
            for o in c.all_objects:
                original_rotate_mode = o.rotation_mode
                if o.name[:6].upper() == "_INST_":
                    if original_rotate_mode != "XZY":
                        o.rotation_mode = "QUATERNION"
                        o.rotation_mode = "XZY"

                    pcmodelInstances.append([o.name[6:].split(".")[0], (o.location.x, o.location.y, o.location.z), (o.rotation_euler.x, o.rotation_euler.y, o.rotation_euler.z), (o.scale.x, o.scale.y,o.scale.z)])
                    if original_rotate_mode != "XZY":
                        o.rotation_mode = "QUATERNION"
                        o.rotation_mode = original_rotate_mode
                elif o.name[:9].upper() == "_INSTCOL_":
                    if original_rotate_mode != "XZY":
                        o.rotation_mode = "QUATERNION"
                        o.rotation_mode = "XZY"

                    pccolInstances.append([o.name[9:].split(".")[0]+"_col", (o.location.x, o.location.y, o.location.z), (o.rotation_euler.x, o.rotation_euler.y, o.rotation_euler.z), (o.scale.x, o.scale.y,o.scale.z)])
                    if original_rotate_mode != "XZY":
                        o.rotation_mode = "QUATERNION"
                        o.rotation_mode = original_rotate_mode
                elif "INST(" in o.name:
                    if original_rotate_mode != "XZY":
                        o.rotation_mode = "QUATERNION"
                        o.rotation_mode = "XZY"
                    splitInst = o.name.split("(")

                    inst_names = splitInst[1].replace(")","").split(",")

                    inst_names.append("")
                    pcmodelInst, pccolInst = Instantiate(inst_names[0],inst_names[1],o)
                    pcmodelInstances.append(pcmodelInst)
                    if pccolInst != "":
                        pccolInstances.append(pccolInst)
                    if original_rotate_mode != "XZY":
                        o.rotation_mode = "QUATERNION"
                        o.rotation_mode = original_rotate_mode
                else:
                    if not "FrontiersAsset" in o:
                        o.select_set(True)
            bpy.ops.export_scene.fbx(filepath=f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{c.name.replace(' ', '_')}.fbx", use_selection = True, apply_scale_options = 'FBX_SCALE_UNITS', use_visible = True, add_leaf_bones=False,mesh_smooth_type='FACE')
            fbxModels.append(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{c.name.replace(' ', '_')}")

        bpy.ops.object.select_all(action='DESELECT') # Deselects all
        for obj in collection.objects:
            if not "FrontiersAsset" in obj:
                obj.select_set(True)

        bpy.ops.export_scene.fbx(filepath=f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{collection.name.replace(' ', '_')}.fbx", use_selection = True, apply_scale_options = 'FBX_SCALE_UNITS', use_visible = True, add_leaf_bones=False,mesh_smooth_type='FACE')
        fbxModels.append(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{collection.name.replace(' ', '_')}")

        if bpy.context.scene.eoTerrain == False:
            keepFiles = ["level", "txt", "rfl"]
            if bpy.context.scene.keepPcm == True:
                keepFiles.append("pcmodel")
            if bpy.context.scene.keepPcl == True:
                keepFiles.append("pccol")
            if bpy.context.scene.keepTex == True:
                keepFiles.append("dds")
            if bpy.context.scene.keepMat == True:
                keepFiles.append("material")
            clearFolder(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00", keepFiles)
            clearFolder(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc", keepFiles)
            if bpy.context.scene.keepDen == False:
                clearFolder(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_density", ["level", "txt", "rfl"])

        os.chdir(os.path.dirname(directoryModelconverter))
        pcmodel = []
        instanced_pccol = []
        for f in range(len(fbxModels)):
            fbxName = fbxModels[f].split("\\")[-1]
            print(f"Terrain - {fbxName}")
            if bpy.context.scene.noVis == False and not "_novis" in fbxName.lower():
                print("_novis" in fbxName.lower())
                os.popen(f'ModelConverter --frontiers "{fbxModels[f]}.fbx" "{fbxModels[f]}.terrain-model"').read()
                shutil.move(f"{fbxModels[f]}.terrain-model", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\{fbxName}.terrain-model")

                pcmodelObj = {"UnknownUInt32_1": 1, "InstanceName": "", "AssetName": "", "Position": {"X": 0, "Y": 0, "Z": 0}, "Rotation": {"X": 0, "Y": 0, "Z": 0}, "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}}
                pcmodelObj["InstanceName"] = fbxModels[f].split('\\')[-1] + "_model"
                pcmodelObj["AssetName"] = fbxModels[f].split('\\')[-1]
                pcmodel.append(pcmodelObj)
        for i in range(len(pcmodelInstances)): # terrain instancing
            pcmodelObj = {"UnknownUInt32_1": 1, "InstanceName": "", "AssetName": "", "Position": {"X": 0, "Y": 0, "Z": 0}, "Rotation": {"X": 0, "Y": 0, "Z": 0}, "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}}
            pcmodelObj["InstanceName"] = f"{pcmodelInstances[i][0]}_model_{i}"
            pcmodelObj["AssetName"] = pcmodelInstances[i][0]
            pcmodelObj["Position"]["X"] = pcmodelInstances[i][1][0]
            pcmodelObj["Position"]["Y"] = pcmodelInstances[i][1][2]
            pcmodelObj["Position"]["Z"] = -pcmodelInstances[i][1][1]
            pcmodelObj["Rotation"]["X"] = pcmodelInstances[i][2][0]
            pcmodelObj["Rotation"]["Y"] = pcmodelInstances[i][2][2]
            pcmodelObj["Rotation"]["Z"] = -pcmodelInstances[i][2][1]
            pcmodelObj["Scale"]["X"] = pcmodelInstances[i][3][0]
            pcmodelObj["Scale"]["Y"] = pcmodelInstances[i][3][2]
            pcmodelObj["Scale"]["Z"] = pcmodelInstances[i][3][1]
            pcmodel.append(pcmodelObj)
        for i in range(len(pccolInstances)): #Collision instancing
            pccolObj = {"UnknownUInt32_1": 1, "InstanceName": "", "AssetName": "", "Position": {"X": 0, "Y": 0, "Z": 0}, "Rotation": {"X": 0, "Y": 0, "Z": 0}, "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}}
            pccolObj["InstanceName"] = f"{pccolInstances[i][0]}_model_{i}"
            pccolObj["AssetName"] = pccolInstances[i][0]
            pccolObj["Position"]["X"] = pccolInstances[i][1][0]
            pccolObj["Position"]["Y"] = pccolInstances[i][1][2]
            pccolObj["Position"]["Z"] = -pccolInstances[i][1][1]
            pccolObj["Rotation"]["X"] = pccolInstances[i][2][0]
            pccolObj["Rotation"]["Y"] = pccolInstances[i][2][2]
            pccolObj["Rotation"]["Z"] = -pccolInstances[i][2][1]
            pccolObj["Scale"]["X"] = pccolInstances[i][3][0]
            pccolObj["Scale"]["Y"] = pccolInstances[i][3][2]
            pccolObj["Scale"]["Z"] = pccolInstances[i][3][1]
            instanced_pccol.append(pccolObj)

        if bpy.context.scene.keepPcm == False:
            print("Don't keep pcmodel")
            pcmodelFile = open(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\terrain.hedgehog.pointcloud.json", "x")
            pcmodelFile.write(json.dumps(pcmodel, indent=2))
            pcmodelFile.close()

            os.chdir(os.path.dirname(directoryKnuxtools))
            os.popen(f'knuxtools "{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\terrain.hedgehog.pointcloud.json" -e=pcmodel').read()
            shutil.move(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\terrain.pcmodel", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\terrain.pcmodel")

        else:
            print("Keep pcmodel")
            if not os.path.exists(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\terrain.pcmodel"):
                print("Add anyway")
                pcmodelFile = open(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\terrain.hedgehog.pointcloud.json", "x")
                pcmodelFile.write(json.dumps(pcmodel, indent=2))
                pcmodelFile.close()

                os.chdir(os.path.dirname(directoryKnuxtools))
                os.popen(f'knuxtools "{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\terrain.hedgehog.pointcloud.json" -e=pcmodel').read()
                shutil.move(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\terrain.pcmodel", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\terrain.pcmodel")
        if bpy.context.scene.keepPcl == False and instanced_pccol != []:
            print("add collision instance")
            pccolFile = open(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\instance_collision.hedgehog.pointcloud.json", "x")
            pccolFile.write(json.dumps(instanced_pccol, indent=2))
            pccolFile.close()

            os.chdir(os.path.dirname(directoryKnuxtools))
            os.popen(f'knuxtools "{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\instance_collision.hedgehog.pointcloud.json" -e=pccol').read()
            shutil.move(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\instance_collision.pccol", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc\\instance_collision.pccol")

        tempFolderContents = os.listdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\")
        for f in range(len(tempFolderContents)): # For every file in the temp folder
            if tempFolderContents[f].split(".")[-1].lower() == "material": # If the file is a .material
                if bpy.context.scene.keepMat == False:
                    shutil.move(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{tempFolderContents[f]}", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\{tempFolderContents[f]}")
                else:
                    try:
                        shutil.move(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{tempFolderContents[f]}", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\")
                    except:
                        pass

        os.chdir(os.path.dirname(directoryBtmesh))
        for f in range(len(fbxModels)):
            fbxName = fbxModels[f].split("\\")[-1]
            print(f"Collision - {fbxName}")
            if bpy.context.scene.noCol == False and not "_nocol" in fbxName.lower():
                print("_nocol" in fbxName.lower())
                os.popen(f'btmesh "{fbxModels[f]}.fbx"').read()
                shutil.move(f"{fbxModels[f]}_col.btmesh", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc\\{fbxName}_col.btmesh")
                shutil.move(f"{fbxModels[f]}_col.pccol", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc\\{fbxName}_col.pccol")

        loggedImages = []
        for o in collection.all_objects:
            if o.type == "MESH" and not "FrontiersAsset" in o:
                for m in o.data.materials:
                    try:
                        for n in m.node_tree.nodes:
                            if n.type == "TEX_IMAGE":
                                if os.path.exists(os.path.abspath(bpy.path.abspath(n.image.filepath))):
                                    loggedImages.append(os.path.abspath(bpy.path.abspath(n.image.filepath)))
                                else:
                                    n.image.file_format = "PNG"
                                    n.image.name = n.image.name.replace(".dds", ".png").replace(".DDS", ".png")
                                    n.image.filepath_raw = f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{n.image.name}"
                                    n.image.save()
                                    loggedImages.append(n.image.filepath)
                    except Exception as e:
                        print(e)

        for i in loggedImages:
            print(i)
            if i[-4:].lower() == ".dds":
                print(f"From: {i}, To: {absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00")
                shutil.copy2(i, f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00")
                loggedImages.pop(loggedImages.index(i))

        texList = open(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\texList.txt", "x")
        texList.write("\n".join(loggedImages))
        texList.close()

        os.chdir(os.path.dirname(directoryTexconv))
        texListLocation = f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\texList.txt"
        texDestination = f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00"
        if bpy.context.scene.keepTex == False:
            print(os.popen(f'texconv -flist "{texListLocation}" -y -f BC7_UNORM -o "{texDestination}"').read())
        else:
            if not os.path.exists(texDestination):
                print(os.popen(f'texconv -flist "{texListLocation}" -f BC7_UNORM -o "{texDestination}"').read())

        shutil.rmtree(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp")

        if bpy.context.scene.noPack == False:
            pack([f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_density"], directoryHedgearcpack)
        self.report({"INFO"}, f"Quick Export Finished")
        return{"FINISHED"}

class ExportObjects(bpy.types.Operator):
    bl_idname = "qexport.exportobjects"
    bl_label = "Objects"
    bl_description = "Exports your level's objects and paths"

    def ID_generator(self):
        Id = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
        hexValues = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
        for i in range(32):
            Id = Id.replace("X", hexValues[random.randrange(len(hexValues))], 1) # generates a random ID
        return Id


    def execute(self, context):

        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        directoryHedgeset = os.path.abspath(bpy.path.abspath(preferences.directoryHedgeset)) # Gets Hedgeset path from preferences
        directoryHedgearcpack = os.path.abspath(bpy.path.abspath(preferences.directoryHedgearcpack)) # Gets HedgeArcPack path from preferences

        absoluteModDir = os.path.abspath(bpy.path.abspath(bpy.context.scene.modDir)) # Gets mod folder directory
        worldId = bpy.context.scene.worldId # Gets the world ID to be edited

        if preferences.directoryHedgeset == "" or preferences.directoryHedgearcpack == "": # Gives an error if a program is missing
            def missingProgramError(self, context):
                missingPrograms = [] # List of missing programs
                if preferences.directoryHedgeset == "":
                    missingPrograms.append("HedgeSet.exe")
                if preferences.directoryHedgearcpack == "":
                    missingPrograms.append("HedgeArcPack.exe")
                self.layout.label(text=f"The filepath(s) for: {', '.join(missingPrograms)} are not set. \nPlease set the path(s) in Settings.") # Tells the user about the missing prorgrams

            bpy.context.window_manager.popup_menu(missingProgramError, title = "Program missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        if bpy.context.scene.modDir == "": # Gives an error if no mod directory is sent
            def missingProgramError(self, context):
                self.layout.label(text="No Mod directory is set") # Sets the popup label

            bpy.context.window_manager.popup_menu(missingProgramError, title = "Mod missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        unpack([f"{absoluteModDir}\\raw\\gedit\\{worldId}_gedit.pac"], directoryHedgearcpack)

        if bpy.context.scene.eoObjects == False:
            clearFolder(f"{absoluteModDir}\\raw\\gedit\\{worldId}_gedit", ["level", "txt", "rfl"])

        bpy.ops.object.mode_set(mode = 'OBJECT')

        #Get check info
        path_check = context.scene.FrontiersRails.objPath_check
        # Get the collection

        Node_startindex = context.scene.FrontiersRails.Railnode_startindex

        collection_name = bpy.context.scene.objCollection
        collection = collection_name

        if collection_name == None:
            self.report({"WARNING"}, f"Collection{collection_name} not found")
            return {"CANCELLED"}

        collections = [collection_name]
        for c in collection_name.children:
            collections.append(c)

        blend_file_path = bpy.data.filepath
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        blend_dir = os.path.dirname(blend_file_path)
        path_dir = os.path.join(blend_dir,script_dir)

        #Set up compatible objects depending on the files in template file
        ObjectDirectory = f"objects"
        ObjectDirectory_path = os.path.join(path_dir,ObjectDirectory)
        volume_objects = ["CameraFollow", "CameraPan","CameraFix","CameraRailSideView","CameraRailForwardView"] #Only volumes with double code
        compatible_objects =[]
        try:
            json_files = [file for file in os.listdir(ObjectDirectory_path) if file.endswith('.json')]
            if not json_files:
                print(f"No .json files found in the custom template directory {ObjectDirectory_path}.")
            else:
                for file in json_files:
                    is_volume_object = False
                    for volOBJ in volume_objects:
                        object_name = file.split(".")[0]
                        if object_name == volOBJ:
                            is_volume_object = True
                            break
                    if is_volume_object == False:
                        compatible_objects.append(object_name)
        except Exception as direcerror:
            print(f'Custom directory gave this error: {direcerror}')
            pass

        volume_objects = ["CameraFollow", "CameraPan","CameraFix","CameraRailSideView","CameraRailForwardView"] #Only volumes with double code
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
                    print(f"No .json files found in the custom template directory {CustomDirectory_path}.")
                else:
                    Customdir = True
                    for file in txt_files:
                        txt_file_names.append((file.split("."))[0])
                    compatible_objects.extend(txt_file_names)
            except Exception as direcerror:
                print(f'Custom directory gave this error: {direcerror}')
                pass

        for c in collections:
        # RAILS SECTION ---------------------------------------------------------------------
            collection: bpy.types.Collection = c
            gedit_text = ""
            changed_UID_list =[]
            bpy.ops.object.select_all(action='DESELECT')

            for obj in collection.objects:
                if obj.type != 'CURVE':
                    continue

                curve_objects = path_export.curve_to_hson_objects(
                    obj,
                    Node_startindex,
                    changed_UID_list,
                    lambda t: self.report({"WARNING"}, t)
                )

                gedit_text += "".join(curve_objects)
                Node_startindex += len(curve_objects) - 1

            print(gedit_text)

            if changed_UID_list != []:
                self.report({"INFO"}, f"Duplicate ID's were found. Objects with changed IDs are: {changed_UID_list}")


        # OBJECTS SECTION --------------------------------------------------------------
            collection = c
            changed_ID_list =[]
            printed_text = ""
            try:
                gedit_text
            except:
                gedit_text = ""
            obj_text = ""
            Volumeindex = 0
            bpy.ops.object.select_all(action='DESELECT')
            # Iterate through all objects in the collection
            for obj in collection.objects:
                properties = {}
                name = obj.name
                coordinates = [round(obj.location.x,1), round(obj.location.z,1), -round(obj.location.y,1)]
                #coordinates = "["+ coordinates + "]"
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                #Creates rotation values
                original_rotation_mode = obj.rotation_mode
                obj.rotation_mode = 'QUATERNION'
                rotation = [round(obj.rotation_quaternion.x,3), round(obj.rotation_quaternion.z,3), -round(obj.rotation_quaternion.y,3), round(obj.rotation_quaternion.w,3)]
                obj.rotation_mode = original_rotation_mode
                #rotation = "["+ rotation + "]"

                # Generates a random ID
                if "DataID" not in obj:
                    Id = self.ID_generator()
                    obj["DataID"] = Id
                    Id = '{'+Id+'}'
                else:
                    Id = obj["DataID"]
                    Id = '{'+Id+'}'
                for Otherobj in bpy.data.objects:
                    if "DataID" in Otherobj:
                        if Otherobj["DataID"] == obj["DataID"] and Otherobj != obj:
                            changed_ID_list.append(Otherobj.name)
                            OtherID = self.ID_generator()
                            Otherobj["DataID"] = OtherID

                printed_text += f"Object: {obj.name}\n"#adds name, coords and rotation to the coordinate window
                printed_text += f"Location: {coordinates}\n"
                printed_text += f"Rotation: {rotation}\n"
                #If it is a light
                if obj.type == 'LIGHT':
                    #check if it is one of the two supported lights
                    if obj.data.type == 'POINT':
                        file_name = f"objects\PointLight.json"
                        file_path = os.path.join(path_dir, file_name)
                        with open(file_path, "r") as file: #with open opens the file temporarily in order to avoid memory leak
                            light_temp = json.load(file)
                        if "json_parameters" in obj and "use_display_json_parameters" in obj and obj["use_display_json_parameters"] == True: #if Manual parameters are checked. do this instead of geonodes.
                            for parameter in obj.json_parameters:
                                PropertyName = parameter.name
                                PropertyType = PropertyName.split("/")[-1]
                                propvector = False
                                if PropertyType == "float":
                                    PropertyValue = parameter.float_value
                                elif PropertyType == "enum":
                                    enumParameter = parameter.enum_items
                                    foundEnum = False
                                    for enumItems in enumParameter:
                                        if enumItems.selected == True:
                                            PropertyValue = enumItems.value
                                            foundEnum = True
                                            break
                                    if foundEnum == False:
                                        PropertyValue = enumParameter[0].value
                                elif PropertyType == "int":
                                    PropertyValue = parameter.int_value
                                elif PropertyType == "bool":
                                    PropertyValue = parameter.bool_value
                                elif PropertyType == "vector":
                                    propvector = True
                                    PropertyValue = parameter.vector_value
                                elif PropertyType == "string":
                                    if parameter.object_value in bpy.data.objects and "DataID" in bpy.data.objects[parameter.object_value]:
                                         IDstring = "{"+bpy.data.objects[parameter.object_value]+"}"
                                         PropertyValue = IDstring
                                    else:
                                        PropertyValue = parameter.string_value
                                elif PropertyType == "ERR":
                                    print(f'for object {name},Attribute:{AttName} was passed for being incompatible in current version.')
                                    continue
                                CurrentLevel = light_temp["parameters"]

                                if "/" in PropertyName:#If propertyname is on the form [Firstlayer][Secondlayer], Make sure that the script replaces the value on that layer.

                                    PropertyName = PropertyName.split("/")

                                    for key in PropertyName[:-2]:
                                        if "[" in key:
                                            ListKey = key.split("[")
                                            Listindex = int(ListKey[1].split("]")[0])
                                            CurrentLevel = CurrentLevel[ListKey[0]][Listindex]
                                        else:
                                            CurrentLevel = CurrentLevel[key]
                                    # if type(CurrentLevel) == list:
                                    #     CurrentLevel = CurrentLevel[0]
                                    PropertyName = PropertyName[-2]

                                if propvector == True:
                                    CurrentLevel[PropertyName] = [PropertyValue[0],PropertyValue[1],PropertyValue[2]]
                                else:
                                    CurrentLevel[PropertyName] = PropertyValue
                        light_temp["id"] = Id
                        light_temp["name"] = name
                        light_temp["position"] = coordinates

                        Intense = obj.data.energy/64 #Have to divide blenders intensity to accurately portrait frontiers lights.
                        CurrentLevel = light_temp["parameters"]
                        CurrentLevel["colorR"] = obj.data.color[0]*255*Intense
                        CurrentLevel["colorG"] = obj.data.color[1]*255*Intense
                        CurrentLevel["colorB"] = obj.data.color[2]*255*Intense
                        CurrentLevel["sourceRadius"] = obj.data.shadow_soft_size
                        render_engine = bpy.context.scene.render.engine
                        if render_engine == 'BLENDER_EEVEE':
                            CurrentLevel["enableShadow"] = obj.data.use_shadow
                        elif render_engine == 'CYCLES':
                            CurrentLevel["enableShadow"] = obj.data.cycles.cast_shadow
                        obj_text += f'{json.dumps(light_temp, indent=2)},\n' #Adds code to full gedit text that is then printed
                else:
                    theobject = name.split(".")[0]
                    if "FrontiersCamera" in obj:
                        compatible_list = compatible_objects + volume_objects
                    else:
                        compatible_list = compatible_objects
                    if theobject in compatible_list: #Checks if object is compatible with Gedit templates
                        # Construct the full path to the text file
                        if Customdir == True and theobject in txt_file_names: #Check if the object is one of the custom ones.
                            file_name = f"{theobject}.json"
                            file_path = os.path.join(CustomDirectory_path, file_name)
                        else:
                            file_name = f"objects\{theobject}.json"
                            file_path = os.path.join(path_dir, file_name)

                        with open(file_path, "r") as file: #with open opens the file temporarily in order to avoid memory leak
                            object_temp = json.load(file)

                        try: #this is for properties which is unstable. Thats why there is a try/except argument here in case things break
                            if "json_parameters" in obj and "use_display_json_parameters" in obj and obj["use_display_json_parameters"] == True: #if Manual parameters are checked. do this instead of geonodes.
                                for parameter in obj.json_parameters:
                                    PropertyName = parameter.name
                                    PropertyType = PropertyName.split("/")[-1]
                                    propvector = False
                                    if PropertyType == "float":
                                        PropertyValue = parameter.float_value
                                    elif PropertyType == "enum":
                                        enumParameter = parameter.enum_items
                                        foundEnum = False
                                        for enumItems in enumParameter:
                                            if enumItems.selected == True:
                                                PropertyValue = enumItems.value
                                                foundEnum = True
                                                break
                                        if foundEnum == False:
                                            PropertyValue = enumParameter[0].value
                                    elif PropertyType == "int":
                                        PropertyValue = parameter.int_value
                                    elif PropertyType == "bool":
                                        PropertyValue = parameter.bool_value
                                    elif PropertyType == "vector":
                                        propvector = True
                                        PropertyValue = parameter.vector_value
                                    elif PropertyType == "string":
                                        if parameter.object_value != None and parameter.object_value.name in bpy.data.objects and "DataID" in parameter.object_value and parameter.object_value.type != "CURVE":
                                            IDstring = "{"+parameter.object_value["DataID"]+"}"
                                            PropertyValue = IDstring
                                        elif parameter.object_value != None and parameter.object_value.name in bpy.data.objects and "UID" in parameter.object_value and parameter.object_value.type == "CURVE":
                                            UIDstring = "SetPath_"+parameter.object_value["UID"]
                                            PropertyValue = UIDstring
                                        else:
                                            PropertyValue = parameter.string_value
                                    elif PropertyType.startswith("list"):
                                        if PropertyType == "listINT":
                                            PropertyValue = [parameter.list_value[item].listint for item in range(len(parameter.list_value))]
                                        elif PropertyType == "listFLOAT":
                                            PropertyValue = [parameter.list_value[item].listfloat for item in range(len(parameter.list_value))]
                                        else:
                                            PropertyValue = []
                                            for item in range(len(parameter.list_value)):
                                                if parameter.list_value[item].listobject != None and parameter.list_value[item].listobject.name in bpy.data.objects and "DataID" in parameter.list_value[item].listobject and parameter.list_value[item].listobject.type == "MESH":
                                                    PropertyValue.append("{"+parameter.list_value[item].listobject["DataID"]+"}")
                                                elif parameter.list_value[item].listobject != None and parameter.list_value[item].listobject.name in bpy.data.objects and "UID" in parameter.list_value[item].listobject and parameter.list_value[item].listobject.type == "CURVE":
                                                    PropertyValue.append("SetPath_"+parameter.list_value[item].listobject["UID"])
                                                else:
                                                    parameter.list_value[item].liststring

                                            while("" in PropertyValue):
                                                PropertyValue.remove("")
                                    elif PropertyType == "ERR":
                                        print(f'for object {name},Attribute:{AttName} was passed for being incompatible in current version.')
                                        continue
                                    CurrentLevel = object_temp["parameters"]

                                    if "/" in PropertyName:#If propertyname is on the form [Firstlayer][Secondlayer], Make sure that the script replaces the value on that layer.

                                        PropertyName = PropertyName.split("/")

                                        for key in PropertyName[:-2]:
                                            if "[" in key:
                                                ListKey = key.split("[")
                                                Listindex = int(ListKey[1].split("]")[0])
                                                CurrentLevel = CurrentLevel[ListKey[0]][Listindex]
                                            else:
                                                CurrentLevel = CurrentLevel[key]
                                        # if type(CurrentLevel) == list:
                                        #     CurrentLevel = CurrentLevel[0]
                                        PropertyName = PropertyName[-2]

                                    if propvector == True:
                                        CurrentLevel[PropertyName] = [PropertyValue[0],PropertyValue[1],PropertyValue[2]]
                                    else:
                                        CurrentLevel[PropertyName] = PropertyValue



                            else:
                                #this code generates the property names and values and puts them in a dictionary... Somehow...
                                C = bpy.context

                                propdata = C.object.evaluated_get(C.evaluated_depsgraph_get()).data #I think this imports all depsgraph data of the object
                                for i in range(len(propdata.attributes)): #This does iterate through all possible attributes
                                    try:
                                        field_src = propdata.attributes[i].data
                                        listobject = False
                                        AttName = propdata.attributes[i].name #Get attribute name
                                        AttName = AttName.split(";") # Splits AttName into a list. Index 0 is the type, index 1 is the attribute name in the template and the rest is for the name
                                        CurrentLevel = object_temp["parameters"]

                                        if len(AttName) > 1: #If a name exists, put it in Property name
                                            PropertyName = AttName[1]
                                            if "/" in PropertyName:#If propertyname is on the form [Firstlayer][Secondlayer], Make sure that the script replaces the value on that layer.

                                                PropertyName = PropertyName.split("/")

                                                for key in PropertyName[:-1]:
                                                    CurrentLevel = CurrentLevel[key]
                                                if type(CurrentLevel) == list:
                                                    CurrentLevel = CurrentLevel[0]
                                                PropertyName = PropertyName[-1]
                                            if "-" in PropertyName:#If propertyname is on the form -[parameter], the script will look above the parameter tab
                                                PropertyName = PropertyName.split("-")
                                                PropertyName = PropertyName[-1]
                                                CurrentLevel = object_temp
                                            if "[" in PropertyName:#If propertyname is defined with an index(i.e a list), put on that index
                                                PropertyName = PropertyName.split("[")
                                                proplistindex = PropertyName[1].split("]")
                                                proplistindex = int(proplistindex[0])
                                                PropertyName = PropertyName[0]
                                                listobject = True
                                            if AttName[0] == "VEC":#if type is a vector(Must be handled seperately from the rest due to field_src being different for vectors)

                                                field = [0.0] * len(field_src)*3
                                                field_src.foreach_get("vector", field) # Gets attribute value (a number)
                                                if listobject == True:
                                                    CurrentLevel[PropertyName][proplistindex] = [field[0],field[1],field[2]]
                                                else:
                                                    CurrentLevel[PropertyName] = [field[0],field[1],field[2]]

                                            elif AttName[0] == "RELVEC":

                                                field = [0.0] * len(field_src)*3
                                                field_src.foreach_get("vector", field) # Gets attribute value (a number)
                                                if listobject == True:
                                                    CurrentLevel[PropertyName][proplistindex] = [field[0]+obj.location.x,field[1]+obj.location.z,field[2]-obj.location.y]
                                                else:
                                                    CurrentLevel[PropertyName] = [field[0]+obj.location.x,field[1]+obj.location.z,field[2]-obj.location.y]

                                            elif AttName[1] == "ROTVEC":#if type is a vector(Must be handled seperately from the rest due to field_src being different for vectors)

                                                field = [0.0] * len(field_src)*3
                                                field_src.foreach_get("vector", field) # Gets attribute value (a number)
                                                EulerRot = [field[0],field[1],field[2]]
                                                obj.rotation_mode = 'XYZ'
                                                bpy.context.active_object.rotation_euler[0] = EulerRot[0]
                                                bpy.context.active_object.rotation_euler[1] = EulerRot[1]
                                                bpy.context.active_object.rotation_euler[2] = EulerRot[2]
                                                obj.rotation_mode = 'QUATERNION'
                                                rotation = [round(obj.rotation_quaternion.x,3), round(obj.rotation_quaternion.z,3), -round(obj.rotation_quaternion.y,3), round(obj.rotation_quaternion.w,3)]
                                                obj.rotation_mode = 'XYZ'
                                                bpy.context.active_object.rotation_euler[0] = 0.0
                                                bpy.context.active_object.rotation_euler[1] = 0.0
                                                bpy.context.active_object.rotation_euler[2] = 0.0
                                                obj.rotation_mode = original_rotation_mode
                                                CurrentLevel[PropertyName] = EulerRot

                                            else:

                                                if AttName[0] == "BOOL" or AttName[0] == "FLOAT" or AttName[0] == "INT" or AttName[0] == "NAME" or AttName[0] == "PROP":
                                                    field = [0.0] * len(field_src)
                                                    field_src.foreach_get('value', field) # Gets attribute value (a number)

                                                    if AttName[0] == "BOOL": #if the type is a bool object (true or false)
                                                        bool_value = bool(field[0]) #Turn the value of the attribute into a bool (0 turns to false and 1 to true)
                                                        if listobject == True:
                                                            CurrentLevel[PropertyName][proplistindex] = bool_value
                                                        else:
                                                            CurrentLevel[PropertyName] = bool_value #replace it in the template

                                                    elif AttName[0] == "FLOAT": #if it is a float, put it in as a the float value
                                                        if listobject == True:
                                                            CurrentLevel[PropertyName][proplistindex] = float(field[0])
                                                        else:
                                                            CurrentLevel[PropertyName] = float(field[0])

                                                    elif AttName[0] == "INT": #if it is a integer, put it in as a integer value
                                                        if listobject == True:
                                                            print(f'{CurrentLevel[PropertyName][proplistindex]}')
                                                            CurrentLevel[PropertyName][proplistindex] = int(field[0])
                                                        else:
                                                            CurrentLevel[PropertyName] = int(field[0])

                                                    elif AttName[0] == "NAME": #if type is name, this uses the attname list as the values and adds that instead
                                                        NameIndex = field[0] + 1 #Sets the index from the value of the name skipping the type and property
                                                        if listobject == True:
                                                            CurrentLevel[PropertyName][proplistindex] = AttName[NameIndex]
                                                        else:
                                                            CurrentLevel[PropertyName] = AttName[NameIndex]

                                                    elif AttName[0] == "PROP": #if type is PROP, this looks in the object properties to find name attributes
                                                        NameIndex = field[0] - 1 #Sets the index from the value of the name skipping the type and property
                                                        PropObjectName = obj[PropertyName]
                                                        PropObjectName = PropObjectName.split(";")
                                                        if listobject == True:
                                                            CurrentLevel[PropertyName][proplistindex] = PropObjectName[NameIndex]
                                                        else:
                                                            CurrentLevel[PropertyName] = PropObjectName[NameIndex]

                                    except Exception as error:
                                        print(f'Error for object {name} with Attribute:{AttName} is: {error}')
                                        pass
                        except Exception as error:
                            print(f'Error for object {name}: {error}')
                            pass
                        #adds the values
                        object_temp["id"] = Id
                        object_temp["name"] = name
                        object_temp["position"] = coordinates
                        if "rotation" in object_temp:
                            object_temp["rotation"] = rotation
                        if obj.parent:
                            if obj.parent.type == 'CURVE' and "UID" in obj.parent:
                                path_name = f"SetPath_{obj.parent['UID']}"
                                pathnameoptions = ["pathName","pathname","movePathName"]
                                for pathoption in pathnameoptions:
                                    if pathoption in object_temp["parameters"]:
                                        object_temp["parameters"][pathoption] = path_name
                                    # If "pathName" not found, recursively search in nested subcategories
                                    else:
                                        for key, value in object_temp["parameters"].items():
                                            if isinstance(value, dict):
                                                CurrentLevel = object_temp["parameters"][key]
                                                if pathoption in CurrentLevel:
                                                    CurrentLevel[pathoption] = path_name
                            if obj.name.startswith("CameraVolumeSub.") and "DataID2" in obj.parent:
                                parentVolume = "{"+obj.parent["DataID2"] +"}"
                                object_temp["parameters"]["target"] = parentVolume
                            elif obj.name.startswith("CameraVolumeSub.") and "DataID" in obj.parent and obj.parent.name.startswith("CameraVolume."):
                                parentVolume = "{"+obj.parent["DataID"] +"}"
                                object_temp["parameters"]["target"] = parentVolume
#                        if obj.children is not None:
#                            childlist = []
#                            for child in obj.children:
#                                if child.type == 'MESH' and "DataID" in child:
#                                    childID = "{"+child["DataID"]+"}"
#                                    childlist.append(childID)
#                                elif child.type == 'MESH' and "DataID" not in child:
#                                    childID = self.ID_generator()
#                                    child["DataID"] = childID
#                                    childID = "{"+child["DataID"]+"}"
#                                    childlist.append(childID)
#                            if childlist != []:
#                                if "actions" in object_temp["parameters"]:
#                                    object_temp["parameters"]["actions"][0]["objectIds"] = childlist
#                                # If "Actions" not found, recursively search in nested subcategories
#                                else:
#                                    for key, value in object_temp["parameters"].items():
#                                        if isinstance(value, dict):
#                                            CurrentLevel = object_temp["parameters"][key]
#                                            if "actions" in CurrentLevel:
#                                                CurrentLevel["actions"][0]["objectIds"] = childlist
                        if obj.parent is not None:
                            true_location = obj.matrix_world.translation # get global location
                            mathutils.Matrix.identity(obj.matrix_parent_inverse) #Turn the parent inverse matrix into an identity matrix (makes parent the origin)
                            obj.location = true_location - obj.parent.location #make sure the object stays at global position if inverse matrix changed
                            #rest adds parentId to object code
                            if "DataID" in obj.parent:
                                parentID = "{"+obj.parent["DataID"]+"}"
                            else:
                                parentID = self.ID_generator()
                                obj.parent["DataID"] = parentID
                                parentID = "{"+obj.parent["DataID"]+"}"
                            object_temp["parentId"] = parentID

                        obj_text += f'{json.dumps(object_temp, indent=2)},\n' #Adds code to full gedit text that is then printed

                    for thevolume in volume_objects: #checks for volume objects
                        #if name.startswith(thevolume+'.') and "FrontiersCamera" not in obj:
                        if name.split(".")[0] == thevolume and "FrontiersCamera" not in obj:
                            Volumeindex += 1
                            #Reset rotation

                            obj.rotation_mode = 'XYZ'
                            bpy.context.active_object.rotation_euler[0] = 0.0
                            bpy.context.active_object.rotation_euler[1] = 0.0
                            bpy.context.active_object.rotation_euler[2] = 0.0
                            obj.rotation_mode = 'QUATERNION'
                            rotation = [round(obj.rotation_quaternion.x,3), round(obj.rotation_quaternion.z,3), -round(obj.rotation_quaternion.y,3), round(obj.rotation_quaternion.w,3)]
                            obj.rotation_mode = original_rotation_mode

                            # Generates a random ID
                            if "DataID" not in obj:
                                Id = self.ID_generator()
                                obj["DataID"] = Id
                                Id = '{'+Id+'}'
                            else:
                                Id = obj["DataID"]
                                Id = '{'+Id+'}'
                            for Otherobj in bpy.data.objects:
                                if "DataID" in Otherobj:
                                    if Otherobj["DataID"] == obj["DataID"] and Otherobj != obj:
                                        changed_ID_list.append(Otherobj.name)
                                        OtherID = self.ID_generator()
                                        Otherobj["DataID"] = OtherID
                                camX = ""
                                file_name = f"objects\_legacy_{thevolume}.json"
                                file_path = os.path.join(path_dir, file_name)

                            if "DataID2" not in obj:
                                SecondId = self.ID_generator()
                                obj["DataID2"] = SecondId
                                SecondId = '{'+SecondId+'}'
                            else:
                                SecondId = obj["DataID2"]
                                SecondId = '{'+SecondId+'}'
                            for Otherobj in bpy.data.objects:
                                if "DataID2" in Otherobj:
                                    if Otherobj["DataID2"] == obj["DataID2"] and Otherobj != obj:
                                        changed_ID_list.append(Otherobj.name)
                                        OtherID = self.ID_generator()
                                        Otherobj["DataID2"] = OtherID # generates a random ID2

                            with open(file_path, "r") as file: #with open opens the file temporarily in order to avoid memory leak
                                volume_temp = file.read() # Opens the file as a text file
                                volume_temp = volume_temp.split(";") # Splits at the semicolon in the file (there are 2 jsons in one file)
                                otherVolume_temp = volume_temp[1] # Sets volume_temp and otherVolume_temp to one half of the file each
                                volume_temp = volume_temp[0]

                                volume_temp = json.loads(volume_temp) # Converts each half of the file to a python dictionary
                                otherVolume_temp = json.loads(otherVolume_temp)
                            try: #this is for properties which is unstable. Thats why there is a try/except argument here in case things break
                                #this code generates the property names and values and puts them in a dictionary... Somehow...
                                C = bpy.context
                                properties = {}
                                propdata = C.object.evaluated_get(C.evaluated_depsgraph_get()).data #I think this imports all depsgraph data of the object
                                for i in range(len(propdata.attributes)): #This does iterate through all possible attributes
                                    try:
                                        field_src = propdata.attributes[i].data

                                        AttName = propdata.attributes[i].name #Get attribute name
                                        AttName = AttName.split(";") # Splits AttName into a list. Index 0 is the type, index 1 is the attribute name in the template and the rest is for the name
                                        if AttName[0] == "VOL":
                                            CurrentLevel = volume_temp["parameters"]
                                        elif AttName[0] == "CAM":
                                            CurrentLevel = otherVolume_temp["parameters"]
                                        if len(AttName) > 1: #If a name exists, put it in Property name
                                            PropertyName = AttName[2]
                                            if "/" in PropertyName:#If propertyname is on the form [Firstlayer][Secondlayer], Make sure that the script replaces the value on that layer.

                                                PropertyName = PropertyName.split("/")

                                                for key in PropertyName[:-1]:
                                                    CurrentLevel = CurrentLevel[key]
                                                if type(CurrentLevel) == list:
                                                    CurrentLevel = CurrentLevel[0]
                                                PropertyName = PropertyName[-1]
                                            if "-" in PropertyName:#If propertyname is on the form -[parameter], the script will look above the parameter tab
                                                PropertyName = PropertyName.split("-")
                                                PropertyName = PropertyName[-1]
                                                if AttName[0] == "VOL":
                                                    CurrentLevel = volume_temp
                                                elif AttName[0] == "CAM":
                                                    CurrentLevel = otherVolume_temp

                                            if AttName[1] == "VEC":#if type is a vector(Must be handled seperately from the rest due to field_src being different for vectors)

                                                field = [0.0] * len(field_src)*3
                                                field_src.foreach_get("vector", field) # Gets attribute value (a number)
                                                CurrentLevel[PropertyName] = [field[0],field[1],field[2]]

                                            elif AttName[1] == "RELVEC":

                                                field = [0.0] * len(field_src)*3
                                                field_src.foreach_get("vector", field) # Gets attribute value (a number)
                                                CurrentLevel[PropertyName] = [field[0]+obj.location.x,field[1]+obj.location.z,field[2]-obj.location.y]

                                            elif AttName[1] == "ROTVEC":#if type is a vector(Must be handled seperately from the rest due to field_src being different for vectors)

                                                field = [0.0] * len(field_src)*3
                                                field_src.foreach_get("vector", field) # Gets attribute value (a number)
                                                EulerRot = [field[0],field[1],field[2]]
                                                obj.rotation_mode = 'XYZ'
                                                bpy.context.active_object.rotation_euler[0] = EulerRot[0]
                                                bpy.context.active_object.rotation_euler[1] = EulerRot[1]
                                                bpy.context.active_object.rotation_euler[2] = EulerRot[2]
                                                obj.rotation_mode = 'QUATERNION'
                                                rotation = [round(obj.rotation_quaternion.x,3), round(obj.rotation_quaternion.z,3), -round(obj.rotation_quaternion.y,3), round(obj.rotation_quaternion.w,3)]
                                                obj.rotation_mode = 'XYZ'
                                                bpy.context.active_object.rotation_euler[0] = 0.0
                                                bpy.context.active_object.rotation_euler[1] = 0.0
                                                bpy.context.active_object.rotation_euler[2] = 0.0
                                                obj.rotation_mode = original_rotation_mode
                                                CurrentLevel[PropertyName] = EulerRot

                                            else:

                                                if AttName[1] == "BOOL" or AttName[1] == "FLOAT" or AttName[1] == "INT" or AttName[1] == "NAME":
                                                    field = [0.0] * len(field_src)
                                                    field_src.foreach_get('value', field) # Gets attribute value (a number)



                                                    if AttName[1] == "BOOL": #if the type is a bool object (true or false)
                                                        bool_value = bool(field[0]) #Turn the value of the attribute into a bool (0 turns to false and 1 to true)
                                                        CurrentLevel[PropertyName] = bool_value #replace it in the template

                                                    elif AttName[1] == "FLOAT": #if it is a float, put it in as a the float value
                                                        CurrentLevel[PropertyName] = float(field[0])

                                                    elif AttName[1] == "INT": #if it is a integer, put it in as a integer value
                                                        CurrentLevel[PropertyName] = int(field[0])

                                                    elif AttName[1] == "NAME": #if type is name, this uses the attname list as the values and adds that instead
                                                        NameIndex = field[0] + 2 #Sets the index from the value of the name skipping the type and property
                                                        CurrentLevel[PropertyName] = AttName[NameIndex]
                                    except Exception as atterror:
                                        print(f'passed Error for object {name} with {AttName} is: {atterror}')
                                        pass
                            except Exception as error:
                                print(f'Error for object {name} is: {error}')
                                pass

                            # Adds the values that are used in all volumes
                            volume_temp["parameters"]["target"] = Id
                            volume_temp["id"] = SecondId
                            otherVolume_temp["id"] = Id
                            otherVolume_temp["name"] = name
                            volume_temp["name"] =  "Volume." + f"{Volumeindex}"
                            volume_temp["position"] = coordinates
                            if "rotation" in volume_temp:
                                volume_temp["rotation"] = rotation
                            if obj.parent:
                                if obj.parent.type == 'CURVE' and "UID" in obj.parent:
                                    path_name = f"SetPath_{obj.parent['UID']}"
                                    if "pathName" in otherVolume_temp["parameters"]:
                                        otherVolume_temp["parameters"]["pathName"] = path_name
                                    # If "pathName" not found, recursively search in nested subcategories
                                    else:
                                        for key, value in otherVolume_temp["parameters"].items():
                                            if isinstance(value, dict):
                                                CurrentLevel = otherVolume_temp["parameters"][key]
                                                if "pathName" in CurrentLevel:
                                                    CurrentLevel["pathName"] = path_name

                            obj_text += json.dumps(volume_temp, indent = 2)
                            obj_text += ",\n"
                            obj_text += json.dumps(otherVolume_temp, indent = 2) #Adds code to full gedit text that is then printed
                            obj_text += ",\n"


                obj.select_set(False)

            #Code that opens the window with the gedit code
            if obj_text != "":
                obj_text = textwrap.indent(obj_text, '    ')
                gedit_text += obj_text
            gedit_text = '{\n  "version": 1,\n  "objects": [\n' + gedit_text[:-2] + "\n  ]\n}"

            gedit = open(f"{absoluteModDir}\\raw\\gedit\\{worldId}_gedit\\{worldId}_{collection.name}.hson", "x")
            gedit.write(gedit_text)
            gedit.close()

            os.chdir(os.path.dirname(directoryHedgeset))
            print(os.popen(f'HedgeSet "{absoluteModDir}\\raw\\gedit\\{worldId}_gedit\\{worldId}_{collection.name}.hson" "{absoluteModDir}\\raw\\gedit\\{worldId}_gedit\\{worldId}_{collection.name}.gedit" -game=frontiers -platform=pc').read())

            os.remove(f"{absoluteModDir}\\raw\\gedit\\{worldId}_gedit\\{worldId}_{collection.name}.hson")

        if bpy.context.scene.noPack == False:
            pack([f'{absoluteModDir}\\raw\\gedit\\{worldId}_gedit'], directoryHedgearcpack)
        self.report({"INFO"}, f"Quick Export Finished")
        return{"FINISHED"}

class ExportHeightmap(bpy.types.Operator):
    bl_idname = "qexport.exportheightmap"
    bl_label = "Heightmap"
    bl_description = "Exports your level's Heightmap"

    def execute(self, context):
        startTime = time.time()
        bpy.types.Scene.heightmapprogress = 0.0
        updateprogress(0.0)

        mapsize = int(bpy.context.scene.mapsize)
        mapheight = bpy.context.scene.mapheight

        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        absoluteModDir = os.path.abspath(bpy.path.abspath(bpy.context.scene.modDir)) # Gets mod folder directory
        worldId = bpy.context.scene.worldId # Gets the world ID to be edited

        directoryTexconv = os.path.abspath(bpy.path.abspath(preferences.directoryTexconv)) # Gets HedgeSet path from preferences
        directoryHedgearcpack = os.path.abspath(bpy.path.abspath(preferences.directoryHedgearcpack)) # Gets HedgeArcPack path from preferences
        if not "[FLC] Heightmap" in bpy.data.objects:
            return {'FINISHED'}
        if preferences.directoryTexconv == "" or preferences.directoryHedgearcpack == "": # Gives an error if a program is missing
            def missingProgramError(self, context):
                missingPrograms = [] # List of missing programs
                if preferences.directoryTexconv == "":
                    missingPrograms.append("texconv.exe")
                if preferences.directoryHedgearcpack == "":
                    missingPrograms.append("HedgeArcPack.exe")
                self.layout.label(text=f"The filepath(s) for: {', '.join(missingPrograms)} are not set. \nPlease set the path(s) in Settings.") # Tells the user about the missing prorgrams

            bpy.context.window_manager.popup_menu(missingProgramError, title = "Program missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        if bpy.context.scene.modDir == "": # Gives an error if no mod directory is sent
            def missingProgramError(self, context):
                self.layout.label(text="No Mod directory is set") # Sets the popup label

            bpy.context.window_manager.popup_menu(missingProgramError, title = "Mod missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        unpack([f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_height.pac"], directoryHedgearcpack)

        bpy.data.objects["[FLC] Heightmap"].data.materials[0] = bpy.data.materials["[FLC] Heightmap-Render"]

        tempfolder = f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_height\\levelcreator-temp\\"
        if os.path.exists(tempfolder):
            shutil.rmtree(tempfolder)
        os.mkdir(tempfolder)

        cameraObjs = []
        for row in range(int(round(mapsize/1024))):
            for col in range(int(round(mapsize/1024))):
                cameraObj = bpy.data.objects.new(f'[FLC] Cam-{(row * (int(round(mapsize/1024)))) + col}', bpy.data.cameras.new(name=f'[FLC] Cam-{((row * (int(round(mapsize/1024)))) + col)}'))
                bpy.context.scene.collection.objects.link(cameraObj)
                cameraObj.location = (-((mapsize/2) - 512) + (col * 1024), ((mapsize/2) - 512) - (row * 1024), mapheight + 10)
                cameraObj.data.type = 'ORTHO' # Sets camera to orthographic
                cameraObj.data.ortho_scale = 1024 # Sets the camera to capture the whole heightmap
                cameraObj.data.clip_end = mapheight + 11
                cameraObjs.append(cameraObj)

        objsshown = []
        for o in bpy.data.objects:
            if o.hide_render == False and o.name != "[FLC] Heightmap":
                objsshown.append(o.name)
                o.hide_render = True

        activecam = bpy.context.scene.camera
        bpy.context.scene.camera = bpy.data.objects["[FLC] Cam-0"]
        color_depth = bpy.context.scene.render.image_settings.color_depth
        bpy.context.scene.render.image_settings.color_depth = '16'
        resolution_x = bpy.context.scene.render.resolution_x
        bpy.context.scene.render.resolution_x = 1024
        resolution_y = bpy.context.scene.render.resolution_y
        bpy.context.scene.render.resolution_y = 1024
        view_transform = bpy.context.scene.view_settings.view_transform
        bpy.context.scene.view_settings.view_transform = 'Raw'
        taa_render_samples = bpy.context.scene.eevee.taa_render_samples
        bpy.context.scene.eevee.taa_render_samples = 1
        engine = bpy.context.scene.render.engine
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        worldcol = bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)

        use_multiview = bpy.context.scene.render.use_multiview
        bpy.context.scene.render.use_multiview = True
        views_format = bpy.context.scene.render.views_format
        bpy.context.scene.render.views_format = 'MULTIVIEW'
        leftuse = bpy.context.scene.render.views["left"].use
        bpy.context.scene.render.views["left"].use = False
        rightuse = bpy.context.scene.render.views["left"].use
        bpy.context.scene.render.views["right"].use = False

        for i in range((int(round(mapsize/1024)))**2):
            view = bpy.context.scene.render.views.new(f"[FLC] View-{i}")
            view.camera_suffix = f"-{i}"

        print(f"\n\nRENDER SETUP COMPLETE ----------\nTIME ELAPSED: {time.time() - startTime}")
        previousTime = time.time()

        bpy.ops.render.render(write_still=False)
        updateprogress(0.87)

        print(f"\n\nRENDER COMPLETE ----------\nTIME ELAPSED: {time.time() - previousTime}")
        previousTime = time.time()

        image = bpy.data.images["Render Result"] # Gets the Rendered image
        image.file_format = 'PNG' # Sets the file format
        try:
            image.save_render(filepath=f"{tempfolder}Heightmap.png") # Outputs the image straight to the temporary folder
        except Exception as e:
            print(f"Possible Error: {e}")

        bpy.data.objects["[FLC] Heightmap"].data.materials[0] = bpy.data.materials["[FLC] Heightmap-Preview"]

        for c in cameraObjs:
            bpy.data.cameras.remove(bpy.data.cameras[c.data.name])

        for o in objsshown:
            try:
                bpy.data.objects[o].hide_render = False
            except KeyError:
                pass

        bpy.context.scene.camera = activecam
        bpy.context.scene.render.image_settings.color_depth = color_depth
        bpy.context.scene.render.resolution_x = resolution_x
        bpy.context.scene.render.resolution_y = resolution_y
        bpy.context.scene.view_settings.view_transform = view_transform
        bpy.context.scene.eevee.taa_render_samples = taa_render_samples
        bpy.context.scene.render.engine = engine
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = worldcol

        bpy.context.scene.render.use_multiview = use_multiview
        bpy.context.scene.render.views_format = views_format
        bpy.context.scene.render.views["left"].use = leftuse
        bpy.context.scene.render.views["right"].use = rightuse

        for i in range((int(round(mapsize/1024)))**2):
            view = bpy.context.scene.render.views.remove(bpy.context.scene.render.views[f"[FLC] View-{i}"])

        for f in os.listdir(tempfolder):
            renamed = f"{worldId}_heightmap_{int(f.split('-')[1][:-4]):03}"
            os.chdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(directoryTexconv)))}") # Goes to the directory
            print(os.popen(f'texconv -f R16_UNORM -xlum -y "{tempfolder}\\{f}" -o "{tempfolder[:-1]}"').read()) # Converts the image via command line
            os.rename(f"{tempfolder}\\{f[:-4]}.dds", f"{renamed}.dds")
            shutil.move(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(directoryTexconv)))}\\{renamed}.dds", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_height\\{renamed}.dds") # Copies the DDSs to the blend file's folder

        shutil.rmtree(tempfolder)

        updateprogress(0.13)

        if bpy.context.scene.noPack == False:
            pack([f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_height"], directoryHedgearcpack)

        print(f"\n\nCONVERTING COMPLETE ----------\nTIME ELAPSED: {time.time() - previousTime}")

        bpy.types.Scene.heightmapprogress = 1.0
        bpy.types.Scene.heightmapprogresstext = "DONE"

        print(f"\n\nHEIGHTMAP EXPORT COMPLETE ----------\nTIME ELAPSED: {time.time() - startTime}")

        return {'FINISHED'}

class ExportSplatmap(bpy.types.Operator):
    bl_idname = "qexport.exportsplatmap"
    bl_label = "Splatmap"
    bl_description = "Exports your Heightmap's Splatmap, Area and Scale maps"

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        absoluteModDir = os.path.abspath(bpy.path.abspath(bpy.context.scene.modDir)) # Gets mod folder directory
        worldId = bpy.context.scene.worldId # Gets the world ID to be edited

        directoryTexconv = os.path.abspath(bpy.path.abspath(preferences.directoryTexconv)) # Gets HedgeSet path from preferences
        directoryHedgearcpack = os.path.abspath(bpy.path.abspath(preferences.directoryHedgearcpack)) # Gets HedgeArcPack path from preferences

        if not "[FLC] Splatmap" in bpy.data.images:
            def splatmapError(self, context):
                self.layout.label(text="No Splatmap found!") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(splatmapError, title = "Splatmap Failed", icon = "ERROR") # Makes the popup appear
            return {'FINISHED'}
        if preferences.directoryTexconv == "" or preferences.directoryHedgearcpack == "": # Gives an error if a program is missing
            def missingProgramError(self, context):
                missingPrograms = [] # List of missing programs
                if preferences.directoryTexconv == "":
                    missingPrograms.append("texconv.exe")
                if preferences.directoryHedgearcpack == "":
                    missingPrograms.append("HedgeArcPack.exe")
                self.layout.label(text=f"The filepath(s) for: {', '.join(missingPrograms)} are not set. \nPlease set the path(s) in Settings.") # Tells the user about the missing prorgrams

            bpy.context.window_manager.popup_menu(missingProgramError, title = "Program missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation
        if bpy.context.scene.modDir == "": # Gives an error if no mod directory is sent
            def missingProgramError(self, context):
                self.layout.label(text="No Mod directory is set") # Sets the popup label

            bpy.context.window_manager.popup_menu(missingProgramError, title = "Mod missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        unpack([f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_cmn.pac"], directoryHedgearcpack)

        tempfolder = f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_cmn\\levelcreator-temp\\"
        if os.path.exists(tempfolder):
            shutil.rmtree(tempfolder)
        os.mkdir(tempfolder)

        image = bpy.data.images["[FLC] Splatmap"]
        image.filepath_raw = f"{tempfolder}{worldId}_splatmap.png"
        image.file_format = 'PNG'
        image.save()

        image = bpy.data.images["[FLC] Scale"]
        image.filepath_raw = f"{tempfolder}{worldId}_scale.png"
        image.file_format = 'PNG'
        image.save()

        image = bpy.data.images["[FLC] Area"]
        image.filepath_raw = f"{tempfolder}{worldId}_area.png"
        image.file_format = 'PNG'
        image.save()

        os.chdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(directoryTexconv)))}") # Goes to the directory
        os.popen(f'texconv -f R8_UNORM -xlum -y "{tempfolder}{worldId}_splatmap.png" -o "{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_cmn"').read() # Converts the image via command line
        os.remove(f"{tempfolder}{worldId}_splatmap.png")
        os.popen(f'texconv -f R8_UNORM -xlum -y "{tempfolder}{worldId}_scale.png" -o "{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_cmn"').read() # Converts the image via command line
        os.remove(f"{tempfolder}{worldId}_scale.png")
        os.popen(f'texconv -f R8_UNORM -xlum -y "{tempfolder}{worldId}_area.png" -o "{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_cmn"').read() # Converts the image via command line
        os.remove(f"{tempfolder}{worldId}_area.png")

        if bpy.context.scene.noPack == False:
            pack([f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_height"], directoryHedgearcpack)

        shutil.rmtree(tempfolder)

        return {'FINISHED'}

class ExportDensity(bpy.types.Operator):
    bl_idname = "qexport.exportdensity"
    bl_label = "Density"
    bl_description = "Exports your level's density objects"

    def execute(self, context):
        return {'FINISHED'}

class RepackAll(bpy.types.Operator):
    bl_idname = "qexport.repackall"
    bl_label = "Heightmap"
    bl_description = "Repacks gedit, trr_s00, misc, trr_cmn, trr_density, trr_height and trr_heightfield"

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets the absolute path for HedgeArcPack
        directoryHedgearcpack = os.path.abspath(bpy.path.abspath(preferences.directoryHedgearcpack))
        print(directoryHedgearcpack)

        if preferences.directoryHedgearcpack == "": # Gives an error if hedgearcpack is missing
            def missingProgramError(self, context):
                self.layout.label(text="The filepath for HedgeArcPack.exe is not set. \nPlease set it in Settings.") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(missingProgramError, title = "HedgeArcPack missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'}

        absoluteModDir = os.path.abspath(bpy.path.abspath(bpy.context.scene.modDir)) # Gets mod folder directory
        worldId = bpy.context.scene.worldId # Gets the world ID to be edited

        if bpy.context.scene.modDir == "": # If there is no mod directory set
            def noModError(self, context):
                self.layout.label(text="No mod folder is selected") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(noModError, title = "Mod Not Found", icon = "QUESTION") # Makes the popup appear
            return{'FINISHED'}

        if not os.path.exists(f"{absoluteModDir}\\mod.ini"): # If there is no mod.ini, it must be an invalid mod folder
            def iniError(self, context):
                self.layout.label(text="mod.ini not found, check that you have selected a valid mod folder") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(iniError, title = "mod.ini Not Found", icon = "QUESTION") # Makes the popup appear
            return{'FINISHED'}

        filesToPack = [ # List of files to be packed
            f"{absoluteModDir}\\raw\\gedit\\{worldId}_gedit",
            f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc",
            f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00",
            f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_cmn",
            f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_density",
            f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_height",
            f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_heightfield"
        ]

        filesToPack, directoryHedgearcpack

        return{"FINISHED"}

class Settings(bpy.types.Operator):
    bl_idname = "qexport.settings"
    bl_label = "Settings"
    bl_description = "Addon Settings"

    def execute(self, context):
        bpy.ops.screen.userpref_show()
        bpy.context.preferences.active_section = 'ADDONS'

        bpy.data.window_managers["WinMan"].addon_search = "Frontiers Level Creator"

        bpy.ops.preferences.addon_expand(module = __name__.split(".")[0])
        bpy.ops.preferences.addon_show(module = __name__.split(".")[0])

        return{"FINISHED"}


class QexportSettings(bpy.types.PropertyGroup): # Other settings
    bpy.types.Scene.trrCollection = bpy.props.PointerProperty(
        name="Terrain Collection",
        type=bpy.types.Collection,
        description="Collection that your terrain objects are in. \nIf this is empty, all terrain will be exported, regardless of collections.\nTo make a collection only export collision, add '_NoVis'\nTo make a collection not export collision, add '_NoCol'"
    )
    bpy.types.Scene.objCollection = bpy.props.PointerProperty(
        name="Objects Collection",
        type=bpy.types.Collection,
        description="Collection that your objects are in. \n\nThe type of paths exported will depend on the name of the path object.\n2D section path: 'SVPath'\nObject path: 'ObjPath'\nPath properties (can be applied to any type of path)\nDisable Smoothing: Add '_str'\nDisable Rotation: Add '_NoRot'"
    )
    bpy.types.Scene.modDir = bpy.props.StringProperty(
        name="Mod Directory",
        subtype='DIR_PATH',
        default="",
        description="Path to your mod folder"
    )
    bpy.types.Scene.worldId = bpy.props.EnumProperty(
        name="World ID",
        items=[
            ("w1f01", "w1f01 (Fishing)", ""),
            ("w1h01", "w1h01 (Hacking)", ""),
            ("w1r03", "w1r03 (Kronos)", ""),
            ("w1r04", "w1r04 (Ouranos)", ""),
            ("w1r05", "w1r05 (Rhea)", ""),
            ("w1r06", "w1r06 (Final Horizon)", ""),
            ("w2r01", "w2r01 (Ares)", ""),
            ("w3r01", "w3r01 (Chaos)", ""),
            ("w5r01", "w5r01 (The END)", ""),
            ("w5t01", "w5t01 (Training Room)", ""),
            ("w5t02", "w5t02 (Master Trials)", ""),
            ("w6d01", "w6d01 (1-1)", ""),
            ("w8d01", "w8d01 (1-2)", ""),
            ("w9d04", "w9d04 (1-3)", ""),
            ("w6d02", "w6d02 (1-4)", ""),
            ("w7d04", "w7d04 (1-5)", ""),
            ("w6d06", "w6d06 (1-6)", ""),
            ("w9d06", "w9d06 (1-7)", ""),
            ("w6d05", "w6d05 (2-1)", ""),
            ("w8d03", "w8d03 (2-2)", ""),
            ("w7d02", "w7d02 (2-3)", ""),
            ("w7d06", "w7d06 (2-4)", ""),
            ("w8d04", "w8d04 (2-5)", ""),
            ("w6d03", "w6d03 (2-6)", ""),
            ("w8d05", "w8d05 (2-7)", ""),
            ("w6d04", "w6d04 (3-1)", ""),
            ("w6d08", "w6d08 (3-2)", ""),
            ("w8d02", "w8d02 (3-3)", ""),
            ("w6d09", "w6d09 (3-4)", ""),
            ("w6d07", "w6d07 (3-5)", ""),
            ("w8d06", "w8d06 (3-6)", ""),
            ("w7d03", "w7d03 (3-7)", ""),
            ("w7d08", "w7d08 (4-1)", ""),
            ("w9d02", "w9d02 (4-2)", ""),
            ("w7d01", "w7d01 (4-3)", ""),
            ("w9d03", "w9d03 (4-4)", ""),
            ("w6d10", "w6d10 (4-5)", ""),
            ("w7d07", "w7d07 (4-6)", ""),
            ("w9d05", "w9d05 (4-7)", ""),
            ("w7d05", "w7d05 (4-8)", ""),
            ("w9d07", "w9d07 (4-9)", "")
        ],
        default="w6d01",
        description="The world you wish to export to"
    )

    # ADVANCED
    bpy.types.Scene.noPack = bpy.props.BoolProperty(    # Access through "bpy.context.scene.noPack"
        name="Don't automatically repack",
        default=False,
        description="Disables automatic repacking of files when using Quick Export (Except for the Repack All button obviously)"
    )
    bpy.types.Scene.eoTerrain = bpy.props.BoolProperty( # Access through "bpy.context.scene.eoTerrain"
        name="Don't Clear Terrain",
        default=False,
        description="Makes the program not clear the terrain folders before exporting"
    )
    bpy.types.Scene.eoObjects = bpy.props.BoolProperty( # Access through "bpy.context.scene.eoObjects"
        name="Don't Clear Objects",
        default=False,
        description="Makes the program not clear the object folders before exporting"
    )
    bpy.types.Scene.keepMat = bpy.props.BoolProperty(   # Access through "bpy.context.scene.keepMat"
        name="Keep .Materials",
        default=False,
        description="Don't edit pre-existing materials"
    )
    bpy.types.Scene.keepTex = bpy.props.BoolProperty(   # Access through "bpy.context.scene.keepTex"
        name="Keep Textures",
        default=False,
        description="Don't edit pre-existing textures"
    )
    bpy.types.Scene.keepHgt = bpy.props.BoolProperty(   # Access through "bpy.context.scene.keepHgt"
        name="Keep Heightmap",
        default=False,
        description="Don't edit the pre-existing heightmap"
    )
    bpy.types.Scene.keepPcm = bpy.props.BoolProperty(   # Access through "bpy.context.scene.keepPcm"
        name="Keep .pcmodels",
        default=False,
        description="Don't edit pre-existing pcmodels"
    )
    bpy.types.Scene.keepPcl = bpy.props.BoolProperty(   # Access through "bpy.context.scene.keepPcl"
        name="Keep .pccols",
        default=False,
        description="Don't edit pre-existing pccols"
    )
    bpy.types.Scene.keepDen = bpy.props.BoolProperty(   # Access through "bpy.context.scene.keepDen"
        name="Keep Density",
        default=False,
        description="Don't edit pre-existing density"
    )
    bpy.types.Scene.noVis = bpy.props.BoolProperty(   # Access through "bpy.context.scene.noVis"
        name="No Visual Terrain",
        default=False,
        description="Doesn't export .terrain-model"
    )
    bpy.types.Scene.noCol = bpy.props.BoolProperty(   # Access through "bpy.context.scene.noCol"
        name="No Collision",
        default=False,
        description="Doesn't export .btmesh"
    )