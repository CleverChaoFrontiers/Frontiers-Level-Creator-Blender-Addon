bl_info = {
    "name": "Frontiers Level Creator",
    "author": "CleverChao, LightningWyvern, Piranha Mayhem",
    "version": (3, 9, 0),#REMEMBER TO CHANGE THIS
    "blender": (3, 0, 0),
    "category": "Object",
    "location": "View3D > toolbar > Tool > Frontiers Level Creator",
    "description": "Tools used for creating level mods for Sonic Frontiers"}

import bpy # type: ignore
import os
from bpy.types import Operator, AddonPreferences, WindowManager # type: ignore
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty # type: ignore

from .operators.Frontiers_gedit_script import PrintCoordinatesOperator
from .operators.Frontiers_gedit_script import FrontiersCoords

from .operators.Frontiers_FBX_script import exportFBXfrontiers
from .operators.Frontiers_FBX_script import FrontiersFBX

from .operators.Frontiers_terrain_script import TerrainScriptfrontiers
from .operators.Frontiers_terrain_script import FrontiersTerrProps

from .operators.Frontiers_rail_script import PrintRailsOperator
from .operators.Frontiers_rail_script import FrontiersRails
from .operators.Frontiers_rail_script import SetBevelOperator

from .operators.Frontiers_Import_script import HSONImportOperator
from .operators.Frontiers_Import_script import FrontiersImportProperties

from .operators.Frontiers_heightmapper_script import HeightmapperOperator
from .operators.Frontiers_heightmapper_script import HeightmapperRender
from .operators.Frontiers_heightmapper_script import HeightmapperImport
from .operators.Frontiers_heightmapper_script import HeightmapperProps

from .operators.Frontiers_parameter_script import OBJECT_PT_JsonParameters,JsonParametersPropertyGroup,JsonParameterListItem, parametersListvalues,OBJECT_OT_AddListItem,OBJECT_OT_RemoveListItem
from .operators.Frontiers_displaceCurve_script import FrontiersDisplaceGroup, OBJECT_OT_DisplaceOnCurve

from .operators.Frontiers_toolpaths import DownloadHedgearcpack, DownloadHedgeset, DownloadHedgeneedle, DownloadBtmesh, DownloadKnuxtools, DownloadModelconverter, DownloadModelfbx, DownloadTexconv
from .operators.Frontiers_quick_export import QexportSettings, CompleteExport, ExportTerrain, ExportObjects, ExportHeightmap, RepackAll, Settings

from .operators.Frontiers_density_script import OBJECT_OT_duplicate_link_with_nodes,OBJECT_OT_FrontiersPointCloudExport,FrontiersDensityProperties,DensityPanel,remove_densityscatter,DensityPaintPanel,DensityAddOperator,DensitySubtractOperator,DensityForwardGroupOperator,DensityBackwardsGroupOperator,DensityAssignIndex

from .operators.Frontiers_quick_import import QimportSettings, CompleteImport, ImportTerrain, ImportObjects, ImportHeightmap, SettingsImp

