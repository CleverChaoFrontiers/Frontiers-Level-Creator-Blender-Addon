import bpy # type: ignore (Supresses the warning associated with it being a Blender library)
import mathutils # type: ignore
import os
import time
import shutil
import json
import io
import contextlib
import math
import struct
from .Frontiers_parameter_script import update_parameters

debugMode = False
class read:
    def int(bytes, size): # Read integer
        value = int.from_bytes(bytes[:int(size/8)], "big") # Gets the value of the first int in the given bytes
        if debugMode: print(f"read.int() : bytes={bytes}, size={size}, value={value}")
        return value # Returns the value
    
    def float(bytes): # Read floating point
        value = struct.unpack(">f", bytes[:4])[0] # Gets the value of the first int in the given bytes
        if debugMode: print(f"read.float() : bytes={bytes}, value={value}")
        return value # Returns the value
    
    def bool(bytes): # Read boolean
        if bytes[0] == 0:
            return False 
        elif bytes[0] == 1:
            return True
        else:
            raise Exception("Unsupported value for boolean")
    
    def str(bytes): # Read string
        characters = []
        length = 0
        for c in bytes:
            if c != 0: # A 0, or \x00, represents the end of characters in a string
                characters.append(c.to_bytes().decode("utf-8")) # Decodes the byte to a UTF-8 character
                length += 1
            else:
                length = length + (4 - (length % 4)) # Extends the real length to the "real" end of the string - all strings are padded at the end with enough \x00's to bring the length to the next multiple of 4
                break # Stops processing bytes
        value = "".join(characters) # Converts all the decoded characters into one string
        if debugMode: print(f"read.str() : bytes={bytes}, value={value}, length={length}")
        return value, length # Returns the value, length and real length
    
    def strlist(bytes, items): # Read a list of strings, basically a string but with segments separated by \x00 or 0's
        stringlist = []
        length = 0
        index = 0
        for i in range(items):
            characters = []
            while True:
                byte = bytes[index]
                index += 1
                if byte != 0:
                    characters.append(byte.to_bytes().decode("utf-8")) # Decodes the byte to a UTF-8 character
                    length += 1
                else:
                    break
            stringlist.append("".join(characters))
        length += items - 1
        length = length + (4 - (length % 4))
        if debugMode: print(f"read.strlist() : bytes={bytes}, stringlist={stringlist}, length={length}")
        return stringlist, length

    def enum(bytes, enums): # Read enumerator
        choice = enums[bytes[0]]
        if debugMode: print(f"read.enum() : bytes={bytes}, enums={enums}, choice={choice}")
        return choice

def unpackCheck(file, directoryHedgearcpack):
    if os.path.exists(file): # If the .pac exists
        if os.path.exists(f"{file[:-4]}\\"): # If the .pac is already unpacked
            print(f"unpackCheck(): File {file} already unpacked")
            return "unpacked"
        else: # If the .pac is not unpacked
            print(f"unpackCheck(): File {file} found but not unpacked")
            os.chdir(os.path.dirname(directoryHedgearcpack)) # Change the working directory to HedgeArcPack's directory so it can be run
            print(os.popen(f'hedgearcpack "{file}"').read()) # Unpack it
            return "notunpacked"
    else: # If the .pac doesn't exist
        print(f"unpackCheck(): File {file} not found")
        return "notfound"

def readMaterial(path):
    with open(path, "rb") as f:
        pointer = 0 # The pointer is to keep track of what bytes have been fully read/decoded/taken care of

        f.seek(16, 1) # Skips 13 bytes with unknown purposes
        pointer += 16

        miragenodes = []
        while True: # Loops through sections of data until it reaches the end of the list of nodes
            f.seek(2, 1) # Unknown data
            miragenodes.append({"DataSize": 0, "Value": 0, "Name": ""}) # Adds a data entry to the list

            # Reads and sets all the data
            miragenodes[-1]["DataSize"] = read.int(f.read(2), 16)
            miragenodes[-1]["Value"] = read.int(f.read(4), 32)
            miragenodes[-1]["Name"] = f.read(8).decode("utf-8")

            pointer += 16
            if read.int(f.read(4), 32) - 20 == pointer: # Finds the set of 4 bytes marking the end of the list
                break
            f.seek(pointer)

        pointer += 16
        f.seek(pointer)

        # Read general material properties
        materialflag = read.int(f.read(1), 8)
        renderbackface = read.bool(f.read(1))
        additiveblending = read.bool(f.read(1))
        unknownflag = read.int(f.read(1), 8)
        f.seek(3, 1)

        texturecount = read.int(f.read(1), 8) # Gets number of textures in material

        pointer += 20
        f.seek(pointer)

        (shader, subshader), shaderslength = read.strlist(f.read(), 2) # Gets the shader name and length
        pointer += shaderslength
        f.seek(pointer)

        pointer += 4
        f.seek(pointer)

        propertypointers = [] # List of pointers to each property
        while True:
            currentpointer = f.read(4) # Read a pointer
            pointer += 4
            if read.int(currentpointer, 32) + 8 == pointer: # Marks the end of the list of pointers
                propertypointers.pop(-1)
                propertypointers.pop(-1)
                break # Stop reading
            else:
                propertypointers.append(read.int(currentpointer, 32)) # Add the pointer to the list
        pointer += 0
        f.seek(0, 1)
        print(f"pointer: {pointer}")
        print(f"len(propertypointers): {len(propertypointers)}")

        properties = []
        for p in propertypointers:
            properties.append({"Name": "", "Flag1": 0, "Flag2": 0, "x": 0.0, "y": 0.0, "z": 0.0, "w": 0.0}) # Adds a data entry to the list
            properties[-1]["Name"], incrementpointer = read.str(f.read()) # Reads the name
            pointer += incrementpointer # Jumps to the end of the string
            f.seek(pointer)
            # Reads all the properties
            properties[-1]["x"] = round(read.float(f.read(4)), 4)
            properties[-1]["y"] = round(read.float(f.read(4)), 4)
            properties[-1]["z"] = round(read.float(f.read(4)), 4)
            properties[-1]["w"] = round(read.float(f.read(4)), 4)
            properties[-1]["Flag1"] = read.int(f.read(2), 16)
            properties[-1]["Flag2"] = read.int(f.read(2), 16)
            pointer += 28
            f.seek(pointer)

        # Same thing as before, but there's always a property that's missing a pointer, so this handles that
        f.seek(propertypointers[-1] + 28)
        properties.append({"Name": "", "Flag1": 0, "Flag2": 0, "x": 0.0, "y": 0.0, "z": 0.0, "w": 0.0})
        properties[-1]["Name"], incrementpointer = read.str(f.read())
        pointer += incrementpointer
        f.seek(pointer)
        properties[-1]["x"] = round(read.float(f.read(4)), 4)
        properties[-1]["y"] = round(read.float(f.read(4)), 4)
        properties[-1]["z"] = round(read.float(f.read(4)), 4)
        properties[-1]["w"] = round(read.float(f.read(4)), 4)
        properties[-1]["Flag1"] = read.int(f.read(2), 16)
        properties[-1]["Flag2"] = read.int(f.read(2), 16)
        pointer += 20
        f.seek(pointer)

        #pointer += 12 # Skip past unknown data
        f.seek(pointer)
        if f.read()[12:].startswith(b"enable_multi_tangent_space"): # If the enable_multi_tangent_space parameter is present, skip an extra 32 bytes
            pointer += 48 # Skip past the enable_multi_tangent_space data
            emts = True
        else:
            emts = False

        pointer += (texturecount * 4) - 4
        f.seek(pointer)

        texturenames, incrementpointer = read.strlist(f.read(), texturecount) # Reads the list of texture names
        pointer += incrementpointer

        pointer += (texturecount * 4) + 12
        textures = []

        for n in texturenames:
            textures.append({"Name": n, "Texture": "", "Type": "", "AddressU": "", "AddressV": "", "TexCoordIndex": ""}) # Creates a new data entry
            f.seek(pointer)
            (textures[-1]["Texture"], textures[-1]["Type"]), incrementpointer = read.strlist(f.read(), 2) # Reads the texture filename
            pointer += incrementpointer + 4
            f.seek(pointer)
            # Reads other data
            textures[-1]["TexCoordIndex"] = read.int(f.read(1), 8)
            textures[-1]["AddressU"] = read.int(f.read(1), 8)
            textures[-1]["AddressV"] = read.int(f.read(1), 8)
            pointer += 8

        # Puts data into a dictionary
        materialData = {
            "name": os.path.basename(f.name).split(".")[0],
            "settings": {
                "additiveBlending": additiveblending,
                "renderBackface": renderbackface,
            },
            "shader": shader,
            "subShader": subshader,
            "textures": textures
        }

        f.close() # Closes the file

        return materialData

