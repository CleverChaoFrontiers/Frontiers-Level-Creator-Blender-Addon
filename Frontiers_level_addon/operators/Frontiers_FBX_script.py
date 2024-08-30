
import bpy
import random
from math import radians
import pathlib
from pathlib import Path
import os

# Defines the operator to Export FBX
class exportFBXfrontiers(bpy.types.Operator):
    bl_idname = "object.export_fbx"
    bl_label = "Export FBX for Frontiers"

    def execute (self, context):
        collection_name = context.scene.FrontiersFBX.FBXcollection_name
        col = collection_name
        if bpy.context.mode != 'OBJECT': #sets to object mode if mode not object
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        if col is not None:
            for obj in col.objects:
                obj.select_set(True)
            # Open the FBX export window
            bpy.ops.export_scene.fbx('INVOKE_DEFAULT', use_selection = True, apply_scale_options = 'FBX_SCALE_UNITS', use_visible = True, add_leaf_bones=False,mesh_smooth_type='FACE')
        else:
            self.report({"WARNING"}, f"Collection{collection_name} not found")
            return {'CANCELLED'}
        return {'FINISHED'}

#creates a name window and saves the name when called
class FrontiersFBX(bpy.types.PropertyGroup):
    FBXcollection_name: bpy.props.PointerProperty(
        name="FBX Collection",
        description = "Collection with terrain to export as an FBX",
        type=bpy.types.Collection
    )