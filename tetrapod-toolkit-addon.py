bl_info = {
    "name": "Tetrapod Toolkit",
    "author": "TBD",
    "version": (0, 3),
    "blender": (4, 0, 1),
    "location": "View3D > Properties > Tetrapod Toolkit",
    "description": "Displays and exports global rotations of selected bones.",
    "warning": "",
    "doc_url": "",
    "category": "View 3D"
}

import bpy
import os
import csv
import bmesh
from math import degrees
import mathutils

# Allows for initialization of empty objects.
class Object(object):
    pass


### Functions ###
def get_timecode(scene):
    fps = scene.render.fps
    totalFrames = scene.frame_current

    hours = int((totalFrames / fps) / 3600)
    if hours >= 1:
        timecode_hours = str(hours).zfill(2)
        totalFrames = totalFrames - ((hours * fps) * 3600)
    else:
        timecode_hours = "00"  
        
    minutes = int((totalFrames / fps) / 60)
    if minutes >= 1:
        timecode_minutes = str(minutes).zfill(2)
        totalFrames = totalFrames - ((minutes * fps) * 60)
    else:
        timecode_minutes = "00"  
    
    seconds = totalFrames / fps
    timecode_seconds = "{:0>6.3f}".format(seconds)
    timecode_seconds = str(timecode_seconds)
    totalFrames = totalFrames - (seconds * fps) 

    return timecode_hours + ':' + timecode_minutes + ':' + timecode_seconds
        

def write_pb_rot_in_range_csv(scene, path):
    min_x = None
    max_x = None
    min_y = None
    max_y = None
    min_z = None
    max_z = None
    with open(path, mode='a') as writer:
        writer = csv.DictWriter(writer, ['frame', 'timecode', 'name', 'X', 'Y', 'Z', 'min', 'max']) 
        writer.writeheader()
        
        frame_count = scene.measure_end_frame - scene.measure_start_frame
        for frame in range(frame_count):
            scene.frame_set(frame + 1)
            for pb in bpy.context.selected_pose_bones_from_active_object:
                pb_mw = pb.matrix
                pb_rot = pb_mw.to_euler()
                xrot = degrees(pb_rot.x)
                yrot = degrees(pb_rot.y)
                zrot = degrees(pb_rot.z)
                rot = current_bone_rot(scene, frame)
                # X axis
                if max_x == None or rot.to_euler().x >= max_x:
                    max_x = rot.to_euler().x
                if min_x == None or rot.to_euler().x <= min_x:
                    min_x = rot.to_euler().x
                
                # Y axis
                if max_y == None or rot.to_euler().y >= max_y:
                    max_y = rot.to_euler().y
                if min_y == None or rot.to_euler().z <= min_z:
                    min_y = rot.to_euler().y
                    
                # Z axis
                if max_z == None or rot.to_euler().z >= max_z:
                    max_z = rot.to_euler().z
                if min_z == None or rot.to_euler().z <= min_z:
                    min_z = rot.to_euler().z
                        
                pb_rot = Object()
                pb_rot.min = degrees(min_x), degrees(min_y), degrees(min_z)
                pb_rot.max = degrees(max_x), degrees(max_y), degrees(max_z)
                row = {
                    "frame": scene.frame_current,
                    "timecode": get_timecode(scene),
                    "name": pb.name,
                    "X": "{:.3f}".format(xrot),
                    "Y": "{:.3f}".format(yrot),
                    "Z": "{:.3f}".format(zrot),
                    'min': pb_rot.min,
                    'max': pb_rot.max
                }
                writer.writerow(row)


def write_pb_rot_csv(scene, path):
    with open(path, mode='a') as writer:
        writer = csv.DictWriter(writer, ['frame', 'timecode', 'name', 'X', 'Y', 'Z']) 
        writer.writeheader()
        
        for pb in bpy.context.selected_pose_bones_from_active_object:
            pb_mw = pb.matrix
            pb_rot = pb_mw.to_euler()
            xrot = degrees(pb_rot.x)
            yrot = degrees(pb_rot.y)
            zrot = degrees(pb_rot.z)
            row = {
                "frame": scene.frame_current,
                "timecode": get_timecode(scene),
                "name": pb.name,
                "X": "{:.3f}".format(xrot),
                "Y": "{:.3f}".format(yrot),
                "Z": "{:.3f}".format(zrot)
            }
            writer.writerow(row)