from .operators.Frontiers_camera_script import OBJECT_OT_FrontiersCamConnect
class LevelCreatorPreferences(AddonPreferences):
    bl_idname = __package__
    
    # Defines a Property to store the directory path
    CustomTemplatePath: bpy.props.StringProperty(  # type: ignore
        name="Directory Path",
        subtype='DIR_PATH',
        description="Directory to read files from"
    )

    directoryHedgearcpack: bpy.types.Scene.directoryHedgearcpack = bpy.props.StringProperty(
        name="HedgeArcPack",
        subtype='FILE_PATH',
        default="",
        description="Path to HedgeArcPack"
    )
    directoryHedgeset: bpy.types.Scene.directoryHedgeset = bpy.props.StringProperty(
        name="HedgeSet",
        subtype='FILE_PATH',
        default="",
        description="Path to HedgeSet"
    )
    directoryHedgeneedle: bpy.types.Scene.directoryHedgeneedle = bpy.props.StringProperty(
        name="HedgeNeedle",
        subtype='FILE_PATH',
        default="",
        description="Path to HedgeNeedle"
    )
    directoryBtmesh: bpy.types.Scene.directoryBtmesh = bpy.props.StringProperty(
        name="btmesh",
        subtype='FILE_PATH',
        default="",
        description="Path to BTmesh"
    )
    directoryKnuxtools: bpy.types.Scene.directoryKnuxtools = bpy.props.StringProperty(
        name="KnuxTools",
        subtype='FILE_PATH',
        default="",
        description="Path to KnuxTools"
    )
    directoryModelconverter: bpy.types.Scene.directoryModelconverter = bpy.props.StringProperty(
        name="ModelConverter",
        subtype='FILE_PATH',
        default="",
        description="Path to ModelConverter"
    )
    directoryModelfbx: bpy.props.StringProperty( # type: ignore (this ONE SINGLE property does not work the same as the others because Blender (I DO NOT KNOW WHY??) )
        name="ModelFBX",
        subtype='FILE_PATH',
        default="",
        description="Path to ModelFBX"
    )
    directoryTexconv: bpy.types.Scene.directoryTexconv = bpy.props.StringProperty(
        name="texconv",
        subtype='FILE_PATH',
        default="",
        description="Path to texconv"
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Additional Templates")
        row = box.row()
        row.prop(self, "CustomTemplatePath")

        # Add "Tool Filepaths" section label
        box = layout.box()
        row = box.row()
        row.label(text="Tool Filepaths")

        # Add directory paths field and download buttons
        row = box.row()
        row.prop(self, "directoryHedgearcpack", text="HedgeArcPack")
        row.operator("download.hedgearcpack", text="", icon="IMPORT") 

        row = box.row()
        row.prop(self, "directoryHedgeset", text="HedgeSet")
        row.operator("download.hedgeset", text="", icon="IMPORT")

        row = box.row()
        row.prop(self, "directoryHedgeneedle", text="HedgeNeedle")
        row.operator("download.hedgeneedle", text="", icon="IMPORT")

        row = box.row()
        row.prop(self, "directoryBtmesh", text="btmesh")
        row.operator("download.btmesh", text="", icon="IMPORT")

        row = box.row()
        row.prop(self, "directoryKnuxtools", text="KnuxTools")
        row.operator("download.knuxtools", text="", icon="IMPORT")

        row = box.row()
        row.prop(self, "directoryModelconverter", text="ModelConverter")
        row.operator("download.modelconverter", text="", icon="IMPORT")

        row = box.row()
        row.prop(self, "directoryModelfbx", text="ModelFBX")
        row.operator("download.modelfbx", text="", icon="IMPORT")

        row = box.row()
        row.prop(self, "directoryTexconv", text="texconv")
        row.operator("download.texconv", text="", icon="IMPORT")

class OBJECT_OT_addon_prefs(Operator):
    """Display preferences"""
    bl_idname = "object.addon_prefs"
    bl_label = "Add-on Preferences Example"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        info = ("Custom Template directory: %s" %
                (addon_prefs.CustomTemplatePath))

        self.report({'INFO'}, info)
        print(info)

        return {'FINISHED'}
class FrontiersAddonPanel(bpy.types.Panel):
    bl_label = "Frontiers Export Tools"
    bl_idname = "PT_PrintCoordinatesPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Frontiers Level Creator'
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="version 3.9.5 PLAYTEST")#REMEMBER TO CHANGE THIS

