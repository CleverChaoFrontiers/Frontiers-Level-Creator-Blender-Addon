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
import copy
from .Frontiers_rail_script import Find_node_rot

def pack(files, directoryHedgearcpack):
    for f in range(len(files)): # For every file that needs to be packed
        if os.path.exists(files[f]): # Check if file exists
            os.chdir(os.path.dirname(directoryHedgearcpack)) # Go to the directory that hedgearcpack is in
            if bpy.context.scene.hedgegameChoice == "shadow":
                print(os.popen(f'hedgearcpack "{files[f]}" -T=sxsg').read()) # Run hedgearcpack to pack the file for shadow
            else:
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
            if not files[f].split(".")[-1].lower() in keepFiles: # If the file extension is not in the list of extensions to be kept
                os.remove(f"{filepath}\\{files[f]}") # Removes file

def ID_generator(self):
    Id = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    hexValues = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
    for i in range(32):
        Id = Id.replace("X", hexValues[random.randrange(len(hexValues))], 1) # generates a random ID
    return Id

def updateprogress(advance, name, milestone):
    if (4, 0, 0) < bpy.app.version:
        bpy.types.Scene.exportprogress =  bpy.types.Scene.exportprogress + advance
        bpy.types.Scene.exportprogresstext = f"{name} ({round(bpy.types.Scene.exportprogress * 100)}%)"
        if bpy.types.Scene.exportprogress >= milestone:
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            milestone = (math.floor(bpy.types.Scene.exportprogress * 10) / 10) + 0.1
        return milestone

#def Find_node_rot(curve_obj,index,path_dir):#New fixed rotation whooo! Based heavily on the density script
#    beveled_curve = False
#    if bpy.context.mode != 'OBJECT':
#        bpy.ops.object.mode_set(mode='OBJECT')
#    if curve_obj.data.bevel_mode != 'ROUND':
#        original_bevel_mode = curve_obj.data.bevel_mode
#        original_bevel_size = curve_obj.data.bevel_depth
#        curve_obj.data.bevel_mode = 'ROUND'
#        if curve_obj.data.bevel_depth != 0:
#            curve_obj.data.bevel_depth = 0
#        beveled_curve = True
#    object_name = "Frontiers_rotation_plane"
#    nodetree_name = "FrontiersRailRotation"
#    filepath = os.path.join(path_dir, r"Other\\frontiers_rotation_solution.blend")
#    # Check if the file exists and is a valid blend file
#    if nodetree_name not in bpy.data.node_groups:
#        try:
#            with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to): #try loading the nodetree. Cancel script if failed
#                data_to.node_groups = [nodetree_name]   
#        except Exception as error:
#            print(f"Failed to load {filepath}: {error}")
#            return
#    bpy.ops.mesh.primitive_plane_add(size = 1.0)
#    appended_rotobject = bpy.context.view_layer.objects.active
#        
#    geo_node_mod = appended_rotobject.modifiers.new(name="Frontiersrotation", type='NODES')
#    geo_node_mod.node_group = bpy.data.node_groups[nodetree_name]
#    if appended_rotobject != None:
#        appended_rotobject.modifiers["Frontiersrotation"]["Input_2"] = index
#        appended_rotobject.modifiers["Frontiersrotation"]["Input_3"] = curve_obj
#    else:
#        return 0,False
#    bpy.ops.object.select_all(action='DESELECT')
#    appended_rotobject.select_set(True)
#    bpy.context.view_layer.objects.active = appended_rotobject
#    bpy.ops.object.modifier_apply(modifier="Frontiersrotation",single_user=True)
#    bpy.ops.object.mode_set(mode='EDIT') # Switches to Edit Mode
#    bm = bmesh.from_edit_mesh(appended_rotobject.data) # Gets the Blender Mesh from the rotobject
#    for theface in bm.faces:
#        face = theface
#    appended_rotobject.rotation_mode = 'QUATERNION'
#    objectRotation = face.normal.to_track_quat('Z', 'Y')
#    bpy.ops.object.mode_set(mode='OBJECT')
#    bpy.ops.object.select_all(action='DESELECT')
#    curve_obj.select_set(True)
#    bpy.context.view_layer.objects.active = curve_obj
#    if beveled_curve:
#        curve_obj.data.bevel_depth = original_bevel_size
#        curve_obj.data.bevel_mode = original_bevel_mode
#    bpy.data.objects.remove(appended_rotobject, do_unlink=True)
#    return objectRotation,True

