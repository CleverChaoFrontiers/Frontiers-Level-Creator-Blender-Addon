import bpy

#creates a name window and saves the name when called
class FrontiersDisplaceGroup(bpy.types.PropertyGroup):
    displace_object: bpy.props.PointerProperty(
        name="Object",
        description = "Object to displace across curve",
        type=bpy.types.Object
    )
    displace_curve: bpy.props.PointerProperty(
        name="Curve",
        description = "Curve to displace objects on",
        type=bpy.types.Object
    )
    displace_length: bpy.props.FloatProperty(
        name="Length",
        description = "Length betwe",
        default=8
    )
    displace_forwarddirection: bpy.props.EnumProperty(
        items=[("Pos_X_raildirec","X","X axis"),("Pos_Y_raildirec","Y","Y axis"),("negative_X_raildirec","-X","-X axis"),("negative_Y_raildirec","-Y","-Y axis")], 
        name="Forward axis", 
        description = "Axis that point forward along the path"
    )
def displace_on_curve(curve_obj, object_obj, Length=1,forward_direction = "Pos_X_raildirec"):
    # Get the location of the curve object
    curve_location = curve_obj.location
    spline = curve_obj.data.splines[0]
    # Add Follow Path constraint
    if forward_direction == "Pos_X_raildirec":
        trackaxis = 'FORWARD_X'
    elif forward_direction == "Pos_Y_raildirec":
        trackaxis = 'FORWARD_Y'
    elif forward_direction == "negative_X_raildirec":
        trackaxis = 'TRACK_NEGATIVE_X'
    elif forward_direction == "negative_Y_raildirec":
        trackaxis = 'TRACK_NEGATIVE_Y'
    else:
        print(f"wrong value. forward_direction = {forward_direction}")
        trackaxis = 'FORWARD_X'
    splinelength = 0.0
    if spline.type != "BEZIER":
        points_in_curve = spline.points
    else:
        points_in_curve = spline.bezier_points
    for i in range(len(points_in_curve) - 1):
        if i != len(points_in_curve):
            segment = (points_in_curve[i+1].co - points_in_curve[i].co).length
            splinelength += segment
    # Set the target curve
    LastLength = 0
    print(splinelength)
    print(round((splinelength/Length)))
    # Duplicate the object once outside the loop
    object_obj.select_set(True)
    bpy.context.view_layer.objects.active = object_obj
    #bpy.ops.object.duplicate(linked=0,mode='TRANSLATION')
    obj = bpy.context.view_layer.objects.active

    for i in range(round((splinelength/Length))):
        # Reuse the duplicated object
        bpy.ops.object.select_all(action='DESELECT')
        obj_copy = obj.copy()
        bpy.context.collection.objects.link(obj_copy)
        obj_copy.select_set(True)
        bpy.context.view_layer.objects.active = obj_copy
        bpy.ops.object.location_clear(clear_delta=False)
        # Add Follow Path constraint to the duplicate
        bpy.ops.object.constraint_add(type='FOLLOW_PATH')
        constraint = obj_copy.constraints[-1]  # Get the last constraint added, which is the Follow Path constraint
        constraint.target = curve_obj
        constraint.use_fixed_location = True
        constraint.use_curve_follow = True
        constraint.forward_axis = trackaxis
        constraint.up_axis = 'UP_Z'

        # Set the offset to follow the curve until reaching the position of the current_point
        constraint.offset_factor = i*Length/splinelength

        # Apply the modifier
        bpy.ops.constraint.apply(constraint=constraint.name)
class OBJECT_OT_DisplaceOnCurve(bpy.types.Operator):
    bl_label = "Displace on Curve"
    bl_idname = "object.displace_on_curve"
    bl_options = {'UNDO'}
    def execute(self, context):
        #bpy.ops.ed.undo_push(message="Set undo step")
        displacecurve_obj = context.scene.FrontiersDisplaceGroup.displace_curve
        frontiersdisplaceobject = context.scene.FrontiersDisplaceGroup.displace_object
        Length = context.scene.FrontiersDisplaceGroup.displace_length
        forwarddirection = context.scene.FrontiersDisplaceGroup.displace_forwarddirection
        displace_on_curve(displacecurve_obj, frontiersdisplaceobject, Length,forwarddirection)
        return {'FINISHED'}