class QuickExport(bpy.types.Panel):
    bl_label = "Quick Export"
    bl_idname = "PT_QuickExport"
    bl_parent_id = "PT_PrintCoordinatesPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator("qexport.completeexport", text="Export All", icon="EXPORT")
        layout.operator("qexport.exportterrain", text="Terrain", icon="CUBE")
        layout.prop(context.scene, "trrCollection", text="Terrain")
        layout.operator("qexport.exportobjects", text="Objects", icon="PIVOT_INDIVIDUAL")
        layout.prop(context.scene, "objCollection", text="Objects")
        layout.operator("qexport.exportheightmap", text="Heightmap", icon="FCURVE")
        layout.operator("qexport.repackall", text="Repack All", icon="FOLDER_REDIRECT")
        layout.operator("qexport.settings", text="Settings", icon="PREFERENCES")
        layout.label(text="Mod Settings")
        row = layout.row()
        row.prop(context.scene, "modDir", text="Mod")
        row = layout.row()
        row.prop(context.scene, "worldId", text="World")

class QuickImport(bpy.types.Panel):
    bl_label = "Quick Import"
    bl_idname = "PT_QuickImport"
    bl_parent_id = "PT_PrintCoordinatesPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator("qimport.completeimport", text="Import All", icon="IMPORT")
        layout.operator("qimport.importterrain", text="Terrain", icon="CUBE")
        layout.operator("qimport.importobjects", text="Objects", icon="PIVOT_INDIVIDUAL")
        layout.operator("qimport.importheightmap", text="Heightmap", icon="FCURVE")
        layout.operator("qimport.settings", text="Settings", icon="PREFERENCES")
        layout.label(text="Import Settings")
        row = layout.row()
        row.prop(context.scene, "worldDir", text="World Folder")

class QuickExportAdvanced(bpy.types.Panel):
    bl_label = "Advanced"
    bl_idname = "PT_QuickExportAdvanced"
    bl_parent_id = "PT_QuickExport"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        
        # Add label
        layout = self.layout
        layout.prop(context.scene, "noPack", text="Don't Repack")
        layout.prop(context.scene, "noVis", text="No Visual Terrain")
        layout.prop(context.scene, "noCol", text="No Collision")
        layout.label(text="Don't Clear")
        layout.prop(context.scene, "eoTerrain", text="Terrain")
        layout.prop(context.scene, "eoObjects", text="Objects")
        layout.label(text="Keep Files")
        layout.prop(context.scene, "keepMat", text="Materials")
        layout.prop(context.scene, "keepTex", text="Textures")
        layout.prop(context.scene, "keepHgt", text="Heightmap")
        layout.prop(context.scene, "keepPcm", text="pcmodel")
        layout.prop(context.scene, "keepPcl", text="pccol")
        layout.prop(context.scene, "keepDen", text="Density")


class Coord_panel(bpy.types.Panel):
    bl_label = "Coordinates and HSON code"
    bl_idname = "PT_CoordSubPanel"
    bl_parent_id = "PT_PrintCoordinatesPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        tool = context.scene.FrontiersCoords
        layout.prop(tool, "collection_name")
        layout.operator("object.print_coordinates")

class Rail_panel(bpy.types.Panel):
    bl_label = "Path HSON code"
    bl_idname = "PT_RailSubPanel"
    bl_parent_id = "PT_PrintCoordinatesPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}
    def draw(self, context):
        layout = self.layout
        railtool = context.scene.FrontiersRails
        layout.prop(railtool, "objPath_check")
        layout.prop(railtool, "straightPath_Check")
        layout.prop(railtool, "RotationPath_Check")
        layout.operator("object.set_bevel_operator")
        layout.prop(railtool, "Railcoll_name")
        layout.prop(railtool, "Railnode_startindex")
        layout.operator("object.rail_script")
        
class FBX_panel(bpy.types.Panel):
    bl_label = "Terrain FBX model"
    bl_idname = "PT_FBXSubPanel"
    bl_parent_id = "PT_PrintCoordinatesPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}
    def draw(self, context):
        layout = self.layout
        fbxtool = context.scene.FrontiersFBX
        layout.prop(fbxtool, "FBXcollection_name")
        layout.operator("object.export_fbx")
        
