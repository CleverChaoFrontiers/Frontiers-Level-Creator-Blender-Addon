import bpy # type: ignore (Supresses the warning associated with it being a Blender library)
import os
import shutil
import json
import random
import textwrap
import mathutils # type: ignore
import math
import bmesh # type: ignore
import datetime, time, uuid
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
    if "OTHER" in keepFiles:
        for f in range(len(files)): # For every file/folder
            if os.path.isfile(f"{filepath}\\{files[f]}"): # Only if is file, not folder
                if not files[f].split(".")[-1].lower() in keepFiles and files[f].split(".")[-1].lower() in ["terrain-model", "btmesh", "gedit", "densitypointcloud", "densitysetting", "dds", "uv-anim", "pcmodel", "pccol"]: # If the file extension is not in the list of extensions to be kept
                    os.remove(f"{filepath}\\{files[f]}") # Removes file
    else:
        for f in range(len(files)): # For every file/folder
            if os.path.isfile(f"{filepath}\\{files[f]}"): # Only if is file, not folder
                if not files[f].split(".")[-1].lower() in keepFiles: # If the file extension is not in the list of extensions to be kept
                    os.remove(f"{filepath}\\{files[f]}") # Removes file

def updateprogress(advance, name, milestone):
    if (4, 0, 0) < bpy.app.version:
        bpy.types.Scene.exportprogress =  bpy.types.Scene.exportprogress + advance
        bpy.types.Scene.exportprogresstext = f"{name} ({round(bpy.types.Scene.exportprogress * 100)}%)"
        if bpy.types.Scene.exportprogress >= milestone:
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            milestone = (math.floor(bpy.types.Scene.exportprogress * 10) / 10) + 0.1
        return milestone

# New Terrain Functions - - - - - - - - - - - - -

def generalerror(title, error): # Function to call an error and halt the program e.g. generalerror("File Not Found", "The file could not be found!")
    def generalerrormessage(self, context): # Creates the error box
        self.layout.label(text=error) # Sets the text
    bpy.context.window_manager.popup_menu(generalerrormessage, title=title, icon="ERROR") # Makes the popup appear

def endwarning(current, message, priority): # Function to register a warning that will be displayed at the end
    # current is the existing list of errors - has the structure [[priority 0 messages], [priority 1], [2], ... [4]], 0 is highest priority and 4 is the lowest 
    # message is the message that will be displayed
    # priority is how severe the warning is

    current[priority].append(f"[{priority}] : {message}")
    return current

def printconsole(currentlog, text, level): # Print different amounts of information depending on the level of debug data that needs to be printed
    # currentlog is the existing log
    # text is the text to be printed
    # level is debug level

    if level <= bpy.context.scene.debuglevel:
        print(text)
    
        if bpy.context.scene.debuglog == True:
            currentlog.append(text)
            return currentlog
        else:
            return currentlog

def verifyprogram(missinglist, invalidlist, path, programname):
    if path == "": # If filepath is not set
        missinglist.append(programname)
    elif (not os.path.exists(path)) or (not path.lower().endswith(programname.lower())): # If filepath is missing or is not a program
        invalidlist.append(programname)
    return missinglist, invalidlist

def packcheck(path, directoryhedgearcpack, halt, warnings):
    # path is the .pac that should be checked if it is unpacked
    # halt is whether the program should be stopped if the .pac is not found
    # warnings passes in the current list of endwarnings

    if os.path.exists(path): # If the pac exists
        if os.path.exists(f"{path.replace('.pac', '')}\\"): # If the pac has already been extracted
            pass
        else:
            os.chdir(os.path.dirname(directoryhedgearcpack)) # Switch to the directory HedgeArcPack is in
            os.popen(f'HedgeArcPack "{path}"').read() # Attempt to extract the .pac
            
            if not os.path.exists(f"{path.replace('.pac', '')}\\"): # If the unpack failed, halt the program regardless
                generalerror("Unpack failed", f"{path} could not be unpacked")
    else:
        if halt == True:
            generalerror("Missing .pac", f"{path} could not be found") # Halt the program
        else:
            warnings = endwarning(warnings, f"{path} could not be found, skipped", 2) # Warn the user at the end
    return warnings

def clearfolder2(path):
    clearfiles = []
    if bpy.context.scene.exptrr in ["clear"]:
        clearfiles.append("terrain-model")
    if bpy.context.scene.expcol in ["clear"]:
        clearfiles.append("btmesh")
    if bpy.context.scene.expmat in ["clear"]:
        clearfiles.append("material")
    if bpy.context.scene.expdds in ["clear"]:
        clearfiles.append("dds")
    if bpy.context.scene.expuva in ["clear"]:
        clearfiles.append("uv-anim")
    if bpy.context.scene.exppcm in ["clear"]:
        clearfiles.append("pcmodel")
    if bpy.context.scene.exppcl in ["clear"]:
        clearfiles.append("pccol")

    for f in os.listdir(path):
        if f.split(".")[-1] in clearfiles:
            os.remove(f"{path}\\{f}")
        elif bpy.context.scene.expmsc == "clear" and (not f.split(".")[-1] in ["rfl", "txt", "level"]):
            os.remove(f"{path}\\{f}")

def transferfile(location, destination):
    overwritefiles = []
    if bpy.context.scene.exptrr in ["write"]:
        overwritefiles.append("terrain-model")
    if bpy.context.scene.expcol in ["write"]:
        overwritefiles.append("btmesh")
    if bpy.context.scene.expmat in ["write"]:
        overwritefiles.append("material")
    if bpy.context.scene.expdds in ["write"]:
        overwritefiles.append("dds")
    if bpy.context.scene.expuva in ["write"]:
        overwritefiles.append("uv-anim")
    if bpy.context.scene.exppcm in ["write"]:
        overwritefiles.append("pcmodel")
    if bpy.context.scene.exppcl in ["write"]:
        overwritefiles.append("pccol")
    
    if location.split(".")[-1].lower() in overwritefiles:
        shutil.copy2(location, destination)
    elif bpy.context.scene.expmsc == "write":
        shutil.copy2(location, destination)
    elif not os.path.exists(destination):
        shutil.copy2(location, destination)

