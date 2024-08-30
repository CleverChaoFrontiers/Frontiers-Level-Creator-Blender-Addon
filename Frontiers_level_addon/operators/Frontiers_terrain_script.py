
import bpy
import random
from math import radians
import pathlib
from pathlib import Path
import os

#The terrain script
class TerrainScriptfrontiers(bpy.types.Operator):
    bl_idname = "object.terrain_script"
    bl_label = "Create .pcmodel/.pccol Template"
    bl_description = "Create .pcmodel/.pccol Template and places it in blend-file folder"
    
    def execute (self, context):
        #imports all menu variables
        Jsonfile_name = context.scene.FrontiersTerrProps.json_name
        Col_check = context.scene.FrontiersTerrProps.collision_check
        Cyber_check =context.scene.FrontiersTerrProps.cyberspace_check
        Coord = context.scene.FrontiersTerrProps.transform_coords
        Rotat = context.scene.FrontiersTerrProps.rotation_coords
        if Cyber_check: #if cyberspace is checked, all coordinates are 0
            location_x = 0.0
            location_y = 0.0
            location_z = 0.0
            rotation_x = 0.0
            rotation_y = 0.0
            rotation_z = 0.0
        else:
            location_x = Coord[0]
            location_y = Coord[1]
            location_z = Coord[2]
            rotation_x = Rotat[0]
            rotation_y = Rotat[1]
            rotation_z = Rotat[2]
        #Finds the path to the template
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        blend_file_path = bpy.data.filepath 
        blend_dir = os.path.dirname(blend_file_path)
        path_dir = os.path.join(blend_dir,script_dir)
        
        file_name = f"other\\terrainTemplate.txt" 
        terr_path = os.path.join(path_dir, file_name)

        

        

        if Col_check == False: # checks if collision is checked
            with open(blend_dir + f'\{Jsonfile_name}.hedgehog.pointcloud.json', 'w') as file:
                file.write("[\n")  
            template = open(f"{terr_path}").read() # gets the template for the object
            writeText = template.replace("DATA_NAME", str(Jsonfile_name)) # adds the name to the template
            
            writeText = writeText.replace("DATA_POSITIONX", (str(location_x))) # adds the location to the template
            writeText = writeText.replace("DATA_POSITIONY", (str(location_z)))
            writeText = writeText.replace("DATA_POSITIONZ", (str(-location_y)))
            
            writeText = writeText.replace("DATA_ROTATIONX", (str(rotation_x))) # adds the rotation to the template
            writeText = writeText.replace("DATA_ROTATIONY", (str(rotation_z)))
            writeText = writeText.replace("DATA_ROTATIONZ", (str(-rotation_y)))
            
            with open(blend_dir + f'\{Jsonfile_name}.hedgehog.pointcloud.json', 'a') as file:
                file.write(writeText) # writes to the external txt
            
            for i in range(3):
                with open(blend_dir + f'\{Jsonfile_name}.hedgehog.pointcloud.json', 'rb+') as fh: # remove the final comma from the json
                    fh.seek(-1, 2) 
                    fh.truncate() 
            with open(blend_dir + f'\{Jsonfile_name}.hedgehog.pointcloud.json', 'a') as file:
                file.write("\n]")
            self.report({"INFO"}, f"File: '{Jsonfile_name}.hedgehog.pointcloud.json' has been created in {blend_dir}")
            
        elif Col_check == True: # checks name of object
            with open(blend_dir + f'\{Jsonfile_name}_col.hedgehog.pointcloud.json', 'w') as file:
                file.write("[\n")
            template = open(f"{terr_path}").read() # gets the template for the object
            writeText = template.replace("DATA_NAME", str(Jsonfile_name)) # adds the name to the template
            
            writeText = writeText.replace("DATA_POSITIONX", (str(location_x))) # adds the location to the template
            writeText = writeText.replace("DATA_POSITIONY", (str(location_z)))
            writeText = writeText.replace("DATA_POSITIONZ", (str(-location_y)))
            
            writeText = writeText.replace("DATA_ROTATIONX", (str(rotation_x))) # adds the rotation to the template
            writeText = writeText.replace("DATA_ROTATIONY", (str(rotation_z)))
            writeText = writeText.replace("DATA_ROTATIONZ", (str(-rotation_y)))
            

            
            file = open(blend_dir + f'\{Jsonfile_name}_col.hedgehog.pointcloud.json', 'a')
            file.write(writeText) # writes to the external txt
            file.close()


                
            for i in range(3):
                with open(blend_dir + f'\{Jsonfile_name}_col.hedgehog.pointcloud.json', 'rb+') as fh: # remove the final comma from the json
                    fh.seek(-1, 2) 
                    fh.truncate() 



            file = open(blend_dir + f'\{Jsonfile_name}_col.hedgehog.pointcloud.json', 'a')
            file.write("\n]")
            file.close()
            self.report({"INFO"}, f"File: '{Jsonfile_name}_col.hedgehog.pointcloud.json' has been created in {blend_dir}")
        return {'FINISHED'}
    
class FrontiersTerrProps(bpy.types.PropertyGroup):
    collision_check: bpy.props.BoolProperty(
        name="Is collision",
        description="Creates a collision template instead that should be converted to a .pccol file",
        default = False)
    cyberspace_check: bpy.props.BoolProperty(
        name="Is Cyberspace Level",
        description="locks coordinates and rotation to origin. This is recommended for Cyberspace levels",
        default = True)
    transform_coords: bpy.props.FloatVectorProperty(
            name="Coordinates",
            description = "Set Coordinates for PC-Model (Uses Blender Coordinate system) (ignored if 'Is Cyberspace Level' is checked)",
            default=(0, 0, 0), 
            subtype='XYZ')
    rotation_coords: bpy.props.FloatVectorProperty(
            name="Rotation",
            description = "Set Rotation for PC-Model (Uses Blender Coordinate system)(ignored if 'Is Cyberspace Level' is checked)",
            default=(0, 0, 0), 
            subtype='EULER')
    json_name: bpy.props.StringProperty(
        name="FBX file Name",
        description = "Write the name of your FBX file",
        default="WRITE FBX FILE NAME HERE"
    )