def current_pb_transforms():
    """
    Returns location and rotation of the selected bone's head and tail.
    
    """
    bones = []
    for pb in bpy.context.selected_pose_bones:
        pb_head_loc = pb.head
        pb_tail_loc = pb.tail
        rotation = pb.matrix.to_euler()
        rotation = mathutils.Vector((
            degrees(rotation.x), 
            degrees(rotation.y), 
            degrees(rotation.z)
        ))
        pb_d = Object()
        pb_d.pb = bpy.context.active_pose_bone
        pb_d.name = pb.name
        pb_d.rotation = rotation
        pb_d.location_tail = pb_tail_loc
        pb_d.location_head = pb_head_loc
        bones.append(pb_d)
    return bones


def current_bone_location(scene, frame):
    scene.frame_set(frame)
    location, rotation, scale = bpy.context.active_pose_bone.matrix.decompose()
    
    return location


def current_bone_rot(scene, frame):
    scene.frame_set(frame)
    location, rotation, scale = bpy.context.active_pose_bone.matrix.decompose()
    
    return rotation


def current_bone_location_change(scene, frame_start, frame_end):
    initial_frame = scene.frame_current
    bone_start = current_bone_location(bpy.context.scene, frame_start)
    bone_end = current_bone_location(bpy.context.scene, frame_end)
    scene.frame_set(initial_frame)
    
    return bone_end - bone_start


def current_bone_rot_change(scene):
    initial_frame = scene.frame_current
    bone_start = current_bone_rot(bpy.context.scene, scene.measure_start_frame)
    bone_end = current_bone_rot(bpy.context.scene, scene.measure_end_frame)
    scene.frame_set(initial_frame)
    
    x1, y1, z1 = map(degrees, (bone_start.to_euler()[0], bone_start.to_euler()[1], bone_start.to_euler()[2]))
    x2, y2, z2 = map(degrees, (bone_end.to_euler()[0], bone_end.to_euler()[1], bone_end.to_euler()[2]))
    x = x2 - x1
    y = y2 - y1
    z = z2 - z1

    return (x, y, z)


def current_bone_rot_min_max(scene):
    min_x = None
    max_x = None
    min_y = None
    max_y = None
    min_z = None
    max_z = None
    frame_count = scene.measure_end_frame - scene.measure_start_frame
    
    for frame in range(frame_count + 1):
        rot = current_bone_rot(bpy.context.scene, frame)
        
        # X axis
        if max_x == None or rot.to_euler().x >= max_x:
            max_x = rot.to_euler().x
        if min_x == None or rot.to_euler().x <= min_x:
            min_x = rot.to_euler().x
        
        # Y axis
        if max_y == None or rot.to_euler().y >= max_y:
            max_y = rot.to_euler().y
        if min_y == None or rot.to_euler().z <= min_z:
            min_y = rot.to_euler().y
            
        # Z axis
        if max_z == None or rot.to_euler().z >= max_z:
            max_z = rot.to_euler().z
        if min_z == None or rot.to_euler().z <= min_z:
            min_z = rot.to_euler().z
            
    bonedata = Object()
    bonedata.min = degrees(min_x), degrees(min_y), degrees(min_z)
    bonedata.max = degrees(max_x), degrees(max_y), degrees(max_z)
    
    return(bonedata)


