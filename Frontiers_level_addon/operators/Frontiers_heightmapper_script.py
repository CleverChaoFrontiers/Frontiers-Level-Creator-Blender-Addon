import bpy # type: ignore (Supresses the warning associated with it being a Blender library)
import os
import time
import shutil
import json

def updateprogress(advance):
    if (4, 0, 0) < bpy.app.version:
        bpy.types.Scene.heightmapprogress =  bpy.types.Scene.heightmapprogress + advance
        bpy.types.Scene.heightmapprogresstext = f"LOADING ({round(bpy.types.Scene.heightmapprogress * 100)}%)"
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        return

class HeightmapperOperator(bpy.types.Operator):
    bl_idname = "heightmapper.heightmapper"
    bl_label = "Open Heightmapper"
    bl_description = "Creates a heightmap if there is none, or opens the editor for the existing one"

    if (4, 0, 0) < bpy.app.version:
        bpy.types.Scene.heightmapprogress = 0.0 # Resets the progress bar
        bpy.types.Scene.heightmapprogresstext = "- - -"

    def execute(self, context): # When button is pressed
        startTime = time.time()
        mapsize = int(bpy.context.scene.mapsize)
        if "[FLC] Heightmap" in bpy.data.objects:
            bpy.data.objects["[FLC] Heightmap"].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects["[FLC] Heightmap"]
        else:
            if (4, 0, 0) < bpy.app.version:
                bpy.types.Scene.heightmapprogress = 0.0

            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection # Deselects all collections
            try:
                bpy.context.view_layer.objects[0].select_set(True)
                bpy.context.view_layer.objects.active = bpy.context.view_layer.objects[0] # Selects a random object so that object mode can be switched to
                bpy.ops.object.mode_set(mode="OBJECT", toggle=False) # Changes to object mode
            except Exception as e:
                print(e)

            bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0), scale=(mapsize, mapsize, mapsize), enter_editmode=True) # Create plane
            plane = bpy.context.selected_objects[0] # Get plane
            plane.name = "[FLC] Heightmap" # Rename plane
            bpy.ops.transform.resize(value=(mapsize/2, mapsize/2, mapsize/2))
            mapsizesubds = {1024: 3, 2048: 7, 4096: 15, 8192: 15, 16384: 15} # Detail limit due to blender running out of memory
            bpy.ops.mesh.subdivide(number_cuts=mapsizesubds[mapsize]) # Subdivide plane
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False) # Change back to object mode
            bpy.ops.object.modifier_add(type='MULTIRES') # Adds multires modifier
            updatemilestones = [1, 1, 5, 16, 77]
            for i in range(8):
                bpy.ops.object.multires_subdivide(modifier="Multires", mode='LINEAR') # Subdivides the plane further with multires
                if i >= 3:
                    updateprogress(updatemilestones[i-3] / 100)
            nonsculptdriver = bpy.context.object.modifiers["Multires"].driver_add("levels").driver
            nonsculptdriver.type = "AVERAGE"
            var = nonsculptdriver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "lodnormal"
            var.targets[0].id_type = "SCENE"
            var.targets[0].id = bpy.context.scene
            var.targets[0].data_path = "lodnormal"
            sculptdriver = bpy.context.object.modifiers["Multires"].driver_add("sculpt_levels").driver
            sculptdriver.type = "AVERAGE"
            var = sculptdriver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "lodsculpt"
            var.targets[0].id_type = "SCENE"
            var.targets[0].id = bpy.context.scene
            var.targets[0].data_path = "lodsculpt"

        print(f"\n\nHEIGHTMAP OBJECT COMPLETE ----------\nTIME ELAPSED: {time.time() - startTime}")
        previousTime = time.time()

        with bpy.data.libraries.load(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/heightmapper_resources.blend') as (data_from, data_to):
            if not "Heightmap Edit" in bpy.data.workspaces:
                data_to.workspaces = data_from.workspaces
            if not all(x in bpy.data.materials for x in ["[FLC] Heightmap-Preview", "[FLC] Heightmap-Render", "[FLC] Heightmap-Normal"]):
                data_to.materials = data_from.materials

        heightdriver = bpy.data.materials["[FLC] Heightmap-Preview"].node_tree.nodes["Height"].inputs[0].driver_add("default_value").driver
        heightdriver.type = "AVERAGE"
        var = heightdriver.variables.new()
        var.type = 'SINGLE_PROP'
        var.name = "mapheight"
        var.targets[0].id_type = "SCENE"
        var.targets[0].id = bpy.context.scene
        var.targets[0].data_path = "mapheight"

        heightdriver = bpy.data.materials["[FLC] Heightmap-Render"].node_tree.nodes["Height"].inputs[1].driver_add("default_value").driver
        heightdriver.type = "AVERAGE"
        var = heightdriver.variables.new()
        var.type = 'SINGLE_PROP'
        var.name = "mapheight"
        var.targets[0].id_type = "SCENE"
        var.targets[0].id = bpy.context.scene
        var.targets[0].data_path = "mapheight"

        bpy.context.window.workspace = bpy.data.workspaces['Heightmap Edit']
        bpy.context.scene.tool_settings.sculpt.lock_x = True
        bpy.context.scene.tool_settings.sculpt.lock_y = True # These prevent the user from sculpting terrain that is impossible to import by only allowing editing vertices vertically.

        bpy.data.materials["[FLC] Heightmap-Preview"].use_fake_user = 1
        bpy.data.materials["[FLC] Heightmap-Render"].use_fake_user = 1
        bpy.data.materials["[FLC] Heightmap-Normal"].use_fake_user = 1

        if len(bpy.data.objects["[FLC] Heightmap"].data.materials) == 0:
            bpy.data.objects["[FLC] Heightmap"].data.materials.append(None)
        
        bpy.data.objects["[FLC] Heightmap"].data.materials[0] = bpy.data.materials["[FLC] Heightmap-Preview"]

        print(f"\n\nMATERIAL ADDING COMPLETE ----------\nTIME ELAPSED: {time.time() - previousTime}")

        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.heightmapprogress = 1.0
            bpy.types.Scene.heightmapprogresstext = "DONE"

        print(f"\n\nHEIGHTMAP CREATION COMPLETE ----------\nTIME ELAPSED: {time.time() - startTime}")
        
        return {'FINISHED'}
    
class HeightmapperExport(bpy.types.Operator):
    bl_idname = "heightmapper.export"
    bl_label = "Export Heightmap"
    bl_description = "Exports the Heightmap to the folder the .blend is in"

    def execute(self, context): # When button is pressed
        startTime = time.time()
        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.heightmapprogress = 0.0
        updateprogress(0.0)

        mapsize = int(bpy.context.scene.mapsize)
        mapheight = bpy.context.scene.mapheight

        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        directoryTexconv = os.path.abspath(bpy.path.abspath(preferences.directoryTexconv)) # Gets HedgeSet path from preferences
        if not "[FLC] Heightmap" in bpy.data.objects:
            def heightmapError(self, context):
                self.layout.label(text="No Heightmap found!") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(heightmapError, title = "Export Failed", icon = "IMPORT") # Makes the popup appear
            if (4, 0, 0) < bpy.app.version:
                bpy.types.Scene.heightmapprogress = 1.0
                bpy.types.Scene.heightmapprogresstext = "CANCELLED"
            return {'FINISHED'}
        if (bpy.data.filepath == ""):
            def saveError(self, context):
                self.layout.label(text=".blend file is not saved!") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(saveError, title = "Export Failed", icon = "IMPORT") # Makes the popup appear
            if (4, 0, 0) < bpy.app.version:
                bpy.types.Scene.heightmapprogress = 1.0
                bpy.types.Scene.heightmapprogresstext = "CANCELLED"
            return {'FINISHED'}
        if preferences.directoryTexconv == "": # Gives an error if a program is missing
            def missingProgramError(self, context):
                self.layout.label(text=f"The filepath for texconv is not set. \nPlease set the path in Settings.") # Tells the user about the missing prorgrams
            bpy.context.window_manager.popup_menu(missingProgramError, title = "Program missing", icon = "QUESTION") # Makes the popup appear
            if (4, 0, 0) < bpy.app.version:
                bpy.types.Scene.heightmapprogress = 1.0
                bpy.types.Scene.heightmapprogresstext = "CANCELLED"
            return {'FINISHED'} # Cancels the operation

        bpy.data.objects["[FLC] Heightmap"].data.materials[0] = bpy.data.materials["[FLC] Heightmap-Render"]
        bpy.data.objects["[FLC] Heightmap"].hide_render = False

        tempfolder = f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\"
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
        updateprogress(0.55)

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
            os.chdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(directoryTexconv)))}") # Goes to the directory
            os.popen(f'texconv -f R16_UNORM -xlum -y "{tempfolder}\\{f}" -o "{tempfolder[:-1]}"').read() # Converts the image via command line
            shutil.copy2(f"{tempfolder}\\{f[:-4]}.dds", f"{os.path.dirname(bpy.data.filepath)}") # Copies the DDSs to the blend file's folder
        

        bpy.data.objects["[FLC] Heightmap"].data.materials[0] = bpy.data.materials["[FLC] Heightmap-Normal"]

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
        updateprogress(0.35)

        print(f"\n\nRENDER COMPLETE ----------\nTIME ELAPSED: {time.time() - previousTime}")
        previousTime = time.time()

        image = bpy.data.images["Render Result"] # Gets the Rendered image
        image.file_format = 'PNG' # Sets the file format
        try:
            image.save_render(filepath=f"{tempfolder}Heightmap_nrm.png") # Outputs the image straight to the temporary folder
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

        for f in os.listdir(tempfolder):
            if "nrm" in f:
                os.chdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(directoryTexconv)))}") # Goes to the directory
                os.popen(f'texconv -f R8G8B8A8_UNORM -xlum -y "{tempfolder}\\{f}" -o "{tempfolder[:-1]}"').read() # Converts the image via command line
                shutil.copy2(f"{tempfolder}\\{f[:-4]}.dds", f"{os.path.dirname(bpy.data.filepath)}") # Copies the DDSs to the blend file's folder
            else:
                os.chdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(directoryTexconv)))}") # Goes to the directory
                os.popen(f'texconv -f R16_UNORM -xlum -y "{tempfolder}\\{f}" -o "{tempfolder[:-1]}"').read() # Converts the image via command line
                shutil.copy2(f"{tempfolder}\\{f[:-4]}.dds", f"{os.path.dirname(bpy.data.filepath)}") # Copies the DDSs to the blend file's folder

        shutil.rmtree(tempfolder)

        updateprogress(0.1)

        print(f"\n\nCONVERTING COMPLETE ----------\nTIME ELAPSED: {time.time() - previousTime}")

        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.heightmapprogress = 1.0
            bpy.types.Scene.heightmapprogresstext = "DONE"

        print(f"\n\nHEIGHTMAP EXPORT COMPLETE ----------\nTIME ELAPSED: {time.time() - startTime}")

        return {'FINISHED'}