# Transform conversion functions
def posblend2he(positioninput): # Conversion function from Blender XYZ to HE2 XYZ
    position = list(positioninput) # Allows the function to accept both arrays and lists

    positionoutput = [position[0], position[2], -position[1]] # Keep X, swap Y and Z, flip the *new* Z
    return positionoutput

def erotblend2he(rotationinput): # Conversion function from Blender XYZ Euler to HE2 XYZ Euler (RADIANS IN, DEGREES OUT)
    rotation = list(rotationinput)

    rotationoutput = [rotation[0], rotation[2], -rotation[1]] # Keep X, swap Y and Z, flip the *new* Z
    return rotationoutput

def qrotblend2he(rotationinput): # Conversion function from Blender XYZ Euler to HE2 XYZW Quaternion (RADIANS IN, RADIANS OUT)
    rotation = mathutils.Euler(list(rotationinput)).to_quaternion()

    rotationoutput = [rotation[1], rotation[3], -rotation[2], rotation[0]] # X first, swap Y and Z, flip the *new* Z, W last

def sclblend2he(scaleinput): # Conversion function from Blender XYZ to HE2 XYZ
    scale = list(scaleinput) # Allows the function to accept both arrays and lists

    scaleoutput = [scale[0], scale[2], scale[1]] # Keep X, swap Y and Z
    return scaleoutput