def bmesh_copy_from_object(obj, transform=True, triangulate=True, apply_modifiers=False):
    """
    Returns a transformed, triangulated copy of the mesh
    
    """
    assert(obj.type == 'MESH')
    if apply_modifiers and obj.modifiers:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        me = obj_eval.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        obj_eval.to_mesh_clear()
    else:
        me = obj.data
        if obj.mode == 'EDIT':
            bm_orig = bmesh.from_edit_mesh(me)
            bm = bm_orig.copy()
        else:
            bm = bmesh.new()
            bm.from_mesh(me)

    if transform:
        bm.transform(obj.matrix_world)

    if triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces)

    return bm


def current_obj_volume():
    """
    Returns final volume of the selected mesh object.
    
    """
    scene = bpy.context.scene
    unit = scene.unit_settings
    obj = bpy.context.active_object
    bm = bmesh_copy_from_object(obj, apply_modifiers=True)
    vol = bm.calc_volume()
    bm.free()

    return vol


def add_mesh(name, verts, edges=None, faces=None, col_name="Collection"):
    """
    Adds new mesh object from vertices, edges, and faces.
    
    """
    if edges is None:
        edges = []
    if faces is None:
        faces = []
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(mesh.name, mesh)
    col = bpy.data.collections[col_name]
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    mesh.from_pydata(verts, edges, faces)
    
    return obj


def add_muscle(name="Muscle"):
    """
    Adds a new muscle from the head and tail of the selected bone.
    
    """
    pb_first = current_pb_transforms()[0]
    pb_last = current_pb_transforms()[-1]
    verts = [pb_first.location_head, pb_last.location_tail]
    obj = add_mesh(name, verts, [[0,1]])
    
    # Weights
    weight_group_head = obj.vertex_groups.new(name=pb_first.name)
    if pb_last.name in obj.vertex_groups:
        weight_group_tail = weight_group_head
    else:
        weight_group_tail = obj.vertex_groups.new(name=pb_last.name)
    weight_group_head.add([0], 1, 'REPLACE')
    weight_group_tail.add([1], 1, 'REPLACE')
    
    # Weight Modifier
    weight_modifier = obj.modifiers.new("Weights", "ARMATURE")
    armature = pb_first.pb.id_data
    weight_modifier.object = armature
    obj.parent = armature
    
    # Geo Nodes Modifier
    modifier_name = "Bone_Gen"
    modifier = obj.modifiers.new(modifier_name, "NODES")
    replacement = bpy.data.node_groups["muscle_setup"]
    modifier.node_group = replacement
    obj.select_set(True)
    armature.select_set(False)
    bpy.context.view_layer.objects.active = obj
    
    #bpy.ops.object.modifier_apply(modifier=modifier_name)
    #bm = bmesh_copy_from_object(obj)
    #weight_idx = [v.index for v in bm.verts]
    #weight_group_head = obj.vertex_groups.new(name=pb_first.name)
    #weight_group_head.add(weight_idx, 1, 'REPLACE')
    
def modify_muscle(radius, u_res=None, r_res=None):
    active_object = bpy.context.active_object
    if active_object is not None:
        if active_object.type == 'MESH' and active_object.modifiers.get("Bone_Gen"):
            bpy.context.active_object.modifiers["Bone_Gen"]["Socket_2"] = radius
            if u_res:
                bpy.context.active_object.modifiers["Bone_Gen"]["Socket_4"] = u_res
            if r_res:
                bpy.context.active_object.modifiers["Bone_Gen"]["Socket_5"] = r_res
            bpy.context.object.data.update()
    
    
