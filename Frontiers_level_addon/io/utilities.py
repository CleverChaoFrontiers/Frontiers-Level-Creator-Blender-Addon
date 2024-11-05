import bpy
import mathutils # type:ignore

def CreateMesh(vertices, uvs, normals, triangles, colors, meshName):
    triangles_grouped = [(i[0], i[1], i[2]) for i in triangles]
    mesh = bpy.data.meshes.new(meshName + " Mesh")
    mesh.from_pydata(vertices, [], triangles_grouped)
    mesh.update()
    
    try:
        if uvs:
            for i in uvs:
                uv_layer = mesh.uv_layers.new(name=f"UVMap{uvs.index(i)}")
                for loop in mesh.loops:
                    uv_layer.data[loop.index].uv = i[loop.vertex_index]
    except Exception as e:
        print(f"Line 16:{e}")

    if normals:
        mesh.normals_split_custom_set([-normals[loop.vertex_index] for loop in mesh.loops])
        #for loop in mesh.loops:
        #    loop.normal = normals[loop.vertex_index]

    if colors:
        color_layer = mesh.vertex_colors.new(name="Color")
        for poly in mesh.polygons:
            for idx in poly.loop_indices:
                loop_index = idx
                vertex_index = mesh.loops[loop_index].vertex_index
                color_layer.data[loop_index].color = colors[vertex_index]

    for i, tri in enumerate(triangles):
        mesh.polygons[i].material_index = tri[3]  

    return mesh