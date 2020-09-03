#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

bl_info = \
    {
        "name" : "BlenderProxy",
        "author" : "Manuel Geissinger <manuel@artunchained.de>",
        "version" : (0, 3, 0),
        "blender" : (2, 7, 3),
        "location" : "View 3D > Object > Display Tools > Blender Proxy",
        "description" : "Script for quick low to high poly instanciation",
        "warning" : "",
        "wiki_url" : "",
        "tracker_url" : "",
        "category" : "Object",
    }

import bpy
from bpy.props import *
from bpy.types import Operator
from bpy.app.handlers import persistent
import random
import time

bpy.types.Scene.polyCount = IntProperty(name="Desired polycount", default=18, description="Desired polycount", min=1, max=10000)
bpy.types.Scene.lowMode = EnumProperty(items = [('POLY', 'Polygon cloud', 'Polygon cloud'), ('DECI', 'Decimate modifier', 'Decimate modifier'), ('NORE', 'Don''t decimate', 'Don''t decimate')], name = "Lowpoly mode", default = 'DECI') 
bpy.types.Scene.decival = FloatProperty(name="Ratio", default=0.005, description="Decimate ratio")
bpy.types.Scene.before = BoolProperty(name='Decimate each object', description='If checked, the poly reduction will be on every object. For a higher number of objects, turn off!', default=False)
bpy.types.Scene.autoMode = BoolProperty(name='Auto', description='Prepare and cleanup render automatically. Will fail if the preparation process takes too long, as Blender wont wait for the script to finish', default=True)


@persistent
def pre_render_handler(scene, runIt = False):
    if bpy.context.scene.autoMode:
        runIt = True
    
    if runIt:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.viewport_shade = 'BOUNDBOX'


        for scene in bpy.data.scenes:
            for obj in scene.objects:
                isBP = False
                link = ""
                linkType = ""
                try:
                    isBP = obj["isBP"]
                    link = obj["BPLink"]
                    linkType = obj["BPLinkType"]
                except:
                    isBP = False
                if isBP:
                    if linkType == "Group":
                        if bpy.data.groups[link]:
                            obj.dupli_type = 'GROUP'
                            obj.dupli_group = bpy.data.groups[link]
                       
                    if linkType == "Object":
                            tempDup = bpy.data.objects[link].copy()
                            tempDup.location = obj.location
                            tempDup.scale = obj.scale
                            tempDup.rotation_euler = obj.rotation_euler
                            bpy.context.scene.objects.link(tempDup)
                            tempDup.layers = obj.layers
                            tempDup["isBPTemp"] = True
                            if obj.parent:
                                tempDup.parent = obj.parent
                            obj.hide_render = True
                
@persistent        
def post_render_handler(scene, runIt = False):
    if bpy.context.scene.autoMode:
        runIt = True
    
    if runIt:
        #for all proxy objects
        for scene in bpy.data.scenes:
            for obj in scene.objects:
                isBP = False
                try:
                    isBP = obj["isBP"]
                except:
                    isBP = False
                if isBP:
                    obj.hide = False
                    obj.hide_render = False
                    #print(obj.name)
                    linkType = ""
                    
                    try:
                        linkType = obj["BPLinkType"]
                    except:
                        pass
                    
                    if linkType == "Group":
                        obj.dupli_group = None
                        obj.dupli_type = 'NONE'
                        
                isBPTemp = False  
                try:
                    isBPTemp = obj["isBPTemp"]
                except:
                    isBPTemp = False                
                if isBPTemp:
                    bpy.context.scene.objects.unlink(obj)

        bpy.context.scene.update()

        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas: 
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.viewport_shade = 'SOLID'

                
class BlenderProxyRenderImage(bpy.types.Operator):
    bl_idname = "object.bp_render"
    bl_label = "Render Image"
 
    def execute(self, context):
        pre_render_handler(bpy.context.scene, True)
        return {'FINISHED'}
 
class BlenderProxyCleanup(bpy.types.Operator):
    bl_idname = "object.bp_cleanup"
    bl_label = "Cleanup"
 
    def execute(self, context):
        post_render_handler(bpy.context.scene, True)
        return {'FINISHED'} 
    
class BlenderProxyAdd(bpy.types.Operator):
    bl_idname = "object.bp_add"
    bl_label = "Add highpoly link"
    bl_options = {'UNDO'}
    
    def execute(self, context):   
        for obj in bpy.context.selected_objects:
            obj["isBP"] = True
            obj["BPLink"] = context.scene.objGroup
            obj["BPLinkType"] = "Group"
           
        return {'FINISHED'}
    
class BlenderProxyClear(bpy.types.Operator):
    bl_idname = "object.bp_clear"
    bl_label = "Clear highpoly link"
    bl_options = {'UNDO'}
    
    
    def execute(self, context):   
        for obj in bpy.context.selected_objects:
            obj["isBP"] = False
            obj["BPLink"] = ""
            
        return {'FINISHED'}

def makeLowpo(obj):
    if bpy.context.scene.lowMode == "POLY":
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')                
        bpy.context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.object.mode_set(mode = 'OBJECT')
        points = obj.data.vertices

        for i in range(1, bpy.context.scene.polyCount):
            randPoly = round(random.random() * len(obj.data.polygons))-1
            obj.data.polygons[randPoly].select = True
            for point in obj.data.polygons[randPoly].vertices:
                points[point].select = True
        
        bpy.ops.object.mode_set(mode = 'EDIT')     
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')

        bpy.ops.object.mode_set(mode = 'OBJECT')
        
    if bpy.context.scene.lowMode == "DECI":
        dm = obj.modifiers.new('Decimate','DECIMATE')
        dm.ratio = bpy.context.scene.decival
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
        
    if bpy.context.scene.lowMode == "NORE":
        pass
    