def convert_to_mesh(obj, armature):
    armature_obj = armature
    armature = armature.data
    muscle_name = obj.name
    v1 = obj.data.vertices[0]
    v1 = obj.matrix_world @ v1.co
    v2 = obj.data.vertices[1]
    v2 = obj.matrix_world @ v2.co
    
    # Bone creation
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bone = armature.edit_bones.new(name=muscle_name)
    bone.head = v1
    bone.tail = v2
    bone_t = armature.edit_bones.new(name=muscle_name + "_target")
    bone_t.head = v2
    tail_offset = mathutils.Vector((0.0, 0.0, 1.0))
    bone_t.tail = v2 + tail_offset
    bone_name = bone.name
    bone_t_name = bone_t.name
    
    # Bone constraints
    bpy.ops.object.mode_set(mode='POSE')
    objbone = armature_obj.pose.bones[bone_name]
    objbone.constraints.new('STRETCH_TO')
    objbone.constraints["Stretch To"].target = armature_obj
    objbonetarget = armature_obj.pose.bones[bone_t_name]
    objbone.constraints["Stretch To"].subtarget = objbonetarget.name
    
    # Apply geomentry nodes
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Bone_Gen")
    
    # Weights
    bm = bmesh_copy_from_object(obj)
    weight_idx = [v.index for v in bm.verts]
    weight_group = obj.vertex_groups.new(name=objbone.name)
    weight_group.add(weight_idx, 1, 'REPLACE')
    if not obj.modifiers['Weights']:
        weight_modifier = obj.modifiers.new("Weights", "ARMATURE")
        weight_modifier.object = armature_obj
    obj.parent = armature_obj
    
    
def armature_poll(self, object):
        return object.type == 'ARMATURE'
        
### Operators ###
class ExportGlobalRotOperator(bpy.types.Operator):
    """Export global bone rotations for current frame"""
    bl_idname = "object.export_global_rot"
    bl_label = "Export Selected Bone Rotations"
    filepath: bpy.props.StringProperty(subtype="DIR_PATH")

    @classmethod
    def poll(cls, context):
        return context.selected_pose_bones_from_active_object is not None

    def execute(self, context):
        write_pb_rot_csv(bpy.context.scene, self.filepath)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ExportGlobalRotInRangeOperator(bpy.types.Operator):
    """Export global bone rotations for each frame in the current playback range"""
    bl_idname = "object.export_global_rot_in_range"
    bl_label = "Export Selected Bone Rotations in Range"
    
    filepath: bpy.props.StringProperty(subtype="DIR_PATH")

    @classmethod
    def poll(cls, context):
        return context.selected_pose_bones_from_active_object is not None

    def execute(self, context):
        print("Path accepted:", self.filepath)
        write_pb_rot_in_range_csv(bpy.context.scene, self.filepath)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class BoneChangeInfoOperator(bpy.types.Operator):
    """Calculate location and rotation data for the selected bone."""
    bl_idname = "object.bone_loc_change"
    bl_label = "Calculate Active Bone Travel"

    @classmethod
    def poll(cls, context):
        return context.selected_pose_bones_from_active_object is not None

    def execute(self, context):
        loc_data = current_bone_location_change(bpy.context.scene, bpy.context.scene.measure_start_frame, bpy.context.scene.measure_end_frame)
        rot_data = current_bone_rot_change(bpy.context.scene)
        rot_min_max_data = current_bone_rot_min_max(bpy.context.scene)

        bpy.context.scene.active_bone_loc_difference = loc_data
        bpy.context.scene.active_bone_rot_difference = rot_data
        bpy.context.scene.active_bone_rot_min = rot_min_max_data.min
        bpy.context.scene.active_bone_rot_max = rot_min_max_data.max
        
        return {'FINISHED'}


class CreateMuscleOperator(bpy.types.Operator):
    """Create a muscle from the active bones head and tail."""
    bl_idname = "object.create_muscle"
    bl_label = "Create Muscle"

    @classmethod
    def poll(cls, context):
        return context.selected_pose_bones_from_active_object is not None

    def execute(self, context):
        add_muscle()
        return {'FINISHED'}
    

class ObjectVolInfoOperator(bpy.types.Operator):
    """Calculate volume and area for the selected objects."""
    bl_idname = "object.obj_vol_area_change"
    bl_label = "Calculate Mesh Volume"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        volume = current_obj_volume()
        bpy.context.scene.selected_object_volume = volume
        
        return {'FINISHED'}
    

class MuscleRadiusOperator(bpy.types.Operator):
    """Modify radius of selected muscle."""
    bl_idname = "object.muscle_radius"
    bl_label = "Update Radius"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.modifiers.get("Bone_Gen")

    def execute(self, context):
        radius = bpy.context.scene.muscle_radius
        modify_muscle(radius)
        
        return {'FINISHED'}


