from queue import Empty
import bpy

class OBJECT_OT_FrontiersCamConnect(bpy.types.Operator):
    bl_label = "Connect Blender Camera"
    bl_idname = "object.frontiers_cam_connect"
    bl_description = "Connect the blender camera to active camera object"
    bl_options = {'UNDO'}
    def execute(self, context):
        obj = bpy.context.view_layer.objects.active

        if "FrontiersCamera" in obj:
            if bpy.context.scene.camera != None:
                cam = bpy.context.scene.camera
            else:
                bpy.ops.object.camera_add()
                cam = bpy.context.scene.camera
            if cam.animation_data is not None and cam.animation_data.drivers: 
                for driver in cam.animation_data.drivers:
                    cam.driver_remove(driver.data_path)
            if cam.data.animation_data is not None and cam.data.animation_data.drivers: 
                for driver in cam.data.animation_data.drivers:
                    cam.data.driver_remove(driver.data_path)
            if cam.parent != None:
                cam.parent = None
            if cam.constraints:
                # Iterate through all constraints and remove them
                for constraint in cam.constraints:
                    cam.constraints.remove(constraint)
            for emptobj in bpy.data.collections[obj.users_collection[0].name].objects:
                if "FrontiersCameraEmpty" in emptobj:
                    bpy.data.objects.remove(emptobj, do_unlink=True)
            for mod in obj.modifiers:
                if mod.type == 'NODES':
                    modifier = mod
                    break
            if not modifier:
                print("No Geometry Nodes modifier found.")
                return
            if obj.name.startswith("CameraFollow") or obj.name.startswith("CameraRailForwardView"):
                    if obj.name.startswith("CameraRailForwardView"):
                        cam.parent = obj
                    location_dict = {"r": f'modifiers["{modifier.name}"]["Input_17"]',"theta": f'modifiers["{modifier.name}"]["Input_19"]',"phi":f'modifiers["{modifier.name}"]["Input_18"]'}
                    driver_locx = cam.driver_add('location', 0).driver
                    driver_locy = cam.driver_add('location', 1).driver
                    driver_locz = cam.driver_add('location', 2).driver
                    driver_rotx = cam.driver_add('rotation_euler', 0).driver
                    driver_roty = cam.driver_add('rotation_euler', 1).driver
                    driver_rotz = cam.driver_add('rotation_euler', 2).driver
                    driver_fov = cam.data.driver_add(f'lens').driver
                    for driver in [driver_locx,driver_locy,driver_locz,driver_rotx,driver_roty,driver_rotz]:
                        if driver != driver_roty:
                            for key in location_dict:
                            
                                value = location_dict[key]
                                var = driver.variables.new()
                                var.name = key
                                var.type = 'SINGLE_PROP'
                                target = var.targets[0]
                                target.id_type = 'OBJECT'
                                target.id = obj
                                target.data_path = value
                        else:
                            var = driver.variables.new()
                            var.name = "zrot"
                            var.type = 'SINGLE_PROP'
                            target = var.targets[0]
                            target.id_type = 'OBJECT'
                            target.id = obj
                            target.data_path = 'modifiers["GeometryNodes"]["Input_25"]'
                    #     FOV Driver
                    fov_var = driver_fov.variables.new()
                    fov_var.name = "fov_var"
                    fov_var.type = 'SINGLE_PROP'
                    target = fov_var.targets[0]
                    target.id_type = 'OBJECT'
                    target.id = obj
                    target.data_path = f'modifiers["{modifier.name}"]["Input_30"]'
                    #     Set the driver expression
                    driver_locx.expression = "r * sin(radians(phi)) *cos(radians(theta))"
                    driver_locy.expression = "-r * cos(radians(phi))*cos(radians(theta))"
                    driver_locz.expression = "r*sin(radians(theta))"
                    driver_rotx.expression = "radians(90-theta)"
                    driver_roty.expression = "-radians(zrot)"
                    driver_rotz.expression = "radians(phi)"
                    driver_fov.expression = "fov_var"
                    #   Set Constraints
                    if obj.name.startswith("CameraFollow"):
                        location_constraint = cam.constraints.new(type='COPY_LOCATION')
                        location_constraint.target = obj
                        location_constraint.use_offset = True
            elif obj.name.startswith("CameraFix"):

                    fix_empty = bpy.data.objects.new("empty", None)
                    bpy.data.collections[obj.users_collection[0].name].objects.link(fix_empty)
                    fix_empty.empty_display_size = 1
                    fix_empty.empty_display_type = 'ARROWS'   
                    fix_empty["FrontiersCameraEmpty"] = True
                    #fix_empty.users_collection = obj.users_collection
                    location_dict = {"x": [f'modifiers["{modifier.name}"]["Input_20"][0]',"var"],"y": [f'modifiers["{modifier.name}"]["Input_20"][2]',"-var"],"z":[f'modifiers["{modifier.name}"]["Input_20"][1]',"var"]}
                    # driver_locx = fix_empty.driver_add('location', 0).driver
                    # driver_locy = fix_empty.driver_add('location', 1).driver
                    # driver_locz = fix_empty.driver_add('location', 2).driver
                    driver_fov = cam.data.driver_add(f'lens').driver
                    index = 0
                    for key in location_dict:
                        driver = fix_empty.driver_add('location', index).driver
                        value = location_dict[key]
                        var = driver.variables.new()
                        var.name = "var"
                        var.type = 'SINGLE_PROP'
                        target = var.targets[0]
                        target.id_type = 'OBJECT'
                        target.id = obj
                        target.data_path = location_dict[key][0]
                        driver.expression = location_dict[key][1]
                        index += 1
                    #     FOV Driver
                    fov_var = driver_fov.variables.new()
                    fov_var.name = "fov_var"
                    fov_var.type = 'SINGLE_PROP'
                    target = fov_var.targets[0]
                    target.id_type = 'OBJECT'
                    target.id = obj
                    target.data_path = f'modifiers["{modifier.name}"]["Input_28"]'
                    driver_fov.expression = fov_var.name
                    #   Set Constraints
                    location_constraint = cam.constraints.new(type='COPY_LOCATION')
                    location_constraint.target = obj
                    track_constraint = cam.constraints.new(type='TRACK_TO')
                    track_constraint.target = fix_empty
            elif obj.name.startswith("CameraRailSideView"):
                    location_dict = {"r": f'modifiers["{modifier.name}"]["Input_17"]',"theta": f'modifiers["{modifier.name}"]["Input_18"]',"elevate":f'modifiers["{modifier.name}"]["Input_28"]'}
                    driver_locx = cam.driver_add('location', 0).driver
                    driver_locy = cam.driver_add('location', 1).driver
                    driver_locz = cam.driver_add('location', 2).driver
                    driver_fov = cam.data.driver_add(f'lens').driver
                    for driver in [driver_locx,driver_locy,driver_locz]:
                        for key in location_dict:
                            value = location_dict[key]
                            var = driver.variables.new()
                            var.name = key
                            var.type = 'SINGLE_PROP'
                            target = var.targets[0]
                            target.id_type = 'OBJECT'
                            target.id = obj
                            target.data_path = value
                    #     FOV Driver
                    fov_var = driver_fov.variables.new()
                    fov_var.name = "fov_var"
                    fov_var.type = 'SINGLE_PROP'
                    target = fov_var.targets[0]
                    target.id_type = 'OBJECT'
                    target.id = obj
                    target.data_path = f'modifiers["{modifier.name}"]["Input_33"]'
                    #     Set the driver expression
                    driver_locx.expression = "r*sin(radians(theta))"
                    driver_locy.expression = "-r*cos(radians(theta))"
                    driver_locz.expression = "elevate"
                    driver_fov.expression = "fov_var"
                    #   Set Constraints
                    location_constraint = cam.constraints.new(type='COPY_LOCATION')
                    location_constraint.target = obj
                    location_constraint.use_offset = True
                    track_constraint = cam.constraints.new(type='TRACK_TO')
                    track_constraint.target = obj
            elif obj.name.startswith("CameraPan"):
                location_constraint = cam.constraints.new(type='COPY_LOCATION')
                location_constraint.target = obj
                driver_fov = cam.data.driver_add(f'lens').driver
                #     FOV Driver
                fov_var = driver_fov.variables.new()
                fov_var.name = "fov_var"
                fov_var.type = 'SINGLE_PROP'
                target = fov_var.targets[0]
                target.id_type = 'OBJECT'
                target.id = obj
                target.data_path = f'modifiers["{modifier.name}"]["Input_24"]'
        else:
            self.report({"WARNING"}, f"Object is not a compatible Camera object.")
        return {'FINISHED'}