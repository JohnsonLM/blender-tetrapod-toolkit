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
from math import degrees

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
    with open(path, mode='a') as writer:
        writer = csv.DictWriter(writer, ['frame', 'timecode', 'name', 'X', 'Y', 'Z']) 
        writer.writeheader()
        
        frame_count = scene.measure_end_frame - scene.measure_start_frame
        for frame in range(frame_count):
            scene.frame_set(frame + 1)
            for pb in bpy.context.selected_pose_bones_from_active_object:
                pb_mw = pb.matrix
                pb_rot = pb_mw.to_euler()
                xrot = degrees(pb_rot.x) - 90
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


def write_pb_rot_csv(scene, path):
    with open(path, mode='a') as writer:
        writer = csv.DictWriter(writer, ['frame', 'timecode', 'name', 'X', 'Y', 'Z']) 
        writer.writeheader()
        
        for pb in bpy.context.selected_pose_bones_from_active_object:
            pb_mw = pb.matrix
            pb_rot = pb_mw.to_euler()
            xrot = degrees(pb_rot.x) - 90
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


def selected_pb_rot(scene):
    pb = bpy.context.active_pose_bone
    pb_mw = pb.matrix
    pb_rot = pb_mw.to_euler()
    xrot = degrees(pb_rot.x) - 90
    yrot = degrees(pb_rot.y)
    zrot = degrees(pb_rot.z)
    
    bonedata = Object()
    bonedata.name = pb.name
    bonedata.xrot = "{:.3f}".format(xrot)
    bonedata.yrot= "{:.3f}".format(yrot)
    bonedata.zrot = "{:.3f}".format(zrot)
    
    return bonedata


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


### Operators ###
class ExportGlobalRotOperator(bpy.types.Operator):
    """Export global bone rotations for current frame"""
    bl_idname = "object.export_global_rot"
    bl_label = "Export Global Rotations (Current Frame)"
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
    bl_label = "Export Global Rotations (Playback Range)"
    
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
    """Info on location change of selected bone"""
    bl_idname = "object.bone_loc_change"
    bl_label = "Calculate Selected Bone Travel"

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
        bone = selected_pb_rot(bpy.context.scene)
       
        box = layout.box()
        row = box.row()
        row.label(text="Timecode:", icon='TIME')
        row = box.row()
        row.label(text=get_timecode(bpy.context.scene))
        
        box = layout.box()
        row = box.row()
        row.label(text="Selected Bone:", icon='BONE_DATA')
        row = box.row()
        row.label(text=bone.name)
        row = box.row()
        row.label(text="X: " + bone.xrot)
        row.label(text="Y: " + bone.yrot)
        row.label(text="Z: " + bone.zrot)
        
        row = layout.row()
        row.label(text="Measure Frame Range:")
        row = layout.row()
        row.prop(bpy.context.scene, "measure_start_frame")
        row.prop(bpy.context.scene, "measure_end_frame")
    
        layout.row().separator()
        row = layout.row()
        row.label(text="Export Selected Bone Rotations:")
        
        row = layout.row()
        row.operator("object.export_global_rot")    
        row = layout.row()
        row.operator("object.export_global_rot_in_range")
        
        layout.row().separator()
        ob = context.object
        row = layout.row()
        row.label(text="Calculate Travel:")
        row = layout.row()
        row.operator("object.bone_loc_change")
        
        box = layout.box()
        row = box.row()
        row.label(text="Positional Change:")
        row = box.row()
        row.label(text="X: " + str(degrees(bpy.context.scene.active_bone_loc_difference[0])))
        row.label(text="Y: " + str(degrees(bpy.context.scene.active_bone_loc_difference[1])))
        row.label(text="Z: " + str(degrees(bpy.context.scene.active_bone_loc_difference[2])))
        
        row = box.row()
        row.label(text="Rotational Change:")
        row = box.row()
        row.label(text="X: " + str(bpy.context.scene.active_bone_rot_difference[0]))
        row.label(text="Y: " + str(bpy.context.scene.active_bone_rot_difference[1]))
        row.label(text="Z: " + str(bpy.context.scene.active_bone_rot_difference[2]))
        
        row = box.row()
        row.label(text="Min Angle:")
        row = box.row()
        row.label(text="X: " + str(bpy.context.scene.active_bone_rot_min[0]))
        row.label(text="Y: " + str(bpy.context.scene.active_bone_rot_min[1]))
        row.label(text="Z: " + str(bpy.context.scene.active_bone_rot_min[2]))
        
        row = box.row()
        row.label(text="Max Angle:")
        row = box.row()
        row.label(text="X: " + str(bpy.context.scene.active_bone_rot_max[0]))
        row.label(text="Y: " + str(bpy.context.scene.active_bone_rot_max[1]))
        row.label(text="Z: " + str(bpy.context.scene.active_bone_rot_max[2]))
    

def register():
    bpy.types.Scene.active_bone_rot_difference = bpy.props.FloatVectorProperty(name="Rot_Difference")
    bpy.types.Scene.active_bone_loc_difference = bpy.props.FloatVectorProperty(name="Loc_Difference")
    bpy.types.Scene.active_bone_rot_min = bpy.props.FloatVectorProperty(name="Rot Min")
    bpy.types.Scene.active_bone_rot_max = bpy.props.FloatVectorProperty(name="Rot Max")
    bpy.utils.register_class(ExportGlobalRotOperator)
    bpy.utils.register_class(ExportGlobalRotInRangeOperator)
    bpy.utils.register_class(BoneChangeInfoOperator)
    bpy.utils.register_class(BoneRotationStatsPanel)
    bpy.types.Scene.measure_start_frame = bpy.props.IntProperty(name="Start", default=(1))
    bpy.types.Scene.measure_end_frame = bpy.props.IntProperty(name="End", default=(80))


def unregister():
    bpy.utils.unregister_class(ExportGlobalRotOperator)
    bpy.utils.unregister_class(ExportGlobalRotInRangeOperator)
    bpy.utils.unregister_class(BoneChangeInfoOperator)
    bpy.utils.unregister_class(BoneRotationStatsPanel)
    del bpy.types.Scene.measure_start_frame
    del bpy.types.Scene.measure_end_frame
    del bpy.types.Scene.active_bone_loc_difference
    del bpy.types.Scene.active_bone_rot_difference
    del bpy.types.Scene.active_bone_rot_min
    del bpy.types.Scene.active_bone_rot_max
    
if __name__ == "__main__":
    register()