def updateprogress(advance):
    bpy.types.Scene.heightmapprogress =  bpy.types.Scene.heightmapprogress + advance
    bpy.types.Scene.heightmapprogresstext = f"LOADING ({round(bpy.types.Scene.heightmapprogress * 100)}%)"
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    return

class CompleteImport(bpy.types.Operator):
    bl_idname = "qimport.completeimport"
    bl_label = "Complete Import"
    bl_description = "Imports terrain, objects and the heightmap"

    def execute(self, context):
        return{"FINISHED"}

class ImportTerrain(bpy.types.Operator):
    bl_idname = "qimport.importterrain"
    bl_label = "Terrain"
    bl_description = "Imports terrain"

    def execute(self, context):
        startTime = time.time()

        worldFolder = os.path.abspath(bpy.path.abspath(bpy.context.scene.worldDir)) # Gets the chosen world folder
        geditFolder = os.path.dirname(os.path.dirname(worldFolder))
        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        directoryKnuxtools = os.path.abspath(bpy.path.abspath(preferences.directoryKnuxtools)) # Gets KnuxTools path from preferences
        directoryHedgearcpack = os.path.abspath(bpy.path.abspath(preferences.directoryHedgearcpack)) # Gets HedgeArcPack path from preferences
        directoryHedgeneedle = os.path.abspath(bpy.path.abspath(preferences.directoryHedgeneedle)) # Gets HedgeNeedle path from preferences
        directoryModelfbx = os.path.abspath(bpy.path.abspath(preferences.directoryModelfbx)) # Gets ModelFBX path from preferences
        worldTypeId = os.path.abspath(bpy.path.abspath(bpy.context.scene.worldDir)).split('\\')[-1][:2] # e.g. w6, w1, w3
        worldType = os.path.abspath(bpy.path.abspath(bpy.context.scene.worldDir)).split('\\')[-1] # e.g. w6d01, w1r03, w3r01
        commonFolder = f"{os.path.dirname(os.path.abspath(bpy.path.abspath(bpy.context.scene.worldDir)))}\\{worldTypeId}_common"
        print(worldType)
        if os.path.exists(f'{commonFolder}.pac'):
            print(f"Common Folder {unpackCheck(f'{commonFolder}.pac', directoryHedgearcpack)}")

        if preferences.directoryKnuxtools == "" or preferences.directoryHedgearcpack == "" or preferences.directoryHedgeneedle == "" or preferences.directoryModelfbx == "": # Gives an error if a program is missing
            def missingProgramError(self, context):
                missingPrograms = [] # List of missing programs
                if preferences.directoryKnuxtools == "":
                    missingPrograms.append("KnuxTools.exe")
                if preferences.directoryHedgearcpack == "":
                    missingPrograms.append("HedgeArcPack.exe")
                if preferences.directoryHedgeneedle == "":
                    missingPrograms.append("HedgeNeedle.exe")
                if preferences.directoryModelfbx == "":
                    missingPrograms.append("ModelFBX.exe")
                self.layout.label(text=f"The filepath(s) for: {', '.join(missingPrograms)} are not set. \nPlease set the path(s) in Settings.") # Tells the user about the missing prorgrams

            bpy.context.window_manager.popup_menu(missingProgramError, title = "Program missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        if bpy.context.scene.worldDir == "": # Gives an error if no world directory is sent
            def missingProgramError(self, context):
                self.layout.label(text="No World folder is set") # Sets the popup label

            bpy.context.window_manager.popup_menu(missingProgramError, title = "World folder not set", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        if not bpy.data.is_saved:
            def saveError(self, context):
                self.layout.label(text="The .blend file is not saved!") # Sets the popup label
            bpy.context.window_manager.popup_menu(saveError, title = "File not saved", icon = "DISK_DRIVE") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        unpackChecks = [f"{worldFolder}\\{worldType}_trr_s00.pac", f"{worldFolder}\\{worldType}_misc.pac"]
        for pac in unpackChecks:
            if unpackCheck(pac, directoryHedgearcpack) == "notfound":
                def missingProgramError(self, context):
                    self.layout.label(text=f"File '{pac}' not found") # Tells the user about the missing prorgrams
                bpy.context.window_manager.popup_menu(missingProgramError, title = "File missing", icon = "QUESTION") # Makes the popup appear
                return {'FINISHED'} # Cancels the operation
        
        loggedModels = []
        loggedMaterials = []
        loggedImages = []
        loggedPcmodels = []
        loggedPcmodelInstances = [[], [], [], []]
        loggedBtmeshes = []
        loggedPccols = []
        for file in os.listdir(f"{worldFolder}\\{worldType}_trr_s00\\"): # Logs all relevant files in trr_s00
            extension = file.split(".")[-1].lower()
            if extension == "terrain-model":
                loggedModels.append(f"{worldFolder}\\{worldType}_trr_s00\\{file}")
            elif extension == "material":
                loggedMaterials.append(f"{worldFolder}\\{worldType}_trr_s00\\{file}")
            elif extension == "dds":
                loggedImages.append(f"{worldFolder}\\{worldType}_trr_s00\\{file}")
            elif extension == "pcmodel":
                loggedPcmodels.append(f"{worldFolder}\\{worldType}_trr_s00\\{file}")
            else:
                pass
        for file in os.listdir(f"{worldFolder}\\{worldType}_misc\\"): # Logs all relevant files in misc
            extension = file.split(".")[-1].lower()
            if extension == "btmesh":
                loggedBtmeshes.append(f"{worldFolder}\\{worldType}_misc\\{file}")
            elif extension == "pccol":
                loggedPccols.append(f"{worldFolder}\\{worldType}_misc\\{file}")
            else:
                pass

        print(f"\nloggedModels: {loggedModels}\n\nloggedMaterials: {loggedMaterials}\n\nloggedImages: {loggedImages}\n\nloggedPcmodels: {loggedPcmodels}\n\loggedBtmeshes: {loggedBtmeshes}\n\loggedPccols: {loggedPccols}\n\n")
        
        if os.path.exists(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp"):
            shutil.rmtree(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp")
        os.mkdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp")

        for model in loggedModels:
            os.chdir(os.path.dirname(directoryHedgeneedle))
            needlefile = open(model, "rb")
            if needlefile.read(8) == b"NEDARCV1":
                needlefile.close()
                os.popen(f'HedgeNeedle "{model}"').read()
                lodName = model.split('\\')[-1][:-14]
                try:
                    shutil.move(f"{model[:-14]}\\{lodName}.0.terrain-model", f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\")
                    shutil.rmtree(f"{model[:-14]}\\")
                    os.chdir(os.path.dirname(directoryModelfbx))
                    trrModelPath = f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{lodName}.0.terrain-model"
                    os.popen(f'ModelFBX "{trrModelPath}"').read()
                    print(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{lodName}.0.terrain-model.fbx --> {lodName}.fbx")
                    os.chdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\")
                    os.rename(f"{lodName}.0.terrain-model.fbx", f"{lodName}.fbx")
                except:
                    pass                    
            else:
                needlefile.close()
                try:
                    modelbasename = model.split('\\')[-1] # modelname.terrain-model
                    shutil.copy2(model, f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{modelbasename}")
                    os.chdir(os.path.dirname(directoryModelfbx))
                    trrModelPath = f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{modelbasename}"
                    os.popen(f'ModelFBX "{trrModelPath}"').read()
                    print(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{modelbasename}.fbx --> {modelbasename[:-14]}.fbx")
                    os.chdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\")
                    os.rename(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{modelbasename}.fbx",f"{modelbasename[:-14]}.fbx")
                except Exception as e:
                    print(e)    
        print(f"\n\nMODEL EXTRACTION COMPLETE ----------\nTIME ELAPSED: {time.time() - startTime}")
        previousTime = time.time()

        for pcmodel in loggedPcmodels:
            os.chdir(os.path.dirname(directoryKnuxtools))
            os.popen(f'KnuxTools "{pcmodel}"').read()
            with open(f"{pcmodel[:-8]}.hedgehog.pointcloud.json", "r") as file:
                pcmodelJson = json.load(file)
                for i in pcmodelJson:
                    try:
                        loggedPcmodelInstances[0].append(i["AssetName"])
                    except:
                        loggedPcmodelInstances[0].append(i["ModelName"])
                    loggedPcmodelInstances[1].append(i["Position"])
                    loggedPcmodelInstances[2].append(i["Rotation"])
                    loggedPcmodelInstances[3].append(i["Scale"])
            os.remove(f"{pcmodel[:-8]}.hedgehog.pointcloud.json")
        #print(loggedPcmodelInstances)
        print(f"\n\nPCMODELS LOADING COMPLETE ----------\nTIME ELAPSED: {time.time() - previousTime}")
        previousTime = time.time()

        alreadyImported = []
        importedObjects = []
        for instance in range(len(loggedPcmodelInstances[0])):
            try:
                if loggedPcmodelInstances[0][instance] in alreadyImported:
                    pass
                else:
                    with contextlib.redirect_stdout(io.StringIO()): # Stops FBX import from clogging up the console
                        old_objs = set(context.scene.objects)
                        bpy.ops.import_scene.fbx(filepath=f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\{loggedPcmodelInstances[0][instance]}.fbx")
                        alreadyImported.append(list(set(context.scene.objects) - old_objs)[0].name)

                trrObj = bpy.data.objects.new(loggedPcmodelInstances[0][instance], bpy.data.objects[loggedPcmodelInstances[0][instance]].data)
                bpy.context.collection.objects.link(trrObj)
                trrObj.rotation_mode = "XYZ"
                trrObj.rotation_euler = (math.radians(90), 0, 0)
                bpy.ops.object.select_all(action='DESELECT')
                trrObj.select_set(True)
                bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=False, properties=False)
                trrObj.location = (loggedPcmodelInstances[1][instance]["X"], -loggedPcmodelInstances[1][instance]["Z"], loggedPcmodelInstances[1][instance]["Y"])
                trrObj.scale = (loggedPcmodelInstances[3][instance]["X"], loggedPcmodelInstances[3][instance]["Z"], loggedPcmodelInstances[3][instance]["Y"])
                trrObj.rotation_mode = "QUATERNION"
                trrObj.rotation_mode = "XZY"
                trrObj.rotation_euler = (loggedPcmodelInstances[2][instance]["X"], -loggedPcmodelInstances[2][instance]["Z"], loggedPcmodelInstances[2][instance]["Y"])
                importedObjects.append(trrObj)
            except Exception as e:
                print(f"Line 393:{e}")

        bpy.ops.object.select_all(action='DESELECT')
        for o in importedObjects:
            o.select_set(True)
        #bpy.ops.transform.rotate(value=math.radians(-90), orient_axis='X', orient_type='GLOBAL', center_override=(0.0, 0.0, 0.0))

        bpy.ops.object.select_all(action='DESELECT')
        for obj in alreadyImported:
            bpy.data.objects[obj].select_set(True)
        bpy.ops.object.delete() 

        print(f"\n\nMODEL LOADING COMPLETE ----------\nTIME ELAPSED: {time.time() - previousTime}")
        previousTime = time.time()

        removeMats = []
        for o in importedObjects:
            try:
                for ms in o.material_slots:
                    if ms.material.name[-4] == ".":
                        removeMats.append(ms.material.name)
                        ms.material = bpy.data.materials[ms.material.name[:-4]]
            except Exception as exception:
                print(exception)
        
        for m in removeMats:
            try:
                bpy.data.materials.remove(bpy.data.materials[m])
            except KeyError:
                pass

        print(f"\n\nMODEL CLEANING UP COMPLETE ----------\nTIME ELAPSED: {time.time() - previousTime}")
        previousTime = time.time()

        materialFiles = []
        for f in os.listdir(f"{worldFolder}\\{worldType}_trr_s00\\"):
            if f.endswith('.material'):
                materialFiles.append(f"{worldFolder}\\{worldType}_trr_s00\\{f}")
        if os.path.exists(commonFolder):
            for f in os.listdir(f"{commonFolder}\\"):
                if f.endswith('.material'):
                    materialFiles.append(f"{commonFolder}\\{f}")

        print(f"{len(materialFiles)} materials found:\n{materialFiles}")

        for f in materialFiles:
            try:
                materialData = readMaterial(f).copy()
                material = bpy.data.materials[materialData["name"]]
                node_tree = material.node_tree
                links = node_tree.links
                for i in materialData["textures"]:
                    imageNode = node_tree.nodes.new("ShaderNodeTexImage")
                    textureName = i["Texture"]
                    try:
                        imageNode.image = bpy.data.images.load(f"{worldFolder}\\{worldType}_trr_s00\\{textureName}.dds")
                    except:
                        try:
                            imageNode.image = bpy.data.images.load(f"{commonFolder}\\{textureName}.dds")
                        except Exception as e:
                            print(f"image not found: {e}")
                    if i["Type"] == "diffuse":
                        links.new(imageNode.outputs[0], node_tree.nodes["Principled BSDF"].inputs[0])
                    elif i["Type"] == "specular":
                        links.new(imageNode.outputs[1], node_tree.nodes["Principled BSDF"].inputs[10])
                    elif i["Type"] == "normal":
                        links.new(imageNode.outputs[0], node_tree.nodes["Normal Map"].inputs[1])
                        imageNode.image.colorspace_settings.name = "Non-Color"
                        node_tree.nodes["Normal Map"].space = "TANGENT"
                    elif i["Type"] == "emission":
                        links.new(imageNode.outputs[1], node_tree.nodes["Principled BSDF"].inputs[24])
                    elif i["Type"] == "opacity":
                        links.new(imageNode.outputs[1], node_tree.nodes["Principled BSDF"].inputs[4])
                        material.blend_method = "CLIP"
                        material.name = f"{material.name}@LYR(punch)"
                    elif i["Type"] == "transparency":
                        links.new(imageNode.outputs[1], node_tree.nodes["Principled BSDF"].inputs[4])
                        material.blend_method = "BLEND"
                        material.name = f"{material.name}@LYR(trans)"
            except Exception as e:
                print(e)

        print(f"\n\nMATERIAL LOADING COMPLETE ----------\nTIME ELAPSED: {time.time() - previousTime}")
        previousTime = time.time()

        shutil.rmtree(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp")
        
        print(f"\n\nIMPORT COMPLETE ----------\nTIME ELAPSED: {time.time() - startTime}")
        return{"FINISHED"}
    
class ImportObjects(bpy.types.Operator):
    bl_idname = "qimport.importobjects"
    bl_label = "Objects"
    bl_description = "Imports objects"

    def execute(self, context):
        startTime = time.time()

        worldFolder = os.path.abspath(bpy.path.abspath(bpy.context.scene.worldDir)) # Gets the chosen world folder
        worldId = worldFolder.split("\\")[-1]
        geditFolder = f"{os.path.dirname(os.path.dirname(worldFolder))}\\gedit\\{worldId}_gedit"
        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        directoryHedgearcpack = os.path.abspath(bpy.path.abspath(preferences.directoryHedgearcpack)) # Gets HedgeArcPack path from preferences
        directoryHedgeset = os.path.abspath(bpy.path.abspath(preferences.directoryHedgeset)) # Gets HedgeSet path from preferences

        print(f"Gedit folder {unpackCheck(f'{geditFolder}.pac', directoryHedgearcpack)}")

        if preferences.directoryHedgearcpack == "" or preferences.directoryHedgeset == "": # Gives an error if a program is missing
            def missingProgramError(self, context):
                missingPrograms = [] # List of missing programs
                if preferences.directoryHedgearcpack == "":
                    missingPrograms.append("HedgeArcPack.exe")
                if preferences.directoryHedgeset == "":
                    missingPrograms.append("HedgeSet.exe")
                self.layout.label(text=f"The filepath(s) for: {', '.join(missingPrograms)} are not set. \nPlease set the path(s) in Settings.") # Tells the user about the missing prorgrams

            bpy.context.window_manager.popup_menu(missingProgramError, title = "Program missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        if bpy.context.scene.worldDir == "": # Gives an error if no world directory is sent
            def missingProgramError(self, context):
                self.layout.label(text="No World folder is set") # Sets the popup label

            bpy.context.window_manager.popup_menu(missingProgramError, title = "World folder not set", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        if not bpy.data.is_saved:
            def saveError(self, context):
                self.layout.label(text="The .blend file is not saved!") # Sets the popup label
            bpy.context.window_manager.popup_menu(saveError, title = "File not saved", icon = "DISK_DRIVE") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation
        
        geditFiles = []
        for f in os.listdir(geditFolder):
            if f.endswith(".gedit"):
                os.chdir(os.path.dirname(directoryHedgeset))
                print(os.popen(f'HedgeSet "{geditFolder}\\{f}" -game=frontiers -platform=pc').read())

                hsonName = f.replace(".gedit", ".hson")
                geditFiles.append(f"{geditFolder}\\{f.replace('.gedit', '.hson')}")
        
        # Find the Level Creator asset pack
        lcAssetPacks = []
        for l in bpy.context.preferences.filepaths.asset_libraries:
            if "flc-identifier" in os.listdir(l.path):
                lcAssetPacks.append(l)
        
        if len(lcAssetPacks) > 1: # If 2+ asset packs are installed for some reason, get whichever has the latest version
            assetPack = lcAssetPacks[0]
            assetPackVer = 0
            for p in lcAssetPacks:
                newAssetPackVer = open(f"{p.path}\\flc-identifier", "rb").read()
                if int.from_bytes(newAssetPackVer, "big") > assetPackVer:
                    assetPack = p
                    assetPackVer = int.from_bytes(newAssetPackVer, "big")
        else:
            assetPack = lcAssetPacks[0]

        print(assetPack.name)

        objectAssets = []
        exceptions = [] # Exceptions for loading objects
        assetBlends = [f for f in os.listdir(assetPack.path) if f.endswith('.blend')]
        for f in assetBlends:
            if not f in exceptions:
                try:
                    with bpy.data.libraries.load(f"{assetPack.path}\\{f}") as (data_from, data_to):
                        data_to.objects = data_from.objects
                        objectAssets = objectAssets + data_to.objects
                except:
                    def assetError(self, context):
                        self.layout.label(text="Please check that the asset pack you're using is for the right version of Blender") # Sets the popup label
                    bpy.context.window_manager.popup_menu(assetError, title = "Unknown Error", icon = "ERROR") # Makes the popup appear
                    return {'FINISHED'} # Cancels the operation
        
        for o in objectAssets:
            if o.split(".")[0] in ["CameraFollow", "CameraPan","CameraFix","CameraRailSideView","CameraRailForwardView"]:
                if bpy.data.objects.get(o) is not None:
                    if not "FrontiersCamera" in bpy.data.objects[o]:
                        bpy.data.objects.remove(bpy.data.objects[o])
                elif bpy.data.objects.get(f"{o}.001") is not None:
                    if "FrontiersCamera" in bpy.data.objects[f"{o}.001"]:
                        bpy.data.objects[f"{o}.001"].name = bpy.data.objects[f"{o}.001"].name.split(".")[0]
                    else:
                        bpy.data.objects.remove(bpy.data.objects[f"{o}.001"])

        print(objectAssets)

        ids = {}
        children = []
        parents = []
        paths = [] # Path objects ids
        pathnodes = [] # Lists of path nodes ids for each path
        pathnodepos = {} # Positions of all path nodes
        pathnoderot = {} # Rotations of all path nodes
        for f in geditFiles:
            geditFile = open(f, "r")
            geditData = json.loads(geditFile.read())
            print(geditData)
            if not "objects" in geditData:
                print("Empty gedit")
                continue
            for o in geditData["objects"]:
                print(o)
                if o["type"] == "Path":
                    paths.append(o["id"])
                    pathnodes.append(o["parameters"]["setParameter"]["nodeList"])
                    curve = bpy.data.curves.new("Curve", 'CURVE')
                    curve.dimensions = '3D'
                    path = curve.splines.new(type='POLY')
                    path.points.add(len(o["parameters"]["setParameter"]["nodeList"]) - 1)
                    if o["parameters"]["setParameter"]["pathType"] == "GR_PATH":
                        blendObj = bpy.data.objects.new('Path', curve)
                        if blendObj.data.bevel_depth != 0.0:
                            # Set bevel to 0.0 radius
                            blendObj.data.bevel_depth = 0.0
                        else:
                            # Set bevel to profile preset crown with 0.25 radius
                            blendObj.data.bevel_depth = 0.25
                            blendObj.data.bevel_mode = 'PROFILE'
                    elif o["parameters"]["setParameter"]["pathType"] == "SV_PATH":
                        blendObj = bpy.data.objects.new('Path_SVPath', curve)
                    else:
                        blendObj = bpy.data.objects.new('Path_ObjPath', curve)
                    bpy.context.scene.collection.objects.link(blendObj)
                    bpy.ops.object.select_all(action='DESELECT')
                    blendObj.select_set(True)
                    bpy.context.view_layer.objects.active = blendObj 
                elif o["type"] == "PathNode":
                    pathnodepos[o["id"]] = o["position"]
                    pathnoderot[o["id"]] = o["position"]
                    continue # Skip all object handling if PathNode
                else:
                    if o["type"] in objectAssets:
                        blendObj = bpy.data.objects[o["type"]].copy()
                        try:
                            blendObj.data = bpy.data.objects[o["type"]].data.copy()
                        except:
                            print("Empty Object Found, Skipping")
                            continue
                        bpy.context.scene.collection.objects.link(blendObj)
                        bpy.ops.object.select_all(action='DESELECT')
                        blendObj.select_set(True)
                        bpy.context.view_layer.objects.active = blendObj 
                    else:
                        bpy.ops.object.empty_add(type='PLAIN_AXES')
                        blendObj = bpy.context.object
                        blendObj.name = o["type"]
                blendObj.location = (o["position"][0], -o["position"][2], o["position"][1])
                try:
                    blendObj.rotation_mode = "QUATERNION"
                    blendObj.rotation_quaternion = (o["rotation"][3], o["rotation"][0], -o["rotation"][2], o["rotation"][1])
                except:
                    print("noRot")
                ids[o["id"]] = blendObj
                if "parentId" in o:
                    children.append(o["id"])
                    parents.append(o["parentId"])
                blendObj["DataID"] = o["id"][1:-1]
                try:
                    blendObj.use_display_json_parameters = True
                    update_parameters(blendObj, bpy.context)
                except:
                    continue
                for p in blendObj.json_parameters:
                    parampath = p.name.split("/")
                    print(parampath)
                    propertyType = parampath[-1]
                    if len(parampath) == 2:
                        if propertyType == "float":
                            p.float_value = o["parameters"][parampath[0]]
                        elif propertyType == "enum":
                            for e in p.enum_items:
                                if e.value == o["parameters"][parampath[0]]:
                                    e.selected = True
                                else:
                                    e.selected = False
                        elif propertyType == "int":
                            try:
                                p.int_value = o["parameters"][parampath[0]]
                            except:
                                print("Int assignment error: probably a template issue")
                        elif propertyType == "bool":
                            p.bool_value = o["parameters"][parampath[0]]
                        elif propertyType == "vector":
                            p.vector_value = o["parameters"][parampath[0]]
                        elif propertyType == "string":
                            p.string_value = o["parameters"][parampath[0]]
                    elif len(parampath) == 3:
                        if parampath[0].endswith("]"):
                            if propertyType == "float":
                                p.float_value = o["parameters"][parampath[0][:parampath[0].find("[")]][int(parampath[0][parampath[0].find("[") + 1:-1])][parampath[1]]
                            elif propertyType == "enum":
                                for e in p.enum_items:
                                    if e.value == o["parameters"][parampath[0][:parampath[0].find("[")]][int(parampath[0][parampath[0].find("[") + 1:-1])][parampath[1]]:
                                        e.selected = True
                                    else:
                                        e.selected = False
                            elif propertyType == "int":
                                try:
                                    p.int_value = o["parameters"][parampath[0]][parampath[1]]
                                except:
                                    print("Int assignment error: probably a template issue")
                            elif propertyType == "bool":
                                p.bool_value = o["parameters"][parampath[0]][parampath[1]]
                            elif propertyType == "vector":
                                p.vector_value = o["parameters"][parampath[0]][parampath[1]]
                            elif propertyType == "string":
                                p.string_value = o["parameters"][parampath[0]][parampath[1]]
                        else:
                            if propertyType == "float":
                                p.float_value = o["parameters"][parampath[0]][parampath[1]]
                            elif propertyType == "enum":
                                for e in p.enum_items:
                                    if e.value == o["parameters"][parampath[0]][parampath[1]]:
                                        e.selected = True
                                    else:
                                        e.selected = False
                            elif propertyType == "int":
                                try:
                                    p.int_value = o["parameters"][parampath[0]][parampath[1]]
                                except:
                                    print("Int assignment error: probably a template issue")
                            elif propertyType == "bool":
                                p.bool_value = o["parameters"][parampath[0]][parampath[1]]
                            elif propertyType == "vector":
                                p.vector_value = o["parameters"][parampath[0]][parampath[1]]
                            elif propertyType == "string":
                                p.string_value = o["parameters"][parampath[0]][parampath[1]]
                    elif len(parampath) == 4:
                        if propertyType == "float":
                            p.float_value = o["parameters"][parampath[0]][parampath[1]][parampath[2]]
                        elif propertyType == "enum":
                            for e in p.enum_items:
                                if e.value == o["parameters"][parampath[0]][parampath[1]][parampath[2]]:
                                    e.selected = True
                                else:
                                    e.selected = False
                        elif propertyType == "int":
                            try:
                                p.int_value = o["parameters"][parampath[0]][parampath[1]][parampath[2]]
                            except:
                                print("Int assignment error: probably a template issue")
                        elif propertyType == "bool":
                            p.bool_value = o["parameters"][parampath[0]][parampath[1]][parampath[2]]
                        elif propertyType == "vector":
                            p.vector_value = o["parameters"][parampath[0]][parampath[1]][parampath[2]]
                        elif propertyType == "string":
                            p.string_value = o["parameters"][parampath[0]][parampath[1]][parampath[2]]
                    else:
                        raise Exception("Parameter Name Error")
            
            for path in range(len(paths)):
                points = ids[paths[path]].data.splines[0].points
                for point in range(len(points)):
                    points[point].co = (pathnodepos[pathnodes[path][point]][0] - ids[paths[path]].location.x, -pathnodepos[pathnodes[path][point]][2] - ids[paths[path]].location.y, pathnodepos[pathnodes[path][point]][1] - ids[paths[path]].location.z, 0.0) 
            geditFile.close()
        
        for o in objectAssets:
            try:
                bpy.data.objects.remove(bpy.data.objects[o], do_unlink=True)
            except:
                pass
        for c in range(len(children)):
            ids[children[c]].parent = ids[parents[c]]
        print(ids)

        return{"FINISHED"}
    
class ImportHeightmap(bpy.types.Operator):
    bl_idname = "qimport.importheightmap"
    bl_label = "Heightmap"
    bl_description = "Imports heightmap"

    def execute(self, context):
        startTime = time.time()
        bpy.types.Scene.heightmapprogress = 0.0
        updateprogress(0.0)

        previoustime = time.time()

        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        directoryTexconv = os.path.abspath(bpy.path.abspath(preferences.directoryTexconv)) # Gets texconv path from preferences
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

        if bpy.context.scene.worldDir == "": # Gives an error if no world directory is sent
            def missingProgramError(self, context):
                self.layout.label(text="No World folder is set") # Sets the popup label

            bpy.context.window_manager.popup_menu(missingProgramError, title = "World folder not set", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation
        mapsize = 4

        worldFolder = os.path.abspath(bpy.path.abspath(bpy.context.scene.worldDir)) # Gets the chosen world folder
        worldId = worldFolder.split("\\")[-1]
        heightfolder = f"{worldFolder}\\{worldId}_trr_height"
        tempfolder = f"{worldFolder}\\levelcreator-temp\\"
        if os.path.exists(tempfolder):
            shutil.rmtree(tempfolder)
        os.mkdir(tempfolder)

        previoustime = time.time()

        tileimgs = []
        os.chdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(directoryTexconv)))}") # Goes to the directory
        for f in os.listdir(heightfolder):
            if f.lower().endswith(".dds") and "heightmap" in f.lower() and not "nrm" in f.lower():
                os.popen(f'texconv -ft png -y "{heightfolder}\\{f}" -o "{tempfolder[:-1]}"').read() # Converts the image via command line
                tileimgs.append(bpy.data.images.load(f"{tempfolder}{f[:-4]}.png", check_existing=True))
                previoustime = time.time()

        with bpy.data.libraries.load(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/heightmapper_resources.blend') as (data_from, data_to):
            if not "[FLC] Composite" in bpy.data.node_groups:
                data_to.node_groups = data_from.node_groups
        
        bpy.context.scene.use_nodes = True
        nodes = bpy.context.scene.node_tree.nodes
        links = bpy.context.scene.node_tree.links

        compositenode = nodes.new('CompositorNodeComposite')
        groupNode = nodes.new(type='CompositorNodeGroup')
        groupNode.node_tree = bpy.data.node_groups["[FLC] Composite"]
        links.new(groupNode.outputs[0], compositenode.inputs[0])
        
        imagenodes = []
        for i in range(16):
            imagenodes.append(nodes.new(type='CompositorNodeImage'))
            imagenodes[-1].image = tileimgs[i]
            links.new(imagenodes[-1].outputs[0], groupNode.inputs[i])
        nodes.active = compositenode
        
        tempcam = bpy.data.objects.new("tempcamobj", bpy.data.cameras.new(name="tempcam"))
        activecam = bpy.context.scene.camera
        bpy.context.scene.camera = tempcam
        bpy.context.scene.collection.objects.link(tempcam)

        color_depth = bpy.context.scene.render.image_settings.color_depth
        bpy.context.scene.render.image_settings.color_depth = '16'
        resolution_x = bpy.context.scene.render.resolution_x
        bpy.context.scene.render.resolution_x = 4096
        resolution_y = bpy.context.scene.render.resolution_y
        bpy.context.scene.render.resolution_y = 4096
        view_transform = bpy.context.scene.view_settings.view_transform
        bpy.context.scene.view_settings.view_transform = 'Standard'

        updateprogress(0.02)

        bpy.ops.render.render(write_still=False)

        updateprogress(0.02)

        bpy.context.scene.camera = activecam
        bpy.data.cameras.remove(bpy.data.cameras[tempcam.data.name])

        for i in imagenodes:
            nodes.remove(i)
        nodes.remove(compositenode)
        nodes.remove(groupNode)
        for i in tileimgs:
            bpy.data.images.remove(i)
        bpy.data.node_groups.remove(bpy.data.node_groups["[FLC] Composite"])

        bpy.data.images["Render Result"].save_render(filepath=f"{tempfolder}Heightmap.png")
        heightmapimg = bpy.data.images.load(f"{tempfolder}Heightmap.png", check_existing=True)
        heightmapimg.colorspace_settings.name = 'Non-Color'

        bpy.context.scene.render.image_settings.color_depth = color_depth
        bpy.context.scene.render.resolution_x = resolution_x
        bpy.context.scene.render.resolution_y = resolution_y
        bpy.context.scene.view_settings.view_transform = view_transform

        updateprogress(0.04)

        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection # Deselects all collections
        try:
            bpy.context.view_layer.objects[0].select_set(True)
            bpy.context.view_layer.objects.active = bpy.context.view_layer.objects[0] # Selects a random object so that object mode can be switched to
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False) # Changes to object mode
        except Exception as e:
            print(e)

        bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0), scale=(1, 1, 1), enter_editmode=True) # Create plane
        plane = bpy.context.selected_objects[0] # Get plane
        plane.name = "[FLC] Heightmap-base" # Rename plane
        bpy.ops.mesh.subdivide(number_cuts=63) # Subdivide plane
        bpy.ops.mesh.subdivide(number_cuts=63)
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False) # Change back to object mode
        bpy.ops.transform.resize(value=(2048, 2048, 2048))

        updateprogress(0.44)

        heighttex = bpy.data.textures.new("[FLC] Heightmap-Tex", type='IMAGE')
        heighttex.image = heightmapimg

        displacemod = plane.modifiers.new("Displace", "DISPLACE") # Adds multires modifier
        displacemod.texture = heighttex
        displacemod.strength = 0.4887025
        displacemod.mid_level = 0.0

        bpy.ops.object.modifier_apply(modifier=displacemod.name)
        bpy.data.textures.remove(heighttex)
        bpy.data.images.remove(heightmapimg)

        updateprogress(0.06)

        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection # Deselects all collections
        try:
            bpy.context.view_layer.objects[0].select_set(True)
            bpy.context.view_layer.objects.active = bpy.context.view_layer.objects[0] # Selects a random object so that object mode can be switched to
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False) # Changes to object mode
        except Exception as e:
            print(e)

        bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0), scale=(mapsize * 1024, mapsize * 1024, mapsize * 1024), enter_editmode=True) # Create plane
        finalheightmap = bpy.context.selected_objects[0] # Get plane
        finalheightmap.name = "[FLC] Heightmap" # Rename plane
        bpy.ops.transform.resize(value=(2048, 2048, 2048))
        bpy.ops.mesh.subdivide(number_cuts=15) # Subdivide plane
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False) # Change back to object mode
        bpy.ops.object.modifier_add(type='MULTIRES') # Adds multires modifier
        for i in range(8):
            bpy.ops.object.multires_subdivide(modifier="Multires", mode='LINEAR') # Subdivides the plane further with multires
        bpy.context.object.modifiers["Multires"].levels = 5 # Sets the LOD for Object mode
        bpy.context.object.modifiers["Multires"].sculpt_levels = 7 # Sets the LOD for Sculpt mode

        updateprogress(0.2)

        shrinkmod = finalheightmap.modifiers.new("Shrinkwrap", "SHRINKWRAP") # Adds multires modifier
        shrinkmod.target = plane
        shrinkmod.use_project_z = True
        shrinkmod.use_negative_direction = True
        shrinkmod.wrap_method = "PROJECT"

        bpy.ops.object.modifier_apply(modifier=shrinkmod.name)

        bpy.data.objects.remove(plane)

        shutil.rmtree(tempfolder)

        updateprogress(0.22)

        bpy.types.Scene.heightmapprogress = 1.0
        bpy.types.Scene.heightmapprogresstext = "DONE"

        print(f"\n\nHEIGHTMAP IMPORT COMPLETE ----------\nTIME ELAPSED: {time.time() - startTime}")

        return{"FINISHED"}

class ImportSplatmap(bpy.types.Operator):
    bl_idname = "qimport.importsplatmap"
    bl_label = "Splatmap"
    bl_description = "Imports splatmap"

    def execute(self, context):
        splatmapdata = bpy.types.Scene.loadedsplatmap
        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        directoryKnuxtools = os.path.abspath(bpy.path.abspath(preferences.directoryKnuxtools)) # Gets KnuxTools path from preferences
        directoryTexconv = os.path.abspath(bpy.path.abspath(preferences.directoryTexconv)) # Gets texconv path from preferences
        directoryHedgearcpack = os.path.abspath(bpy.path.abspath(preferences.directoryHedgearcpack)) # Gets HedgeArcPack path from preferences
        if not "[FLC] Heightmap" in bpy.data.objects:
            return {'FINISHED'}
        if preferences.directoryTexconv == "" or preferences.directoryHedgearcpack == "" or preferences.directoryKnuxtools == "": # Gives an error if a program is missing
            def missingProgramError(self, context):
                missingPrograms = [] # List of missing programs
                if preferences.directoryTexconv == "":
                    missingPrograms.append("texconv.exe")
                if preferences.directoryHedgearcpack == "":
                    missingPrograms.append("HedgeArcPack.exe")
                if preferences.directoryKnuxtools == "":
                    missingPrograms.append("KnuxTools.exe")
                self.layout.label(text=f"The filepath(s) for: {', '.join(missingPrograms)} are not set. \nPlease set the path(s) in Settings.") # Tells the user about the missing prorgrams

            bpy.context.window_manager.popup_menu(missingProgramError, title = "Program missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        worldFolder = os.path.abspath(bpy.path.abspath(bpy.context.scene.worldDir)) # Gets the chosen world folder
        worldId = worldFolder.split("\\")[-1]
        splatmapheightDirectory = f"{worldFolder}\\{worldId}_trr_height"
        splatmapcmnDirectory = f"{worldFolder}\\{worldId}_trr_cmn"
        tempfolder = f"{worldFolder}\\levelcreator-temp\\"
        if os.path.exists(tempfolder):
            shutil.rmtree(tempfolder)
        os.mkdir(tempfolder)

        for f in os.listdir(splatmapheightDirectory):
            if f.lower().endswith(".terrain-material"):
                trrmat = f"{splatmapheightDirectory}\\{f}"
                trrmatjsonfile = f"{trrmat[:-17]}.hedgehog.terrain-material.json"
                break
        
        os.chdir(os.path.dirname(directoryKnuxtools))
        os.popen(f"KnuxTools {trrmat}")

        with open(trrmatjsonfile, "r") as file:
            trrmatjson = json.load(file)
            file.close()
        
        splatmapdata["name"] = trrmat.split("\\")[-1]
        splatmapdata["filepath"] = trrmat

        for t in range(len(trrmatjson)):
            splatmapdata["data"].append({"index": 0, "type": "", "image": ""})
            splatmapdata["data"][-1]["index"] = trrmatjson[t]["Index"]
            splatmapdata["data"][-1]["type"] = trrmatjson[t]["Type"]
            splatmapdata["data"][-1]["image"] = trrmatjson[t]["BaseDiffuse"]

        with bpy.data.libraries.load(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/heightmapper_resources.blend') as (data_from, data_to):
            if not "[FLC] Splatmap" in bpy.data.node_groups:
                data_to.node_groups = data_from.node_groups
        
        material = bpy.data.materials.new("[FLC] Splatmap")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        for i in nodes:
            nodes.remove(i)
        
        outputnode = nodes.new('ShaderNodeOutputMaterial')

        splatmapnode = nodes.new('ShaderNodeTexImage')
        splatmapnode.image = None
        splatmapnode.interpolation = "Closest"
        splatmapnode.name = "SplatNode"
        missingnode = nodes.new('ShaderNodeTexImage')
        missingnode.image = bpy.data.images.load(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/missing.png', check_existing=True)
        missingnode.interpolation = "Closest"

        baseinput = missingnode.outputs[0]
        for d in splatmapdata["data"]:
            groupNode = nodes.new(type='ShaderNodeGroup')
            groupNode.node_tree = bpy.data.node_groups["[FLC] Splatmap"]
            groupNode.inputs[3].default_value = d["index"]
            links.new(baseinput, groupNode.inputs[2])
            baseinput = groupNode.outputs[0]
            trrtexnode = nodes.new('ShaderNodeTexImage')
            trrtexnode.image = bpy.data.images.load(f'{splatmapheightDirectory}\\{d["image"]}.dds', check_existing=True)
            mappingNode = nodes.new(type='ShaderNodeMapping')
            mappingNode.inputs[3].default_value[0] = 512
            mappingNode.inputs[3].default_value[1] = 512
            mappingNode.inputs[3].default_value[2] = 512
            coordNode = nodes.new(type='ShaderNodeTexCoord')
            links.new(splatmapnode.outputs[0], groupNode.inputs[0])
            links.new(trrtexnode.outputs[0], groupNode.inputs[1])
            links.new(coordNode.outputs[2], mappingNode.inputs[0])
            links.new(mappingNode.outputs[0], trrtexnode.inputs[0])
        links.new(baseinput, outputnode.inputs[0])

        scalemat = bpy.data.materials.new("[FLC] Scale")
        scalemat.use_nodes = True
        nodes = scalemat.node_tree.nodes
        for i in nodes:
            nodes.remove(i)
        outputnode = nodes.new('ShaderNodeOutputMaterial')
        imgnode = nodes.new('ShaderNodeTexImage')
        imgnode.image = None
        imgnode.name = "scale"
        scalemat.node_tree.links.new(imgnode.outputs[0], outputnode.inputs[0])

        areamat = bpy.data.materials.new("[FLC] Area")
        areamat.use_nodes = True
        nodes = areamat.node_tree.nodes
        for i in nodes:
            nodes.remove(i)
        outputnode = nodes.new('ShaderNodeOutputMaterial')
        imgnode = nodes.new('ShaderNodeTexImage')
        imgnode.image = None
        imgnode.name = "area"
        areamat.node_tree.links.new(imgnode.outputs[0], outputnode.inputs[0])


        bpy.context.view_layer.objects.active.data.materials.append(bpy.data.materials["[FLC] Splatmap"])
        bpy.context.view_layer.objects.active.data.materials[0] = bpy.data.materials["[FLC] Splatmap"]
        for f in os.listdir(os.path.abspath(bpy.path.abspath(splatmapcmnDirectory))):
            if f.endswith("splatmap.dds"):
                splatmapimg = bpy.data.images.load(f"{splatmapcmnDirectory}\\{f}", check_existing = True)
                splatmapimg.name = "[FLC] Splatmap"
            if f.endswith("scale.dds"):
                scaleimg = bpy.data.images.load(f"{splatmapcmnDirectory}\\{f}", check_existing = True)
                scaleimg.name = "[FLC] Scale"
            if f.endswith("area.dds"):
                areaimg = bpy.data.images.load(f"{splatmapcmnDirectory}\\{f}", check_existing = True)
                areaimg.name = "[FLC] Area"

        bpy.data.materials["[FLC] Splatmap"].node_tree.nodes["SplatNode"].image = splatmapimg
        bpy.data.materials["[FLC] Splatmap"].node_tree.nodes["SplatNode"].image.colorspace_settings.name = "Non-Color"
        bpy.data.materials["[FLC] Scale"].node_tree.nodes["scale"].image = scaleimg
        bpy.data.materials["[FLC] Area"].node_tree.nodes["area"].image = areaimg

        return {'FINISHED'}
    
class ImportDensity(bpy.types.Operator):
    bl_idname = "qimport.importdensity"
    bl_label = "Density"
    bl_description = "Imports density"

    def execute(self, context):
        return {'FINISHED'}
    
class SettingsImp(bpy.types.Operator):
    bl_idname = "qimport.settings"
    bl_label = "Settings"
    bl_description = "Addon Settings"

    def execute(self, context):
        bpy.ops.screen.userpref_show()
        bpy.context.preferences.active_section = 'ADDONS'

        bpy.data.window_managers["WinMan"].addon_search = "Frontiers Level Creator"

        bpy.ops.preferences.addon_expand(module = __name__.split(".")[0])
        bpy.ops.preferences.addon_show(module = __name__.split(".")[0])

        return{"FINISHED"}

class QimportSettings(bpy.types.PropertyGroup): # Other settings
    bpy.types.Scene.worldDir = bpy.props.StringProperty( 
        name="World Folder",
        subtype='DIR_PATH',
        default="",
        description="Path to the folder to be imported"
    )