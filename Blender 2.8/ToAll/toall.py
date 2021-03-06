import bpy
from bpy.props import *

bl_info = {
    "name": "To All",
    "author": "Manuel Geissinger",
    "version": (1, 0),
    "blender": (2, 75, 0),
    "location": "Properties",
    "description": "Copies settings, modifiers or materials to all selected objects",
    "warning": "",
    "wiki_url": "",
    "category": "Objects",
    }
    
bpy.types.Scene.excludeMod = BoolProperty(name='Exclude viewport invisible', description='This will exclude modifiers that are set to invisible (eye-icon)', default=True)

    
class toAll(bpy.types.Operator):
    bl_idname = "scene.to_all"
    bl_label = "Copy to all"
    bl_options = {'REGISTER', 'UNDO'}
    
    mode = bpy.props.StringProperty(default="")

    def execute(self, context):
        if bpy.context.active_object is not None:
            scene = bpy.context.scene
            active = bpy.context.active_object
            
            if "selected" in self.mode:
                objects = bpy.context.selected_objects
            if "children" in self.mode:
                objects = active.children
                
            for ob in objects:
                if ob != active:
                    if "material" in self.mode:
                        if ob.data != active.data: #exclude instaces
                            if ob.type == 'MESH' or ob.type == 'CURVE':
                                if not "append" in self.mode:
                                    ob.data.materials.clear()
                                    
                                for mat in active.data.materials:
                                    ob.data.materials.append(mat)
                                
                    if "modifier" in self.mode:
                        if ob.type == 'MESH' or ob.type == 'CURVE':
                            if not "append" in self.mode:
                                for mod in ob.modifiers:
                                    ob.modifiers.remove(mod)
                                    
                            for mod in active.modifiers:
                                if not (bpy.context.scene.excludeMod and mod.show_viewport == False):
                                    currentMod = ob.modifiers.new(mod.name, mod.type)
                                    
                                    # collect names of writable properties
                                    properties = [p.identifier for p in mod.bl_rna.properties if not p.is_readonly]

                                    # copy those properties
                                    for prop in properties:
                                        setattr(currentMod, prop, getattr(mod, prop))


        return {'FINISHED'}


class materialPanel(bpy.types.Panel):
    bl_label = "Copy material to all"
    bl_idname = "SCENE_material_to_all"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        row = layout.row()
   
        row = layout.row(align=True)
        row.operator(toAll.bl_idname, text="Copy to selected").mode = "material, selected"
        row.operator(toAll.bl_idname, text="Copy to children").mode = "material, children"
        
        row = layout.row(align=True)
        row.operator(toAll.bl_idname, text="Append to selected").mode = "material, selected, append"
        row.operator(toAll.bl_idname, text="Append to children").mode = "material, children, append"

class modifierPanel(bpy.types.Panel):
    bl_label = "Copy modifiers to all"
    bl_idname = "SCENE_modifier_to_all"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "modifier"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        row = layout.row()
   
        row = layout.row(align=True)
        row.operator(toAll.bl_idname, text="Copy to selected").mode = "modifier, selected"
        row.operator(toAll.bl_idname, text="Copy to children").mode = "modifier, children"
        
        row = layout.row(align=True)
        row.operator(toAll.bl_idname, text="Append to selected").mode = "modifier, selected, append"
        row.operator(toAll.bl_idname, text="Append to children").mode = "modifier, children, append"
        
        row = layout.row(align=True)
        row.prop(context.scene, "excludeMod")  
                   
        
def register():
    bpy.utils.register_class(toAll)
    bpy.utils.register_class(materialPanel)
    bpy.utils.register_class(modifierPanel)


def unregister():
    bpy.utils.unregister_class(toAll)
    bpy.utils.unregister_class(materialPanel)
    bpy.utils.unregister_class(modifierPanel)


if __name__ == "__main__":
    register()