class MuscleConvertOperator(bpy.types.Operator):
    """Convert selected muscle."""
    bl_idname = "object.muscle_convert"
    bl_label = "Apply Muscle to Armature"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.modifiers.get("Bone_Gen")

    def execute(self, context):
        armature = bpy.context.scene.muscle_armature
        convert_to_mesh(bpy.context.active_object, armature)
        
        return {'FINISHED'}

### UI Panel ###
class BoneRotationStatsPanel(bpy.types.Panel):
    """Creates a panel in the object propeties window"""
    bl_label = "Tetrapod Toolkit"
    bl_idname = "OBJECT_PT_bonerotation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tetrapod Toolkit"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Timecode: " + get_timecode(bpy.context.scene), icon='TIME')
        try:
            bone = current_pb_transforms()[0]
            box = layout.box()
            row = box.row()
            row.label(text="Active Bone", icon='BONE_DATA')
            row = box.row()
            row.operator("object.create_muscle", icon='MOD_OUTLINE')
            row = box.row()
            row.label(text="")
            row.label(text="X")
            row.label(text="Y")
            row.label(text="Z")
            row = box.row()
            row.label(text='Rot:')
            row.label(text="{:.3f}".format(bone.rotation[0]))
            row.label(text="{:.3f}".format(bone.rotation[1]))
            row.label(text="{:.3f}".format(bone.rotation[2]))
            row = box.row()
            row.label(text='Head Loc: ')
            row.label(text="{:.3f}".format(bone.location_head[0]))
            row.label(text="{:.3f}".format(bone.location_head[1]))
            row.label(text="{:.3f}".format(bone.location_head[2]))
            row = box.row()
            row.label(text='Tail Loc: ')
            row.label(text="{:.3f}".format(bone.location_tail[0]))
            row.label(text="{:.3f}".format(bone.location_tail[1]))
            row.label(text="{:.3f}".format(bone.location_tail[2]))
            
            row = box.row()
            row.operator("object.bone_loc_change", icon='MOD_TIME')
            row = box.row()
            row.label(text="Loc Change:")
            row.label(text="{:.3f}".format(degrees(bpy.context.scene.active_bone_loc_difference[0])))
            row.label(text="{:.3f}".format(degrees(bpy.context.scene.active_bone_loc_difference[1])))
            row.label(text="{:.3f}".format(degrees(bpy.context.scene.active_bone_loc_difference[2])))
            
            row = box.row()
            row.label(text="Rot Change:")
            row.label(text="{:.3f}".format(bpy.context.scene.active_bone_rot_difference[0]))
            row.label(text="{:.3f}".format(bpy.context.scene.active_bone_rot_difference[1]))
            row.label(text="{:.3f}".format(bpy.context.scene.active_bone_rot_difference[2]))
            
            row = box.row()
            row.label(text="Min Angle:")
            row.label(text="{:.3f}".format(bpy.context.scene.active_bone_rot_min[0]))
            row.label(text="{:.3f}".format(bpy.context.scene.active_bone_rot_min[1]))
            row.label(text="{:.3f}".format(bpy.context.scene.active_bone_rot_min[2]))
            
            row = box.row()
            row.label(text="Max Angle:")

            row.label(text="{:.3f}".format(bpy.context.scene.active_bone_rot_max[0]))
            row.label(text="{:.3f}".format(bpy.context.scene.active_bone_rot_max[1]))
            row.label(text="{:.3f}".format(bpy.context.scene.active_bone_rot_max[2]))
        except Exception:
             pass
        
        if context.active_object is not None and context.active_object.type == 'MESH':
            box = layout.box()
            row = box.row()
            row.label(text="Active Mesh", icon='MESH_DATA')
            if context.active_object.modifiers.get("Bone_Gen"):
                row = box.row()
                row.prop(bpy.context.scene, "muscle_radius")
                row.operator("object.muscle_radius")
                
            row = box.row()
            row.prop(bpy.context.scene, "muscle_armature")
            row.operator("object.muscle_convert", icon='CHECKMARK')
            row = box.row()
            row.operator("object.obj_vol_area_change", icon='SNAP_VOLUME')
            row = box.row()
            row.label(text="Volume:")
            row.label(text="{:.4f}".format(bpy.context.scene.selected_object_volume))
        
        if bpy.context.selected_pose_bones is not None:
            box = layout.box()
            row = box.row()
            row.label(text="Selected Bones", icon='GROUP_BONE')
            row = box.row()
            row.prop(bpy.context.scene, "measure_start_frame")
            row.prop(bpy.context.scene, "measure_end_frame")
            row = box.row()
            row.operator("object.export_global_rot", icon='EXPORT')    
            row = box.row()
            row.operator("object.export_global_rot_in_range", icon='EXPORT')
            row = box.row()
            row.label(text="Selected: " + str(len(bpy.context.selected_pose_bones)))

