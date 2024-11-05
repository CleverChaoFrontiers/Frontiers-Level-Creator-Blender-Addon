import bpy # type: ignore
import webbrowser

class DownloadHedgearcpack(bpy.types.Operator):
    bl_idname = "download.hedgearcpack"
    bl_label = "Download"

    def execute(self, context): 
        webbrowser.open("https://github.com/Radfordhound/HedgeLib/releases/latest/", new=0, autoraise=True)
        return {"FINISHED"}
    
class DownloadHedgeset(bpy.types.Operator):
    bl_idname = "download.hedgeset"
    bl_label = "Download"

    def execute(self, context): 
        webbrowser.open("https://ci.appveyor.com/project/Radfordhound/hedgelib/build/job/dl3b5w0juqivrr6v/artifacts/", new=0, autoraise=True)
        return {"FINISHED"}
    
class DownloadHedgeneedle(bpy.types.Operator):
    bl_idname = "download.hedgeneedle"
    bl_label = "Download"

    def execute(self, context): 
        webbrowser.open("https://ci.appveyor.com/project/Radfordhound/hedgelib/build/job/dl3b5w0juqivrr6v/artifacts/", new=0, autoraise=True)
        return {"FINISHED"}
    

class DownloadBtmesh(bpy.types.Operator):
    bl_idname = "download.btmesh"
    bl_label = "Download"

    def execute(self, context): 
        webbrowser.open("https://github.com/blueskythlikesclouds/btmesh/releases/latest/", new=0, autoraise=True)
        return {"FINISHED"}

class DownloadKnuxtools(bpy.types.Operator):
    bl_idname = "download.knuxtools"
    bl_label = "Download"

    def execute(self, context): 
        webbrowser.open("https://github.com/Knuxfan24/KnuxLib/releases/latest/", new=0, autoraise=True) 
        return {"FINISHED"}

class DownloadModelconverter(bpy.types.Operator):
    bl_idname = "download.modelconverter"
    bl_label = "Download"

    def execute(self, context): 
        webbrowser.open("https://github.com/blueskythlikesclouds/ModelConverter/releases/latest/", new=0, autoraise=True)
        return {"FINISHED"}
    
class DownloadModelfbx(bpy.types.Operator):
    bl_idname = "download.modelfbx"
    bl_label = "Download"

    def execute(self, context): 
        webbrowser.open("https://github.com/DarioSamo/libgens-sonicglvl/tree/master", new=0, autoraise=True)
        return {"FINISHED"}
    
class DownloadTexconv(bpy.types.Operator):
    bl_idname = "download.texconv"
    bl_label = "Download"

    def execute(self, context):
        webbrowser.open("https://github.com/microsoft/DirectXTex/releases/latest/", new=0, autoraise=True) 
        return {"FINISHED"}
    
class DownloadGeditTemplate(bpy.types.Operator):
    bl_idname = "download.gedittemplate"
    bl_label = "Download"

    def execute(self, context):
        webbrowser.open("https://github.com/Ashrindy/AshDumpLib/blob/master/AshDumpLib/HedgehogEngine/BINA/RFL/frontiers.template.hson.json", new=0, autoraise=True) 
        return {"FINISHED"}
    
class Toolpaths(bpy.types.PropertyGroup): # Properties
    bpy.types.Scene.directoryHedgearcpack = bpy.props.StringProperty( # The directory for texconv (the program required to convert heightmaps to DDS correctly)
        name="HedgeArcPack",
        subtype='FILE_PATH',
        default="",
        description="Path to HedgeArcPack"
    )
    bpy.types.Scene.directoryHedgeset = bpy.props.StringProperty( # The directory for texconv (the program required to convert heightmaps to DDS correctly)
        name="HedgeSet",
        subtype='FILE_PATH',
        default="",
        description="Path to HedgeSet"
    )
    bpy.types.Scene.directoryHedgeneedle = bpy.props.StringProperty( # The directory for texconv (the program required to convert heightmaps to DDS correctly)
        name="HedgeNeedle",
        subtype='FILE_PATH',
        default="",
        description="Path to HedgeNeedle"
    )
    bpy.types.Scene.directoryBtmesh = bpy.props.StringProperty( # The directory for texconv (the program required to convert heightmaps to DDS correctly)
        name="btmesh",
        subtype='FILE_PATH',
        default="",
        description="Path to BTmesh"
    )
    bpy.types.Scene.directoryKnuxtools = bpy.props.StringProperty( # The directory for texconv (the program required to convert heightmaps to DDS correctly)
        name="KnuxTools",
        subtype='FILE_PATH',
        default="",
        description="Path to KnuxTools"
    )
    bpy.types.Scene.directoryModelconverter = bpy.props.StringProperty( # The directory for texconv (the program required to convert heightmaps to DDS correctly)
        name="ModelConverter",
        subtype='FILE_PATH',
        default="",
        description="Path to ModelConverter"
    )
    bpy.types.Scene.directoryModelfbx = bpy.props.StringProperty( # The directory for texconv (the program required to convert heightmaps to DDS correctly)
        name="ModelFBX",
        subtype='FILE_PATH',
        default="",
        description="Path to ModelFBX"
    )
    bpy.types.Scene.directoryTexconv = bpy.props.StringProperty( # The directory for texconv (the program required to convert heightmaps to DDS correctly)
        name="texconv",
        subtype='FILE_PATH',
        default="",
        description="Path to texconv"
    )
    bpy.types.Scene.directoryGeditTemplate = bpy.props.StringProperty( # The directory for texconv (the program required to convert heightmaps to DDS correctly)
        name="Gedit Template",
        subtype='FILE_PATH',
        default="",
        description="Path to Gedit Template"
    )