def Instantiate(pcmodelname,pccolname,object):
    if pcmodelname != None:
        pcmodel = [pcmodelname.split(".")[0], (object.location.x, object.location.y, object.location.z), (object.rotation_euler.x, object.rotation_euler.y, object.rotation_euler.z), (object.scale.x, object.scale.y,object.scale.z)]
    else:
        pcmodel = None
    if pccolname != None:
        pccol = [pccolname.split(".")[0], (object.location.x, object.location.y, object.location.z), (object.rotation_euler.x, object.rotation_euler.y, object.rotation_euler.z),(object.scale.x, object.scale.y,object.scale.z)]
    else:
        pccol = None
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

    if (4, 0, 0) < bpy.app.version:
        bpy.types.Scene.exportprogress = 0.0 # Resets the progress bar
        bpy.types.Scene.exportprogresstext = "- - -"

    def execute(self, context):
        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.exportprogress = 0.0
        milestone = 0
        updateprogress(0.0, "Terrain", milestone)

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

        if not bpy.data.is_saved:
            def saveError(self, context):
                self.layout.label(text="The .blend file is not saved!") # Sets the popup label
            bpy.context.window_manager.popup_menu(saveError, title = "File not saved", icon = "DISK_DRIVE") # Makes the popup appear
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
        
        unpack([f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00.pac", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc.pac"], directoryHedgearcpack)

        if bpy.context.view_layer.objects.active == None:
            for o in bpy.data.objects:
                bpy.context.view_layer.objects.active = o
                break
        try:
            bpy.ops.object.mode_set(mode = 'OBJECT')
        except RuntimeError:
            pass

        oldmats = []
        newmats = []
        for m in bpy.data.materials:
            if "." in m.name:
                if m.name[:m.name.find(".")] in bpy.data.materials:
                    oldmats.append(m)
                    newmats.append(bpy.data.materials[m.name[:m.name.find(".")]])
        
        if len(oldmats) != 0:
            for o in bpy.data.objects:
                if o.type == "MESH":
                    for ms in o.material_slots:
                        if ms.material in oldmats:
                            ms.material = newmats[oldmats.index(ms.material)]
        
        for m in oldmats:
            bpy.data.materials.remove(m)
                    

        collection = bpy.context.scene.trrCollection # Gets the chosen collection
        fbxModels = [] # Initialises the list of paths to FBX models
        fbxCollectionNames = []

        if os.path.exists(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp"):
            shutil.rmtree(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp")

        os.mkdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp")
        if collection == None:
            collection = bpy.context.scene.collection

        print(f"Exporting from Collection \"{collection.name}\".")
        
        estimated = ((len(collection.children) + 1) * 6) + (len(bpy.data.images) * 0.4)
        print(f"Est: {estimated}")

        pcmodelInstances = [] # Secret feature mainly for placing multiple animated .models (I needed it for a project)
        pccolInstances = []
        for c in collection.children:
            bpy.ops.object.select_all(action='DESELECT') # Deselects all
            for o in c.all_objects:
                original_rotate_mode = o.rotation_mode
                #if o.name[:6].upper() == "_INST_":
                #    if original_rotate_mode != "XZY":
                #        o.rotation_mode = "QUATERNION"
                #        o.rotation_mode = "XZY"
                #
                #    pcmodelInstances.append([o.name[6:].split(".")[0], (o.location.x, o.location.y, o.location.z), (o.rotation_euler.x, o.rotation_euler.y, o.rotation_euler.z), (o.scale.x, o.scale.y,o.scale.z)])
                #    if original_rotate_mode != "XZY":
                #        o.rotation_mode = "QUATERNION"
                #        o.rotation_mode = original_rotate_mode
                #elif o.name[:9].upper() == "_INSTCOL_":
                #    if original_rotate_mode != "XZY":
                #        o.rotation_mode = "QUATERNION"
                #        o.rotation_mode = "XZY"
                #
                #    pccolInstances.append([o.name[9:].split(".")[0]+"_col", (o.location.x, o.location.y, o.location.z), (o.rotation_euler.x, o.rotation_euler.y, o.rotation_euler.z), (o.scale.x, o.scale.y,o.scale.z)])
                #    if original_rotate_mode != "XZY":
                #        o.rotation_mode = "QUATERNION"
                #        o.rotation_mode = original_rotate_mode
                #elif "INST(" in o.name:
                #    if original_rotate_mode != "XZY":
                #        o.rotation_mode = "QUATERNION"
                #        o.rotation_mode = "XZY"
                #    splitInst = o.name.split("(")
                #    
                #    inst_names = splitInst[1].replace(")","").split(",")
                #    
                #    inst_names.append("")
                #    pcmodelInst, pccolInst = Instantiate(inst_names[0],inst_names[1],o)
                #    pcmodelInstances.append(pcmodelInst)
                #    if pccolInst != "":
                #        pccolInstances.append(pccolInst)
                #    if original_rotate_mode != "XZY":
                #        o.rotation_mode = "QUATERNION"
                #        o.rotation_mode = original_rotate_mode
                print(f"o.name.lower() {o.name.lower()}")
                if o.name.lower().startswith("inst("):
                    instsettings = o.name[5:o.name.find(")")].replace(", ", ",")
                    instsettings = instsettings.split(",")
                    instname = instsettings[0].replace('"', '')
                    
                    if original_rotate_mode != "XZY":
                        o.rotation_mode = "QUATERNION"
                        o.rotation_mode = "XZY"

                    if len(instsettings) > 1:
                        if instsettings[1].lower() == "visual":
                            pcmodelInst, pccolInst = Instantiate(instname,None,o)
                        elif instsettings[1].lower() == "collision":
                            pcmodelInst, pccolInst = Instantiate(None,instname,o)
                    else:
                        pcmodelInst, pccolInst = Instantiate(instname,instname,o)

                    if pcmodelInst != None:
                        pcmodelInstances.append(pcmodelInst)
                    if pccolInst != None:
                        pccolInstances.append(pccolInst)
                    
                    if original_rotate_mode != "XZY":
                        o.rotation_mode = "QUATERNION"
                        o.rotation_mode = original_rotate_mode
                else:
                    if not "FrontiersAsset" in o:
                        o.select_set(True)
            exportname = c.name.replace(' ', '_')
            for rm in ["InstOnly_", "instonly_", "INSTONLY_", "_NoCol", "_NoVis", "_nocol", "_novis", "_NOCOL", "_NOVIS"]:
                exportname = exportname.replace(rm, "")
            bpy.ops.export_scene.fbx(filepath=f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{exportname}.fbx", use_selection = True, apply_scale_options = 'FBX_SCALE_UNITS', use_visible = True, add_leaf_bones=False,mesh_smooth_type='FACE')
            fbxModels.append(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{exportname}")
            fbxCollectionNames.append(c.name)
        

            milestone = updateprogress(4 / estimated, "Terrain", milestone)

        bpy.ops.object.select_all(action='DESELECT') # Deselects all
        for obj in collection.objects:
            if not "FrontiersAsset" in obj:
                obj.select_set(True)

        exportname = collection.name.replace(' ', '_')
        for rm in ["InstOnly_", "instonly_", "INSTONLY_", "_NoCol", "_NoVis", "_nocol", "_novis", "_NOCOL", "_NOVIS"]:
            exportname = exportname.replace(rm, "")
        bpy.ops.export_scene.fbx(filepath=f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{exportname}.fbx", use_selection = True, apply_scale_options = 'FBX_SCALE_UNITS', use_visible = True, add_leaf_bones=False,mesh_smooth_type='FACE')
        fbxModels.append(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{exportname}")
        fbxCollectionNames.append(collection.name)

        keepFiles = ["level", "txt", "rfl"]
        if bpy.context.scene.exptrr in ["add", "write", "keep"]:
            keepFiles.append("terrain-model")
        if bpy.context.scene.expcol in ["add", "write", "keep"]:
            keepFiles.append("btmesh")
        if bpy.context.scene.expmat in ["add", "write", "keep"]:
            keepFiles.append("material")
        if bpy.context.scene.expdds in ["add", "write", "keep"]:
            keepFiles.append("dds")
        if bpy.context.scene.expuva in ["add", "write", "keep"]:
            keepFiles.append("uv-anim")
        if bpy.context.scene.exppcm in ["add", "write", "keep"]:
            keepFiles.append("pcmodel")
        if bpy.context.scene.exppcl in ["add", "write", "keep"]:
            keepFiles.append("pccol")
        if bpy.context.scene.expmsc in ["add", "write", "keep"]:
            keepFiles.extend(["pt-anim", "path", "pxd", "pcrt", "light", "model", "fxcol", "vat"])
        clearFolder(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00", keepFiles)
        clearFolder(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc", keepFiles)

        os.chdir(os.path.dirname(directoryModelconverter))
        pcmodel = []
        instanced_pccol = []
        for f in range(len(fbxModels)):
            fbxName = fbxCollectionNames[f]
            fbxName = fbxName.replace("instonly", "").replace("INSTONLY_", "").replace("InstOnly_", "")
            fbxName = fbxName.replace("_nocol", "").replace("_NOCOL", "").replace("_NoCol", "")
            print(f"Terrain - {fbxName}")
            if not "_novis" in fbxCollectionNames[f].lower():
                if bpy.context.scene.exptrr in ["clear", "write"]:
                    os.popen(f'ModelConverter --frontiers "{fbxModels[f]}.fbx" "{fbxModels[f]}.terrain-model"').read()
                    shutil.move(f"{fbxModels[f]}.terrain-model", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\{fbxName}.terrain-model")

                    if not "instonly_" in fbxCollectionNames[f].lower():
                        pcmodelObj = {"UnknownUInt32_1": 1, "InstanceName": "", "AssetName": "", "Position": {"X": 0, "Y": 0, "Z": 0}, "Rotation": {"X": 0, "Y": 0, "Z": 0}, "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}}
                        pcmodelObj["InstanceName"] = fbxModels[f].split('\\')[-1] + "_model"
                        pcmodelObj["AssetName"] = fbxModels[f].split('\\')[-1]
                        pcmodel.append(pcmodelObj)
                elif bpy.context.scene.exptrr == "add":
                    if not os.path.exists(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\{fbxName}.terrain-model"):
                        os.popen(f'ModelConverter --frontiers "{fbxModels[f]}.fbx" "{fbxModels[f]}.terrain-model"').read()
                        shutil.move(f"{fbxModels[f]}.terrain-model", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\{fbxName}.terrain-model")

                        if not "instonly_" in fbxCollectionNames[f].lower():
                            pcmodelObj = {"UnknownUInt32_1": 1, "InstanceName": "", "AssetName": "", "Position": {"X": 0, "Y": 0, "Z": 0}, "Rotation": {"X": 0, "Y": 0, "Z": 0}, "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}}
                            pcmodelObj["InstanceName"] = fbxModels[f].split('\\')[-1] + "_model"
                            pcmodelObj["AssetName"] = fbxModels[f].split('\\')[-1]
                            pcmodel.append(pcmodelObj)

        if bpy.context.scene.exppcm in ["clear", "write", "add"]:
            for i in range(len(pcmodelInstances)): # terrain instancing

                instName = pcmodelInstances[i][0]
                instName = instName.replace("instonly", "").replace("INSTONLY_", "").replace("InstOnly_", "")
                instName = instName.replace("_nocol", "").replace("_NOCOL", "").replace("_NoCol", "")

                pcmodelObj = {"UnknownUInt32_1": 1, "InstanceName": "", "AssetName": "", "Position": {"X": 0, "Y": 0, "Z": 0}, "Rotation": {"X": 0, "Y": 0, "Z": 0}, "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}}
                pcmodelObj["InstanceName"] = f"{instName}_model_{i}"
                pcmodelObj["AssetName"] = instName

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
        
        if bpy.context.scene.exppcl in ["clear", "write", "add"]:
            for i in range(len(pccolInstances)): #Collision instancing
                if "instonly_" in fbxName.lower():
                    instName = pccolInstances[i][0]
                    instName = instName.replace("instonly", "").replace("INSTONLY_", "").replace("InstOnly_", "")
                    instName = instName.replace("_novis", "").replace("_NOVIS", "").replace("_NoVis", "")

                    pccolObj = {"UnknownUInt32_1": 1, "InstanceName": "", "AssetName": "", "Position": {"X": 0, "Y": 0, "Z": 0}, "Rotation": {"X": 0, "Y": 0, "Z": 0}, "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}}
                    pccolObj["InstanceName"] = f"{instName}_model_{i}"
                    pccolObj["AssetName"] = instName
                else:
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

        if bpy.context.scene.exppcm in ["clear", "write", "add"]:
            if not (bpy.context.scene.exppcm == "add" and os.path.exists(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\terrain.pcmodel")):
                print("Don't keep pcmodel")
                pcmodelFile = open(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\terrain.hedgehog.pointcloud.json", "x")
                pcmodelFile.write(json.dumps(pcmodel, indent=2))
                pcmodelFile.close()

                os.chdir(os.path.dirname(directoryKnuxtools))
                os.popen(f'knuxtools "{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\terrain.hedgehog.pointcloud.json" -e=pcmodel').read()
                shutil.move(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\terrain.pcmodel", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\terrain.pcmodel")
                
        if bpy.context.scene.exppcl in ["clear", "write", "add"] and instanced_pccol != []:
            if not (bpy.context.scene.exppcl == "add" and os.path.exists(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc\\instance_collision.pccol")):
                print("add collision instance")
                pccolFile = open(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\instance_collision.hedgehog.pointcloud.json", "x")
                pccolFile.write(json.dumps(instanced_pccol, indent=2))
                pccolFile.close()

                os.chdir(os.path.dirname(directoryKnuxtools))
                os.popen(f'knuxtools "{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\instance_collision.hedgehog.pointcloud.json" -e=pccol').read()
                shutil.move(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\instance_collision.pccol", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc\\instance_collision.pccol")

        if bpy.context.scene.expmat in ["clear", "write"]:
            tempFolderContents = os.listdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\")
            for f in range(len(tempFolderContents)): # For every file in the temp folder
                if tempFolderContents[f].split(".")[-1].lower() == "material": # If the file is a .material
                    shutil.move(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{tempFolderContents[f]}", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\{tempFolderContents[f]}")
        elif bpy.context.scene.expmat == "add":
            tempFolderContents = os.listdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\")
            for f in range(len(tempFolderContents)): # For every file in the temp folder
                if tempFolderContents[f].split(".")[-1].lower() == "material": # If the file is a .material
                    if not os.path.exists(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\{tempFolderContents[f]}"):
                        shutil.move(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{tempFolderContents[f]}", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\{tempFolderContents[f]}")
        
        os.chdir(os.path.dirname(directoryBtmesh))
        for f in range(len(fbxModels)):
            fbxName = fbxCollectionNames[f]
            fbxFileName = fbxModels[f].split("\\")[-1]
            print(f"Collision - {fbxName}")
            os.popen(f'btmesh "{fbxModels[f]}.fbx"').read()

            if bpy.context.scene.expcol in ["clear", "write"] and not "_nocol" in fbxName.lower():
                shutil.move(f"{fbxModels[f]}_col.btmesh", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc\\{fbxFileName}_col.btmesh")
                if bpy.context.scene.exppcl in ["clear", "write"] and not "instonly_" in fbxName.lower():
                    shutil.move(f"{fbxModels[f]}_col.pccol", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc\\{fbxFileName}_col.pccol")

            elif bpy.context.scene.expcol == "add" and not "_nocol" in fbxName.lower():
                if not os.path.exists(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc\\{fbxName}_col.btmesh"):
                    shutil.move(f"{fbxModels[f]}_col.btmesh", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc\\{fbxFileName}_col.btmesh")
                    if bpy.context.scene.exppcl in ["clear", "write"] and not "instonly_" in fbxName.lower():
                        shutil.move(f"{fbxModels[f]}_col.pccol", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc\\{fbxFileName}_col.pccol")

            milestone = updateprogress(2 / estimated, "Terrain", milestone)

        if bpy.context.scene.expdds in ["clear", "write", "add"]:
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
                                        if not n.image.filepath in loggedImages:
                                            loggedImages.append(n.image.filepath)
                                            milestone = updateprogress(0.2 / estimated, "Terrain", milestone)
                        except Exception as e:
                            print(e)

            for i in loggedImages:
                print(i)
                if i[-4:].lower() == ".dds":
                    filename = i.split("\\")[-1]
                    if not (bpy.context.scene.expdds == "add" and os.path.exists(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00\\{filename}")):
                        print(f"From: {i}, To: {absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00")
                        shutil.copy2(i, f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00")
                        loggedImages.pop(loggedImages.index(i))
                        milestone = updateprogress(0.2 / estimated, "Terrain", milestone)

            texList = open(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\texList.txt", "x")
            texList.write("\n".join(loggedImages))
            texList.close()

            os.chdir(os.path.dirname(directoryTexconv))
            texListLocation = f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\texList.txt"
            texDestination = f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00"
                
            print(os.popen(f'texconv -flist "{texListLocation}" -y -f BC7_UNORM -o "{texDestination}"').read())

        shutil.rmtree(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp")

        if bpy.context.scene.noPack == False:
            pack([f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_s00", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_misc"], directoryHedgearcpack)
        
        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.exportprogress = 1.0
            bpy.types.Scene.exportprogresstext = "DONE"
        
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

        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.exportprogress = 0.0
        milestone = 0
        updateprogress(0.0, "Objects", milestone)
    
        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        directoryHedgeset = os.path.abspath(bpy.path.abspath(preferences.directoryHedgeset)) # Gets Hedgeset path from preferences
        directoryHedgearcpack = os.path.abspath(bpy.path.abspath(preferences.directoryHedgearcpack)) # Gets HedgeArcPack path from preferences
        game_choice = context.scene.hedgegameChoice
        if game_choice == "shadow":
            hedgeset_game_choice = preferences.Hedgeset_shadowtemp
        absoluteModDir = os.path.abspath(bpy.path.abspath(bpy.context.scene.modDir)) # Gets mod folder directory
        worldId = bpy.context.scene.worldId # Gets the world ID to be edited

        if bpy.context.scene.expobj == "keep":
            self.report({"INFO"}, f"Quick Export Finished")
            return {'FINISHED'}
        
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

        if bpy.context.scene.expobj == "clear":
            clearFolder(f"{absoluteModDir}\\raw\\gedit\\{worldId}_gedit", ["level", "txt", "rfl"])
        
        if bpy.context.view_layer.objects.active == None:
            for o in bpy.data.objects:
                bpy.context.view_layer.objects.active = o
                break
        try:
            bpy.ops.object.mode_set(mode = 'OBJECT')
        except RuntimeError:
            pass

        #Get check info
        path_check = context.scene.FrontiersRails.objPath_check
        # Get the collection
         
        Node_startindex = context.scene.FrontiersRails.Railnode_startindex

        collection_name = bpy.context.scene.objCollection
        collection = collection_name

        if collection_name == None:
            self.report({"WARNING"}, f"Collection{collection_name} not found")
            return {"CANCELLED"}

        objecttotal = 0

        collections = [collection_name]
        objecttotal += len(collection_name.objects)
        for c1 in collection_name.children:
            collections.append(c1)
            objecttotal += len(c1.objects)
            for c2 in c1.children:
                collections.append(c2)
                objecttotal += len(c2.objects)
                for c3 in c2.children:
                    collections.append(c3)
                    objecttotal += len(c3.objects)

        blend_file_path = bpy.data.filepath
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        blend_dir = os.path.dirname(blend_file_path)
        path_dir = os.path.join(blend_dir,script_dir)

        #Set up compatible objects depending on the files in template file
        if game_choice == "shadow":
            ObjectDirectory = f"shadow_objects"
        else:
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

        # RAILS SECTION ---------------------------------------------------------------------
        for c in collections:
            if os.path.exists(f"{absoluteModDir}\\raw\\gedit\\{worldId}_gedit\\{worldId}_{collection.name}.gedit") and bpy.context.scene.expobj == "add":
                continue

            collection = c
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
                    if obj.name.lower().find("objpath") != -1:
                        PathType = 'OBJ_PATH'
                    elif obj.name.lower().find("svpath") != -1:
                        PathType = 'SV_PATH'
                    elif "HedgehogPath" in obj.modifiers:
                        PathType = bpy.data.node_groups["HedgehogPath"].nodes["PATH_TYPE"].inputs[obj.modifiers["HedgehogPath"]["Socket_5"]+1].name
                    else:
                        PathType = 'GR_PATH'
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
                            
                    if obj.name.lower().find("_str") != -1 or curve_data.splines.active.type != "BEZIER":
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
                        if i == 0:
                            originStr = False
                            origincoord = f'{point.co.x + obj.location.x}, {point.co.z + obj.location.z}, {-(point.co.y+obj.location.y)}'
                            if curve_data.splines.active.type == "BEZIER":
                                if point.handle_right_type == 'VECTOR' and point.handle_left_type == 'VECTOR':
                                    originStr = True
                            if obj.name.lower().find("_norot") == -1:
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
            
                            if obj.name.lower().find("_norot") == -1:
                                try:
                                    if i ==len(points_in_curve)-1:
                                        #RotPoint,lastLength = Find_node_rot(obj, point,next_point,lastLength,Final_curve_point=True)
                                        RotPoint,rot_checker = Find_node_rot(obj, i, path_dir)
                                        if rot_checker == False:
                                            pass
                                        rotation = f'{round(RotPoint.x,3)}, {round(RotPoint.z,3)}, {-round(RotPoint.y,3)}, {round(RotPoint.w,3)}'
                                        #rotation = '0.0, 0.0, 0.0, 1.0'
                                    else:
                                        next_point = points_in_curve[i + 1]
                                        # Call the function to spawn cube, set up constraint, print rotation, and delete cube
                                        #RotPoint,lastLength = Find_node_rot(obj, point,next_point,lastLength)
                                        RotPoint,rot_checker = Find_node_rot(obj, i, path_dir)
                                        if rot_checker == False:
                                            pass
                                        #RotPoint = RotPoint.to_quaternion()
                                        #Rotation
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
                            if obj.name.lower().find("_str") != -1 or (point.handle_right_type == 'VECTOR' and point.handle_left_type == 'VECTOR'):
                                node_temp = node_temp.replace('LINETYPE_SNS', 'LINETYPE_STRAIGHT')
                            node_text += node_temp
                            # print(i,point)
                            # print(len(points_in_curve))
                            # if i ==len(points_in_curve)-1:
                            #     quit
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
                    if obj.name.lower().find("_str") != -1 or originStr:
                        path_temp = path_temp.replace('LINETYPE_SNS', 'LINETYPE_STRAIGHT')
                    path_text += path_temp
                    node_ID_list =""
                    obj.select_set(False)

                    milestone = updateprogress(1 / objecttotal, "Objects", milestone)

            gedit_text += path_text
            gedit_text += node_text
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
                        file_name = f"{ObjectDirectory}\PointLight.json" 
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
                    if obj.data.type == 'SPOT':
                        file_name = f"{ObjectDirectory}\SpotLight.json" 
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
                        rotation = obj.rotation_quaternion
                        rotation = mathutils.Euler((rotation.to_euler().x + math.radians(90), rotation.to_euler().y, rotation.to_euler().z)).to_quaternion()
                        light_temp["rotation"] = [rotation.x, rotation.z, -rotation.y, rotation.w]
                        
                        Intense = obj.data.energy/64 #Have to divide blenders intensity to accurately portrait frontiers lights.
                        CurrentLevel = light_temp["parameters"]
                        CurrentLevel["colorR"] = obj.data.color[0]*255*Intense
                        CurrentLevel["colorG"] = obj.data.color[1]*255*Intense
                        CurrentLevel["colorB"] = obj.data.color[2]*255*Intense
                        CurrentLevel["outerConeAngle"] = (math.degrees(obj.data.spot_size)) / 2
                        CurrentLevel["innerConeAngle"] = (math.degrees(obj.data.spot_size) * (1 - obj.data.spot_blend)) / 2
                        if obj.data.use_custom_distance == True:
                            CurrentLevel["attenuationRadius"] = obj.data.cutoff_distance
                        else:
                            CurrentLevel["attenuationRadius"] = 32768
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
                            file_name = f"{ObjectDirectory}\{theobject}.json" 
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
                milestone = updateprogress(1 / objecttotal, "Objects", milestone)

            #Code that opens the window with the gedit code
            if obj_text != "":
                obj_text = textwrap.indent(obj_text, '    ')
                gedit_text += obj_text
            gedit_text = '{\n  "version": 1,\n  "objects": [\n' + gedit_text[:-2] + "\n  ]\n}"

            gedit = open(f"{absoluteModDir}\\raw\\gedit\\{worldId}_gedit\\{worldId}_{collection.name}.hson", "x")
            gedit.write(gedit_text)
            gedit.close()

            os.chdir(os.path.dirname(directoryHedgeset))
            print(os.popen(f'HedgeSet "{absoluteModDir}\\raw\\gedit\\{worldId}_gedit\\{worldId}_{collection.name}.hson" "{absoluteModDir}\\raw\\gedit\\{worldId}_gedit\\{worldId}_{collection.name}.gedit" -game={hedgeset_game_choice} -platform=pc').read())

            os.remove(f"{absoluteModDir}\\raw\\gedit\\{worldId}_gedit\\{worldId}_{collection.name}.hson")

        if bpy.context.scene.noPack == False:
            pack([f'{absoluteModDir}\\raw\\gedit\\{worldId}_gedit'], directoryHedgearcpack)
        
        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.exportprogress = 1.0
            bpy.types.Scene.exportprogresstext = "DONE"
        
        self.report({"INFO"}, f"Quick Export Finished")
        return{"FINISHED"}
    
class ExportHeightmap(bpy.types.Operator):
    bl_idname = "qexport.exportheightmap"
    bl_label = "Heightmap"
    bl_description = "Exports your level's Heightmap"

    def execute(self, context):
        startTime = time.time()

        if bpy.context.scene.exphgt == "keep":
            return {'FINISHED'}
        
        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.exportprogress = 0.0
        milestone = 0
        updateprogress(0.0, "Heightmap", milestone)

        mapsize = int(bpy.context.scene.mapsize)
        mapheight = bpy.context.scene.mapheight
        
        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        absoluteModDir = os.path.abspath(bpy.path.abspath(bpy.context.scene.modDir)) # Gets mod folder directory
        worldId = bpy.context.scene.worldId # Gets the world ID to be edited

        directoryTexconv = os.path.abspath(bpy.path.abspath(preferences.directoryTexconv)) # Gets HedgeSet path from preferences
        directoryHedgearcpack = os.path.abspath(bpy.path.abspath(preferences.directoryHedgearcpack)) # Gets HedgeArcPack path from preferences
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
        
        if not os.path.exists(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_height.pac"):
            def missingFolderError(self, context):
                self.layout.label(text="No trr_height folder found") # Sets the popup label

            bpy.context.window_manager.popup_menu(missingFolderError, title = "Folder missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation
        
        unpack([f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_height.pac"], directoryHedgearcpack)

        if bpy.context.scene.exphgt == "clear":
            for f in os.listdir(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_height"):
                if "heightmap" in f and "dds" in f:
                    os.remove(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_height\\{f}")

        if not "[FLC] Heightmap" in bpy.data.objects:
            return {'FINISHED'}
        
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
        milestone = updateprogress(0.55, "Heightmap", milestone)

        print(f"\n\nRENDER COMPLETE ----------\nTIME ELAPSED: {time.time() - previousTime}")
        previousTime = time.time()

        image = bpy.data.images["Render Result"] # Gets the Rendered image
        image.file_format = 'PNG' # Sets the file format
        try:
            image.save_render(filepath=f"{tempfolder}h.png") # Outputs the image straight to the temporary folder
        except Exception as e:
            print(f"Possible Error: {e}")

        bpy.data.objects["[FLC] Heightmap"].data.materials[0] = bpy.data.materials["[FLC] Heightmap-Preview"]

        for c in cameraObjs:
            bpy.data.cameras.remove(bpy.data.cameras[c.data.name])

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

        os.chdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(directoryTexconv)))}") # Goes to the texconv directory
        for f in os.listdir(tempfolder):
            id = format(int(f[2:-4]), "03d")
            os.popen(f'texconv -f R16_UNORM -xlum -y "{tempfolder}{f}" -o "{tempfolder[:-1]}"').read() # Converts the image via command line
            os.rename(f"{tempfolder}{f[:-4]}.dds", f"{tempfolder}{worldId}_heightmap_{id}.dds")
            shutil.copy2(f"{tempfolder}{worldId}_heightmap_{id}.dds", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_height\\{worldId}_heightmap_{id}.dds")
        

        bpy.data.objects["[FLC] Heightmap"].data.materials[0] = bpy.data.materials["[FLC] Heightmap-Normal"]
        bpy.data.objects["[FLC] Heightmap"].hide_render = False

        cameraObj = bpy.data.objects.new(f'[FLC] Cam-Normal', bpy.data.cameras.new(name=f'[FLC] Cam-Normal'))
        bpy.context.scene.collection.objects.link(cameraObj)
        cameraObj.location = (0, 0, mapheight + 10)
        cameraObj.data.type = 'ORTHO' # Sets camera to orthographic
        cameraObj.data.ortho_scale = mapsize # Sets the camera to capture the whole heightmap
        cameraObj.data.clip_end = mapheight + 11

        activecam = bpy.context.scene.camera
        bpy.context.scene.camera = bpy.data.objects["[FLC] Cam-Normal"]
        color_depth = bpy.context.scene.render.image_settings.color_depth
        bpy.context.scene.render.image_settings.color_depth = '8'
        resolution_x = bpy.context.scene.render.resolution_x
        bpy.context.scene.render.resolution_x = 4096
        resolution_y = bpy.context.scene.render.resolution_y
        bpy.context.scene.render.resolution_y = 4096
        view_transform = bpy.context.scene.view_settings.view_transform
        bpy.context.scene.view_settings.view_transform = 'Standard'
        taa_render_samples = bpy.context.scene.eevee.taa_render_samples
        bpy.context.scene.eevee.taa_render_samples = 1
        engine = bpy.context.scene.render.engine
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        worldcol = bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.5, 1.0, 1.0)

        print(f"\n\nRENDER SETUP COMPLETE ----------\nTIME ELAPSED: {time.time() - startTime}")
        previousTime = time.time()

        bpy.ops.render.render(write_still=False)
        milestone = updateprogress(0.35, "Heightmap", milestone)

        print(f"\n\nRENDER COMPLETE ----------\nTIME ELAPSED: {time.time() - previousTime}")
        previousTime = time.time()

        image = bpy.data.images["Render Result"] # Gets the Rendered image
        image.file_format = 'PNG' # Sets the file format
        try:
            image.save_render(filepath=f"{tempfolder}hgt.png") # Outputs the image straight to the temporary folder
        except Exception as e:
            print(f"Possible Error: {e}")

        bpy.data.objects["[FLC] Heightmap"].data.materials[0] = bpy.data.materials["[FLC] Heightmap-Preview"]

        bpy.data.cameras.remove(bpy.data.cameras[cameraObj.data.name])

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

        os.chdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(directoryTexconv)))}") # Goes to the directory
        os.popen(f'texconv -f R8G8B8A8_UNORM -xlum -y "{tempfolder}hgt.png" -o "{tempfolder[:-1]}"').read() # Converts the image via command line
        os.rename(f"{tempfolder}hgt.dds", f"{tempfolder}{worldId}_heightmap_nrm.dds")
        shutil.copy2(f"{tempfolder}{worldId}_heightmap_nrm.dds", f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_height\\{worldId}_heightmap_nrm.dds")

        shutil.rmtree(tempfolder)

        milestone = updateprogress(0.1, "Heightmap", milestone)

        if bpy.context.scene.noPack == False:
            pack([f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_height"], directoryHedgearcpack)

        print(f"\n\nCONVERTING COMPLETE ----------\nTIME ELAPSED: {time.time() - previousTime}")

        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.exportprogress = 1.0
            bpy.types.Scene.exportprogresstext = "DONE"

        print(f"\n\nHEIGHTMAP EXPORT COMPLETE ----------\nTIME ELAPSED: {time.time() - startTime}")

        return {'FINISHED'}

class ExportSplatmap(bpy.types.Operator):
    bl_idname = "qexport.exportsplatmap"
    bl_label = "Splatmap"
    bl_description = "Exports your Heightmap's Splatmap, Area and Scale maps"
    
    def execute(self, context):
        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.exportprogress = 0.0
        milestone = 0
        updateprogress(0.0, "Splatmap", milestone)

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

        milestone = updateprogress(0.1, "Splatmap", milestone)

        if bpy.context.scene.expspl != "keep":
            image = bpy.data.images["[FLC] Splatmap"]
            image.update()
            image.size
            image.filepath_raw = f"{tempfolder}{worldId}_splatmap.png"
            image.file_format = 'PNG'
            image.save()

            os.chdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(directoryTexconv)))}") # Goes to the directory
            if bpy.context.scene.expspl == "clear":
                os.popen(f'texconv -f R8_UNORM -xlum -y "{tempfolder}{worldId}_splatmap.png" -o "{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_cmn"').read() # Converts the image via command line
            else:
                os.popen(f'texconv -f R8_UNORM -xlum -n "{tempfolder}{worldId}_splatmap.png" -o "{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_cmn"').read() # Converts the image via command line
            os.remove(f"{tempfolder}{worldId}_splatmap.png")
        
        milestone = updateprogress(0.3, "Splatmap", milestone)

        if bpy.context.scene.expmap != "keep":
            image = bpy.data.images["[FLC] Scale"]
            image.update()
            image.size
            image.filepath_raw = f"{tempfolder}{worldId}_scale.png"
            image.file_format = 'PNG'
            image.save()

            image = bpy.data.images["[FLC] Area"]
            image.update()
            image.size
            image.filepath_raw = f"{tempfolder}{worldId}_area.png"
            image.file_format = 'PNG'
            image.save()

            os.chdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(directoryTexconv)))}") # Goes to the directory
            if bpy.context.scene.expmap == "clear":
                os.popen(f'texconv -f BC4_UNORM -xlum -y "{tempfolder}{worldId}_scale.png" -o "{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_cmn"').read() # Converts the image via command line
                os.popen(f'texconv -f R8_UNORM -xlum -y "{tempfolder}{worldId}_area.png" -o "{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_cmn"').read() # Converts the image via command line
            else:
                os.popen(f'texconv -f BC4_UNORM -xlum -n "{tempfolder}{worldId}_scale.png" -o "{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_cmn"').read() # Converts the image via command line
                os.popen(f'texconv -f R8_UNORM -xlum -n "{tempfolder}{worldId}_area.png" -o "{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_cmn"').read() # Converts the image via command line
            os.remove(f"{tempfolder}{worldId}_scale.png")
            os.remove(f"{tempfolder}{worldId}_area.png")

        milestone = updateprogress(0.6, "Splatmap", milestone)

        if bpy.context.scene.noPack == False:
            pack([f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_cmn"], directoryHedgearcpack)

        shutil.rmtree(tempfolder)

        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.exportprogress = 1.0
            bpy.types.Scene.exportprogresstext = "DONE"
        
        return {'FINISHED'}
    
class ExportDensity(bpy.types.Operator):
    bl_idname = "qexport.exportdensity"
    bl_label = "Density"
    bl_description = "Exports your level's density objects"
    
    def execute(self, context):
        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.exportprogress = 0.0
        milestone = 0
        updateprogress(0.0, "Density", milestone)

        if not bpy.context.scene.expden == "keep":
            collection = context.scene.denCollection # Name of collection that will be exported goes here
            preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
            directoryKnuxtools = os.path.abspath(bpy.path.abspath(preferences.directoryKnuxtools)) # Gets Hedgeset path from preferences
            directoryHedgearcpack = os.path.abspath(bpy.path.abspath(preferences.directoryHedgearcpack)) # Gets HedgeArcPack path from preferences

            absoluteModDir = os.path.abspath(bpy.path.abspath(bpy.context.scene.modDir)) # Gets mod folder directory
            worldId = bpy.context.scene.worldId # Gets the world ID to be edited

            if preferences.directoryKnuxtools == "" or preferences.directoryHedgearcpack == "": # Gives an error if a program is missing
                def missingProgramError(self, context):
                    missingPrograms = [] # List of missing programs
                    if preferences.directoryKnuxtools == "":
                        missingPrograms.append("KnuxTools.exe")
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
            
            if bpy.context.scene.expspl == "keep":
                return {'FINISHED'}
            
            unpack([f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_density.pac"], directoryHedgearcpack)

            if bpy.context.scene.expspl == "clear":
                for f in os.listdir(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_density"):
                    if f.endswith("densitypointcloud"):
                        os.remove(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_density\\{f}")

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
            
            objecttotal = len(collection.objects)
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
                        print(f"{obj.name}   \t{round(math.degrees(face.normal.x), 3)},{round(math.degrees(face.normal.z), 3)},{round(math.degrees(face.normal.y), 3)}   \t{vertsDone}/{numVerts}\t{round((vertsDone / numVerts) * 100, 2)}%\t{round((objectsDone / numObjects) * 100, 2)}%") # Debug
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.delete(use_global=False)
                objectsDone += 1
                print(f"{obj.name}  \t{objectsDone}/{numObjects}\t{round((objectsDone / numObjects) * 100, 2)}%") # This prints the progress to the console
                
                milestone = updateprogress(1 / objecttotal, "Density", milestone)

            jsonfile = open(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_density\\{worldId}_pointcloud.hedgehog.densitypointcloud.json", "x")
            jsonfile.write(json.dumps(printCode, indent = 2)) # Adds the code to the text
            jsonfile.close()

            os.chdir(os.path.dirname(directoryKnuxtools))
            os.popen(f'knuxtools "{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_density\\{worldId}_pointcloud.hedgehog.densitypointcloud.json"').read()
            os.remove(f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_density\\{worldId}_pointcloud.hedgehog.densitypointcloud.json")

            pack([f"{absoluteModDir}\\raw\\stage\\{worldId}\\{worldId}_trr_density"], directoryHedgearcpack)

        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.exportprogress = 1.0
            bpy.types.Scene.exportprogresstext = "DONE"
        
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

class NameShow(bpy.types.Operator):
    bl_idname = "qexport.nameshow"
    bl_label = "Object Names"
    bl_description = "Overlays the names of Frontiers Objects"

    bpy.types.Scene.nameshow = False
    def execute(self, context):
        if bpy.context.scene.nameshow == False:
            bpy.context.scene.nameshow = True
            for o in bpy.data.objects:
                if o.name.split(".")[0] not in ["Ring", "NormalFloor"] and "FrontiersAsset" in o:
                    o.show_name = True
        else:
            bpy.context.scene.nameshow = False
            for o in bpy.data.objects:
                if o.name.split(".")[0] not in ["Ring", "NormalFloor"] and "FrontiersAsset" in o:
                    o.show_name = False
        return{"FINISHED"}


class QexportSettings(bpy.types.PropertyGroup): # Other settings
    def worldidchoice(self, _):
        world_items = {
        "frontiers" : [
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
        "shadow" : [
            # ARK
            ("w01a11", "w01a11 (ARK Act 1)", ""),
            ("w01a20", "w01a20 (ARK Act 2)", ""),

            # Rail Canyon
            ("w02a10", "w02a10 (Rail Canyon Act 1)", ""),
            ("w02a20", "w02a20 (Rail Canyon Act 2)", ""),

            # Kingdom Valley
            ("w03a10", "w03a10 (Kingdom Valley Act 1)", ""),
            ("w03a20", "w03a20 (Kingdom Valley Act 2)", ""),

            # Sunset Heights
            ("w04a10", "w04a10 (Sunset Heights Act 1)", ""),
            ("w04a20", "w04a20 (Sunset Heights Act 2)", ""),

            # Chaos Island
            ("w05a10", "w05a10 (Chaos Island Act 1)", ""),
            ("w05a20", "w05a20 (Chaos Island Act 2)", ""),

            # Radical Highway
            ("w06a10", "w06a10 (Radical Highway Act 1)", ""),
            ("w06a20", "w06a20 (Radical Highway Act 2)", ""),

            # White Space
            ("w09a10", "w09a10 (White Space)", ""),

            # Bosses
            ("w11b10", "w11b10 (Biolizard)", ""),
            ("w12b10", "w12b10 (Metal Overlord)", ""),
            ("w13b10", "w13b10 (Mephiles)", ""),
            ("w14b10", "w14b10 (Devil Doom)", "")
        ]
        }
        try:
            return world_items[bpy.context.scene.hedgegameChoice]
        except KeyError:
            return [
                ('-', f'no options for {bpy.context.scene.hedgegameChoice}', ''),
            ]
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
    bpy.types.Scene.denCollection = bpy.props.PointerProperty( 
        name="Density Collection",
        type=bpy.types.Collection,
        description="Collection that your density is in"
    )
    bpy.types.Scene.modDir = bpy.props.StringProperty( 
        name="Mod Directory",
        subtype='DIR_PATH',
        default="",
        description="Path to your mod folder"
    )
    bpy.types.Scene.worldId = bpy.props.EnumProperty( 
        name="World ID",
        items= worldidchoice,
        #default=worldidchoice[0],
        description="The world you wish to export to"
    )

    # ADVANCED
    bpy.types.Scene.noPack = bpy.props.BoolProperty(    # Access through "bpy.context.scene.noPack"
        name="Don't automatically repack",
        default=False,
        description="Disables automatic repacking of files when using Quick Export (Except for the Repack All button obviously)"
    )
    bpy.types.Scene.nameshow = bpy.props.BoolProperty(
        name="Show Object Names",
        default=False,
        description="Overlays the names of objects with exceptions like rings\n(Just here until I think of a better place to put this setting)"
    )
    bpy.types.Scene.exptrr = bpy.props.EnumProperty( 
        name="Terrain Writing",
        items=[
            ("clear", "Clear", "Removes all .terrain-models, then adds the new ones"),
            ("write", "Overwrite", "Keeps existing terrain-models, but overwrites them if you export one of the same name"),
            ("add", "Add", "Keeps existing .terrain-models, and only adds new ones, not removing or editing old ones"),
            ("keep", "Keep", "Do not export any new terrain-models")
        ],
        default="clear",
        description="Hover over options for details"
    )
    bpy.types.Scene.expcol = bpy.props.EnumProperty( 
        name="Collison Writing",
        items=[
            ("clear", "Clear", "Removes all .btmeshes, then adds the new ones"),
            ("write", "Overwrite", "Keeps existing btmeshes, but overwrites them if you export one of the same name"),
            ("add", "Add", "Keeps existing .btmeshes, and only adds new ones, not removing or editing old ones"),
            ("keep", "Keep", "Do not export any new btmeshes")
        ],
        default="clear",
        description="Hover over options for details"
    )
    bpy.types.Scene.expobj = bpy.props.EnumProperty( 
        name="Object Writing",
        items=[
            ("clear", "Clear", "Removes all .gedits, then adds the new ones"),
            ("write", "Overwrite", "Keeps existing gedits, but overwrites them if you export one of the same name"),
            ("add", "Add", "Keeps existing .gedits, and only adds new ones, not removing or editing old ones"),
            ("keep", "Keep", "Do not export any new gedits")
        ],
        default="clear",
        description="Hover over options for details"
    )
    bpy.types.Scene.expden = bpy.props.EnumProperty( 
        name="Density Writing",
        items=[
            ("clear", "Clear", "Removes all density, then adds the new density"),
            ("keep", "Keep", "Do not export any new density")
        ],
        default="clear",
        description="Hover over options for details"
    )
    bpy.types.Scene.exphgt = bpy.props.EnumProperty( 
        name="Heightmap Writing",
        items=[
            ("clear", "Clear", "Removes the old heightmap, then adds the new one"),
            ("keep", "Keep", "Do not export any new heightmap")
        ],
        default="clear",
        description="Hover over options for details"
    )
    bpy.types.Scene.expspl = bpy.props.EnumProperty( 
        name="Splatmap Writing",
        items=[
            ("clear", "Clear", "Removes the current splatmap, then adds the new one"),
            ("keep", "Keep", "Do not export any new splatmap")
        ],
        default="clear",
        description="Hover over options for details"
    )
    bpy.types.Scene.expmap = bpy.props.EnumProperty( 
        name="Other Map Writing",
        items=[
            ("clear", "Clear", "Removes all other heightmap related maps, then adds the new ones"),
            ("keep", "Keep", "Do not export any new heightmap related maps")
        ],
        default="clear",
        description="Hover over options for details"
    )
    bpy.types.Scene.expmat = bpy.props.EnumProperty( 
        name="Material Writing",
        items=[
            ("clear", "Clear", "Removes all .materials, then adds the new ones"),
            ("write", "Overwrite", "Keeps existing materials, but overwrites them if you export one of the same name"),
            ("add", "Add", "Keeps existing .materials and only adds new ones, not removing or editing old ones"),
            ("keep", "Keep", "Do not export any new materials")
        ],
        default="clear",
        description="Hover over options for details"
    )
    bpy.types.Scene.expdds = bpy.props.EnumProperty( 
        name="Texture Writing",
        items=[
            ("clear", "Clear", "Removes all textures, then adds the new ones"),
            ("write", "Overwrite", "Keeps existing textures, but overwrites them if you export one of the same name"),
            ("add", "Add", "Keeps existing textures, and only adds new ones, not removing or editing old ones"),
            ("keep", "Keep", "Do not export any new textures")
        ],
        default="clear",
        description="Hover over options for details"
    )
    bpy.types.Scene.expuva = bpy.props.EnumProperty( 
        name="UV-anim Writing",
        items=[
            ("clear", "Clear", "Removes all .UV-anims, then adds the new ones"),
            ("write", "Overwrite", "Keeps existing UV-anims, but overwrites them if you export one of the same name"),
            ("add", "Add", "Keeps existing UV-anims, and only adds new ones, not removing or editing old ones"),
            ("keep", "Keep", "Do not export any new UV-anims")
        ],
        default="clear",
        description="Hover over options for details"
    )
    bpy.types.Scene.exppcm = bpy.props.EnumProperty( 
        name="pcmodel Writing",
        items=[
            ("clear", "Clear", "Removes all .pcmodels, then adds the new ones"),
            ("write", "Overwrite", "Keeps existing pcmodels, but overwrites them if you export one of the same name"),
            ("add", "Add", "Keeps existing pcmodels, and only adds new ones, not removing or editing old ones"),
            ("keep", "Keep", "Do not export any new pcmodels")
        ],
        default="clear",
        description="Hover over options for details"
    )
    bpy.types.Scene.exppcl = bpy.props.EnumProperty( 
        name="pccol Writing",
        items=[
            ("clear", "Clear", "Removes all .pccols, then adds the new ones"),
            ("write", "Overwrite", "Keeps existing pccols, but overwrites them if you export one of the same name"),
            ("add", "Add", "Keeps existing pccols, and only adds new ones, not removing or editing old ones"),
            ("keep", "Keep", "Do not export any new pccols")
        ],
        default="clear",
        description="Hover over options for details"
    )
    bpy.types.Scene.expmsc = bpy.props.EnumProperty( 
        name="Other Writing",
        items=[
            ("clear", "Clear", "Removes all other random types of files, then adds the new ones"),
            ("write", "Overwrite", "Keeps existing other random types of files, but overwrites them if you export one of the same name"),
            ("add", "Add", "Keeps existing other random types of files, and only adds new ones, not removing or editing old ones"),
            ("keep", "Keep", "Do not export any new other random types of files")
        ],
        default="clear",
        description="Hover over options for details"
    )
