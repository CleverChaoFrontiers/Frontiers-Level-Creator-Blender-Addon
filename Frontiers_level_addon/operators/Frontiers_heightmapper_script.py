import bpy
import os
import mathutils
import math
import shutil

def checkMode(context):
    if bpy.context.window.workspace.name == 'Layout':
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False) # Sets to object mode
    if bpy.context.window.workspace.name == 'Heightmapper':
        bpy.data.objects['Heightmap_LEVELCREATOR'].select_set(True)
        bpy.ops.object.mode_set(mode="SCULPT", toggle=False) # Sets to object mode

bpy.msgbus.subscribe_rna( # Listens for when the workspace is changed, then triggers checkMode()
    key=bpy.types.Window,
    owner=None,
    args=(bpy.context,),
    notify=checkMode,
)

bpy.msgbus.publish_rna(key=bpy.types.Window)

class HeightmapperOperator(bpy.types.Operator):
    bl_idname = "heightmapper.heightmapper"
    bl_label = "Open Heightmapper Tool"

    def execute(self, context): # When button is pressed
        if bpy.context.scene.fullRes == False:
            heightmapRes = 10 # This is the number of times that the number of faces doubles. 10 is the recommended minimum, and 12 is the maximum that actually makes a difference on a standard map (good luck running this though)
        else:
            heightmapRes = 12

        bpy.context.window.workspace = bpy.data.workspaces['Layout']

        if ("Heightmap_LEVELCREATOR" in bpy.data.objects): # If a heightmap already exists
            plane = bpy.data.objects['Heightmap_LEVELCREATOR'] # Gets the heightmap
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False) # Sets to object mode
            bpy.ops.object.select_all(action='DESELECT') # Deselect all
            plane.select_set(True) # Select heightmap
            bpy.context.view_layer.objects.active = plane # Set heightmap as active
        else: # If there is no heightmap yet
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection # Deselects all collections so the user doesn't accidentally put the heightmap in terrain or objects

            bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0), scale=(2, 2, 2)) # Adds a plane of scale 2x2x2
            plane = bpy.context.selected_objects[0] # Gets the heightmap
            plane.name = "Heightmap_LEVELCREATOR" # Changes the name of the heightmap
            bpy.ops.object.select_all(action='DESELECT') # Deselect all
            plane.select_set(True) # Select heightmap
            bpy.context.view_layer.objects.active = plane # Set heightmap as active

            bpy.ops.transform.resize(value=(2048, 2048, 2048)) # Scale the heightmap to standard map size
            bpy.ops.object.mode_set(mode="EDIT", toggle=False) # Sets to edit mode
            for i in range(heightmapRes): # This part subdivides to the desired resolution
                bpy.ops.mesh.subdivide(number_cuts=1) # Subdivide the plane

            bpy.ops.object.mode_set(mode="SCULPT", toggle=False) # Sets to sculpt mode

            with bpy.data.libraries.load(os.path.dirname(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/heightmapperWorkspace.blend/'), link=False) as (data_from, data_to): # Opens the blend file containing the heightmap material
                data_to.materials += data_from.materials # Adds the heightmap material to the current file
            mat = bpy.data.materials.get("Heightmap_LEVELCREATOR") # Finds the material
            bpy.context.active_object.data.materials.append(mat) # Adds the material to the heightmap

        if not ("Heightmapper" in bpy.data.workspaces): # If the Heightmapper workspace is not loaded
            bpy.ops.workspace.append_activate( # Appends the Heightmapper workspace from the .blend file in the addon
                idname='Heightmapper',
                filepath= os.path.dirname(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/heightmapperWorkspace.blend/')
            )
            bpy.ops.object.mode_set(mode='SCULPT', toggle=False) # Enables sculpt mode
            bpy.context.scene.tool_settings.sculpt.lock_x = True
            bpy.context.scene.tool_settings.sculpt.lock_y = True # These prevent the user from sculpting terrain that is impossible to import by only allowing editing vertices vertically.
        else: # If the Heightmapper workspace is loaded
            bpy.context.window.workspace = bpy.data.workspaces['Heightmapper'] # Switches to Heightmapper workspace
            bpy.ops.object.mode_set(mode='SCULPT', toggle=False) # Enables sculpt mode

        for screen in bpy.data.workspaces["Heightmapper"].screens: # This whole part basically just raises the render distance of the Heightmapper workspace
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.clip_end = 10000
                            space.shading.type = "SOLID" # Switches to solid mode
                    
        bpy.ops.ed.undo_push() # This is required otherwise Blender crashes if you undo immediately for some reason

        return {'FINISHED'}
    
class HeightmapperRender(bpy.types.Operator):
    bl_idname = "heightmapper.render"
    bl_label = "Open Heightmapper Tool"

    def execute(self, context): # When button is pressed

        heightmapExists = False # This part checks if there is a heightmap
        for o in bpy.data.objects:
            if o.name == "Heightmap_LEVELCREATOR":
                heightmapExists = True
        
        if heightmapExists == False: # Gives an error if there is no heightmap
            def heightmapError(self, context):
                self.layout.label(text="There is no heightmap to render!") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(heightmapError, title = "Render Failed", icon = "OUTLINER_OB_CAMERA") # Makes the popup appear
            return {'FINISHED'}
        
        if (bpy.data.filepath == ""): # If the blender file is not saved, gives an error
            def saveError(self, context):
                self.layout.label(text="The .blend file is not saved, so there is nowhere to output the render to!") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(saveError, title = "Render Failed", icon = "DISK_DRIVE") # Makes the popup appear
            return {'FINISHED'}

        bpy.context.window.workspace = bpy.data.workspaces['Heightmapper'] # Switches to Heightmapper workspace
    
        if not("Camera_LEVELCREATOR" in bpy.data.objects): # If a camera doesn't already exist
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

            bpy.ops.object.camera_add(location = [0.0, 0.0, 3000.0], rotation = [0.0, 0.0, 0.0]) # Creates a camera at 3000m above the centre
            cam = bpy.context.active_object
            cam.name = "Camera_LEVELCREATOR"

            bpy.context.view_layer.objects.active = bpy.data.objects["Heightmap_LEVELCREATOR"]
            bpy.ops.object.mode_set(mode="SCULPT", toggle=False)
        else:
            cam = bpy.data.objects["Camera_LEVELCREATOR"]

        oldCamera = bpy.context.scene.camera # Gets the old active camera's name so that other renders aren't messed up
        oldResX = bpy.context.scene.render.resolution_x # Gets the old render resolution so that other renders aren't messed up
        oldResY = bpy.context.scene.render.resolution_y
        oldRenderPath = bpy.context.scene.render.filepath # Gets the old render file path so that other renders aren't messed up

        bpy.context.scene.view_settings.view_transform = 'Raw' # Filmic messes up the colours, so switch to standard instead
        bpy.context.scene.render.image_settings.color_depth = '16' # Switches to 16 bit colour depth (which frontiers uses)

        for o in bpy.data.objects: # Hides all objects from being rendered except for the heightmap
            if o.name != "Heightmap_LEVELCREATOR":
                o.hide_render = True 

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                activeRegion = area.spaces.active.region_3d
                oldView = activeRegion.view_rotation
        if bpy.context.scene.isTiles == True: # If the user wants the heightmap rendered to tiles
            for t in range(16):
                tileCoords = [t % 4, t // 4] # Assigns number of tiles to a grid e.g. assigns 16 tiles to a 4x4 grid
                cam.location = mathutils.Vector(((tileCoords[0] * 1024) - 1536, (tileCoords[1] * -1024) + 1536, 3000)) # This cool bit of maths changes the camera's position for each tile
                bpy.context.scene.camera = bpy.data.objects["Camera_LEVELCREATOR"] # Sets the scene's active camera to the new camera
                cam.data.type = 'ORTHO' # Sets camera to orthographic
                cam.data.ortho_scale = 1024 # Sets the camera to capture each tile
                cam.data.clip_end = 5000 # Sets the camera to render in each tile
    
                print(tileCoords)

                bpy.context.scene.render.resolution_x = 1024 # Sets proper render resolution
                bpy.context.scene.render.resolution_y = 1024

                if (bpy.data.filepath == ""): # If the blender file is not saved, gives an error
                    def saveError(self, context):
                        self.layout.label(text="The .blend file is not saved, so there is nowhere to output the render to!") # Sets the label of the popup
                    bpy.context.window_manager.popup_menu(saveError, title = "Render Failed", icon = "DISK_DRIVE") # Makes the popup appear
                    return {'FINISHED'}
                else:
                    bpy.context.scene.render.filepath = os.path.dirname(bpy.data.filepath) # Sets the render file path to the location of the blender file
                    bpy.ops.object.mode_set(mode="EDIT", toggle=False) # Changes to edit mode for UV unwrapping

                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            for space in area.spaces:
                                if space.type == 'VIEW_3D':
                                    targetView = mathutils.Euler(mathutils.Vector((math.radians(-90.0), 0.0, 0.0))) # Sets the view rotation to be rotated to
                                    space.region_3d.view_matrix = targetView.to_matrix().to_4x4() # Rotates to the correct view rotation

                                    space.region_3d.update() # Updates the view
                                    bpy.ops.uv.project_from_view(orthographic=True, camera_bounds=False, correct_aspect=True, scale_to_bounds=True) # UV unwrap from view

                    for screen in bpy.data.workspaces["Heightmapper"].screens:
                        for area in screen.areas:
                            if (area.type == "IMAGE_EDITOR"):
                                area.spaces.active.image = bpy.data.images["gradient.exr"] # Opens the gradient image
                                bpy.ops.uv.select_all(action='SELECT') # Select all vertices in UV editor
                                bpy.ops.transform.resize({"area" : area}, value=(1, 16383.9, 1)) # Resize UV map
                                bpy.ops.transform.rotate({"area" : area}, value=math.radians(90), constraint_axis=(False, False, True)) # Rotate UV map
                    
                            
                    bpy.ops.object.mode_set(mode="SCULPT", toggle=False)

                    bpy.ops.render.render(write_still=False) # RENDER!!!!

                    image = bpy.data.images["Render Result"] # Gets the Rendered image
                    image.file_format = 'PNG' # Sets the file format
                    if bpy.context.scene.texconvDirectory == "": # If there is no texconv directory it won't convert the images
                        image.save_render(filepath=f"{os.path.dirname(bpy.data.filepath)}\w1r03_heightmap_{t:03}.png") # Outputs the image straight to the blend file's folder
                    else:
                        image.save_render(filepath=f"{os.path.abspath(bpy.path.abspath(bpy.context.scene.texconvDirectory))}\\w1r03_heightmap_{t:03}.png") # Outputs the image to the texconv directory
                        os.chdir(f"{os.path.abspath(bpy.path.abspath(bpy.context.scene.texconvDirectory))}") # Goes to the directory
                        os.popen(f'texconv -f R16_UNORM -xlum -y "w1r03_heightmap_{t:03}.png"').read() # Converts the image via command line
                        os.remove(f"w1r03_heightmap_{t:03}.png") # Deletes the old PNGs
                        shutil.copy2(f"w1r03_heightmap_{t:03}.dds", f"{os.path.dirname(bpy.data.filepath)}") # Copies the DDSs to the blend file's folder
                        os.remove(f"w1r03_heightmap_{t:03}.dds") # Deletes the DDSs from the texconv directory

        else:
            bpy.context.scene.camera = bpy.data.objects["Camera_LEVELCREATOR"] # Sets the scene's active camera to the new camera
            cam.location = mathutils.Vector((0, 0, 3000))
            cam.data.type = 'ORTHO' # Sets camera to orthographic
            cam.data.ortho_scale = 4096 # Sets the camera to capture the whole heightmap
            cam.data.clip_end = 5000 # Sets the camera to render in the whole heightmap

            bpy.context.scene.render.resolution_x = 4096 # Sets proper render resolution
            bpy.context.scene.render.resolution_y = 4096

            if (bpy.data.filepath == ""): # If the blender file is not saved, gives an error
                def draw(self, context):
                    self.layout.label(text="The .blend file is not saved, so there is nowhere to output the render to!") # Sets the label of the popup
                bpy.context.window_manager.popup_menu(draw, title = "Render Failed", icon = "DISK_DRIVE") # Makes the popup appear
                return {'FINISHED'}
            else:
                bpy.context.scene.render.filepath = os.path.dirname(bpy.data.filepath) # Sets the render file path to the location of the blender file

                bpy.ops.object.mode_set(mode="EDIT", toggle=False) # Changes to edit mode for UV unwrapping
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                targetView = mathutils.Euler(mathutils.Vector((math.radians(-90.0), 0.0, 0.0))) # Sets the view rotation to be rotated to
                                space.region_3d.view_matrix = targetView.to_matrix().to_4x4() # Rotates to the correct view rotation

                                space.region_3d.update() # Updates the view
                                bpy.ops.uv.project_from_view(orthographic=True, camera_bounds=False, correct_aspect=True, scale_to_bounds=True) # UV unwrap from view
                
                for screen in bpy.data.workspaces["Heightmapper"].screens:
                    for area in screen.areas:
                        if (area.type == "IMAGE_EDITOR"):
                            area.spaces.active.image = bpy.data.images["gradient.exr"] # Opens the gradient image
                            bpy.ops.uv.select_all(action='SELECT') # Select all vertices in UV editor
                            bpy.ops.transform.resize({"area" : area}, value=(1, 16383.9, 1)) # Resize UV map
                            bpy.ops.transform.rotate({"area" : area}, value=math.radians(90), constraint_axis=(False, False, True)) # Rotate UV map
                        
                bpy.ops.object.mode_set(mode="SCULPT", toggle=False)

                bpy.ops.render.render(write_still=False) # RENDER!!!!

                image = bpy.data.images["Render Result"] # Gets the Rendered image
                image.file_format = 'PNG' # Sets the file format
                if bpy.context.scene.texconvDirectory == "": # If there is no texconv directory it won't convert the images
                    image.save_render(filepath=f"{os.path.dirname(bpy.data.filepath)}\Heightmap_000.png") # Outputs the image straight to the blend file's folder
                else:
                    image.save_render(filepath=f"{os.path.abspath(bpy.path.abspath(bpy.context.scene.texconvDirectory))}\\Heightmap_000.png") # Outputs the image to the texconv directory
                    os.chdir(f"{os.path.abspath(bpy.path.abspath(bpy.context.scene.texconvDirectory))}") # Goes to the directory
                    os.popen('texconv -f R16_UNORM -xlum -y "Heightmap_000.png"').read() # Converts the image via command line
                    os.remove("Heightmap_000.png") # Deletes the old PNG
                    shutil.copy2(f"Heightmap_000.dds", f"{os.path.dirname(bpy.data.filepath)}") # Copies the DDSs to the blend file's folder
                    os.remove(f"Heightmap_000.dds") # Deletes the DDSs from the texconv directory

        bpy.context.scene.camera = oldCamera # Resets the render settings to the old ones so renders are not messed up
        bpy.context.scene.render.resolution_x = oldResX
        bpy.context.scene.render.resolution_y = oldResY
        bpy.context.scene.render.filepath = oldRenderPath

        for o in bpy.data.objects: # Show all objects for renders
            if o.name != "Heightmap_LEVELCREATOR":
                o.hide_render = False 

        return {'FINISHED'}

class HeightmapperImport(bpy.types.Operator):
    bl_idname = "heightmapper.import"
    bl_label = "Import Heightmap"
    bl_options = {"UNDO"}

    def execute(self, context): # When button is pressed

        needsConverted = False

        if os.path.abspath(bpy.path.abspath(bpy.context.scene.importDirectory)).split(".")[0][-3:].find("000") != -1:
            if (bpy.context.scene.importDirectory.find("w1r0") != -1 or bpy.context.scene.importDirectory.find("w2r0") != -1 or bpy.context.scene.importDirectory.find("w3r") != -1) and bpy.context.scene.importDirectory.find("dds") != -1: # If there is no texconv directory it won't convert the images
                if bpy.context.scene.texconvDirectory == "":
                    def heightmapError(self, context):
                        self.layout.label(text="Looks like you're importing a Frontiers heightmap, you need to enter the texconv directory under 'Render' so that the image can be converted correctly!") # Sets the label of the popup
                    bpy.context.window_manager.popup_menu(heightmapError, title = "Warning", icon = "FCURVE") # Makes the popup appear
                    return {'FINISHED'}
                else:
                    needsConverted = True
            
        heightmapExists = False # This part checks if there is a heightmap
        for o in bpy.data.objects:
            if o.name == "Heightmap_LEVELCREATOR":
                heightmapExists = True
        
        if heightmapExists == False: # Creates a heightmap if there is none
            if bpy.context.scene.fullRes == False:
                heightmapRes = 10 # This is the number of times that the number of faces doubles. 10 is the recommended minimum, and 12 is the maximum that actually makes a difference on a standard map (good luck running this though)
            else:
                heightmapRes = 12
                
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection # Deselects all collections so the user doesn't accidentally put the heightmap in terrain or objects

            bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0), scale=(2, 2, 2)) # Adds a plane of scale 2x2x2
            plane = bpy.context.selected_objects[0] # Gets the heightmap
            plane.name = "Heightmap_LEVELCREATOR" # Changes the name of the heightmap
            bpy.ops.object.select_all(action='DESELECT') # Deselect all
            plane.select_set(True) # Select heightmap
            bpy.context.view_layer.objects.active = plane # Set heightmap as active

            bpy.ops.transform.resize(value=(2048, 2048, 2048)) # Scale the heightmap to standard map size
            bpy.ops.object.mode_set(mode="EDIT", toggle=False) # Sets to edit mode
            for i in range(heightmapRes): # This part subdivides to the desired resolution
                bpy.ops.mesh.subdivide(number_cuts=1) # Subdivide the plane

            with bpy.data.libraries.load(os.path.dirname(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/heightmapperWorkspace.blend/'), link=False) as (data_from, data_to): # Opens the blend file containing the heightmap material
                data_to.materials += data_from.materials # Adds the heightmap material to the current file
            mat = bpy.data.materials.get("Heightmap_LEVELCREATOR") # Finds the material
            bpy.context.active_object.data.materials.append(mat) # Adds the material to the heightmap
        
        if not ("Heightmapper" in bpy.data.workspaces): # If the Heightmapper workspace is not loaded
            bpy.ops.workspace.append_activate( # Appends the Heightmapper workspace from the .blend file in the addon
                idname='Heightmapper',
                filepath= os.path.dirname(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/heightmapperWorkspace.blend/')
            )
            bpy.ops.object.mode_set(mode='SCULPT', toggle=False) # Enables sculpt mode
            bpy.context.scene.tool_settings.sculpt.lock_x = True
            bpy.context.scene.tool_settings.sculpt.lock_y = True # These prevent the user from sculpting terrain that is impossible to import by only allowing editing vertices vertically.
        else: # If the Heightmapper workspace is loaded
            bpy.context.window.workspace = bpy.data.workspaces['Heightmapper'] # Switches to Heightmapper workspace
            bpy.ops.object.mode_set(mode='SCULPT', toggle=False) # Enables sculpt mode

        for screen in bpy.data.workspaces["Heightmapper"].screens: # This whole part basically just raises the render distance of the Heightmapper workspace
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.clip_end = 10000
                            space.shading.type = "SOLID" # Switches to solid mode

        for t in bpy.data.textures:
            if t.name == "Imported Heightmap":
                bpy.data.textures.remove(bpy.data.textures["Imported Heightmap"]) # Removes any previously imported heightmaps
                
        if os.path.abspath(bpy.path.abspath(bpy.context.scene.importDirectory)).split(".")[0][-3:].find("000") != -1:
            
            tiles = []

            print(f"Complete path: {os.path.abspath(bpy.path.abspath(bpy.context.scene.importDirectory))}")
            templatePath = os.path.abspath(bpy.path.abspath(bpy.context.scene.importDirectory)).split(".")[0].replace("000", "###")

            print(templatePath)
            print("\n")

            with bpy.data.libraries.load(os.path.dirname(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/heightmapperWorkspace.blend/'), link=False) as (data_from, data_to): # Opens the blend file containing the heightmap material
                data_to.node_groups += data_from.node_groups # Adds the compositor node groups to the current file

            bpy.context.scene.use_nodes = True

            for n in bpy.context.scene.node_tree.nodes:
                if n.name == "Render Layers":
                    bpy.context.scene.node_tree.nodes.remove(n)

            groupNode = bpy.context.scene.node_tree.nodes.new(type='CompositorNodeGroup')
            groupNode.node_tree = bpy.data.node_groups["Composite_LEVELCREATOR"]
            bpy.context.scene.node_tree.links.new(groupNode.outputs[0], bpy.context.scene.node_tree.nodes["Composite"].inputs[0])

            convertedFiles = []

            for i in range(16):
                filepath = templatePath.replace("###", f"{i:03}")
                filepath = f"{filepath}.dds"
                
                if needsConverted:
                    filename = os.path.abspath(bpy.path.abspath(bpy.context.scene.importDirectory.replace("000", f"{i:03}"))).split("\\")[-1]
                    print(filename)

                    shutil.copy2(filepath, os.path.abspath(bpy.path.abspath(bpy.context.scene.texconvDirectory)))
                    os.chdir(f"{os.path.abspath(bpy.path.abspath(bpy.context.scene.texconvDirectory))}") # Goes to the directory
                    os.popen(f'texconv {filename} -ft png -f R16_UNORM').read() # Converts the image via command line
                    os.remove(f"{os.path.abspath(bpy.path.abspath(bpy.context.scene.texconvDirectory))}\\{filename}") # Deletes the old DDS

                    convertedFiles.append(filename)

                    image = bpy.data.images.load(f"{bpy.context.scene.texconvDirectory}\\{filename[:-4]}.png") # Loads each image
                else:
                    image = bpy.data.images.load(filepath) # Loads each image
                image.colorspace_settings.name = 'Raw'

                print(templatePath.replace("###", f"{i:03}"))

                tiles.append(image)
                
                imageNode = bpy.context.scene.node_tree.nodes.new(type='CompositorNodeImage')
                imageNode.image = image
                bpy.context.scene.node_tree.links.new(imageNode.outputs[0], groupNode.inputs[i])

            bpy.context.window.workspace = bpy.data.workspaces['Heightmapper'] # Switches to Heightmapper workspace
    
            if not("Camera_LEVELCREATOR" in bpy.data.objects): # If a camera doesn't already exist
                bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

                bpy.ops.object.camera_add(location = [0.0, 0.0, 3000.0], rotation = [0.0, 0.0, 0.0]) # Creates a camera at 3000m above the centre
                cam = bpy.context.active_object
                cam.name = "Camera_LEVELCREATOR"

                bpy.context.view_layer.objects.active = bpy.data.objects["Heightmap_LEVELCREATOR"]
                bpy.ops.object.mode_set(mode="SCULPT", toggle=False)
            else:
                cam = bpy.data.objects["Camera_LEVELCREATOR"]

            oldCamera = bpy.context.scene.camera # Gets the old active camera's name so that other renders aren't messed up
            oldResX = bpy.context.scene.render.resolution_x # Gets the old render resolution so that other renders aren't messed up
            oldResY = bpy.context.scene.render.resolution_y
            oldRenderPath = bpy.context.scene.render.filepath # Gets the old render file path so that other renders aren't messed up

            bpy.context.scene.view_settings.view_transform = 'Raw' # Filmic messes up the colours, so switch to standard instead
            bpy.context.scene.render.image_settings.color_depth = '16' # Switches to 16 bit colour depth (which frontiers uses)

            for o in bpy.data.objects: # Hides all objects from being rendered except for the heightmap
                if o.name != "Heightmap_LEVELCREATOR":
                    o.hide_render = True 

            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    activeRegion = area.spaces.active.region_3d
                    oldView = activeRegion.view_rotation

            bpy.context.scene.camera = bpy.data.objects["Camera_LEVELCREATOR"] # Sets the scene's active camera to the new camera
            cam.location = mathutils.Vector((0, 0, 3000))
            cam.data.type = 'ORTHO' # Sets camera to orthographic
            cam.data.ortho_scale = 4096 # Sets the camera to capture the whole heightmap
            cam.data.clip_end = 5000 # Sets the camera to render in the whole heightmap

            bpy.context.scene.render.resolution_x = 4096 # Sets proper render resolution
            bpy.context.scene.render.resolution_y = 4096

            bpy.ops.render.render(write_still=False) # RENDER!!!!

            bpy.context.scene.use_nodes = False

            bpy.context.scene.camera = oldCamera # Resets the render settings to the old ones so renders are not messed up
            bpy.context.scene.render.resolution_x = oldResX
            bpy.context.scene.render.resolution_y = oldResY
            bpy.context.scene.render.filepath = oldRenderPath

            for o in bpy.data.objects: # Show all objects for renders
                if o.name != "Heightmap_LEVELCREATOR":
                    o.hide_render = False 
            
            image = bpy.data.images["Render Result"]
            image.save_render(filepath=f"{os.path.dirname(bpy.data.filepath)}\ImportedHeightmap_temporary.png")
            image = bpy.data.images.load(f"{os.path.dirname(bpy.data.filepath)}\ImportedHeightmap_temporary.png")
            image.name = "Imported Heightmap"
            image.pack()
            os.remove(f"{os.path.dirname(bpy.data.filepath)}\ImportedHeightmap_temporary.png")

            heightTex = bpy.data.textures.new('Imported Heightmap', type = 'IMAGE') # Creates a new texture
            image.colorspace_settings.name = 'Raw' # Sets colour space to raw, allowing correct compatibility with frontiers heightmaps
            heightTex.image = image # Sets the image in the heightmap texture to the imported image

        else:
            image = bpy.data.images.load(os.path.abspath(bpy.path.abspath(bpy.context.scene.importDirectory)), check_existing=True) # Loads the desired image

            heightTex = bpy.data.textures.new('Imported Heightmap', type = 'IMAGE') # Creates a new texture
            image.colorspace_settings.name = 'Raw' # Sets colour space to raw, allowing correct compatibility with frontiers heightmaps
            heightTex.image = image # Sets the image in the heightmap texture to the imported image
            

        dispMod = bpy.data.objects["Heightmap_LEVELCREATOR"].modifiers.clear() # Removes any other modifiers
        dispMod = bpy.data.objects["Heightmap_LEVELCREATOR"].modifiers.new("Displace", type='DISPLACE') # Adds a displace modifier
        dispMod.texture = bpy.data.textures["Imported Heightmap"] # Adds the heightmap to the displace modifier
        dispMod.mid_level = 0.0 # Makes the heightmap only raise the terrain from the base
        dispMod.strength = 0.4887025 # Lowers the strength of the heightmap

        bpy.ops.object.modifier_apply(modifier="Displace")

        bpy.ops.ed.undo_push() # This is required otherwise Blender crashes if you undo immediately for some reason

        if needsConverted:
            for i in range(len(convertedFiles)):
                filename = convertedFiles[i]
                os.remove(f"{filename[:-4]}.png") # Deletes the old PNG
        
        return {'FINISHED'}
    
class HeightmapperProps(bpy.types.PropertyGroup): # Properties
    bpy.types.Scene.texconvDirectory = bpy.props.StringProperty( # The directory for texconv (the program required to convert heightmaps to DDS correctly)
        name="Directory",
        subtype='DIR_PATH',
        default="",
        description="Path to texconv.exe (this converts your heightmap to DDS if you have it)"
    )
    bpy.types.Scene.isTiles = bpy.props.BoolProperty( # Does the program render the heightmap into tiles?
        name="Create Tiles",
        default=True,
        description="Renders the heightmap as a set of tiles that are the right size to be used in-game"
    )
    bpy.types.Scene.importDirectory = bpy.props.StringProperty( # The path for the heightmap that should be imported
        name="Heightmap",
        subtype='FILE_PATH',
        default="",
        description="Imports a heightmap"
    )
    bpy.types.Scene.fullRes = bpy.props.BoolProperty( # The path for the heightmap that should be imported
        name="Full Resolution",
        default=False,
        description="Uses 100% detail for the heightmap, mostly useful when importing an existing heightmap. REQUIRES A VERY GOOD PC"
    )