class Terrain_panel(bpy.types.Panel):
    bl_label = ".pcmodel/.pccol Template"
    bl_idname = "PT_TerrSubPanel"
    bl_parent_id = "PT_PrintCoordinatesPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}
    
    
    def draw(self, context):
        layout = self.layout
        terraintool = context.scene.FrontiersTerrProps
        layout.prop(terraintool, "collision_check")
        layout.prop(terraintool, "cyberspace_check")
        sub = layout.row()
        sub.enabled = not context.scene.FrontiersTerrProps.cyberspace_check
        sub.prop(terraintool, "transform_coords")
        sub.prop(terraintool, "rotation_coords")

        layout.prop(terraintool, "json_name")
        layout.operator("object.terrain_script")
class FrontiersExperimentalPanel(bpy.types.Panel):
    bl_label = "Frontiers Other Tools Panel"
    bl_idname = "PT_EXPPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Frontiers Level Creator'
    
    def draw(self, context):
        layout = self.layout
class HSONImporterPanel(bpy.types.Panel):
    bl_label = "Frontiers GEDIT/HSON Importer"
    bl_idname = "OBJECT_PT_hson_importer"
    bl_parent_id = "PT_EXPPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Frontiers Level Creator"
    bl_options = {'DEFAULT_CLOSED'}


    def draw(self, context):
        layout = self.layout
        layout.label(text="version 1.0.0")#VERSION INFO

        # Add directory path field
        row = layout.row()
        row.prop(context.scene, "hson_directory", text="HSON Path")

        # Add assets library path field
        row = layout.row()
        row.prop(context.scene, "hson_assets_library_path", text="Blend Assets")

        # Add collection name field
        row = layout.row()
        row.prop(context.scene, "hson_collection_name", text="Collection Name")

        # Add checkbox for creating collections
        row = layout.row()
        row.prop(context.scene, "hson_create_collections", text="HSON Collections")

        # Add import button
        row = layout.row()
        row.operator("object.hson_import", text="Import Objects")     

class HeightmapperPanel(bpy.types.Panel):
    bl_label = "Heightmapper"
    bl_idname = "OBJECT_PT_heightmapper"
    bl_parent_id = "PT_EXPPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Frontiers Level Creator"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="v1.1.0") # VERSION INFO

        # Add open heightmapper button
        row = layout.row()
        row.operator("heightmapper.heightmapper", text="Open Heightmapper", icon="FCURVE") 


class HeightmapperRenderPanel(bpy.types.Panel):
    bl_label = "Render"
    bl_idname = "OBJECT_PT_heightmapperrender"
    bl_parent_id = "OBJECT_PT_heightmapper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        
        # Add "Rendering" section label
        layout = self.layout
        layout.label(text="Rendering")

        # Add render heightmap button
        row = layout.row()
        row.operator("heightmapper.render", text="Render Heightmap", icon="OUTLINER_DATA_CAMERA") 

        # Add tiles checkbox
        row = layout.row()
        row.prop(context.scene, "isTiles", text="Create Tiles")

        # Add directory path field
        row = layout.row()
        row.prop(context.scene, "texconvDirectory", text="Texconv file path")

class HeightmapperImportPanel(bpy.types.Panel):
    bl_label = "Import"
    bl_idname = "OBJECT_PT_heightmapperimport"
    bl_parent_id = "OBJECT_PT_heightmapper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        
        # Add "Import" section label
        layout = self.layout
        layout.label(text="Import")

        # Add directory path field
        row = layout.row()
        row.prop(context.scene, "importDirectory", text="Heightmap")

        # Add import heightmap button
        row = layout.row()
        row.operator("heightmapper.import", text="Import Heightmap", icon="IMPORT") 