# PointCloud adding functions
def addpointcloudmodel(pcmodel, name, pos, rot, scale):
    instance = {"UnknownUInt32_1": 1,
                "InstanceName": "",
                "AssetName": "",
                "Position": {"X": 0, "Y": 0, "Z": 0},
                "Rotation": {"X": 0, "Y": 0, "Z": 0},
                "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}}
    instance["InstanceName"] = f"{name}_model_{str(uuid.uuid4())}"
    instance["AssetName"] = name
    instance["Position"]["X"] = posblend2he(pos)[0]
    instance["Position"]["Y"] = posblend2he(pos)[1]
    instance["Position"]["Z"] = posblend2he(pos)[2]
    instance["Rotation"]["X"] = erotblend2he(rot)[0]
    instance["Rotation"]["Y"] = erotblend2he(rot)[1]
    instance["Rotation"]["Z"] = erotblend2he(rot)[2]
    instance["Scale"]["X"] = sclblend2he(scale)[0]
    instance["Scale"]["Y"] = sclblend2he(scale)[1]
    instance["Scale"]["Z"] = sclblend2he(scale)[2]
    pcmodel.append(instance)
    return pcmodel

def addpointcloudcollision(pccol, name, pos, rot, scale):
    instance = {"UnknownUInt32_1": 1,
                "InstanceName": "",
                "AssetName": "",
                "Position": {"X": 0, "Y": 0, "Z": 0},
                "Rotation": {"X": 0, "Y": 0, "Z": 0},
                "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}}
    instance["InstanceName"] = f"{name}_col_{str(uuid.uuid4())}"
    instance["AssetName"] = f"{name}"
    instance["Position"]["X"] = posblend2he(pos)[0]
    instance["Position"]["Y"] = posblend2he(pos)[1]
    instance["Position"]["Z"] = posblend2he(pos)[2]
    instance["Rotation"]["X"] = erotblend2he(rot)[0]
    instance["Rotation"]["Y"] = erotblend2he(rot)[1]
    instance["Rotation"]["Z"] = erotblend2he(rot)[2]
    instance["Scale"]["X"] = sclblend2he(scale)[0]
    instance["Scale"]["Y"] = sclblend2he(scale)[1]
    instance["Scale"]["Z"] = sclblend2he(scale)[2]
    pccol.append(instance)
    return pccol

class CompleteExport(bpy.types.Operator):
    bl_idname = "qexport.completeexport"
    bl_label = "Complete Export"
    bl_description = "Exports Terrain, Objects and Heightmap"

    def parameter_menu(self, obj, hson_temp):
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
                elif parameter.object_value != None and parameter.object_value.name in bpy.data.objects and "DataID" not in parameter.object_value and parameter.object_value.type != "CURVE":
                    parameter.object_value["DataID"] = self.ID_generator()
                    IDstring = "{"+parameter.object_value["DataID"]+"}"
                    PropertyValue = IDstring
                elif parameter.object_value != None and parameter.object_value.name in bpy.data.objects and "UID" not in parameter.object_value and parameter.object_value.type == "CURVE":
                    parameter.object_value["UID"] = str(random.randint(5000, 200000))
                    UIDstring = "SetPath_"+ parameter.object_value["UID"]
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
                print(f'for object {obj.name},Attribute:{PropertyName} was passed for being incompatible in current version.')
                continue
            CurrentLevel = hson_temp["parameters"]
            
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
        ExportSplatmap.execute(self, context)
        ExportDensity.execute(self, context)
        self.report({"INFO"}, f"Quick Export Finished")
        return{"FINISHED"}
    
class ExportTerrain(bpy.types.Operator):
    bl_idname = "qexport.exportterrain"
    bl_label = "Terrain"
    bl_description = "Exports your level's terrain, collision, materials and textures"

    def execute(self, context):
        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences

        currentlog = [] # The list of lines on the debug log
        currentlog = printconsole(currentlog, "Starting Export", 1)
        currentlog = printconsole(currentlog, f"Blender {'.'.join([str(n) for n in bpy.app.version])}", 2) # Prints Blender version
        currentlog = printconsole(currentlog, f"Internal Tools: {preferences.blendhog_sharptoggle}", 2)
        currentlog = printconsole(currentlog, f"Terrain: {bpy.context.scene.exptrr}, Collision: {bpy.context.scene.expcol}, Materials: {bpy.context.scene.expmat}, Textures: {bpy.context.scene.expdds}, UV-anim: {bpy.context.scene.expuva}, pcmodel: {bpy.context.scene.exppcm}, pccol: {bpy.context.scene.exppcl}", 2)

        endwarnings = [[], [], [], [], []]

        directorymodelconverter = os.path.abspath(bpy.path.abspath(preferences.directoryModelconverter)) # Gets ModelConverter path from preferences
        directorybtmesh = os.path.abspath(bpy.path.abspath(preferences.directoryBtmesh)) # Gets btmesh path from preferences
        directoryknuxtools = os.path.abspath(bpy.path.abspath(preferences.directoryKnuxtools)) # Gets KnuxTools path from preferences
        directoryhedgearcpack = os.path.abspath(bpy.path.abspath(preferences.directoryHedgearcpack)) # Gets HedgeArcPack path from preferences
        directorytexconv = os.path.abspath(bpy.path.abspath(preferences.directoryTexconv)) # Gets texconv path from preferences

        absolutemoddir = os.path.abspath(bpy.path.abspath(bpy.context.scene.modDir)) # Gets mod folder directory
        worldid = bpy.context.scene.worldId # Gets the world ID to be edited
        currentlog = printconsole(currentlog, f"Mod Directory: {absolutemoddir}\nWorld ID: {worldid}", 3)

        missinglist = [] # List of missing programs
        invalidlist = [] # List of invalid programs
        if preferences.blendhog_sharptoggle == False:
            # Check which programs are missing or invalid, if Internal Tools is disabled
            currentlog = printconsole(currentlog, "Validating Tool Filepaths", 2)

            setfilepaths = [preferences.directoryModelconverter, preferences.directoryBtmesh, preferences.directoryKnuxtools, preferences.directoryHedgearcpack, preferences.directoryTexconv] # Creates a list of the tool filepaths
            programnames = ["ModelConverter.exe", "btmesh.exe", "KnuxTools.exe", "HedgeArcPack.exe","texconv.exe"] # List of tool names
            for program in range(len(setfilepaths)): # For every program
                currentlog = printconsole(currentlog, f"Validating Tool Filepath: {setfilepaths[program]} for {programnames[program]}", 3)

                missinglist, invalidlist = verifyprogram(missinglist, invalidlist, setfilepaths[program], programnames[program]) # Validate each program
        else:
            # Check which programs are missing, if Internal Tools is enabled
            currentlog = printconsole(currentlog, "Validating Tool Filepaths", 2)

            setfilepaths = [preferences.directoryModelconverter, preferences.directoryBtmesh, preferences.directoryKnuxtools, preferences.directoryHedgearcpack, preferences.directoryTexconv] # Creates a list of the tool filepaths
            programnames = ["ModelConverter.exe", "btmesh.exe", "KnuxTools.exe", "HedgeArcPack.exe","texconv.exe"] # List of tool names
            for program in range(len(setfilepaths)): # For every program
                currentlog = printconsole(currentlog, f"Validating Tool Filepath: {setfilepaths[program]} for {programnames[program]}", 3)

                missinglist, invalidlist = verifyprogram(missinglist, invalidlist, setfilepaths[program], programnames[program]) # Validate each program
        
        # If programs are missing or invalid, show a pop-up error and halt the program
        if missinglist != [] and invalidlist != []:
            generalerror("Program(s) Missing", f"Filepaths for program(s) {', '.join(missinglist)} are missing, and filepaths for program(s) {','.join(invalidlist)} are invalid")
            return{"FINISHED"}
        elif missinglist != []:
            generalerror("Program(s) Missing", f"Filepaths for program(s) {', '.join(missinglist)} are missing")
            return{"FINISHED"}
        elif invalidlist != []:
            generalerror("Program(s) Missing", f"Filepaths for program(s) {', '.join(invalidlist)} are invalid")
            return{"FINISHED"}
        

        # Other checks
        if bpy.context.scene.modDir == "":
            generalerror("Missing Mod Directory", "The mod's directory has not been set")
            return{"FINISHED"}
        
        if "mod.ini" not in os.listdir(absolutemoddir):
            generalerror("Invalid Mod Directory", "The mod's directory may be invalid, make sure to select the root mod directory")
            return{"FINISHED"}
        
        if not os.path.exists(f"{absolutemoddir}\\raw\\stage\\{worldid}"):
            generalerror("Missing Mod Directory", f"{absolutemoddir}\\raw\\stage\\{worldid} is missing")
            return{"FINISHED"}
        
        if bpy.context.scene.trrCollection == None:
            generalerror("No Collection Selected", "Please select a terrain collections")
            return{"FINISHED"}

        # Unpacking files
        for f in [f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_trr_s00.pac", f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_misc.pac"]: # For each essential .pac
            currentlog = printconsole(currentlog, f"Checking {f}", 2)
            packcheck(f, directoryhedgearcpack, True, endwarnings) # Make sure the .pac exists and is extracted, halt if it fails
            if not os.path.exists(f"{f.replace('.pac', '')}\\"):
                return{"FINISHED"}
            currentlog = printconsole(currentlog, f"{f} unpacked", 2)

        for f in []: # For each recommended .pac
            currentlog = printconsole(currentlog, f"Checking {f}", 2)
            packcheck(f, directoryhedgearcpack, False, endwarnings) # Make sure the .pac exists and is extracted
            currentlog = printconsole(currentlog, f"{f} unpacked", 2)

        
        # I hate bpy.ops and I know it's inefficient and context-dependent, but I'm stuck with this until it's possible to export FBX without ops
        currentlog = printconsole(currentlog, "Ensuring an object is selected", 3)
        if bpy.context.view_layer.objects.active == None: # If no object is selected
            currentlog = printconsole(currentlog, "No object is selected", 3)
            for o in bpy.data.objects:
                bpy.context.view_layer.objects.active = o # Select the first object
                currentlog = printconsole(currentlog, "Object is now selected", 3)
                break
        try:
            bpy.ops.object.mode_set(mode = 'OBJECT') # Try to switch to object mode
            currentlog = printconsole(currentlog, "Switched to object mode", 3)
        except RuntimeError:
            currentlog = printconsole(currentlog, "Failed to switch to object mode", 3)
            pass

        if os.path.exists(f"{absolutemoddir}\\levelcreator-temp"):
            shutil.rmtree(f"{absolutemoddir}\\levelcreator-temp") # Remove the temp folder if it still exists
            currentlog = printconsole(currentlog, "Removed leftover temp folder", 2)

        os.mkdir(f"{absolutemoddir}\\levelcreator-temp") # Create a new temp folder
        if os.path.exists(f"{absolutemoddir}\\levelcreator-temp"):
            currentlog = printconsole(currentlog, f"Temp folder created at {absolutemoddir}\\levelcreator-temp", 2)
        else:
            generalerror("Temp folder not created", f"A temporary folder could not be created at {absolutemoddir}\\levelcreator-temp")
            return{"FINISHED"}

        pcmodelinstances = [] # Model PointCloud instances
        pccolinstances = [] # Collision PointCloud instances
        images = []
        models = {} # List of collections/terrain-models

        # Puts the main terrain collection and two layers of sub-collections within one list
        collections = [bpy.context.scene.trrCollection]
        collections.extend(bpy.context.scene.trrCollection.children)
        
        currentlog = printconsole(currentlog, f"Detected collections:\n{', '.join(c.name for c in collections)}", 2)

        for c in collections:
            currentlog = printconsole(currentlog, f"Processing {c.name}", 1)

            if "Full Name" in c: # Certain imported collections have names that are too long, which may be stored as data inside the collection
                modelname = c["Full Name"].replace(' ', '_').replace('.', '_') # Fetches the data in the collection
            else:
                modelname = c.name.replace(' ', '_').replace('.', '_') # Gets the regular name

            modeltags = {"instonly": False, "novis": False, "nocol": False} # Tags relating to PointCloud instances, checks for each tag and removes it if present
            if c.name.lower().startswith("instonly_"):
                modeltags["instonly"] = True
                modelname = modelname[9:]
            if c.name.lower().endswith("_novis"):
                modeltags["novis"] = True
                modelname = modelname[:-6]
            if c.name.lower().endswith("_nocol"):
                modeltags["nocol"] = True
                modelname = modelname[:-6]
            
            models[modelname] = modeltags # Assigns the tag data to the model name

            if not modeltags["instonly"]:
                if not modeltags["novis"]:
                    pcmodelinstances = addpointcloudmodel(pcmodelinstances, modelname, [0, 0, 0], [0, 0, 0], [1, 1, 1])
                if not modeltags["nocol"]:
                    pccolinstances = addpointcloudcollision(pccolinstances, modelname, [0, 0, 0], [0, 0, 0], [1, 1, 1])

            bpy.ops.object.select_all(action='DESELECT') # Deselects all the objects
            for o in c.objects:
                if "FrontiersAsset" in o: # If a Blendhog asset is found
                    currentlog = printconsole(currentlog, f"FrontiersAsset {o.name} found", 3)
                    endwarnings = endwarning(endwarnings, f"Level Creator object found in {c.name}: {o.name}, skipped", 3)
                    continue # Skip the object
                elif o.name.lower().startswith("inst("):
                    currentlog = printconsole(currentlog, f"Instance {o.name} found", 2)
                    instsettings = o.name.split(".")[0][5:-1] # Get rid of the INST()
                    instsettings = instsettings.split(",") # Split up into parameters
                    instsettings[0] = instsettings[0].replace('"', '').replace("'", "") # Get rid of quotes
                    if len(instsettings) > 1:
                        instsettings[1] = instsettings[1].replace(" ", "") # Get rid of spaces
                    else:
                        instsettings.append("")

                    oldrotatemode = o.rotation_mode # Logs the old rotation mode
                    o.rotation_mode = "XZY" # Switches to XZY rotation
                    if instsettings[1].lower() != "collision":
                        pcmodelinstances = addpointcloudmodel(pcmodelinstances, instsettings[0], o.location, o.rotation_euler, o.scale)
                    if instsettings[1].lower() != "visual":
                        pccolinstances = addpointcloudcollision(pccolinstances, instsettings[0], o.location, o.rotation_euler, o.scale)
                    o.rotation_mode = oldrotatemode

                    currentlog = printconsole(currentlog, f"Instance settings: {instsettings}", 3)
                else:
                    currentlog = printconsole(currentlog, f"Mesh {o.name} selected", 3)
                    o.select_set(True) # Selects the object, and selected objects get exported

                
                # Fix materials
                try: # Check if the object has material slots
                    o.material_slots
                except:
                    continue
                for ms in o.material_slots:
                    currentlog = printconsole(currentlog, f"Checking material {ms.material.name}", 2)
                    if "." in ms.material.name: # If there's a . in the material name
                        endwarnings = endwarning(endwarnings, f"Material {ms.material.name} had a '.' in the name, a fix has been attempted", 2)
                        if ms.material.name.split(".")[0] in bpy.data.materials:
                            ms.material = bpy.data.materials[ms.material.name.split(".")[0]] # Try to replace it with the original copy of the material
                            currentlog = printconsole(currentlog, f"Material corrected", 3)
                    if ms.material.use_nodes == True:
                        if bpy.context.scene.expdds != "keep":
                            nodes = ms.material.node_tree.nodes # Gets all the shader nodes of the material
                            foundtex = False # Check if a texture has been found
                            for n in nodes:
                                if n.type == "TEX_IMAGE":
                                    if n.image == None:
                                        if bpy.context.scene.expmat != "keep":
                                            endwarnings = endwarning(endwarnings, f"Material {ms.material.name} has an empty texture, this may cause issues", 2)
                                        continue
                                    foundtex = True
                                    image = n.image
                                    if image.packed_file != None: # If the image is packed in the file
                                        currentlog = printconsole(currentlog, f"Image {image.name} is packed", 3)
                                        image.file_format = "PNG" # Convert to .png
                                        image.save(filepath=f"{absolutemoddir}\\levelcreator-temp\\{image.name.split('.')[0]}.png") # Save the image externally
                                        if not f"{absolutemoddir}\\levelcreator-temp\\{image.name.split('.')[0]}.png" in images:
                                            images.append(f"{absolutemoddir}\\levelcreator-temp\\{image.name.split('.')[0]}.png") # Log the image
                                        else:
                                            currentlog = printconsole(currentlog, f"Image {image.name} already logged", 3)
                                    else:
                                        currentlog = printconsole(currentlog, f"Image {image.name} is not packed", 3)
                                        if not os.path.abspath(bpy.path.abspath(image.filepath)) in images:
                                            images.append(os.path.abspath(bpy.path.abspath(image.filepath))) # Log the image
                                        else:
                                            currentlog = printconsole(currentlog, f"Image {image.name} already logged", 3)
                            if foundtex == False:
                                if bpy.context.scene.expmat != "keep":
                                    endwarnings = endwarning(endwarnings, f"Material {ms.material.name} has no texture, this may cause issues", 2)
                    else:
                        if bpy.context.scene.expmat != "keep":
                            endwarnings = endwarning(endwarnings, f"Material {ms.material.name} does not use nodes, this may cause issues", 2)

            # Export selected objects with correct scale, including hidden objects
            currentlog = printconsole(currentlog, f"Exporting {c.name}", 1)
            bpy.ops.export_scene.fbx(filepath=f"{absolutemoddir}\\levelcreator-temp\\{modelname}.fbx", use_selection=True, apply_scale_options='FBX_SCALE_UNITS', use_visible=False, add_leaf_bones=False, mesh_smooth_type='FACE')
            if not os.path.exists(f"{absolutemoddir}\\levelcreator-temp\\{modelname}.fbx"):
                generalerror("Model Export Failed", f"Collection {c.name} could not be exported as FBX")
                return{"FINISHED"}
        
        existingtextures = [] # If add is enabled, existing textures will not be converted
        if bpy.context.scene.expdds == "add":
            currentlog = printconsole(currentlog, f"Checking for existing textures", 2)
            for f in os.listdir(f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_trr_s00\\"):
                if f.lower().endswith(".dds"):
                    currentlog = printconsole(currentlog, f"Exising texture {f} found", 3)
                    existingtextures.append(f.split(".")[0])

        for pac in [f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_trr_s00\\", f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_misc\\"]:
            currentlog = printconsole(currentlog, f"Clearing folder {pac}", 2)
            clearfolder2(pac) # Clear trr_s00 and misc

        os.chdir(os.path.dirname(directorymodelconverter))
        for name, data in models.items():
            if not data["novis"]and bpy.context.scene.exptrr != "keep": # If not NoVis
                currentlog = printconsole(currentlog, f"Converting {absolutemoddir}\\levelcreator-temp\\{name}.fbx to terrain-model", 2)
                os.popen(f'ModelConverter --frontiers "{absolutemoddir}\\levelcreator-temp\\{name}.fbx" "{absolutemoddir}\\levelcreator-temp\\{name}.terrain-model"').read() # Convert to terrain-model
                if os.path.exists(f"{absolutemoddir}\\levelcreator-temp\\{name}.terrain-model"):
                    transferfile(f"{absolutemoddir}\\levelcreator-temp\\{name}.terrain-model", f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_trr_s00\\{name}.terrain-model")
                else:
                    generalerror("Model Converting Failed", f"{name}.fbx could not be converted to terrain-model")
        
        os.chdir(os.path.dirname(directorybtmesh))
        for name, data in models.items():
            if not data["nocol"] and bpy.context.scene.expcol != "keep": # If not NoCol
                currentlog = printconsole(currentlog, f"Converting {absolutemoddir}\\levelcreator-temp\\{name}.fbx to btmesh", 2)
                os.popen(f'btmesh "{absolutemoddir}\\levelcreator-temp\\{name}.fbx"').read() # Convert to btmesh
                if os.path.exists(f"{absolutemoddir}\\levelcreator-temp\\{name}_col.btmesh"):
                    transferfile(f"{absolutemoddir}\\levelcreator-temp\\{name}_col.btmesh", f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_misc\\{name}_col.btmesh")
                else:
                    generalerror("Model Converting Failed", f"{name}.fbx could not be converted to btmesh")

        if os.path.exists(f"{absolutemoddir}\\levelcreator-temp\\flist.txt"):
            os.remove(f"{absolutemoddir}\\levelcreator-temp\\flist.txt")

        writetolist = [] # List of files texconv needs to convert

        for i in images:
            currentlog = printconsole(currentlog, f"Checking logged image {i}", 3)
            if i.split(".")[-1].lower() == "dds":
                currentlog = printconsole(currentlog, f"Already dds", 3)
                imagename = i.split("\\")[-1]
                transferfile(i, f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_trr_s00\\{imagename}") # Copy the file over if it's already dds
            else:
                currentlog = printconsole(currentlog, f"To be converted", 3)
                writetolist.append(i) # If not dds, log it for conversion
        
        if writetolist != []:
            writetolist = [x for x in writetolist if x not in existingtextures]
            currentlog = printconsole(currentlog, f"writetolist:\n {writetolist}", 2)
            texconvlist = open(f"{absolutemoddir}\\levelcreator-temp\\flist.txt", "x") 
            texconvlist.write("\n".join(writetolist)) # Write conversion list to a file
            texconvlist.close()

            currentlog = printconsole(currentlog, f"Converting textures", 2)
            os.chdir(f"{absolutemoddir}\\levelcreator-temp")
            print(os.popen(f'"{directorytexconv}" -flist "{absolutemoddir}\\levelcreator-temp\\flist.txt" -y -f BC7_UNORM').read()) # Convert the files
        
        if os.path.exists(f"{absolutemoddir}\\levelcreator-temp\\{bpy.context.scene.trrCollection.name}.hedgehog.pointcloud.json"):
            os.remove(f"{absolutemoddir}\\levelcreator-temp\\{bpy.context.scene.trrCollection.name}.hedgehog.pointcloud.json")
        pcmodel = open(f"{absolutemoddir}\\levelcreator-temp\\{bpy.context.scene.trrCollection.name}.hedgehog.pointcloud.json", "x") # Create a pcmodel template
        pcmodel.write(json.dumps(pcmodelinstances, indent=2)) # Write pcmodel data
        pcmodel.close()

        if os.path.exists(f"{absolutemoddir}\\levelcreator-temp\\{bpy.context.scene.trrCollection.name}_col.hedgehog.pointcloud.json"):
            os.remove(f"{absolutemoddir}\\levelcreator-temp\\{bpy.context.scene.trrCollection.name}_col.hedgehog.pointcloud.json")
        pccol = open(f"{absolutemoddir}\\levelcreator-temp\\{bpy.context.scene.trrCollection.name}_col.hedgehog.pointcloud.json", "x") # Create a pccol template
        pccol.write(json.dumps(pccolinstances, indent=2)) # Write pccol data
        pccol.close()

        # Convert templates
        os.chdir(os.path.dirname(directoryknuxtools))
        os.popen(f'knuxtools "{absolutemoddir}\\levelcreator-temp\\{bpy.context.scene.trrCollection.name}.hedgehog.pointcloud.json" -e=pcmodel').read()
        os.popen(f'knuxtools "{absolutemoddir}\\levelcreator-temp\\{bpy.context.scene.trrCollection.name}_col.hedgehog.pointcloud.json" -e=pccol').read()

        if not os.path.exists(f"{absolutemoddir}\\levelcreator-temp\\{bpy.context.scene.trrCollection.name}.pcmodel") or not os.path.exists(f"{absolutemoddir}\\levelcreator-temp\\{bpy.context.scene.trrCollection.name}_col.pccol"):
            generalerror("KnuxTools broken", "KnuxTools may not be working on your device, try building the source code manually.")

        if bpy.context.scene.exppcm != "keep":
            transferfile(f"{absolutemoddir}\\levelcreator-temp\\{bpy.context.scene.trrCollection.name}.pcmodel", f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_trr_s00\\{bpy.context.scene.trrCollection.name}.pcmodel")
        if bpy.context.scene.exppcl != "keep":
            transferfile(f"{absolutemoddir}\\levelcreator-temp\\{bpy.context.scene.trrCollection.name}_col.pccol", f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_misc\\{bpy.context.scene.trrCollection.name}_col.pccol")

        for f in os.listdir(f"{absolutemoddir}\\levelcreator-temp"):
            if f.split(".")[-1].lower() == "material" and bpy.context.scene.expmat != "keep": # Every material in the temp folder gets transferred
                transferfile(f"{absolutemoddir}\\levelcreator-temp\\{f}", f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_trr_s00\\{f}")
            if f.split(".")[-1].lower() == "dds" and bpy.context.scene.expdds != "keep": # Every texture
                transferfile(f"{absolutemoddir}\\levelcreator-temp\\{f}", f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_trr_s00\\{f}")
        
        os.chdir(os.path.dirname(directoryhedgearcpack))
        for pac in [f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_trr_s00", f"{absolutemoddir}\\raw\\stage\\{worldid}\\{worldid}_misc"]:
            currentlog = printconsole(currentlog, f"Repacking folder {pac}", 2)
            if bpy.context.scene.hedgegameChoice == "shadow":
                print(os.popen(f'hedgearcpack "{pac}" -T=sxsg').read()) # Run hedgearcpack to pack the file for shadow
            else:
                print(os.popen(f'hedgearcpack "{pac}" -T=rangers').read()) # Run hedgearcpack to pack the file
        
        if os.path.exists(f"{absolutemoddir}\\levelcreator-temp"):
            shutil.rmtree(f"{absolutemoddir}\\levelcreator-temp") # Remove the temp folder

        # Finishing up debug features
        currentlog = printconsole(currentlog, f"Writing debug log", 3)
        if bpy.context.scene.debuglog == True:
            logfile = open(f"{absolutemoddir}\\blendhog{bpy.context.scene.debuglevel}_{datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.txt", "x") # Create a timestamped log file with the debug level in the name
            logfile.write("\n".join(currentlog)) # Write to the log file
            logfile.close() # Close the log file
        
        if endwarnings != [[], [], [], [], []]:
            def endwarningmessage(self, context): # Creates the error box
                for tier in endwarnings:
                    for message in tier:
                        self.layout.label(text=message) # Sets the text
            bpy.context.window_manager.popup_menu(endwarningmessage, title="Warnings", icon="QUESTION") # Makes the popup appear
            
        self.report({"INFO"}, f"Quick Export Finished")
        return{"FINISHED"}
    
class ExportObjects(bpy.types.Operator):
    bl_idname = "qexport.exportobjects"
    bl_label = "Objects"
    bl_description = "Exports your level's objects and paths"
    def parameter_menu(self, obj, hson_temp):
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
                if parameter.object_value != None and parameter.object_value.name in bpy.data.objects and parameter.object_value.type != "CURVE":
                    #if object, adds Id if missing
                    if "DataID" not in parameter.object_value:

                        parameter.object_value["DataID"] = self.ID_generator()
                    IDstring = "{"+parameter.object_value["DataID"]+"}"
                    PropertyValue = IDstring
                elif parameter.object_value != None and parameter.object_value.name in bpy.data.objects and parameter.object_value.type == "CURVE":
                    #if curve, Adds UID if missing
                    if "UID" not in parameter.object_value:
                        parameter.object_value["UID"] = str(random.randint(5000, 200000))
                    UIDstring = f"SetPath_"+ str(parameter.object_value["UID"])
                    PropertyValue = UIDstring
                else:
                    PropertyValue = parameter.string_value
                print(f"PropertyValue is {PropertyValue}")
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
                print(f'for object {obj.name},Attribute:{PropertyName} was passed for being incompatible in current version.')
                continue
            CurrentLevel = hson_temp["parameters"]
            
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
        else:
            hedgeset_game_choice = "frontiers"
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
        
        if not os.path.exists(f"{absoluteModDir}\\mod.ini"): # If there is no mod.ini, it must be an invalid mod folder
            def iniError(self, context):
                self.layout.label(text="mod.ini not found, check that you have selected a valid mod folder") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(iniError, title = "mod.ini Not Found", icon = "QUESTION") # Makes the popup appear
            return{'FINISHED'}
        
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
            node_ID_list =[]
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
                    #Set object directory for Paths
                    file_name = f"{ObjectDirectory}\Path.json"
                    node_name = f"{ObjectDirectory}\PathNode.json"
                    spline_path = os.path.join(path_dir, file_name)
                    node_path = os.path.join(path_dir, node_name)
                    bpy.ops.object.transform_apply(location = False, scale = True, rotation = True)
                    if "UID" in obj:
                        UID_Random = int(obj["UID"])
                    else:
                        UID_Random = random.randint(100000, 200000)
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
                    originrotation = [0.0, 0.0, 0.0, 1.0]
                    for i, point in enumerate(points_in_curve):
                        if i == 0:
                            originStr = False
                            origincoord = [point.co.x + obj.location.x, point.co.z + obj.location.z, -(point.co.y+obj.location.y)]
                            if curve_data.splines.active.type == "BEZIER":
                                if point.handle_right_type == 'VECTOR' and point.handle_left_type == 'VECTOR':
                                    originStr = True
                            if obj.name.lower().find("_norot") == -1:
                                try:
                                    RotPoint,rot_checker = Find_node_rot(obj, i, path_dir)
                                    if rot_checker == False:
                                        pass
                                    originrotation = [round(RotPoint.x,3), round(RotPoint.z,3), -round(RotPoint.y,3), round(RotPoint.w,3)]
                                    
                                except Exception as err:
                                    print(f'First rot error: {err}')
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
                            node_ID_list.append('{'+NodeId+'}')
                            # Print the index and coordinates of each point
                            nodeindex = i
                            nodecoord = [point.co.x + obj.location.x, point.co.z + obj.location.z, -(point.co.y+obj.location.y)]
                            rotation = [0.0, 0.0, 0.0, 1.0]
            
                            if obj.name.lower().find("_norot") == -1:
                                try:
                                    if i ==len(points_in_curve)-1:
                                        #RotPoint,lastLength = Find_node_rot(obj, point,next_point,lastLength,Final_curve_point=True)
                                        RotPoint,rot_checker = Find_node_rot(obj, i, path_dir)
                                        if rot_checker == False:
                                            pass
                                        rotation = [round(RotPoint.x,3), round(RotPoint.z,3), -round(RotPoint.y,3), round(RotPoint.w,3)]
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
                                        rotation = [round(RotPoint.x,3), round(RotPoint.z,3), -round(RotPoint.y,3), round(RotPoint.w,3)]
                                        
                                except Exception as err:
                                    print(f'node for {obj} failed because: {err}')
                                    rotation = [0.0, 0.0, 0.0, 1.0]
                                    pass


                            with open(node_path, "r") as file: #with open opens the file temporarily in order to avoid memory leak
                                node_temp =  json.load(file)
                            node_temp["id"] = "{" + NodeId + "}"
                            node_temp["name"] = this_nodename
                            node_temp["position"] = nodecoord
                            node_temp["rotation"] = rotation
                            node_temp["parameters"]["nodeId"] = nodeindex
                            if obj.name.lower().find("_str") != -1 or (point.handle_right_type == 'VECTOR' and point.handle_left_type == 'VECTOR'):
                                node_temp["parameters"]["lineType"] = 'LINETYPE_STRAIGHT'
                            else:
                                node_temp["parameters"]["lineType"] = 'LINETYPE_SNS'
                            node_text += f'{json.dumps(node_temp, indent=2)},\n' #Adds code to full gedit text that is then printed
                            # print(i,point)
                            # print(len(points_in_curve))
                            # if i ==len(points_in_curve)-1:
                            #     quit
                    #node_ID_list = node_ID_list[:-14] #delete the last comma in the nodeID list
                    with open(spline_path, "r") as file: #with open opens the file temporarily in order to avoid memory leak
                        path_temp =  json.load(file)
                    path_temp["id"] = "{" + PathId + "}"
                    path_temp["name"] = Pathname
                    path_temp["position"] = origincoord
                    path_temp["rotation"] = originrotation
                    path_temp["parameters"]["setParameter"]["pathType"] = PathType
                    path_temp["parameters"]["setParameter"]["nodeList"] = node_ID_list
                    path_temp["parameters"]["setParameter"]["isLoopPath"] = loop_bool
                    path_temp["parameters"]["setParameter"]["pathUID"] = UID_Random
                    if "json_parameters" in obj and "use_display_json_parameters" in obj and obj["use_display_json_parameters"] == True: #if Manual parameters are checked. do this instead of geonodes.
                        self.parameter_menu(obj, path_temp)
                    if obj.name.lower().find("_str") != -1 or originStr:
                        path_temp["parameters"]["setParameter"]["startLineType"] = 'LINETYPE_STRAIGHT'
                    else:
                        path_temp["parameters"]["setParameter"]["startLineType"] = 'LINETYPE_SNS'
                    path_text += f'{json.dumps(path_temp, indent=2)},\n' #Adds code to full gedit text that is then printed
                    node_ID_list =[]
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
                            self.parameter_menu(obj, light_temp)
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
                            self.parameter_menu(obj, light_temp) #call parameters from parameter menu instead using the light_temp collection of json code
                            
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
                        
                        #properties below
                        if "json_parameters" in obj and "use_display_json_parameters" in obj and obj["use_display_json_parameters"] == True: #if Manual parameters are checked. do this instead of geonodes.
                            print("parametermenu found")
                            self.parameter_menu(obj, object_temp) #finds and applies parameters from parameter menu
                            
                        else:
                            #this code generates the property names and values and puts them in a dictionary... Somehow...
                            C = bpy.context
                    
                            propdata = C.object.evaluated_get(C.evaluated_depsgraph_get()).data #I think this imports all depsgraph data of the object
                            if propdata != None:
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

                        #adds the values      
                        object_temp["id"] = Id
                        if "use_blendhog_name" in obj and "blendhog_name" in obj and obj["use_blendhog_name"] == True:
                            object_temp["name"] = obj["blendhog_name"]
                        else:
                            object_temp["name"] = name
                        
                        if "rotation" in object_temp:
                            object_temp["rotation"] = rotation
                        if obj.parent != None:
                            true_location = obj.matrix_world.translation # get global location
                            parent_matrix = obj.parent.matrix_world #Get parent coordinate system
                            parent_matrix_inverse = parent_matrix.inverted() #invert it
                            local_location = parent_matrix_inverse @ true_location #get location of the object in parent coordinate system
                            mathutils.Matrix.identity(obj.matrix_parent_inverse) #Turn the objects parent inverse matrix into an identity matrix (makes parent the origin)
                            obj.location = local_location #set the object to local location (i.e its original location in the parents coordinate system)
                            #rest adds parentId to object code
                            if "DataID" in obj.parent:
                                parentID = "{"+obj.parent["DataID"]+"}"
                            else:
                                parentID = self.ID_generator()
                                obj.parent["DataID"] = parentID
                                parentID = "{"+obj.parent["DataID"]+"}"
                            object_temp["parentId"] = parentID
                        object_temp["position"] = coordinates
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

            if bpy.context.scene.hedgegameChoice == "shadow":
                geditTemplate = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/shadow.json'
            else:
                geditTemplate = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/frontiers.json'
            
            gedit = open(f"{absoluteModDir}\\raw\\gedit\\{worldId}_gedit\\{worldId}_{collection.name}.hson", "x")
            gedit.write(gedit_text)
            gedit.close()

            #from AshDumpLib.HedgehogEngine.BINA.RFL import Reflection, ObjectWorld, ReflectionData # type: ignore
            #ObjectWorld.TemplateData = ReflectionData.Template.GetTemplateFromFilePath(geditTemplate)
            #ObjectWorld.ToGedit(ObjectWorld.FromHsonString(gedit_text)).SaveToFile(f"{absoluteModDir}\\raw\\gedit\\{worldId}_gedit\\{worldId}_{collection.name}.gedit")

            os.chdir(os.path.dirname(directoryHedgeset))
            if not os.path.exists(f"{os.path.dirname(directoryHedgeset)}\\templates\\{hedgeset_game_choice}.json"):
                templatefound = False
                for p in ["miller", "shadow", "shadow_generations", "sxsg"]:
                    if os.path.exists(f"{os.path.dirname(directoryHedgeset)}\\templates\\{p}.json"):
                        hedgeset_game_choice = p
                        templatefound = True
                        break
                if templatefound == False:
                    def templateError(self, context):
                        self.layout.label(text="A Shadow HedgeSet template could not be found") # Sets the label of the popup
                    bpy.context.window_manager.popup_menu(templateError, title = "HedgeSet Template Not Found", icon = "QUESTION") # Makes the popup appear
                    return{'FINISHED'}
            print(f'HedgeSet "{absoluteModDir}\\raw\\gedit\\{worldId}_gedit\\{worldId}_{collection.name}.hson" "{absoluteModDir}\\raw\\gedit\\{worldId}_gedit\\{worldId}_{collection.name}.gedit" -game={hedgeset_game_choice} -platform=pc')
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
                
        if not os.path.exists(f"{absoluteModDir}\\mod.ini"): # If there is no mod.ini, it must be an invalid mod folder
            def iniError(self, context):
                self.layout.label(text="mod.ini not found, check that you have selected a valid mod folder") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(iniError, title = "mod.ini Not Found", icon = "QUESTION") # Makes the popup appear
            return{'FINISHED'}
        
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
        
        self.report({"INFO"}, f"Quick Export Finished")
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

        bpy.data.window_managers["WinMan"].addon_search = "Blendhog Level Creator"

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
            ("w14b10", "w14b10 (Devil Doom)", ""),
            
            # Extras
            ("w20a10", "w20a10 (Tokyo)", "")
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
    bpy.types.Scene.debuglevel = bpy.props.IntProperty( # Access through "bpy.context.scene.debuglevel"
        name="Debug Level",
        default=1,
        description="The amount of information that should be printed to the console while the program is running.\n1: Minimal\n2: Detailed\n3: Diagnostic",
        min=1,
        max=3
    )
    bpy.types.Scene.debuglog = bpy.props.BoolProperty( # Access through "bpy.context.scene.debuglog"
        name="Enable Debug Log",
        default=False,
        description="Prints a debug log to your mod's folder"
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
