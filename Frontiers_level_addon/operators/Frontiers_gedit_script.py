from typing import Any
import bpy
import mathutils
import random
from math import radians, degrees
import pathlib
from pathlib import Path
import os
import json
import sys
import textwrap
# REWORKED SCRIPT
# Defines the operator to print coordinates
class PrintCoordinatesOperator(bpy.types.Operator):
    bl_idname = "object.print_coordinates"
    bl_label = "Print Coordinates"
    def ID_generator(self):
        Id = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
        hexValues = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
        for i in range(32):
            Id = Id.replace("X", hexValues[random.randrange(len(hexValues))], 1) # generates a random ID
        return Id
        
    def execute(self, context):
        collection_name = context.scene.FrontiersCoords.collection_name
        collection = collection_name
        game_choice = context.scene.hedgegameChoice
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Finds path to the folder this script is in [DO NOT TOUCH]
        blend_file_path = bpy.data.filepath # Finds file path of Blender file
        blend_dir = os.path.dirname(blend_file_path) # Gets the name of the directory the Blender file is in
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
        print(compatible_objects)
        # List of compatible objects
        # compatible_objects = ["Ring","Spring","Balloon","DashPanel",
        #                       "DashRing","EggRobo","HintRing","JumpBoard",
        #                       "PortalGate","WideSpring","Motora","PointMarker",
        #                       "SuperRing","ThornCylinder","NormalFloor","UpReel",
        #                       "StartPosition","RedRing","BoardingJumpBoard","Bomb",
        #                       "CloudFloor","FallDeadTrigger","Fan","Ganigani",
        #                       "Hangglider","JumpSelector","Pole","PropellerSpring",
        #                       "RollingFloor","RotateBlock","RotateThornBall","SpringEgg",
        #                       "Thorn","ThornBall","Beeton","Batabata","Grabber","Lander",
        #                       "GrindBooster","GrindThorn","AutorunTrigger","SwitchUsual",
        #                       "SpinnerI","CannonType","Cannon","BreakCliff","DashRoller",
        #                       "DriftPanel","DropFloor","DropTower","Helicopter","JumpPanelClassic",
        #                       "LaserFence","PushBlock","Tank","UpDownPole","WallJumpBlock","PortalGateSecret",
        #                       "SideviewPointMarker","SpringPole","EventTrigger","ThroughFloor",
        #                       "WoodSwing","SpringClassic","WoodBridge","WoodBridgeBreak","PurpleRock","Gismo","Pulley","PulleyColumn",
        #                       "CarMinivan","CarVan","CarHatchback","NormalFloor10m","NormalFloor2m","NitroBottle","DivingVolume","DimensionVolume","SwitchVolume","DriftEndVolume","CameraVolumeSub",
        #                       'Aquaball', 'Bird', 'Bommer', 'Bubble', 'Defender', 'DropChaosEmerald', 'Jellyman', 'Jumper', 'JumperSub', 'Locator', 'PuzzleBarrier', 'Robber', 'Sniper', 'Twister', 
        #                       'Umbrella', 'Wolf', 'WolfManager','ActionChain', 'AirCube', 'AirFloor', 'AirWall', 'AlbatrossChase', 'AlbatrossGroup', 'Amy', 'Animal', 'AnimalRescueArea', 'BreakBox', 
        #                       'BreakWall', 'ChainBooster', 'ChaosEmeraldPillar', 'ChaosEmeraldStorage', 'ClimbingPoint', 'Dove', 'ExDashRing', 'FallReturnVolume', 'FishCoin', 'FishingBig', 'FishingPortal', 
        #                       'FloatTop', 'Knuckles', 'KnucklesWall', 'Kodama', 'KodamaElder', 'KodamaHermit', 'MusicMemory', 'NpcSonic', 'NumberRing', 'Particle', 'ParticleExtent', 'Portal', 'PortalBit', 
        #                       'PowerupSeed', 'Sage', 'SequenceItem', 'SilverMoonRing', 'SlotStar', 'SoundSourcePoint', 'StorageKey', 'Tails', 'TreasureChest','Ashura', 'Blade', 'Charger', 'Daruma', 'Flyer',
        #                      'Skier', 'SkierMissile', 'SkierProhibitedArea', 'SkierPylon', 'Spider', 'SpiderAuraTrain', 'SpiderDivingVolume', 'SpiderNeedle', 'SpiderRippleLaser', 'SpiderRotateLaserTurret', 
        #                      'SpiderSpring', 'SpiderThornBall', 'SpiderTwister', 'Strider', 'Sumo', 'SumoPole', 'Territory', 'Tracker', 'TrackerBase', 'Tyrant', 'Warship', 'WarShipBird', 'WarShipBullet', 
        #                      'WarshipDashRing', 'WarshipLandVolume', 'WarshipVolume',"ChangeBGMTrigger","OneShotSoundTrigger","Note",'Barrier', 'BarrierNPC', 'BossGiantDoll', 'Dragon', 'DragonActionVolume', 
        #                      'DragonAreaVolume', 'DragonRoadSpring', 'DragonStatusVolume', 'EggMan', 'Giant', 'Knight', 'Rifle', 'RifleBeast', 'ParticleVolume',"GoalTrigger","BossRingSupplyGroup"
        #                       ]

        
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

        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Finds path to the folder this script is in [DO NOT TOUCH]
        blend_file_path = bpy.data.filepath # Finds file path of Blender file
        blend_dir = os.path.dirname(blend_file_path) # Gets the name of the directory the Blender file is in
        path_dir = os.path.join(blend_dir,script_dir) # 
        
        if collection is not None:
            changed_ID_list =[]
            printed_text = ""
            gedit_text = ""
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
                                        PropertyValue = ""
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
                        gedit_text += f'{json.dumps(light_temp, indent=2)},\n' #Adds code to full gedit text that is then printed
                    elif obj.data.type == 'SPOT':
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
                                        PropertyValue = ""
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
                        rotation = mathutils.Euler((rotation.to_euler().x + radians(90), rotation.to_euler().y, rotation.to_euler().z)).to_quaternion()
                        light_temp["rotation"] = [rotation.x, rotation.z, -rotation.y, rotation.w]
                        
                        Intense = obj.data.energy/64 #Have to divide blenders intensity to accurately portrait frontiers lights.
                        CurrentLevel = light_temp["parameters"]
                        CurrentLevel["colorR"] = obj.data.color[0]*255*Intense
                        CurrentLevel["colorG"] = obj.data.color[1]*255*Intense
                        CurrentLevel["colorB"] = obj.data.color[2]*255*Intense
                        CurrentLevel["outerConeAngle"] = (degrees(obj.data.spot_size)) / 2
                        CurrentLevel["innerConeAngle"] = (degrees(obj.data.spot_size) * (1 - obj.data.spot_blend)) / 2
                        if obj.data.use_custom_distance == True:
                            CurrentLevel["attenuationRadius"] = obj.data.cutoff_distance
                        else:
                            CurrentLevel["attenuationRadius"] = 32768
                        render_engine = bpy.context.scene.render.engine
                        if render_engine == 'BLENDER_EEVEE':
                            CurrentLevel["enableShadow"] = obj.data.use_shadow
                        elif render_engine == 'CYCLES':
                            CurrentLevel["enableShadow"] = obj.data.cycles.cast_shadow
                        gedit_text += f'{json.dumps(light_temp, indent=2)},\n' #Adds code to full gedit text that is then printed
                else:
                    #for theobject in compatible_objects: #Checks if object is compatible with Gedit templates
                    theobject = name.split(".")[0]
                    if "FrontiersCamera" in obj:
                        compatible_list = compatible_objects + volume_objects
                    else: 
                        compatible_list = compatible_objects
                    if theobject in compatible_list:
                        
                        if theobject == "StartPosition":
                            self.report({"WARNING"}, f"{theobject} found. Make sure to delete original gedit code for {theobject}.")
                        elif theobject == "RedRing":
                            self.report({"WARNING"}, f"{theobject} found. Make sure to delete original gedit code for all {theobject}.")
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
                                            PropertyValue = ""
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
                                            Id = self.ID_generator()
                                            parameter.object_value["DataID"] = Id
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
                        if "use_blendhog_name" in obj and "blendhog_name" in obj and obj["use_blendhog_name"] == True:
                            object_temp["name"] = obj["blendhog_name"]
                        else:
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
                        # if obj.children is not None:
                        #     childlist = []
                        #     for child in obj.children:
                        #         if child.type == 'MESH' and "DataID" in child:
                        #             childID = "{"+child["DataID"]+"}"
                        #             childlist.append(childID)
                        #         elif child.type == 'MESH' and "DataID" not in child:
                        #             childID = self.ID_generator()
                        #             child["DataID"] = childID
                        #             childID = "{"+child["DataID"]+"}"
                        #             childlist.append(childID)
                        #     if childlist != []:
                        #         if "actions" in object_temp["parameters"]:
                        #             object_temp["parameters"]["actions"][0]["objectIds"] = childlist
                        #         # If "Actions" not found, recursively search in nested subcategories
                        #         else:
                        #             for key, value in object_temp["parameters"].items():
                        #                 if isinstance(value, dict):
                        #                     CurrentLevel = object_temp["parameters"][key]
                        #                     if "actions" in CurrentLevel:
                        #                         CurrentLevel["actions"][0]["objectIds"] = childlist
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
                            
                        gedit_text += f'{json.dumps(object_temp, indent=2)},\n' #Adds code to full gedit text that is then printed
                        
                    for thevolume in volume_objects: #checks for volume objects
                        if name.startswith(thevolume+'.') and "FrontiersCamera" not in obj:
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
                                file_name = f"{ObjectDirectory}\_legacy_{thevolume}.json" 
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
                                
                            gedit_text += json.dumps(volume_temp, indent = 2)
                            gedit_text += ",\n"
                            gedit_text += json.dumps(otherVolume_temp, indent = 2) #Adds code to full gedit text that is then printed
                            gedit_text += ",\n"

                        
                obj.select_set(False)

                
        else:
            self.report({"WARNING"}, f"Collection{collection_name} not found")
            return {'CANCELLED'}
        #Code that opens the window with the gedit code
        bpy.ops.wm.window_new()
        Coordinate_text = bpy.data.texts.new("Printed Frontiers Coordinates")
        Coordinate_text.write(printed_text)
        Coordinate_text.write("")
        if gedit_text != "":
            Coordinate_text.write("Compatible objects detected. Gedit code printed in seperate window: \n")
        context.area.type = 'TEXT_EDITOR'
        context.space_data.text = Coordinate_text
        if gedit_text != "":
            gedit_text = textwrap.indent(gedit_text, '    ')
            bpy.ops.wm.window_new()
            GeditPrint = bpy.data.texts.new("Frontiers Gedit Code")
            GeditPrint.write(gedit_text)
            context.area.type = 'TEXT_EDITOR'
            context.space_data.text = GeditPrint
        if changed_ID_list != []:
            self.report({"INFO"}, f"Duplicate ID's were found. Objects with changed IDs are: {changed_ID_list}")
        return {'FINISHED'}

# Define a custom property to store the collection name
class FrontiersCoords(bpy.types.PropertyGroup):
    collection_name: bpy.props.PointerProperty(
        name="Object Collection",
        description = "Choose Object Collection",
        type=bpy.types.Collection
    )