class HeightmapperAdvancedPanel(bpy.types.Panel):
    bl_label = "Advanced"
    bl_idname = "OBJECT_PT_heightmapperadvanced"
    bl_parent_id = "OBJECT_PT_heightmapper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        
        # Add "Import" section label
        layout = self.layout
        layout.label(text="Advanced")

        # Add tiles checkbox
        row = layout.row()
        row.prop(context.scene, "fullRes", text="Full Resolution ⚠")

class DisplaceOnCurvePanel(bpy.types.Panel):
    bl_label = "Place objects along curve"
    bl_idname = "OBJECT_PT_displace_on_curve"
    bl_parent_id = "PT_EXPPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Frontiers Level Creator'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        frontiersdiscurve = context.scene.FrontiersDisplaceGroup

        layout.prop_search(frontiersdiscurve, "displace_object", bpy.data, "objects")
        layout.prop_search(frontiersdiscurve, "displace_curve", bpy.data, "objects")
        layout.prop(frontiersdiscurve, "displace_length")
        layout.prop(frontiersdiscurve, "displace_forwarddirection")
        layout.operator("object.displace_on_curve")
class CameraConnectPanel(bpy.types.Panel):
    bl_label = "Connect Camera to camera object"
    bl_idname = "OBJECT_PT_cam_connect_frontiers"
    bl_parent_id = "PT_EXPPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Frontiers Level Creator'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator("object.frontiers_cam_connect")
preview_collections = {} #This one is for the density script
def enum_previews_from_directory_items(self, context): #Function that finds the thumbnails
    """EnumProperty callback"""
    enum_items = []
    if context is None:
        return enum_items
    World_check = context.scene.FrontiersDensityProperties.Frontiers_Density_World
    wm = context.window_manager
    script_dir = os.path.dirname(os.path.abspath(__file__)) # Finds path to the folder this script is in [DO NOT TOUCH]
    blend_file_path = bpy.data.filepath # Finds file path of Blender file
    blend_dir = os.path.dirname(blend_file_path) # Gets the name of the directory the Blender file is in
    path_dir = os.path.join(blend_dir,script_dir)
    #Set up compatible objects depending on the files in template file
    directories = {
        "density_Kronos": r"density\Frontiers density pack\Thumbnails\kronos",
        "density_Aries": r"density\Frontiers density pack\Thumbnails\aries",
        "density_Chaos": r"density\Frontiers density pack\Thumbnails\chaos",
        "density_SkySanctuary": r"density\Frontiers density pack\Thumbnails\skysanctuary",
        "density_GreenHill": r"density\Frontiers density pack\Thumbnails\greenhill",
        "density_ChemicalPlant": r"density\Frontiers density pack\Thumbnails\chemicalplant",
        "density_Highway": r"density\Frontiers density pack\Thumbnails\highway"
    }
    Thumbnail_pathname = directories.get(World_check, "")
    directory = os.path.join(path_dir, Thumbnail_pathname) #sets the file path to the thumbnails

    # Get the preview collection (defined in register func).
    pcoll = preview_collections["main"]

    if directory == pcoll.Frontiers_Density_thumbnail_dir:
        return pcoll.Frontiers_Density_thumbnail

    print("Scanning directory: %s" % directory)

    if directory:
        print("found")
        # Scan the directory for png files
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".jpg"):
                image_paths.append(fn)
        print(image_paths)
        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.Frontiers_Density_thumbnail = enum_items
    pcoll.Frontiers_Density_thumbnail_dir = directory
    return pcoll.Frontiers_Density_thumbnail