class HeightmapperImport(bpy.types.Operator):
    bl_idname = "heightmapper.import"
    bl_label = "Import Heightmap"
    bl_description = "Imports a Heightmap"
    bl_options = {"UNDO"}

    def execute(self, context): # When button is pressed
        startTime = time.time()
        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.heightmapprogress = 0.0
        updateprogress(0.0)

        previoustime = time.time()

        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        directoryTexconv = os.path.abspath(bpy.path.abspath(preferences.directoryTexconv)) # Gets HedgeSet path from preferences
        if (bpy.data.filepath == ""):
            def saveError(self, context):
                self.layout.label(text=".blend file is not saved!") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(saveError, title = "Import Failed", icon = "IMPORT") # Makes the popup appear
            return {'FINISHED'}
        if preferences.directoryTexconv == "": # Gives an error if a program is missing
            def missingProgramError(self, context):
                self.layout.label(text=f"The filepath for texconv is not set. \nPlease set the path in Settings.") # Tells the user about the missing prorgrams
            bpy.context.window_manager.popup_menu(missingProgramError, title = "Program missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation
        if bpy.context.scene.importDirectory == "": # Gives an error if a program is missing
            def directoryError(self, context):
                self.layout.label(text=f"The import directory is not set.") # Tells the user about the missing prorgrams
            bpy.context.window_manager.popup_menu(directoryError, title = "Filepath missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation
        mapsize = 4

        heightfolder = os.path.abspath(bpy.path.abspath(bpy.context.scene.importDirectory))
        tempfolder = f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\levelcreator-temp\\"
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

        if (4, 0, 0) < bpy.app.version:
            bpy.types.Scene.heightmapprogress = 1.0
            bpy.types.Scene.heightmapprogresstext = "DONE"

        print(f"\n\nHEIGHTMAP IMPORT COMPLETE ----------\nTIME ELAPSED: {time.time() - startTime}")

        return {'FINISHED'}
    
class SplatmapOperator(bpy.types.Operator):
    bl_idname = "heightmapper.splatmap"
    bl_label = "Open Splatmap Edit"
    bl_description = "Opens Splatmap Edit"

    def execute(self, context): # When button is pressed
        if not "[FLC] Heightmap" in bpy.data.objects:
            def heightmapError(self, context):
                self.layout.label(text="No Heightmap found!") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(heightmapError, title = "Splatmap Failed", icon = "ERROR") # Makes the popup appear
            return {'FINISHED'}
        if not "[FLC] Splatmap" in bpy.data.materials:
            def splatmapError(self, context):
                self.layout.label(text="No Splatmap settings found!") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(splatmapError, title = "Splatmap Failed", icon = "ERROR") # Makes the popup appear
            return {'FINISHED'}
        
        with bpy.data.libraries.load(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/heightmapper_resources.blend') as (data_from, data_to):
            if not "Splatmap Edit" in bpy.data.workspaces:
                data_to.workspaces = data_from.workspaces

        if not "[FLC] Splatmap" in bpy.data.images:
            splatmapimg = bpy.data.images.new("[FLC] Splatmap", 1024, 1024, alpha=False)
        else:
            splatmapimg = bpy.data.images["[FLC] Splatmap"]
        
        if not "[FLC] Scale" in bpy.data.images:
            scaleimg = bpy.data.images.new("[FLC] Scale", 2048, 2048, alpha=False)
        else:
            scaleimg = bpy.data.images["[FLC] Scale"]
        
        if not "[FLC] Area" in bpy.data.images:
            areaimg = bpy.data.images.new("[FLC] Area", 2048, 2048, alpha=False)
        else:
            areaimg = bpy.data.images["[FLC] Area"]

        bpy.data.materials["[FLC] Splatmap"].node_tree.nodes["SplatNode"].image = splatmapimg
        bpy.data.materials["[FLC] Splatmap"].node_tree.nodes["SplatNode"].image.colorspace_settings.name = "Non-Color"
        bpy.data.materials["[FLC] Scale"].node_tree.nodes["scale"].image = scaleimg
        bpy.data.materials["[FLC] Area"].node_tree.nodes["area"].image = areaimg

        bpy.data.materials["[FLC] Splatmap"].use_fake_user = 1
        bpy.data.materials["[FLC] Scale"].use_fake_user = 1
        bpy.data.materials["[FLC] Area"].use_fake_user = 1

        if len(bpy.data.objects["[FLC] Heightmap"].data.materials) == 0:
            bpy.data.objects["[FLC] Heightmap"].data.materials.append(None)

        bpy.data.objects["[FLC] Heightmap"].data.materials[0] = bpy.data.materials["[FLC] Splatmap"]
        
        bpy.context.window.workspace = bpy.data.workspaces['Splatmap Edit']
        bpy.data.brushes["TexDraw"].curve_preset = 'CONSTANT'
        bpy.context.scene.tool_settings.image_paint.normal_angle = 90
        bpy.context.object.active_material.paint_active_slot = 0

        return {'FINISHED'}
    
class SplatmapExport(bpy.types.Operator):
    bl_idname = "heightmapper.splatmapexport"
    bl_label = "Export Splatmap"
    bl_description = "Exports the Splatmap to the folder the .blend is in"

    def execute(self, context): # When button is pressed
        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        directoryTexconv = os.path.abspath(bpy.path.abspath(preferences.directoryTexconv)) # Gets HedgeSet path from preferences
        if not "[FLC] Splatmap" in bpy.data.images:
            def splatmapError(self, context):
                self.layout.label(text="No Splatmap found!") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(splatmapError, title = "Splatmap Failed", icon = "ERROR") # Makes the popup appear
            return {'FINISHED'}
        if (bpy.data.filepath == ""):
            def saveError(self, context):
                self.layout.label(text=".blend file is not saved!") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(saveError, title = "Import Failed", icon = "IMPORT") # Makes the popup appear
            return {'FINISHED'}
        if preferences.directoryTexconv == "": # Gives an error if a program is missing
            def missingProgramError(self, context):
                self.layout.label(text=f"The filepath for texconv is not set. \nPlease set the path in Settings.") # Tells the user about the missing prorgrams
            bpy.context.window_manager.popup_menu(missingProgramError, title = "Program missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation

        image = bpy.data.images["[FLC] Splatmap"]
        image.update()
        image.size
        image.filepath_raw = f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\splatmap.png"
        image.file_format = 'PNG'
        image.save()

        image = bpy.data.images["[FLC] Scale"]
        image.update()
        image.size
        image.filepath_raw = f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\scale.png"
        image.file_format = 'PNG'
        image.save()

        image = bpy.data.images["[FLC] Area"]
        image.update()
        image.size
        image.filepath_raw = f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\area.png"
        image.file_format = 'PNG'
        image.save()

        os.chdir(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(directoryTexconv)))}") # Goes to the directory
        os.popen(f'texconv -f R8_UNORM -xlum -y "{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\splatmap.png" -o "{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}"').read() # Converts the image via command line
        os.remove(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\splatmap.png")
        os.popen(f'texconv -f BC4_UNORM -xlum -y "{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\scale.png" -o "{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}"').read() # Converts the image via command line
        os.remove(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\scale.png")
        os.popen(f'texconv -f R8_UNORM -xlum -y "{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\area.png" -o "{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}"').read() # Converts the image via command line
        os.remove(f"{os.path.abspath(bpy.path.abspath(os.path.dirname(bpy.data.filepath)))}\\area.png")

        return {'FINISHED'}

class SplatmapImport(bpy.types.Operator):
    bl_idname = "heightmapper.splatmapimport"
    bl_label = "Import Splatmap"
    bl_description = "Imports a Splatmap"
    bl_options = {"UNDO"}

    def execute(self, context): # When button is pressed
        splatmapcmnDirectory = bpy.context.scene.splatmapcmnDirectory
        if not "[FLC] Heightmap" in bpy.data.objects:
            def heightmapError(self, context):
                self.layout.label(text="No Heightmap found!") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(heightmapError, title = "Splatmap Failed", icon = "ERROR") # Makes the popup appear
            return {'FINISHED'}
        if not "[FLC] Splatmap" in bpy.data.materials:
            def splatmapError(self, context):
                self.layout.label(text="No Splatmap settings found!") # Sets the label of the popup
            bpy.context.window_manager.popup_menu(splatmapError, title = "Splatmap Failed", icon = "ERROR") # Makes the popup appear
            return {'FINISHED'}
        if splatmapcmnDirectory == "":
            def directoryError(self, context):
                self.layout.label(text=f"The import directory is not set.") # Tells the user about the missing prorgrams
            bpy.context.window_manager.popup_menu(directoryError, title = "Filepath missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation
        with bpy.data.libraries.load(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Other/heightmapper_resources.blend') as (data_from, data_to):
            if not "Splatmap Edit" in bpy.data.workspaces:
                data_to.workspaces = data_from.workspaces
        
        bpy.data.materials["[FLC] Splatmap"].use_fake_user = 1
        bpy.data.objects["[FLC] Heightmap"].data.materials[0] = bpy.data.materials["[FLC] Splatmap"]
        
        if "[FLC] Splatmap" in bpy.data.images:
            bpy.data.images["[FLC] Splatmap"].name = "[FLC] Splatmap-OLD"
            bpy.data.images["[FLC] Splatmap"].use_fake_user = 0
        if "[FLC] Scale" in bpy.data.images:
            bpy.data.images["[FLC] Scale"].name = "[FLC] Scale-OLD"
            bpy.data.images["[FLC] Scale"].use_fake_user = 0
        if "[FLC] Area" in bpy.data.images:
            bpy.data.images["[FLC] Area"].name = "[FLC] Area-OLD"
            bpy.data.images["[FLC] Area"].use_fake_user = 0

        for f in os.listdir(os.path.abspath(bpy.path.abspath(splatmapcmnDirectory))):
            if f.endswith("splatmap.dds"):
                splatmapimg = bpy.data.images.load(f"{splatmapcmnDirectory}\\{f}", check_existing = True)
                splatmapimg.name = "[FLC] Splatmap"
                splatmapimg.use_fake_user = 1
                splatmapimg.pack()

                bpy.data.materials["[FLC] Splatmap"].node_tree.nodes["SplatNode"].image = splatmapimg
                bpy.data.materials["[FLC] Splatmap"].node_tree.nodes["SplatNode"].image.colorspace_settings.name = "Non-Color"
            if f.endswith("scale.dds"):
                scaleimg = bpy.data.images.load(f"{splatmapcmnDirectory}\\{f}", check_existing = True)
                scaleimg.name = "[FLC] Scale"
                scaleimg.use_fake_user = 1
                scaleimg.pack()

                bpy.data.materials["[FLC] Scale"].node_tree.nodes["scale"].image = scaleimg
            if f.endswith("area.dds"):
                areaimg = bpy.data.images.load(f"{splatmapcmnDirectory}\\{f}", check_existing = True)
                areaimg.name = "[FLC] Area"
                areaimg.use_fake_user = 1
                areaimg.pack()

                bpy.data.materials["[FLC] Area"].node_tree.nodes["area"].image = areaimg

        bpy.context.window.workspace = bpy.data.workspaces['Splatmap Edit']
        bpy.data.brushes["TexDraw"].curve_preset = 'CONSTANT'
        bpy.context.scene.tool_settings.image_paint.normal_angle = 90
        bpy.context.object.active_material.paint_active_slot = 0
        try:
            bpy.context.space_data.uv_editor.show_texpaint = False
        except AttributeError:
            pass


        return {'FINISHED'}

class SplatmapSettingImport(bpy.types.Operator):
    bl_idname = "heightmapper.splatmapsettingimport"
    bl_label = "Import Splatmap Template"
    bl_description = "Imports the .terrain-material containing indexes for the textures"
    bl_options = {"UNDO"}

    def execute(self, context): # When button is pressed
        splatmapdata = json.loads(bpy.context.scene.loadedsplatmap)
        splatmapheightDirectory = bpy.context.scene.splatmapheightDirectory
        preferences = bpy.context.preferences.addons[__package__.split(".")[0]].preferences # Gets preferences
        directoryKnuxtools = os.path.abspath(bpy.path.abspath(preferences.directoryKnuxtools)) # Gets KnuxTools path from preferences
        if preferences.directoryKnuxtools == "": # Gives an error if a program is missing
            def missingProgramError(self, context):
                self.layout.label(text=f"The filepath for KnuxTools is not set. \nPlease set the path in Settings.") # Tells the user about the missing prorgrams
            bpy.context.window_manager.popup_menu(missingProgramError, title = "Program missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation
        if splatmapheightDirectory == "":
            def directoryError(self, context):
                self.layout.label(text=f"The import directory is not set.") # Tells the user about the missing prorgrams
            bpy.context.window_manager.popup_menu(directoryError, title = "Filepath missing", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation
        
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
        
        if not "[FLC] Splatmap" in bpy.data.materials:
            material = bpy.data.materials.new("[FLC] Splatmap")
        else:
            material = bpy.data.materials["[FLC] Splatmap"]
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

        if not "[FLC] Scale" in bpy.data.materials:
            scalemat = bpy.data.materials.new("[FLC] Scale")
        else:
            scalemat = bpy.data.materials["[FLC] Scale"]
        scalemat.use_nodes = True
        nodes = scalemat.node_tree.nodes
        for i in nodes:
            nodes.remove(i)
        outputnode = nodes.new('ShaderNodeOutputMaterial')
        imgnode = nodes.new('ShaderNodeTexImage')
        imgnode.image = None
        imgnode.name = "scale"
        scalemat.node_tree.links.new(imgnode.outputs[0], outputnode.inputs[0])

        if not "[FLC] Area" in bpy.data.materials:
            areamat = bpy.data.materials.new("[FLC] Area")
        else:
            areamat = bpy.data.materials["[FLC] Area"]
        areamat.use_nodes = True
        nodes = areamat.node_tree.nodes
        for i in nodes:
            nodes.remove(i)
        outputnode = nodes.new('ShaderNodeOutputMaterial')
        imgnode = nodes.new('ShaderNodeTexImage')
        imgnode.image = None
        imgnode.name = "area"
        areamat.node_tree.links.new(imgnode.outputs[0], outputnode.inputs[0])
        
        bpy.context.scene.loadedsplatmap = json.dumps(splatmapdata)

        return {'FINISHED'}

class SplatmapFavourite(bpy.types.Operator):
    bl_idname = "heightmapper.splatmapfavourite"
    bl_label = "Add Favourite"
    bl_description = "Adds the ID to the list below"
    bl_options = {"UNDO"}

    def execute(self, context): # When button is pressed
        text = ""
        splatmapid = bpy.context.scene.splatmapid
        splatmapdata = json.loads(bpy.context.scene.loadedsplatmap)
        splatmapfavourites = json.loads(bpy.context.scene.splatmapfavourites)

        if splatmapdata["name"] == "":
            def splatmapError(self, context):
                self.layout.label(text=f"No splatmap settings loaded") # Tells the user about the missing prorgrams
            bpy.context.window_manager.popup_menu(splatmapError, title = "No Splatmap", icon = "QUESTION") # Makes the popup appear
            return {'FINISHED'} # Cancels the operation
        
        if splatmapid in splatmapfavourites:
            splatmapfavourites.pop(splatmapfavourites.index(splatmapid))
        else:
            splatmapfavourites.append(splatmapid)

        entries = []
        print(splatmapdata["data"])
        for f in splatmapfavourites:
            for d in splatmapdata["data"]:
                if d["index"] == f:
                    entries.append(f'#{f} [{d["type"]}]')
                    break
        text = ", ".join(entries)
        bpy.context.scene.splatmapfavouritetext = text
        
        bpy.context.scene.loadedsplatmap = json.dumps(splatmapdata)
        bpy.context.scene.splatmapfavourites = json.dumps(splatmapfavourites)

        return {'FINISHED'}

class SplatmapSet(bpy.types.Operator):
    bl_idname = "heightmapper.splatmapset"
    bl_label = "Set Brush"
    bl_description = "Sets the brush to use the correct splatmap colour"
    bl_options = {"UNDO"}

    bpy.types.Scene.splatmappreviewscale = 1.0

    def execute(self, context): # When button is pressed
        splatmapdata = json.loads(bpy.context.scene.loadedsplatmap)

        splatmapid = bpy.context.scene.splatmapid
        colour = ((1/255) * splatmapid)
        bpy.data.brushes["TexDraw"].color = (colour, colour, colour)
        bpy.data.brushes["TexDraw"].use_accumulate = True
        bpy.data.brushes["TexDraw"].use_paint_antialiasing = False
        try:
            bpy.context.space_data.uv_editor.show_texpaint = False
        except AttributeError:
            pass

        if "[FLC] Splatmap-Preview" not in bpy.data.textures:
            bpy.data.textures.new("[FLC] Splatmap-Preview", type="IMAGE")
            bpy.data.textures["[FLC] Splatmap-Preview"].use_fake_user = 1
        for d in splatmapdata["data"]:
            if d["index"] == splatmapid:
                bpy.data.textures["[FLC] Splatmap-Preview"].image = bpy.data.images[f'{d["image"]}.dds']
                bpy.data.textures["[FLC] Splatmap-Preview"].use_fake_user = 1
                return {'FINISHED'}
        def materialError(self, context):
            self.layout.label(text=f"No material found with the corresponding ID") # Tells the user about the missing prorgrams
        bpy.context.window_manager.popup_menu(materialError, title = "No Material", icon = "QUESTION") # Makes the popup appear
        return {'FINISHED'} # Cancels the operation
    
class HeightmapperProps(bpy.types.PropertyGroup): # Properties
    bpy.types.Scene.importDirectory = bpy.props.StringProperty( # The path for the heightmap that should be imported
        name="Heightmap",
        subtype='DIR_PATH',
        default="",
        description="Folder to import from"
    )
    bpy.types.Scene.splatmapheightDirectory = bpy.props.StringProperty( # The path for the heightmap that should be imported
        name="Splatmap",
        subtype='DIR_PATH',
        default="",
        description="Folder to import from"
    )
    bpy.types.Scene.splatmapcmnDirectory = bpy.props.StringProperty( # The path for the heightmap that should be imported
        name="Splatmap",
        subtype='DIR_PATH',
        default="",
        description="Folder to import from"
    )
    bpy.types.Scene.splatmapid = bpy.props.IntProperty(
        name="Splatmap ID",
        default=0,
        description="ID of the material to paint with"
    )
    bpy.types.Scene.loadedsplatmap = bpy.props.StringProperty(
        name="loadedsplatmap",
        default='{"name": "No Splatmap Loaded", "filepath": "", "data": []}',
        description='Stores loaded splatmap data as a string so it can be saved to the .blend'
    )
    bpy.types.Scene.splatmapfavouritetext = bpy.props.StringProperty(
        name="splatmapfavouritetext",
        default="No Favourites",
        description="Stores splatmap favourites display text"
    )
    bpy.types.Scene.splatmapfavourites = bpy.props.StringProperty(
        name="splatmapfavourites",
        default="[]",
        description="Stores splatmap favourites as a string so it can be saved to the .blend"
    )
    bpy.types.Scene.lodnormal = bpy.props.IntProperty(
        name="Non-sculpting Level of Detail",
        default=5,
        min=2,
        max=8,
        description="Changes the level of detail the heightmap preview has"
    )
    bpy.types.Scene.lodsculpt = bpy.props.IntProperty(
        name="Sculpting Level of Detail",
        default=7,
        min=2,
        max=8,
        description="[WARNING] Can cause artifacts, glitches and unimportable geometry.\nRecommended to only raise detail as you sculpt, don't lower it afterwards unless you know what you're doing!"
    )
    bpy.types.Scene.mapsize = bpy.props.EnumProperty(
        name="Heightmap Size",
        items=[
            ("1024", "Islet [1024m²]", "1/16th Island Size"),
            ("2048", "Small Island [2048m²]", "Quarter Island Size"),
            ("4096", "Island [4096m²]", "Standard Island Size"),
            ("8192", "Big Island [8192m²]", "EXPERIMENTAL"),
            ("16384", "(DOESN'T WORK) Contient [16384m²]", "Crashes the game lmao, just in case someone finds a fix"),
            ("32768", "(DOESN'T WORK) Little Planet [32768m²]", "Crashes the game lmao, just in case someone finds a fix")
        ],
        default="4096",
        description="[WARNING] Requires RFL modification\n(wXrXX.rfl> needleFxSceneData> stageConfig> terrain> worldSize)\n"
    )
    bpy.types.Scene.mapheight = bpy.props.IntProperty(
        name="Heightmap Height",
        default=1000,
        description="[WARNING] Requires RFL modification\n(wXrXX.rfl> needleFxSceneData> stageConfig> terrain> precision> heightRange)"
    )