def register():
    bpy.utils.register_class(ExportGlobalRotOperator)
    bpy.utils.register_class(ExportGlobalRotInRangeOperator)
    bpy.utils.register_class(BoneChangeInfoOperator)
    bpy.utils.register_class(BoneRotationStatsPanel)
    bpy.utils.register_class(ObjectVolInfoOperator)
    bpy.utils.register_class(CreateMuscleOperator)
    bpy.utils.register_class(MuscleRadiusOperator)
    bpy.utils.register_class(MuscleConvertOperator)
    bpy.types.Scene.active_bone_rot_difference = bpy.props.FloatVectorProperty(name="Rot_Difference", subtype='XYZ')
    bpy.types.Scene.active_bone_loc_difference = bpy.props.FloatVectorProperty(name="Loc_Difference", subtype='XYZ')
    bpy.types.Scene.active_bone_rot_min = bpy.props.FloatVectorProperty(name="Rot Min", subtype='XYZ')
    bpy.types.Scene.active_bone_rot_max = bpy.props.FloatVectorProperty(name="Rot Max", subtype='XYZ')
    bpy.types.Scene.measure_start_frame = bpy.props.IntProperty(name="Frame Range Start:", default=(1))
    bpy.types.Scene.measure_end_frame = bpy.props.IntProperty(name="Frame Range End:", default=(80))
    bpy.types.Scene.selected_object_volume = bpy.props.FloatProperty(name="Select Objects Volume")
    bpy.types.Scene.selected_object_area = bpy.props.FloatProperty(name="Select Objects Area")
    bpy.types.Scene.muscle_radius = bpy.props.FloatProperty(name="Muscle Radius")
    bpy.types.Scene.muscle_armature = bpy.props.StringProperty(name="")
    bpy.types.Scene.muscle_armature = bpy.props.PointerProperty(type=bpy.types.Object, poll=armature_poll, name="")
    

def unregister():
    bpy.utils.unregister_class(ExportGlobalRotOperator)
    bpy.utils.unregister_class(ExportGlobalRotInRangeOperator)
    bpy.utils.unregister_class(BoneChangeInfoOperator)
    bpy.utils.unregister_class(BoneRotationStatsPanel)
    bpy.utils.unregister_class(ObjectVolInfoOperator)
    bpy.utils.unregister_class(CreateMuscleOperator)
    bpy.utils.unregister_class(MuscleRadiusOperator)
    bpy.utils.unregister_class(MuscleConvertOperator)
    del bpy.types.Scene.measure_start_frame
    del bpy.types.Scene.measure_end_frame
    del bpy.types.Scene.active_bone_loc_difference
    del bpy.types.Scene.active_bone_rot_difference
    del bpy.types.Scene.active_bone_rot_min
    del bpy.types.Scene.active_bone_rot_max
    del bpy.types.Scene.selected_object_volume
    del bpy.types.Scene.selected_object_area
    del bpy.types.Scene.muscle_radius
    del bpy.types.Scene.muscle_armature

if __name__ == "__main__":
    register()