def register():#registers the addon when checked in the addon menu
    import bpy # type: ignore
    bpy.utils.register_class(FrontiersAddonPanel)
    bpy.utils.register_class(FrontiersExperimentalPanel)
    
    bpy.utils.register_class(QuickExport)
    bpy.utils.register_class(QuickExportAdvanced)
    bpy.utils.register_class(QuickImport)

    #register Addon preferences
    bpy.utils.register_class(OBJECT_OT_addon_prefs)
    bpy.utils.register_class(LevelCreatorPreferences)

    #register Coords script
    bpy.utils.register_class(Coord_panel)
    bpy.utils.register_class(PrintCoordinatesOperator)
    bpy.utils.register_class(FrontiersCoords)
    bpy.types.Scene.FrontiersCoords = bpy.props.PointerProperty(type=FrontiersCoords)
    #register Rail script
    bpy.utils.register_class(PrintRailsOperator)
    bpy.utils.register_class(FrontiersRails)
    bpy.utils.register_class(Rail_panel)    
    bpy.utils.register_class(SetBevelOperator)
    bpy.types.Scene.FrontiersRails = bpy.props.PointerProperty(type=FrontiersRails)
    #register FBX Script
    bpy.utils.register_class(FBX_panel)
    bpy.utils.register_class(exportFBXfrontiers)
    bpy.utils.register_class(FrontiersFBX)
    bpy.types.Scene.FrontiersFBX = bpy.props.PointerProperty(type=FrontiersFBX)
    #register Terrain Script
    bpy.utils.register_class(Terrain_panel)
    bpy.utils.register_class(TerrainScriptfrontiers)
    bpy.utils.register_class(FrontiersTerrProps)
    bpy.types.Scene.FrontiersTerrProps = bpy.props.PointerProperty(type=FrontiersTerrProps)
    #register Import Script
    bpy.utils.register_class(HSONImporterPanel)
    bpy.utils.register_class(HSONImportOperator)
    bpy.utils.register_class(FrontiersImportProperties)
    bpy.types.Scene.FrontiersImportProperties = bpy.props.PointerProperty(type=FrontiersImportProperties)
    #register Heightmapper Script
    bpy.utils.register_class(HeightmapperPanel)
    bpy.utils.register_class(HeightmapperOperator)
    bpy.utils.register_class(HeightmapperRender)
    bpy.utils.register_class(HeightmapperRenderPanel)
    bpy.utils.register_class(HeightmapperImport)
    bpy.utils.register_class(HeightmapperImportPanel)
    bpy.utils.register_class(HeightmapperAdvancedPanel)
    bpy.utils.register_class(HeightmapperProps)
    #register Parameter Script
    bpy.utils.register_class(OBJECT_PT_JsonParameters)
    bpy.utils.register_class(parametersListvalues)
    bpy.utils.register_class(JsonParameterListItem)#added
    bpy.utils.register_class(JsonParametersPropertyGroup)
    bpy.utils.register_class(OBJECT_OT_AddListItem)
    bpy.utils.register_class(OBJECT_OT_RemoveListItem)
    bpy.types.Object.json_parameters = bpy.props.CollectionProperty(type=JsonParametersPropertyGroup)
    bpy.types.Scene.parameters_active_index = bpy.props.IntProperty()
    #register displace on curve script
    bpy.utils.register_class(FrontiersDisplaceGroup)
    bpy.types.Scene.FrontiersDisplaceGroup = bpy.props.PointerProperty(type=FrontiersDisplaceGroup)
    bpy.utils.register_class(OBJECT_OT_DisplaceOnCurve)
    bpy.utils.register_class(DisplaceOnCurvePanel)


    # Tool paths
    bpy.utils.register_class(DownloadHedgearcpack)
    bpy.utils.register_class(DownloadHedgeset)
    bpy.utils.register_class(DownloadHedgeneedle)
    bpy.utils.register_class(DownloadBtmesh)
    bpy.utils.register_class(DownloadKnuxtools)
    bpy.utils.register_class(DownloadModelconverter)
    bpy.utils.register_class(DownloadModelfbx)
    bpy.utils.register_class(DownloadTexconv)
    # Quick Export (I am sincerely sorry for all of these unnecessary classes)
    bpy.utils.register_class(CompleteExport)
    bpy.utils.register_class(ExportTerrain)
    bpy.utils.register_class(ExportObjects)
    bpy.utils.register_class(ExportHeightmap)
    bpy.utils.register_class(RepackAll)
    bpy.utils.register_class(Settings)
    bpy.utils.register_class(QexportSettings)

    #DENSITY STUFF: THIS IS A LOT MORE THAN NORMAL SO BE WARNED

    bpy.utils.register_class(OBJECT_OT_duplicate_link_with_nodes)
    bpy.utils.register_class(OBJECT_OT_FrontiersPointCloudExport)
    WindowManager.Frontiers_Density_thumbnail = EnumProperty(
        items=enum_previews_from_directory_items,
    )
    import bpy.utils.previews # type: ignore
    pcoll = bpy.utils.previews.new()
    pcoll.Frontiers_Density_thumbnail_dir = ""
    pcoll.Frontiers_Density_thumbnail = ()

    preview_collections["main"] = pcoll
    bpy.utils.register_class(FrontiersDensityProperties)
    bpy.types.Scene.FrontiersDensityProperties = bpy.props.PointerProperty(type=FrontiersDensityProperties)
    bpy.utils.register_class(remove_densityscatter)
    bpy.utils.register_class(DensityPanel)
    bpy.utils.register_class(DensityPaintPanel)
    bpy.utils.register_class(DensityAddOperator)
    bpy.utils.register_class(DensitySubtractOperator)
    bpy.utils.register_class(DensityForwardGroupOperator)
    bpy.utils.register_class(DensityBackwardsGroupOperator)
    bpy.utils.register_class(DensityAssignIndex)


    # Quick Import
    bpy.utils.register_class(CompleteImport)
    bpy.utils.register_class(ImportTerrain)
    bpy.utils.register_class(ImportObjects)
    bpy.utils.register_class(ImportHeightmap)
    bpy.utils.register_class(SettingsImp)
    bpy.utils.register_class(QimportSettings)

    # Camera connect
    bpy.utils.register_class(OBJECT_OT_FrontiersCamConnect)
    bpy.utils.register_class(CameraConnectPanel)
