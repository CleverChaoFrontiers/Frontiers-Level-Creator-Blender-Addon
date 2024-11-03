import bpy
from mathutils import Quaternion
import random
import os
import uuid

from os.path import dirname
ADDON_DIRECTORY = dirname(dirname(os.path.realpath(__file__)))

def _get_path_templates():
	spline_template_path = os.path.join(ADDON_DIRECTORY, "objects\Path.txt")
	node_template_path = os.path.join(ADDON_DIRECTORY, "objects\PathNode.txt")

	with open(spline_template_path, "r") as file:
		spline_template =  file.read()

	with open(node_template_path, "r") as file:
		node_template =  file.read()

	return spline_template, node_template


def _generate_uid():
	return str(random.randint(100000, 200000))


def _get_export_nodetree():
	nodetree_name = "PathExport"

	try:
		return bpy.data.node_groups[nodetree_name]
	except:
		spline_template_path = os.path.join(ADDON_DIRECTORY, "Other\path_export_nodesetup.blend")

		bpy.ops.wm.link(
			filename=nodetree_name,
			directory=f"{spline_template_path}{os.path.sep}NodeTree{os.path.sep}"
		)

		return bpy.data.node_groups[nodetree_name]


def curve_to_hson_objects(
		curve: bpy.types.Object,
		node_start_index: int,
		path_type: str,
		no_rotation: bool,
		straight_path: bool,
		changed_uid_objects: list[str],
		report):

	curve_data: bpy.types.Curve = curve.data
	if len(curve_data.splines) == 0:
		report(f"Curve \"{curve.name}\" has no splines. It has been skipped.")
		return []

	exportModifier = curve.modifiers.new("ExportModifier", 'NODES')
	exportModifier.node_group = _get_export_nodetree()
	eval_mesh = curve.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
	rotation_attr = eval_mesh.attributes["rotation"]
	smoothed_attr = eval_mesh.attributes["smoothed"]
	curve.modifiers.remove(exportModifier)

	result = []
	path_template, node_template = _get_path_templates()

	if path_type == "OBJ_PATH":
		node_prefix = "Obj"
	elif path_type == "SV_PATH":
		node_prefix = "Sv"
	else:
		node_prefix = ""

	############################################################
	# Setup Nodes

	node_ids = []
	origin_position = None
	origin_rotation = None
	origin_straight = None

	for i, v in enumerate(eval_mesh.vertices):
		position = curve.matrix_world @ v.co
		if no_rotation:
			rotation = Quaternion()
		else:
			rotation = curve.matrix_world.to_quaternion() @ Quaternion(rotation_attr.data[i].value)

		data_position = f'{position.x:.3f}, {position.z:.3f}, {-position.y:.3f}'
		data_rotation = f'{rotation.x:.3f}, {rotation.z:.3f}, {-rotation.y:.3f}, {rotation.w:.3f}'
		data_straight = not smoothed_attr.data[i].value

		if i == 0:
			origin_position = data_position
			origin_rotation = data_rotation
			origin_straight = data_straight
			continue

		node_id = str(uuid.uuid4()).upper()
		node_ids.append(f"\"{node_id}\"")

		node_result = (node_template
			.replace('DATA_ID', node_id)
			.replace('DATA_NAME', f"{node_prefix}PathNode{node_start_index + i}")
			.replace('DATA_POSITION', data_position)
			.replace('DATA_ROTATION', data_rotation)
			.replace('DATA_INDEX', str(i))
		)

		if straight_path or data_straight:
			node_result = node_result.replace('LINETYPE_SNS', 'LINETYPE_STRAIGHT')

		result.append(node_result)

	############################################################
	# Setup Path

	if "UID" in curve:
		uid = curve["UID"]
	else:
		uid = _generate_uid()
		curve["UID"] = uid

	for other_obj in bpy.data.objects: #check if there is a duplicate UID in the scene
		if "UID" in other_obj and other_obj["UID"] == uid and other_obj != curve:
			changed_uid_objects.append(other_obj.name)
			other_obj["UID"] = _generate_uid()

	path_result = (path_template
		.replace('DATA_ID', str(uuid.uuid4()).upper())
		.replace('DATA_NAME', curve.name)
		.replace('DATA_TYPE', path_type)
		.replace('DATA_POSITION', origin_position)
		.replace('DATA_ROTATION', origin_rotation)
		.replace('DATA_NODES', ',\n            '.join(node_ids))
		.replace('DATA_LOOP', str(curve_data.splines[0].use_cyclic_u).lower())
		.replace('DATA_UID', uid))

	if straight_path or origin_straight:
		path_result = path_result.replace("LINETYPE_SNS", "LINETYPE_STRAIGHT")

	result.insert(0, path_result)

	return result