class BlenderProxyLowPoly(bpy.types.Operator):
    bl_idname = "object.bp_lowpoly"
    bl_label = "Make Lowpoly"
    bl_options = {'UNDO'}
     
    def execute(self, context):   
        random.seed(1)
        firstObj = True
        firstName = ""
        dupliList = []
        originalList = bpy.context.selected_objects
        #originalObj = context.active_object
        start_time = time.time()

        for obj in originalList:
            if firstObj:
                if not obj.name in bpy.data.groups: 
                    bpy.ops.group.create(name=obj.name)
                firstObj = False
                firstName = obj.name
                
            if obj.type == 'MESH':
                """Create duplicate"""     
                duplicate = obj.copy()         
                duplicate.data = obj.data.copy()  

                context.scene.objects.link(duplicate)            
                duplicate.layers = obj.layers
                
                dupliList.append(duplicate)
                for modifier in duplicate.modifiers:
                    duplicate.modifiers.remove(modifier)
                
                if context.scene.before:
                    #context.scene.objects.active = duplicate
                    makeLowpo(duplicate)
                    duplicate.select = False
                else:
                    duplicate.select = False
                        
        context.scene.update()
            
        
        grp = bpy.data.groups[firstName]
        for obj in originalList:
            #context.scene.objects.active = obj
            #bpy.ops.object.group_link(group=firstName)
            if not obj.name in grp.objects:
                grp.objects.link(obj)
            obj.layers = (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True)
            obj.select = False
    
        firstObj = True        
        for obj in dupliList:
            if firstObj:
                context.scene.objects.active = obj 
                bpy.data.groups[firstName].dupli_offset = obj.location
                firstObj = False       
            obj.select = True
                            
        #if len(bpy.context.selected_objects) > 1:
        #context.scene.objects.active = originalObj
        bpy.ops.object.join()
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
 
        obj = context.active_object    
        obj.select = True
        
        obj["isBP"] = True
        obj["BPLink"] = firstName
        obj["BPLinkType"] = "Group"
      
            
        if not context.scene.before:
            makeLowpo(obj)
    
        return {'FINISHED'}
    
class BlenderProxyPanel(bpy.types.Panel):
    """Blender Proxy"""
    bl_label = "Blender Proxy"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Display Tools'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout

        obj = context.object
        row = layout.row()
        row.label(text="Create")
        
        row = layout.row()
        row.operator(BlenderProxyLowPoly.bl_idname, text = "Make Lowpoly & link")
        row = layout.row()
        row.prop(context.scene, "lowMode")
        row = layout.row()
        if context.scene.lowMode == "POLY":
            row.prop(context.scene, "polyCount")
            row = layout.row()
            row.prop(context.scene, "before")
        if context.scene.lowMode == "DECI":
            row.prop(context.scene, "decival") 
            row = layout.row()
            row.prop(context.scene, "before")
        
        row = layout.row()
        row.label(text="Link")
        
        row = layout.row()
        split = row.split()
        col = split.column()
        col.operator(BlenderProxyAdd.bl_idname, text = "Add highpoly link")
        col = split.column()
        col.operator(BlenderProxyClear.bl_idname, text = "Clear highpoly link")
        
        row = layout.row()
        row.prop_search(context.scene, "objGroup", bpy.data, "groups", text="")
        
        row = layout.row()
        row.label(text="Convert")
        
        row = layout.row()
        row.prop(context.scene, "autoMode")
        row = layout.row()
        col = row.column()
        col.operator(BlenderProxyRenderImage.bl_idname, text = "Prepare Render")
        col = row.column()
        col.operator(BlenderProxyCleanup.bl_idname, text = "Cleanup (after Render)")

#with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
#    data_to.objects = [name for name in data_from.objects if name.startswith("A")]
# the loaded objects can be accessed from 'data_to' outside of the context
# since loading the data replaces the strings for the datablocks or None
# if the datablock could not be loaded.
#with bpy.data.libraries.load(filepath) as (data_from, data_to):
#    data_to.meshes = data_from.meshes
# now operate directly on the loaded data
#for mesh in data_to.meshes:
#    if mesh is not None:
#        print(mesh.name)

def register():
    bpy.utils.register_class(BlenderProxyPanel)
    bpy.utils.register_class(BlenderProxyAdd)
    bpy.utils.register_class(BlenderProxyClear)
    bpy.utils.register_class(BlenderProxyRenderImage)
    bpy.utils.register_class(BlenderProxyCleanup)
    bpy.utils.register_class(BlenderProxyLowPoly)
    bpy.types.Scene.objGroup = bpy.props.StringProperty()
    bpy.app.handlers.render_pre.append(pre_render_handler)
    bpy.app.handlers.render_post.append(post_render_handler)


def unregister():
    bpy.utils.unregister_class(BlenderProxyPanel)
    bpy.utils.unregister_class(BlenderProxyAdd)
    bpy.utils.unregister_class(BlenderProxyClear)
    bpy.utils.unregister_class(BlenderProxyRenderImage)
    bpy.utils.unregister_class(BlenderProxyCleanup)
    bpy.utils.unregister_class(BlenderProxyLowPoly)
    bpy.app.handlers.render_pre.remove(pre_render_handler)
    bpy.app.handlers.render_post.remove(post_render_handler)


if __name__ == "__main__":
    register()