def unregister():#Uninstall the addon when dechecked in the addon menu
    bpy.utils.unregister_class(FrontiersAddonPanel)
    bpy.utils.unregister_class(FrontiersExperimentalPanel)
    
    bpy.utils.unregister_class(QuickExport)
    bpy.utils.unregister_class(QuickExportAdvanced)
    bpy.utils.unregister_class(QuickImport)

    #unregister Addon preferences
    bpy.utils.unregister_class(OBJECT_OT_addon_prefs)
    bpy.utils.unregister_class(LevelCreatorPreferences)
    #unregister Coords script
    bpy.utils.unregister_class(Coord_panel)
    bpy.utils.unregister_class(PrintCoordinatesOperator)
    bpy.utils.unregister_class(FrontiersCoords)
    del bpy.types.Scene.FrontiersCoords
    #unregister Rail script
    bpy.utils.unregister_class(PrintRailsOperator)
    bpy.utils.unregister_class(FrontiersRails)
    bpy.utils.unregister_class(SetBevelOperator)
    del bpy.types.Scene.FrontiersRails
    #unregister FBX Script
    bpy.utils.unregister_class(FBX_panel)
    bpy.utils.unregister_class(exportFBXfrontiers)
    bpy.utils.unregister_class(FrontiersFBX)
    del bpy.types.Scene.FrontiersFBX
    #unregister Terrain Script
    bpy.utils.unregister_class(Terrain_panel)
    bpy.utils.unregister_class(TerrainScriptfrontiers)
    bpy.utils.unregister_class(FrontiersTerrProps)
    del bpy.types.Scene.FrontiersTerrProps
    #unregister Import Script
    bpy.utils.unregister_class(HSONImporterPanel)
    bpy.utils.unregister_class(HSONImportOperator)
    bpy.utils.unregister_class(FrontiersImportProperties)
    del bpy.types.Scene.FrontiersImportProperties
    #unregister Heightmapper Script
    bpy.utils.unregister_class(HeightmapperPanel)
    bpy.utils.unregister_class(HeightmapperOperator)
    bpy.utils.unregister_class(HeightmapperRender)
    bpy.utils.unregister_class(HeightmapperRenderPanel)
    bpy.utils.unregister_class(HeightmapperImport)
    bpy.utils.unregister_class(HeightmapperImportPanel)
    bpy.utils.unregister_class(HeightmapperAdvancedPanel)
    bpy.utils.unregister_class(HeightmapperProps)
    #unregister Parameter Script
    bpy.utils.unregister_class(JsonParameterListItem)#added
    bpy.utils.unregister_class(OBJECT_PT_JsonParameters)
    bpy.utils.unregister_class(parametersListvalues)
    bpy.utils.unregister_class(JsonParametersPropertyGroup)
    bpy.utils.unregister_class(OBJECT_OT_AddListItem)
    bpy.utils.unregister_class(OBJECT_OT_RemoveListItem)
    del bpy.types.Object.json_parameters
    del bpy.types.Scene.parameters_active_index
    #unregister displace on curve script
    bpy.utils.unregister_class(OBJECT_OT_DisplaceOnCurve)
    bpy.utils.unregister_class(DisplaceOnCurvePanel)
    bpy.utils.unregister_class(FrontiersDisplaceGroup)
    del bpy.types.Scene.FrontiersDisplaceGroup
    #Tool paths
    bpy.utils.unregister_class(DownloadHedgearcpack)
    bpy.utils.unregister_class(DownloadHedgeset)
    bpy.utils.unregister_class(DownloadHedgeneedle)
    bpy.utils.unregister_class(DownloadBtmesh)
    bpy.utils.unregister_class(DownloadKnuxtools)
    bpy.utils.unregister_class(DownloadModelconverter)
    bpy.utils.unregister_class(DownloadModelfbx)
    bpy.utils.unregister_class(DownloadTexconv)
    # Quick Export
    bpy.utils.unregister_class(CompleteExport)
    bpy.utils.unregister_class(ExportTerrain)
    bpy.utils.unregister_class(ExportObjects)
    bpy.utils.unregister_class(ExportHeightmap)
    bpy.utils.unregister_class(RepackAll)
    bpy.utils.unregister_class(Settings)
    bpy.utils.unregister_class(QexportSettings)
    
    #Density
    bpy.utils.unregister_class(OBJECT_OT_duplicate_link_with_nodes)
    bpy.utils.unregister_class(OBJECT_OT_FrontiersPointCloudExport)
    from bpy.types import WindowManager # type: ignore

    del WindowManager.Frontiers_Density_thumbnail

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    bpy.utils.unregister_class(remove_densityscatter)
    bpy.utils.unregister_class(DensityPanel)
    bpy.utils.unregister_class(DensityPaintPanel)
    bpy.utils.unregister_class(DensityAddOperator)
    bpy.utils.unregister_class(DensitySubtractOperator)
    bpy.utils.unregister_class(FrontiersDensityProperties)
    bpy.utils.unregister_class(DensityForwardGroupOperator)
    bpy.utils.unregister_class(DensityBackwardsGroupOperator)
    bpy.utils.unregister_class(DensityAssignIndex)
    del bpy.types.Scene.FrontiersDensityProperties

    # Quick Import
    bpy.utils.unregister_class(CompleteImport)
    bpy.utils.unregister_class(ImportTerrain)
    bpy.utils.unregister_class(ImportObjects)
    bpy.utils.unregister_class(ImportHeightmap)
    bpy.utils.unregister_class(SettingsImp)
    bpy.utils.unregister_class(QimportSettings)
    
    # Camera connect
    bpy.utils.unregister_class(OBJECT_OT_FrontiersCamConnect)
    bpy.utils.unregister_class(CameraConnectPanel)