def curve_to_hson_objects_from_name(
		curve: bpy.types.Object,
		node_start_index: int,
		changed_uid_objects: list[str],
		report):

	curve_name = curve.name.lower()

	if "objpath" in curve_name:
		path_type = 'OBJ_PATH'
	elif "svpath" in curve_name:
		path_type = 'SV_PATH'
	else:
		path_type = 'GR_PATH'

	no_rotation = "_norot" in curve_name
	straight_path = "_str" in curve_name

	return curve_to_hson_objects(
		curve,
		node_start_index,
		path_type,
		no_rotation,
		straight_path,
		changed_uid_objects,
		report
	)


class PrintPathOperator(bpy.types.Operator):
	bl_idname = "object.frontiers_path_print"
	bl_label = "Create path Gedit code"
	bl_description = "Create path gedit code from curves to copy-paste into your mod"

	def execute (self, context):
		#Get check info
		settings: FrontiersPath = context.scene.FrontiersPath

		if settings.path_collection is None:
			self.report({"WARNING"}, f"Please specify a collection!")
			return {'CANCELLED'}

		changed_uid_list = []
		gedit_text = ""

		for obj in settings.path_collection.objects:
			if obj.type != 'CURVE':
				continue

			hson_objects = curve_to_hson_objects(
				obj,
				settings.node_start_index,
				settings.path_type,
				not settings.use_rotation,
				settings.no_smoothing,
				changed_uid_list,
				lambda t: self.report({"WARNING"}, t)
			)

			gedit_text += "".join(hson_objects)

		if len(changed_uid_list) != 0:
			self.report({"INFO"}, f"Duplicate ID's were found. Objects with changed IDs are: {changed_uid_list}")

		if gedit_text == "":
			self.report({"WARNING"}, f"Specified collection does not have any curve objects.")
			return {'CANCELLED'}

		bpy.ops.wm.window_new()
		gedit_print = bpy.data.texts.new("Rail Gedit Code")
		gedit_print.write(gedit_text)
		context.area.type = 'TEXT_EDITOR'
		context.space_data.text = gedit_print
		return {'FINISHED'}


class FrontiersPath(bpy.types.PropertyGroup):

	path_type: bpy.props.EnumProperty(
		items=[
			("GR_PATH", "Grind Rail", "Creates code for a grindrail"),
			("OBJ_PATH", "Object path", "Creates an object path (TECHNICAL: USE FOR AUTORUN AND MANUAL GEDIT EDITING. WILL ALSO CHANGE THE NAME OF THE PATHS.)"),
			("SV_PATH", "Sideview(2D) path", "Creates a sideview path (HIGHLY RECOMMENDED FOR 2D SECTIONS. WILL ALSO CHANGE THE NAME OF THE PATHS.)")
		],
		name="Type",
		description="Set the type of path that will be converted to code",
		default = "GR_PATH"
	)

	path_collection: bpy.props.PointerProperty(
		name="Rail Collection",
		description = "Choose Rail Collection",
		type=bpy.types.Collection
	)

	no_smoothing: bpy.props.BoolProperty(
		name="No smoothing",
		description="Make straight lines between nodes. If off, Frontiers will automatically smooth the path.",
		default = False
	)

	use_rotation: bpy.props.BoolProperty(
		name="Rail rotation",
		description="Lets the rail rotate following it's normal, for loops and such.(Remember that each node can be tilted in edit mode with Ctrl+T)",
		default = False
	)

	node_start_index: bpy.props.IntProperty(
		name="Node start index",
		description = "Set Start index (Only change if you are using several collections. Set this to avoid duplicate indices)",
		min = 1,
		soft_min = 1
	)