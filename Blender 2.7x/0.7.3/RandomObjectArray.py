#----------------------------------------------------
#Random Object Array (c) 2014 Manuel Geissinger
#----------------------------------------------------
bl_info = \
    {
        "name" : "RandomObjectArray",
        "author" : "Manuel Geissinger <manuel@artunchained.de>",
        "version" : (0, 7, 3),
        "blender" : (2, 7, 0),
        "location" : "View 3D > Object > Random Object Array",
        "description" : "Script similar to the Array Modifier, but with Random Values",
        "warning" : "",
        "wiki_url" : "",
        "tracker_url" : "",
        "category" : "Object",
    }

import bpy
from bpy.props import *
from bpy.types import Operator, AddonPreferences
from bpy.app.handlers import persistent
import random
import time
import math
import mathutils
from mathutils import*

bpy.types.Scene.numOfObjects = IntProperty(name="Count", default=1, description="Number of Copies to create", min=1, max=10000)

bpy.types.Scene.fixedPosX = FloatProperty(name="X", default=0, description="Static offset")
bpy.types.Scene.fixedPosY = FloatProperty(name="Y", default=0, description="Static offset")
bpy.types.Scene.fixedPosZ = FloatProperty(name="Z", default=0, description="Static offset")

bpy.types.Scene.randomPosX = FloatProperty(name="X", default=0, description="Random offset")
bpy.types.Scene.randomPosY = FloatProperty(name="Y", default=0, description="Random offset")
bpy.types.Scene.randomPosZ = FloatProperty(name="Z", default=0, description="Random offset")

bpy.types.Scene.fixedRotX = FloatProperty(name="X", default=0, description="Static rotation", min=-360, max=360)
bpy.types.Scene.fixedRotY = FloatProperty(name="Y", default=0, description="Static rotation", min=-360, max=360)
bpy.types.Scene.fixedRotZ = FloatProperty(name="Z", default=0, description="Static rotation", min=-360, max=360)

bpy.types.Scene.randRotX = FloatProperty(name="X", default=0, description="Random rotation", min=-360, max=360)
bpy.types.Scene.randRotY = FloatProperty(name="Y", default=0, description="Random rotation", min=-360, max=360)
bpy.types.Scene.randRotZ = FloatProperty(name="Z", default=0, description="Random rotation", min=-360, max=360)

bpy.types.Scene.minSclX = FloatProperty(name="X", default=1, description="Random scale minimum")
bpy.types.Scene.minSclY = FloatProperty(name="Y", default=1, description="Random scale minimum")
bpy.types.Scene.minSclZ = FloatProperty(name="Z", default=1, description="Random scale minimum")

bpy.types.Scene.maxSclX = FloatProperty(name="X", default=1, description="Random scale maximum")
bpy.types.Scene.maxSclY = FloatProperty(name="Y", default=1, description="Random scale maximum")
bpy.types.Scene.maxSclZ = FloatProperty(name="Z", default=1, description="Random scale maximum")

bpy.types.Scene.cangles = BoolProperty(name='Cumulate Rotation', description='Cumulate Rotation: Fixed rotation will cumulate for every new object', default=False)
bpy.types.Scene.fangles = BoolProperty(name='Full Angles', description='Full Angles: If set, random or static rotation angle n° will be either 0° or n° but nothing in between', default=False)

bpy.types.Scene.coffset = BoolProperty(name='Cumulate Offset', description='Cumulate Offset: RFixed offset will cumulate for every new object', default=True)
bpy.types.Scene.dmode = BoolProperty(name='Grid Mode', description='Spread objects on a 2D / 3D grid instead, random values will be added / substracted from the grid point coords', default=False)

bpy.types.Scene.gridSizeX = IntProperty(name="X", description="Grid Size X Axis", default=1, min=1)
bpy.types.Scene.gridSizeY = IntProperty(name="Y", description="Grid Size Y Axis", default=1, min=1)
bpy.types.Scene.gridSizeZ = IntProperty(name="Z", description="Grid Size Z Axis", default=1, min=1)

bpy.types.Scene.kshape = BoolProperty(name='Keep Shape', description='Keep Shape: If set, object will keep its realtive scale', default=True)
  
bpy.types.Scene.singObj = BoolProperty(name='Single Object', description='Joins created duplicates into one object. Be aware that execution may take a long time for a high number or high poly objects.', default=False)
   
bpy.types.Scene.rPosRange = BoolProperty(name='Range +/-', description='If activated, random numbers will be calculated from -n to n instead of 0 to n ', default=True)
 
bpy.types.Scene.rRotRange = BoolProperty(name='Range +/-', description='If activated, random numbers will be calculated from -n to n instead of 0 to n ', default=True)

bpy.types.Scene.nangles = BoolProperty(name='From normal', description='If activated rotation will be calculated from face normals, otherwise they will be global', default=True)
  
bpy.types.Scene.rintersect = BoolProperty(name='Avoid intersections', description='Collision detection that checks the array for intersecting objects', default=False)
 
bpy.types.Scene.coll_mode = EnumProperty(items = [('AABB', 'AABB', 'Axis aligned bounding box collision'), ('ORDI', 'Origin distance', 'Distance between origins in blender units'), ('SIMP', 'Simplified', 'Fastest yet slightly unprecise mode')  ], name = "Collision mode", default = 'AABB') 
bpy.types.Scene.orgDist = FloatProperty(name="Distance", default=1, description="Detect objects within this radius")

bpy.types.Scene.coll_solve = EnumProperty(items = [('DELETE', 'Delete', 'Delete colliding objects'), ('MOVE', 'Move', 'Move colliding objects by the constant offset values again (may not solve intersections). Works best on 3-dimensional arrays'), ('SCALE', 'Scale', 'Scale colliding objects smaller to the minScale value (may not solve all intersections)'), ('SELECT', 'Select', 'Select all colliding objects for the user decide what to do')], name = "Solving method", default = 'DELETE') 
bpy.types.Scene.max_coll = IntProperty(name="Max. collisions", description="Objects intersecting with at least this number of objects will be removed.", default=1, min=1, max=100)

bpy.types.Scene.realtime = BoolProperty(name='Realtime', description='Show preview of the process in realtime', default=True)

bpy.types.Scene.corners = BoolProperty(name='Corners', description='Add corners to the array', default=False)
bpy.types.Scene.numOfCorners = IntProperty(name="Corner count", description="Number of corners", default=1, min=1, max=10)


bpy.types.Scene.aabbSize = IntProperty(name="Bounding box size %", description="Increase or decrease the size of the axis aligned bounding box by a percentage", default=100, min=1, max=500)

bpy.types.Scene.global_mode = EnumProperty(items = [('GLOBAL', 'Global', 'Offset and rotation are global. For target mesh use GLOBAL!'), ('LOCAL', 'Local', 'Offset and rotation are local. For target mesh use GLOBAL!') ], name = "Global / Local", default = 'LOCAL') 

bpy.types.Scene.relOffset = BoolProperty(name='Relative offset', description='Offset will be relative, depending on the objects dimensions. If unchecked the offset will be absolute.', default=False)
bpy.types.Scene.rel_axis = EnumProperty(items = [('X', 'X', 'Axis to use for relative offset'), ('Y', 'Y', 'Axis to use for relative offset'), ('Z', 'Z', 'Axis to use for relative offset')  ], name = "", default = 'X') 
bpy.types.Scene.fillMode = BoolProperty(name='Fill mode', description='Fills the mesh instead of choosing target faces randomly', default=True)


bpy.types.Scene.kchildren = BoolProperty(name='Keep children', description='Keep the children parented to the orginal object. Otherwise they get deleted.', default=False)
bpy.types.Scene.keepP = BoolProperty(name='From parent', description='Keep parent transformation', default=False)
bpy.types.Scene.pickGrp = BoolProperty(name='Pick from Group', description='Pick objects from group randomly', default=False)
bpy.types.Scene.gRate = BoolProperty(name='Use rate', description='Duplicate some objects of the group more than others', default=False)
bpy.types.Scene.grpCount=  IntProperty(name="Object rate", description="Make it that number of times more likely to duplicate this object than others.", default=0, min=0, max=100)

bpy.types.Scene.copyType = EnumProperty(items = [('SINGLE', 'Single object', 'All copies are joined into one object.'), ('INST', 'Instances', 'Copies are created as instances, also known as linked duplicates.'), ('REAL', 'Real copies', 'Objects are created as real objects')], name = "", default = 'INST') 
bpy.types.Scene.shapeKey = BoolProperty(name='Shape key', description='Changes the second shape key of the objec(s) randomly', default=False)

bpy.types.Scene.useSeed = BoolProperty(name='Use random seed', description='Use fixed seed for random values to get a more reproducable result. Otherwise system time is used.', default=True)
bpy.types.Scene.randSeed = IntProperty(name='Seed', description='Random seed value', default=1, min=1, max=1000)
  
bpy.types.Scene.animMode = BoolProperty(name='Anim mode', description='Apply full stack on frame change. Warning, use only for rendering and make sure your roa-object is selected!', default=False)
bpy.types.Scene.shapeK = BoolProperty(name='Shape key', description='Randomizes the first shape key (not the base!) of each duplicate between 0 and 1. Only works with real copies right now.', default=False)

bpy.types.Scene.cScale = BoolProperty(name='Cumulate scale', description='Fixed scale will cumulate for every new object', default=False)
bpy.types.Scene.fScaleX = FloatProperty(name="X", default=1, description="Cumulate scale X")
bpy.types.Scene.fScaleY = FloatProperty(name="Y", default=1, description="Cumulate scale Y")
bpy.types.Scene.fScaleZ = FloatProperty(name="Z", default=1, description="Cumulate scale Z")

bpy.types.Scene.target_mode = EnumProperty(items = [('FACES', 'Faces', 'Clone to the faces of the target mesh'), ('POINTS', 'Points', 'Clone to the points of the target mesh')], name = "", default = 'FACES') 
bpy.types.Scene.cyclic = BoolProperty(name='Cyclic', description='Target is a closed circle', default=False)

  
# User Request
bpy.types.Scene.pobjects = BoolProperty(name='Parent objects', description='Parent duplicates to the original object', default=True)

#rewrite to global / local

def stateChange(propName, theProp): 
    if stateDict[propName] != theProp:
        stateDict[propName] = theProp
        return True
    return False

def checkAll():
    check = False
    check = stateChange("numOfObjects", bpy.context.scene.numOfObjects) or stateChange("realtime", bpy.context.scene.realtime)
    check = check or stateChange("randomPosX", bpy.context.scene.randomPosX) or  stateChange("randomPosY", bpy.context.scene.randomPosY) or  stateChange("randomPosZ", bpy.context.scene.randomPosZ) 
    check = check or stateChange("gridSizeX", bpy.context.scene.gridSizeX) or stateChange("gridSizeY", bpy.context.scene.gridSizeY) or stateChange("gridSizeZ", bpy.context.scene.gridSizeZ)
    check = check or stateChange("fixedPosX", bpy.context.scene.fixedPosX) or stateChange("fixedPosY", bpy.context.scene.fixedPosY) or stateChange("fixedPosZ", bpy.context.scene.fixedPosZ)
    check = check or stateChange("fixedRotX", bpy.context.scene.fixedRotX) or stateChange("fixedRotY", bpy.context.scene.fixedRotY) or stateChange("fixedRotZ", bpy.context.scene.fixedRotZ)
    check = check or stateChange("randRotX", bpy.context.scene.randRotX) or  stateChange("randRotY", bpy.context.scene.randRotY) or  stateChange("randRotZ", bpy.context.scene.randRotZ) 
    check = check or stateChange("minSclX", bpy.context.scene.minSclX) or  stateChange("minSclY", bpy.context.scene.minSclY) or  stateChange("minSclZ", bpy.context.scene.minSclZ) 
    check = check or stateChange("maxSclX", bpy.context.scene.maxSclX) or  stateChange("maxSclY", bpy.context.scene.maxSclY) or  stateChange("maxSclZ", bpy.context.scene.maxSclZ) 
    check = check or stateChange("dmode", bpy.context.scene.dmode) or stateChange("coffset", bpy.context.scene.coffset) or stateChange("rPosRange", bpy.context.scene.rPosRange)
    check = check or stateChange("rRotRange", bpy.context.scene.rRotRange) or stateChange("cangles", bpy.context.scene.cangles) or stateChange("fangles", bpy.context.scene.fangles)
    check = check or stateChange("kshape", bpy.context.scene.kshape) or stateChange("nangles", bpy.context.scene.nangles)
    check = check or stateChange("targetObject", bpy.context.scene.targetObject) or stateChange("objGroup", bpy.context.scene.objGroup) or stateChange("pickGrp", bpy.context.scene.pickGrp)
    check = check or stateChange("relOffset", bpy.context.scene.relOffset) or stateChange("rel_axis", bpy.context.scene.rel_axis) or stateChange("fillMode", bpy.context.scene.fillMode)
    check = check or stateChange("useSeed", bpy.context.scene.useSeed) or stateChange("randSeed", bpy.context.scene.randSeed) or stateChange("shapeK", bpy.context.scene.shapeK)
    check = check or stateChange("cScale", bpy.context.scene.cScale) or stateChange("fScaleX", bpy.context.scene.fScaleX) or stateChange("fScaleY", bpy.context.scene.fScaleY) or stateChange("fScaleZ", bpy.context.scene.fScaleZ)
    check = check or stateChange("target_mode", bpy.context.scene.target_mode) or stateChange("cyclic", bpy.context.scene.cyclic) 
    return check

def prepareRT():
    obj = bpy.context.active_object
    obj.select = True
    bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
    if bpy.context.scene.kchildren:
        for ob in bpy.context.selected_objects:
            if not ".roaRt." in ob.name:
                if not "ROA_RT_BOX_TEMPORARY_OBJECT" in ob.name:
                    ob.select = False
    bpy.ops.object.delete()   
    bpy.context.scene.objects.active = obj
    obj.select = True
    return obj
   

def cleanupRT(obj):    
    bpy.context.scene.objects.active = obj
    obj.select = True
    
def isROA():
    try:
        if bpy.context.active_object is not None:
            originalObject = bpy.context.active_object
            set = originalObject["isROA"]
            return set
        return False
    except:
        return False

stateDict = {"realtime": True,
             "numOfObjects": 1,
             "randomPosX": 0,
             "randomPosY": 0,
             "randomPosZ": 0,
             "gridSizeX": 1,
             "gridSizeY": 1,
             "gridSizeZ": 1,
             "fixedPosX": 0,
             "fixedPosY": 0,
             "fixedPosZ": 0,
             "fixedRotX": 0,
             "fixedRotY": 0,
             "fixedRotZ": 0,
             "randRotX": 0,
             "randRotY": 0,
             "randRotZ": 0,
             "minSclX": 1,
             "minSclY": 1,
             "minSclZ": 1,
             "maxSclX": 1,
             "maxSclY": 1,
             "maxSclZ": 1,
             "dmode": False,
             "coffset": True,
             "rPosRange": True,
             "rRotRange": True,
             "cangles": False,
             "fangles": False,
             "kshape": True,
             "pobjects": True,
             "targetObject": "",
             "nangles": True,
             "global_mode": "GLOBAL",
             "kchildren": False,
             "relOffset": False,
             "pickGrp": False,
             "objGroup": "",
             "rintersect": False,
             "max_coll": 1,
             "coll_mode": "AABB",
             "coll_solve": "DELETE",
             "orgDist": 1,
             "singObj": False,
             "rel_axis": "X",
             "fillMode": True,
             "copyType": "INST",
             "randSeed": 1,
             "useSeed": True,
             "shapeK": False,
             "cScale": False,
             "fScaleX": 1,
             "fScaleY": 1,
             "fScaleZ": 1,
             "target_mode": "FACES",
             "cyclic": False}
             
stateDefault = stateDict.copy()
    
@persistent
def scene_update(scene):
    if bpy.context.scene.realtime:   
        if bpy.context.scene.is_updated:
            if isROA(): 
                if checkAll():  
                    rtOb = prepareRT()
                    if rtOb is not None and rtOb.select == True:
                        bpy.ops.object.roa_apply(isRT=True)
                        cleanupRT(rtOb)            
            else:
               bpy.context.scene.realtime = False 
               stateChange("realtime", bpy.context.scene.realtime)

@persistent
def roa_anim_mode(scene):
    if bpy.context.scene.animMode:
        bpy.context.scene.realtime = False 
        stateChange("realtime", bpy.context.scene.realtime)
        rtOb = prepareRT()
        if rtOb is not None and rtOb.select == True:
            bpy.ops.object.roa_apply(isRT=False)
            cleanupRT(rtOb)    
     

           

# User Request
class ROA_Reset(bpy.types.Operator):
    bl_idname = "object.roa_reset"
    bl_label = "Reset"
    bl_options = {'UNDO'}

    def execute(self, context):   
        context.scene.numOfObjects = stateDefault["numOfObjects"]
        context.scene.fixedPosX = stateDefault["fixedPosX"]
        context.scene.fixedPosY = stateDefault["fixedPosY"]
        context.scene.fixedPosZ = stateDefault["fixedPosZ"]
        context.scene.randomPosX = stateDefault["randomPosX"]
        context.scene.randomPosY = stateDefault["randomPosY"]
        context.scene.randomPosZ = stateDefault["randomPosZ"]
        context.scene.fixedRotX = stateDefault["fixedRotX"]
        context.scene.fixedRotY = stateDefault["fixedRotY"]
        context.scene.fixedRotZ = stateDefault["fixedRotZ"]
        context.scene.randRotX = stateDefault["randRotX"]
        context.scene.randRotY = stateDefault["randRotY"]
        context.scene.randRotZ = stateDefault["randRotZ"]
        context.scene.minSclX = stateDefault["minSclX"]
        context.scene.minSclY = stateDefault["minSclY"]
        context.scene.minSclZ = stateDefault["minSclZ"]
        context.scene.maxSclX = stateDefault["maxSclX"]
        context.scene.maxSclY = stateDefault["maxSclY"]
        context.scene.maxSclZ = stateDefault["maxSclZ"]
        context.scene.cangles = stateDefault["cangles"]
        context.scene.fangles = stateDefault["fangles"]
        context.scene.coffset = stateDefault["coffset"]
        context.scene.dmode = stateDefault["dmode"]
        context.scene.gridSizeX = stateDefault["gridSizeX"]
        context.scene.gridSizeY = stateDefault["gridSizeY"]
        context.scene.gridSizeZ = stateDefault["gridSizeZ"]
        context.scene.kshape = stateDefault["kshape"]
        context.scene.singObj = stateDefault["singObj"]
        context.scene.rPosRange = stateDefault["rPosRange"]
        context.scene.rRotRange = stateDefault["rRotRange"]
        context.scene.nangles = stateDefault["nangles"]
        context.scene.pobjects = stateDefault["pobjects"]
        context.scene.targetObject = stateDefault["targetObject"]
        context.scene.objGroup = stateDefault["objGroup"] 
        context.scene.pickGrp = stateDefault["pickGrp"]    
        context.scene.kchildren = stateDefault["kchildren"]
        context.scene.relOffset = stateDefault["relOffset"]
        context.scene.rintersect = stateDefault["rintersect"]
        context.scene.max_coll = stateDefault["max_coll"] 
        context.scene.coll_mode = stateDefault["coll_mode"]
        context.scene.coll_solve = stateDefault["coll_solve"]
        context.scene.rel_axis = stateDefault["rel_axis"]
        context.scene.fillMode = stateDefault["fillMode"]
        context.scene.copyType = stateDefault["copyType"]
        context.scene.useSeed = stateDefault["useSeed"]
        context.scene.randSeed = stateDefault["randSeed"]
        context.scene.shapeK = stateDefault["shapeK"]
        context.scene.cScale = stateDefault["cScale"]
        context.scene.fScaleX = stateDefault["fScaleX"]
        context.scene.fScaleY = stateDefault["fScaleY"]
        context.scene.fScaleZ = stateDefault["fScaleZ"]  
        context.scene.target_mode = stateDefault["target_mode"]      
        context.scene.cyclic = stateDefault["cyclic"]                    
        return {'FINISHED'}

#Store all values in the original object for interactivity    
class ROA_Set(bpy.types.Operator):
    bl_idname = "object.roa_set"
    bl_label = "Make ROA"
    bl_options = {'UNDO'}
    
    def execute(self, context): 
        if context.active_object is None:
            self.report({'ERROR'}, "ROA needs an active object to work on. (right click it again maybe) ")
            return {'FINISHED'}
        originalObject = context.active_object
        originalObject["isROA"] = True
        return {'FINISHED'}
    
class ROA_Store(bpy.types.Operator):
    bl_idname = "object.roa_store"
    bl_label = "Save"
    bl_options = {'UNDO'}
    def execute(self, context): 
        if context.active_object is None:
            self.report({'ERROR'}, "ROA needs an active object to work on. (right click it again maybe) ")
            return {'FINISHED'}
        originalObject = context.active_object
        #for backwards compatibility
        originalObject["ROAversion"] = '78'
        
        originalObject["numOfObjects"] = context.scene.numOfObjects
        originalObject["fixedPosX"] = context.scene.fixedPosX
        originalObject["fixedPosY"] = context.scene.fixedPosY
        originalObject["fixedPosZ"] = context.scene.fixedPosZ
        originalObject["randomPosX"] = context.scene.randomPosX
        originalObject["randomPosY"] = context.scene.randomPosY
        originalObject["randomPosZ"] = context.scene.randomPosZ        
        originalObject["fixedRotX"] = context.scene.fixedRotX
        originalObject["fixedRotY"] = context.scene.fixedRotY
        originalObject["fixedRotZ"] = context.scene.fixedRotZ                     
        originalObject["randRotX"] = context.scene.randRotX
        originalObject["randRotY"] = context.scene.randRotY
        originalObject["randRotZ"] = context.scene.randRotZ 
        originalObject["minSclX"] = context.scene.minSclX
        originalObject["minSclY"] = context.scene.minSclY
        originalObject["minSclZ"] = context.scene.minSclZ
        originalObject["maxSclX"] = context.scene.maxSclX
        originalObject["maxSclY"] = context.scene.maxSclY
        originalObject["maxSclZ"] = context.scene.maxSclZ
        originalObject["cangles"] = context.scene.cangles
        originalObject["fangles"] = context.scene.fangles
        originalObject["coffset"] = context.scene.coffset
        originalObject["dmode"] = context.scene.dmode
        originalObject["gridSizeX"] = context.scene.gridSizeX
        originalObject["gridSizeY"] = context.scene.gridSizeY
        originalObject["gridSizeZ"] = context.scene.gridSizeZ
        originalObject["kshape"] = context.scene.kshape
        originalObject["singObj"] =  context.scene.singObj  
        originalObject["rPosRange"] = context.scene.rPosRange
        originalObject["rRotRange"] = context.scene.rRotRange
        originalObject["nangles"] = context.scene.nangles
        originalObject["pobjects"] = context.scene.pobjects
        originalObject["targetObject"] = context.scene.targetObject      
        #72
        originalObject["objGroup"] = context.scene.objGroup
        originalObject["pickGrp"] = context.scene.pickGrp    
        originalObject["kchildren"] = context.scene.kchildren
        originalObject["relOffset"] = context.scene.relOffset
        originalObject["rintersect"] = context.scene.rintersect
        originalObject["max_coll"] = context.scene.max_coll
        originalObject["coll_mode"] = context.scene.coll_mode
        originalObject["coll_solve"] = context.scene.coll_solve
        originalObject["rel_axis"] = context.scene.rel_axis
        #73
        originalObject["fillMode"] = context.scene.fillMode
        #74
        originalObject["copyType"] = context.scene.copyType
        #75
        originalObject["useSeed"] = context.scene.useSeed
        originalObject["randSeed"] = context.scene.randSeed
        #76
        originalObject["shapeK"] = context.scene.shapeK
        #77
        originalObject["cScale"] = context.scene.cScale
        originalObject["fScaleX"] = context.scene.fScaleX
        originalObject["fScaleY"] = context.scene.fScaleY
        originalObject["fScaleZ"] = context.scene.fScaleZ   
        #78             
        originalObject["target_mode"] = context.scene.target_mode   
        originalObject["cyclic"] = context.scene.cyclic   
        return {'FINISHED'}

class ROA_Read(bpy.types.Operator):
    bl_idname = "object.roa_read"
    bl_label = "Load"
    bl_options = {'UNDO'}
    
    def execute(self, context): 
        if context.active_object is None:
            self.report({'ERROR'}, "ROA needs an active object to work on. (right click it again maybe) ")
            return {'FINISHED'}
        dataList = {}
        originalObject = context.active_object
        ver = 0
        
        try:
            ver = int(originalObject["ROAversion"])
        except:
            self.report({'ERROR'}, "Sorry, object doesn't seem to have ROA data")
            return {'FINISHED'}
        
        #for backwards compatibility
        if ver > 70:
            try:
                context.scene.numOfObjects = originalObject["numOfObjects"]
                context.scene.fixedPosX = originalObject["fixedPosX"]
                context.scene.fixedPosY = originalObject["fixedPosY"]
                context.scene.fixedPosZ = originalObject["fixedPosZ"]
                context.scene.randomPosX = originalObject["randomPosX"]
                context.scene.randomPosY = originalObject["randomPosY"]
                context.scene.randomPosZ = originalObject["randomPosZ"]
                context.scene.fixedRotX = originalObject["fixedRotX"]
                context.scene.fixedRotY = originalObject["fixedRotY"]
                context.scene.fixedRotZ = originalObject["fixedRotZ"]
                context.scene.randRotX = originalObject["randRotX"]
                context.scene.randRotY = originalObject["randRotY"]
                context.scene.randRotZ = originalObject["randRotZ"]
                context.scene.minSclX = originalObject["minSclX"]
                context.scene.minSclY = originalObject["minSclY"]
                context.scene.minSclZ = originalObject["minSclZ"]
                context.scene.maxSclX = originalObject["maxSclX"]
                context.scene.maxSclY = originalObject["maxSclY"]
                context.scene.maxSclZ = originalObject["maxSclZ"]
                context.scene.cangles = originalObject["cangles"]
                context.scene.fangles = originalObject["fangles"]
                context.scene.coffset = originalObject["coffset"]
                context.scene.dmode = originalObject["dmode"]
                context.scene.gridSizeX = originalObject["gridSizeX"]
                context.scene.gridSizeY = originalObject["gridSizeY"]
                context.scene.gridSizeZ = originalObject["gridSizeZ"]
                context.scene.kshape = originalObject["kshape"]
                context.scene.singObj = originalObject["singObj"]
                context.scene.rPosRange = originalObject["rPosRange"]
                context.scene.rRotRange = originalObject["rRotRange"]
                context.scene.nangles = originalObject["nangles"]
                context.scene.pobjects = originalObject["pobjects"]
                context.scene.targetObject = originalObject["targetObject"]

            except:
                self.report({'ERROR'}, "Sorry, object doesn't seem to have ROA data")

        if ver > 71:  
            try:
                context.scene.objGroup = originalObject["objGroup"] 
                context.scene.pickGrp = originalObject["pickGrp"]    
                context.scene.kchildren = originalObject["kchildren"]
                context.scene.relOffset = originalObject["relOffset"]
                context.scene.rintersect = originalObject["rintersect"]
                context.scene.max_coll = originalObject["max_coll"] 
                context.scene.coll_mode = originalObject["coll_mode"]
                context.scene.coll_solve = originalObject["coll_solve"]
                context.scene.rel_axis = originalObject["rel_axis"]
            except:
                self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")
        if ver > 72:  
            try:
                context.scene.fillMode = originalObject["fillMode"] 
            except:
                self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")
                
        if ver > 73:  
            try:
                context.scene.copyType = originalObject["copyType"] 
            except:
                self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")

        if ver > 74:  
            try:
                context.scene.useSeed = originalObject["useSeed"] 
                context.scene.randSeed = originalObject["randSeed"] 
            except:
                self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")    
        if ver > 75:  
            try:
                context.scene.shapeK = originalObject["shapeK"] 
            except:
                self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")    
        if ver > 76:  
            try:
                context.scene.cScale = originalObject["cScale"] 
                context.scene.fScaleX = originalObject["fScaleX"]
                context.scene.fScaleY = originalObject["fScaleY"]
                context.scene.fScaleZ = originalObject["fScaleZ"]
            except:
                self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")   
        if ver > 76:  
            try:
                context.scene.target_mode = originalObject["target_mode"] 
                context.scene.cyclic = originalObject["cyclic"] 
            except:
                self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")     
        return {'FINISHED'}

#Simple collision detection
def simpleCollision(object1, object2, method):
    if method == 'SIMP':
        #Simplified distance mode
       if abs(object1.location[0]-object2.location[0]) <= bpy.context.scene.orgDist and abs(object1.location[1]-object2.location[1]) <= bpy.context.scene.orgDist and abs(object1.location[2]-object2.location[2]) <= bpy.context.scene.orgDist:
            return 1
       return 0
   
    if method == 'ORDI':
        #Origin distance mode
       if math.sqrt((object1.location[0]-object2.location[0])**2 + (object1.location[1]-object2.location[1])**2 + (object1.location[2]-object2.location[2])**2) <= bpy.context.scene.orgDist:
            return 1
       return 0

    if method == 'AABB':
        #Get Bounding Box vectors
        box1 = [object1.matrix_world * Vector(c) for c in object1.bound_box]
        box2 = [object2.matrix_world * Vector(c) for c in object2.bound_box]
       
        #find min/max  
        box1MinX = box1MaxX = box1[0][0]
        box2MinX = box2MaxX = box2[0][0]
        box1MinY = box1MaxY = box1[0][1]
        box2MinY = box2MaxY = box2[0][1]
        box1MinZ = box1MaxZ = box1[0][2]
        box2MinZ = box2MaxZ = box2[0][2]
        
        for i in range(1, 8):
            box1MinX = box1MinX if box1MinX < box1[i][0] else box1[i][0]
            box2MinX = box2MinX if box2MinX < box2[i][0] else box2[i][0]
            box1MaxX = box1MaxX if box1MaxX > box1[i][0] else box1[i][0]
            box2MaxX = box2MaxX if box2MaxX > box2[i][0] else box2[i][0]
            
            box1MinY = box1MinY if box1MinY < box1[i][1] else box1[i][1]
            box2MinY = box2MinY if box2MinY < box2[i][1] else box2[i][1]
            box1MaxY = box1MaxY if box1MaxY > box1[i][1] else box1[i][1]
            box2MaxY = box2MaxY if box2MaxY > box2[i][1] else box2[i][1]
            
            box1MinZ = box1MinZ if box1MinZ < box1[i][2] else box1[i][2]
            box2MinZ = box2MinZ if box2MinZ < box2[i][2] else box2[i][2]
            box1MaxZ = box1MaxZ if box1MaxZ > box1[i][2] else box1[i][2]
            box2MaxZ = box2MaxZ if box2MaxZ > box2[i][2] else box2[i][2]

        if bpy.context.scene.aabbSize != 100:
            scaleFac = 1 - (bpy.context.scene.aabbSize / 100)
            box1MinX += scaleFac * (box1MaxX - box1MinX)
            box2MinX += scaleFac * (box1MaxX - box1MinX)
            box1MaxX -= scaleFac * (box1MaxX - box1MinX)
            box2MaxX -= scaleFac * (box1MaxX - box1MinX)
            box1MinY += scaleFac * (box1MaxY - box1MinY)
            box2MinY += scaleFac * (box1MaxY - box1MinY)
            box1MaxY -= scaleFac * (box1MaxY - box1MinY)
            box2MaxY -= scaleFac * (box1MaxY - box1MinY)
            box1MinZ += scaleFac * (box1MaxZ - box1MinZ)
            box2MinZ += scaleFac * (box1MaxZ - box1MinZ)
            box1MaxZ -= scaleFac * (box1MaxZ - box1MinZ)
            box2MaxZ -= scaleFac * (box1MaxZ - box1MinZ)
        returnVal = (box1MaxX >= box2MinX) and (box1MinX <= box2MaxX) and (box1MaxY >= box2MinY) and (box1MinY <= box2MaxY) and (box1MaxZ >= box2MinZ) and (box1MinZ <= box2MaxZ)
                
    return returnVal

#Bounding box for realtime preview
def createRTBox():
    activeObj = bpy.context.active_object
    
    bpy.ops.mesh.primitive_cube_add() 
    bound_box = bpy.context.active_object 
    bound_box.name = "ROA_RT_BOX_TEMPORARY_OBJECT"
    bound_box.draw_type = 'BOUNDS'

    if bpy.context.scene.dmode:
        dimX = activeObj.dimensions[0] * bpy.context.scene.gridSizeX * (bpy.context.scene.fixedPosX) / 2
        dimY = activeObj.dimensions[1] * bpy.context.scene.gridSizeY * (bpy.context.scene.fixedPosY) / 2
        dimZ = activeObj.dimensions[2] * bpy.context.scene.gridSizeZ * (bpy.context.scene.fixedPosZ) / 2
    else:
        dimX = activeObj.dimensions[0] + activeObj.dimensions[0] * bpy.context.scene.numOfObjects * (bpy.context.scene.fixedPosX) / 2
        dimY = activeObj.dimensions[1] + activeObj.dimensions[1] * bpy.context.scene.numOfObjects * (bpy.context.scene.fixedPosY) / 2
        dimZ = activeObj.dimensions[2] + activeObj.dimensions[2] * bpy.context.scene.numOfObjects * (bpy.context.scene.fixedPosZ) / 2

    bound_box.parent = activeObj
    bound_box.dimensions = (dimX, dimY, dimZ)     
    bound_box.location = Vector((dimX / 2, dimY / 2, dimZ / 2)) - Vector((activeObj.dimensions[0] / 2, activeObj.dimensions[1] / 2,activeObj.dimensions[2] / 2)) 
    bound_box.select = False
    
    bpy.context.scene.objects.active = activeObj
    
def removeRTBox():
    if bpy.data.objects.get("ROA_RT_BOX_TEMPORARY_OBJECT") is not None:
        activeObj = bpy.context.active_object
        try:
            bpy.context.scene.objects.unlink(bpy.data.objects["ROA_RT_BOX_TEMPORARY_OBJECT"])
        
        except:
            pass
        bpy.context.scene.objects.active = activeObj

class ROA_Apply(bpy.types.Operator):
    bl_idname = "object.roa_apply"
    bl_label = "Apply"
    bl_options = {'UNDO'}
    
    isRT = bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(self, context):
        if context.active_object.select == False: 
            return
        return context.active_object is not None
    
    def execute(self, context):           
        """Leftover from the past, to be changed"""
        if context.scene.copyType == 'SINGLE':
            context.scene.singObj = True
        else:
            context.scene.singObj = False
            
        """Check for incompatibilities"""
        if not context.scene.realtime and context.scene.singObj:
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    if area.spaces.active.local_view is not None:
                        self.report({'ERROR'}, "Single object mode can't be used in the local User Perspective.\n Please press numpad / to leave the local User Perspective before applying.")
                        return {'FINISHED'}
                    
            if not (context.active_object.type == 'MESH' or context.active_object.type == 'CURVE'):
                self.report({'ERROR'}, "Single object mode (joining objects) can be used on mesh type or curve type objects only.")
                return {'FINISHED'}
        if context.scene.copyType == 'REAL' or context.scene.copyType == 'SINGLE': 
            if context.active_object.type == 'EMPTY':
                self.report({'ERROR'}, "None type objects (e.g. Group instances) can only be copied as instances")
                return {'FINISHED'}

        
        """Remove Realtime leftovers"""
        if not self.isRT:
            rtOb = prepareRT()
            context.scene.realtime = False
            stateChange("realtime", bpy.context.scene.realtime)
          
        """Random seed"""
        if context.scene.useSeed:
            random.seed(context.scene.randSeed)      
                    
        """Save all Data"""
        sce = bpy.context.scene
        
        originalObj = context.active_object
        masterObj = originalObj
        
        """Cause of the group mode we need to make this in two steps now"""
        modList = []
        for mod in masterObj.modifiers:
           modList.append(masterObj.modifiers[mod.name].show_viewport)

        """Pick grom group"""
        useGroup = False
        srcList = []
        grpModList = []
        if context.scene.pickGrp and bpy.data.groups:
            if context.scene.objGroup != "":
                obID = 0
                for ob in bpy.data.groups[context.scene.objGroup].objects:
                    srcList.append(ob)
                    """Save and disable modifiers for group objects"""
                    #add ID so copies can be identified later
                    ob["sourceID"] = obID
                    grpModList.append([])
                    for mod in ob.modifiers:
                        grpModList[obID].append(ob.modifiers[mod.name].show_viewport)
                        if mod.type != "CURVE":
                            ob.modifiers[mod.name].show_viewport = False
                    obID += 1
                useGroup = True
                
        """Cause of the group mode we need to make this in two steps now"""     
        for mod in masterObj.modifiers:
            if mod.type != "CURVE":
               masterObj.modifiers[mod.name].show_viewport = False      

        """Partly unneccessary"""
        originalLocation = context.object.location   
        originalLayers = context.object.layers
        originalName = originalObj.name
        originalMatrix = originalObj.matrix_world
        originalRotation = originalObj.rotation_euler
        originalDim = originalObj.dimensions
        
        """Draw state will get removed"""
        originalDeselect = False
        
        lastObj = masterObj

        cuRotX = 0
        cuRotY = 0
        cuRotZ = 0
       
        
        """Target is a mesh"""
        targetObj = None
        cloneToMesh = False
        targetPointList = []
        if (context.scene.targetObject != "") and (context.scene.dmode != True):
            #Global / Local to be removed
            context.scene.global_mode = 'GLOBAL'
            targetObj = context.scene.objects[context.scene.targetObject]
            if targetObj.type == 'MESH':
                targetObjMatrix = targetObj.matrix_world
                if context.scene.target_mode == "FACES":
                    targetObjPolyCount = len(targetObj.data.polygons) 
                    #if context.scene.fillRand:
                        #targetPlaceList = [0] * targetObjPolyCount
                    distFactor = context.scene.numOfObjects / targetObjPolyCount
                    targetPolyIndex = 0

                if context.scene.target_mode == "POINTS":
                    targetPointIndex = 0
                    for vertex in targetObj.data.vertices:  
                        targetPointList.append(targetObj.matrix_world * vertex.co) 
                                
                cloneToMesh = True     
                        
        else:
            context.scene.global_mode = 'LOCAL'
            
        """Create Grid for grid mode"""
        realCount = 0
        if context.scene.dmode:
            offsetGrid = []
            oGridX = context.scene.gridSizeX
            oGridY = context.scene.gridSizeY
            oGridZ = context.scene.gridSizeZ
            
            realCount = objCount = oGridX * oGridY * oGridZ
            """Limit maximum count in realtime preview"""
            if context.scene.realtime:
                if objCount > 125:
                    oGridX = oGridX if oGridX < 5 else 5
                    oGridY = oGridY if oGridY < 5 else 5
                    oGridZ = oGridZ if oGridZ < 5 else 5
                    objCount = oGridX * oGridY * oGridZ
                    
            """Depending on the relative axis we have to create the grid in a different way"""
            if not context.scene.relOffset or context.scene.rel_axis == 'Z':        
                for x in range(0, oGridX, 1):
                    for y in range(0, oGridY, 1):
                        for z in range(0, oGridZ, 1):    
                            offsetGrid.append((x*context.scene.fixedPosX,y*context.scene.fixedPosY,z*context.scene.fixedPosZ))   
            elif context.scene.rel_axis == 'Y':
                for x in range(0, oGridX, 1):
                    for z in range(0, oGridZ, 1):
                        for y in range(0, oGridY, 1):    
                            offsetGrid.append((x*context.scene.fixedPosX,y*context.scene.fixedPosY,z*context.scene.fixedPosZ))                  
            elif context.scene.rel_axis == 'X':  
                for z in range(0, oGridZ, 1):
                    for y in range(0, oGridY, 1):
                        for x in range(0, oGridX, 1):    
                            offsetGrid.append((x*context.scene.fixedPosX,y*context.scene.fixedPosY,z*context.scene.fixedPosZ))                  
        else:
            realCount = objCount = context.scene.numOfObjects + 1            
            """Limit maximum count in realtime preview"""
            if context.scene.realtime:
                if objCount > 125:
                    objCount = 125
            
        """Save objects in list"""
        objList = []
        
        """Calculate preview bounding box"""
        if context.scene.realtime and realCount > 125:
            createRTBox()
        else:
            removeRTBox()
                      
        for index in range(1, objCount):
            """Patterns?"""
            #if index % 2 != 0:
            #    continue
            
            """Pick from group"""
            if useGroup:
                originalObj = srcList[int(random.random() * len(srcList))]
                originalDim = originalObj.dimensions
            
            
            """Offset Range +/-"""
            if context.scene.rPosRange:
                rndPosX = random.random() * context.scene.randomPosX * 2 - context.scene.randomPosX
                rndPosY = random.random() * context.scene.randomPosY * 2 - context.scene.randomPosY
                rndPosZ = random.random() * context.scene.randomPosZ * 2 - context.scene.randomPosZ
            else:
                rndPosX = random.random() * context.scene.randomPosX
                rndPosY = random.random() * context.scene.randomPosY
                rndPosZ = random.random() * context.scene.randomPosZ
            rndPos = (rndPosX, rndPosY, rndPosZ)
            
            """Full Angles"""
            if not bpy.context.scene.fangles:
                if context.scene.rRotRange:
                    rndRotX = random.random() * context.scene.randRotX * 2 - context.scene.randRotX
                    rndRotY = random.random() * context.scene.randRotY * 2 - context.scene.randRotY
                    rndRotZ = random.random() * context.scene.randRotZ * 2 - context.scene.randRotZ
                else:
                    """+ Only"""
                    rndRotX = random.random() * context.scene.randRotX 
                    rndRotY = random.random() * context.scene.randRotY
                    rndRotZ = random.random() * context.scene.randRotZ 
            else:
                """Range + / - for full angles"""
                rangePMX = 1
                rangePMY = 1
                rangePMZ = 1
                if context.scene.rRotRange:
                    if (random.random() < 0.5):
                        rangePMX = -1
                    if (random.random() < 0.5):
                        rangePMY = -1
                    if (random.random() < 0.5):
                        rangePMZ = -1
                        
                if (random.random() < 0.5):
                    rndRotX = context.scene.randRotX * rangePMX
                else:
                    rndRotX = 0
                if (random.random() < 0.5):
                    rndRotY = context.scene.randRotY * rangePMY
                else:
                    rndRotY = 0
                if (random.random() < 0.5):
                    rndRotZ = context.scene.randRotZ * rangePMZ
                else:
                    rndRotZ = 0   
                    
            
            """Keep Shape"""
            if context.scene.kshape:
                rndSclZ = random.random() * (context.scene.maxSclZ - context.scene.minSclZ) + context.scene.minSclZ
                rndScl = (rndSclZ, rndSclZ, rndSclZ)
                """Cumulate scale"""
                if context.scene.cScale:
                    rndSclZ *= context.scene.fScaleZ**index
                    rndScl = (rndSclZ, rndSclZ, rndSclZ)

            else:
                rndSclX = random.random() * (context.scene.maxSclX - context.scene.minSclX) + context.scene.minSclX
                rndSclY = random.random() * (context.scene.maxSclY - context.scene.minSclY) + context.scene.minSclY
                rndSclZ = random.random() * (context.scene.maxSclZ - context.scene.minSclZ) + context.scene.minSclZ
                rndScl = (rndSclX, rndSclY, rndSclZ)
                """Cumulate scale"""
                if context.scene.cScale:
                    rndSclX *= context.scene.fScaleX**index
                    rndSclY *= context.scene.fScaleY**index
                    rndSclZ *= context.scene.fScaleZ**index
                    rndScl = (rndSclX, rndSclY, rndSclZ)
            
            """Cumulate Offset is always true, except for target mesh"""
            if cloneToMesh:
                cuIndex = 1      
            else:
                cuIndex = index
            
            if context.scene.dmode:
                offsetPos = offsetGrid[index]
            else:
                offsetPos = (context.scene.fixedPosX*cuIndex, context.scene.fixedPosY*cuIndex, context.scene.fixedPosZ*cuIndex)

            """Cumulate Rotation"""
            if context.scene.cangles:
                cuRotX = context.scene.fixedRotX * index
                cuRotY = context.scene.fixedRotY * index
                cuRotZ = context.scene.fixedRotZ * index
            else:
                cuRotX = context.scene.fixedRotX
                cuRotY = context.scene.fixedRotY
                cuRotZ = context.scene.fixedRotZ
            
            """Rotation"""
            rotX = (rndRotX+cuRotX)*0.0174533
            rotY = (rndRotY+cuRotY)*0.0174533
            rotZ = (rndRotZ+cuRotZ)*0.0174533
            rotVal = (rotX, rotY, rotZ)
                
       
            """Create duplicates"""     
            duplicate = originalObj.copy()         
            if context.scene.copyType == 'REAL':
                duplicate.data = originalObj.data.copy()  
            currentObj = duplicate  
            currentObj["isROA"] = False
            objList.append(currentObj)    
 
            """Shape key"""
            if context.scene.shapeK:
                shapeKey = bpy.data.objects[duplicate.name].data.shape_keys
                if shapeKey is not None and len(shapeKey.key_blocks) >= 2:
                    shapeKey.key_blocks[1].value = random.random()
                        
                #duplicate.data.shape_keys[0].key_blocks[1].value = random.random()
            
            if useGroup:
                duplicate.location = currentObj.location = masterObj.location 
                                           
            """ Set Parent """
            duplicate.parent = masterObj 
            if cloneToMesh and context.scene.target_mode == "POINTS": 
                #parenting still messes with some things 
                duplicate.matrix_parent_inverse = masterObj.matrix_world.inverted()
               
            """Clone on Mesh, not in grid mode""" 
            if cloneToMesh:
                if context.scene.target_mode == "FACES":
                    currentPoly = targetObj.data.polygons[targetPolyIndex]
                    quat = currentPoly.normal.to_track_quat('Z', 'Y')
                    loc = Matrix.Translation(currentPoly.center)
                    mat = targetObjMatrix * loc * quat.to_matrix().to_4x4()
                    duplicate.matrix_world = mat
                    if context.scene.nangles: 
                        mat.invert()
                        duplicate.matrix_world *= Matrix.Rotation(rotX, 4, 'X') 
                        duplicate.matrix_world *= Matrix.Rotation(rotY, 4, 'Y')
                        duplicate.matrix_world *= Matrix.Rotation(rotZ, 4, 'Z') 
                        duplicate.location += (Vector(offsetPos) + Vector(rndPos)) * mat 
                        duplicate.scale = mathutils.Vector(rndScl)
                    else:
                        duplicate.location += Vector(offsetPos) + Vector(rndPos)
                        duplicate.scale = Vector(rndScl)
                        duplicate.rotation_euler = Vector(rotVal)
        
                    if context.scene.fillMode:
                        targetPolyIndex += 1
                        if targetPolyIndex >= len(targetObj.data.polygons):
                            targetPolyIndex = 0
                    else:
                        targetPolyIndex = round(random.random() * targetObjPolyCount)
                        if targetPolyIndex >= len(targetObj.data.polygons):
                            targetPolyIndex = 0
                            
                if context.scene.target_mode == "POINTS": 
                    if context.scene.nangles:
                        #if cyclic or not
                        if targetPointIndex+1 < len(targetPointList):
                            edgeTangent = Vector(targetPointList[targetPointIndex+1]) - Vector(targetPointList[targetPointIndex])
                        else:
                            if context.scene.cyclic:
                                edgeTangent = Vector(targetPointList[0]) - Vector(targetPointList[targetPointIndex])
                            else:
                                edgeTangent = Vector(targetPointList[targetPointIndex]) - Vector(targetPointList[targetPointIndex-1])
   
                        
                    if context.scene.nangles:  
                        #Always X forward Z Up ?        
                        duplicate.rotation_euler = Vector(edgeTangent.to_track_quat('X', 'Z').to_euler()) + Vector(rotVal)
                        quat = edgeTangent.to_track_quat('X', 'Z')
                        loc = Matrix.Translation(Vector(targetPointList[targetPointIndex]))
                        mat = duplicate.matrix_world * loc * quat.to_matrix().to_4x4()
                        mat.invert()

                        duplicate.location = Vector(targetPointList[targetPointIndex]) #* targetObjMatrix
                        duplicate.location += (Vector(offsetPos) + Vector(rndPos)) * mat
                        duplicate.scale = Vector(rndScl)
                    else:
                        duplicate.location = Vector(targetPointList[targetPointIndex]) + Vector(offsetPos) + Vector(rndPos)
                        duplicate.scale = Vector(rndScl)
                        duplicate.rotation_euler = Vector(rotVal)
                        
                    if context.scene.fillMode:
                        targetPointIndex += 1
                        if targetPointIndex >= len(targetPointList):
                            targetPointIndex = 0
                    else:
                        targetPointIndex  = round(random.random() * len(targetPointList))
                        if targetPointIndex >= len(targetPointList):
                            targetPointIndex = 0
                                              
                              
            else:  
                duplicate.rotation_euler = Vector(rotVal)   
                duplicate.scale = Vector(rndScl) 
                if context.scene.global_mode == 'LOCAL':
                    duplicate.location = Vector(offsetPos) + Vector(rndPos)
                else:
                    duplicate.location = Vector(originalLocation) + Vector(offsetPos) + Vector(rndPos)
            
            """Relative offset"""
            if context.scene.relOffset and targetObj == None:
                """For the sakes of the different modes and simplicity we just override the previously added offset here"""
                if lastObj == masterObj:
                    if context.scene.rel_axis == 'X':
                        duplicate.location[0] = lastObj.scale[0]*lastObj.dimensions[0]/2 + duplicate.scale[0]*duplicate.dimensions[0]/2 + context.scene.fixedPosX                    
                        
                    if context.scene.rel_axis == 'Y':
                        duplicate.location[1] = lastObj.scale[1]*lastObj.dimensions[1]/2 + duplicate.scale[1]*duplicate.dimensions[1]/2 + context.scene.fixedPosY           
       
                    if context.scene.rel_axis == 'Z':
                        duplicate.location[2] = lastObj.scale[2]*lastObj.dimensions[2]/2 + duplicate.scale[2]*duplicate.dimensions[2]/2 + context.scene.fixedPosZ

                else:
                    if context.scene.rel_axis == 'X':
                        if not context.scene.dmode or cuIndex % oGridX != 0:
                            duplicate.location[0] = lastObj.location[0] + lastObj.scale[0]*lastObj.dimensions[0]/2 + duplicate.scale[0]*duplicate.dimensions[0]/2 + context.scene.fixedPosX

                    if context.scene.rel_axis == 'Y':
                        if not context.scene.dmode or cuIndex % oGridY != 0:
                            duplicate.location[1] = lastObj.location[1] + lastObj.scale[1]*lastObj.dimensions[1]/2 + duplicate.scale[1]*duplicate.dimensions[1]/2 + context.scene.fixedPosY
                            
                    if context.scene.rel_axis == 'Z':
                        if not context.scene.dmode or cuIndex % oGridZ != 0:
                            duplicate.location[2] = lastObj.location[2] + lastObj.scale[2]*lastObj.dimensions[2]/2 + duplicate.scale[2]*duplicate.dimensions[2]/2 + context.scene.fixedPosZ
                duplicate.location += Vector(rndPos)
                lastObj = duplicate   
         
              
            duplicate.select = False
            currentObj.select = False
       
        """Update Scene"""   
        joinActiveOb = None
        if not context.scene.realtime and context.scene.singObj:
            firstOb = True
            masterObj.select = False
            for ob in objList:
                sce.objects.link(ob) 
                ob.layers = originalLayers
                ob.select = True
                #apply all modifiers...doesnt make sense, user has to do it
                #ob.to_mesh(sce, True, "PREVIEW")
                if firstOb:
                    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=True)
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                    firstOb = False
                    joinActiveOb = ob
        else:  
            for ob in objList:
                sce.objects.link(ob)            
                ob.layers = originalLayers
        sce.update()
        
        """check for intersections, not in realtime mode"""
        if context.scene.rintersect and not context.scene.realtime:
            collPoints = [0] * len(objList)
            maxPoints = 0
            for i in range(0, len(objList)):
                for v in range(i + 1, len(objList)):
                    collPoints[i] += simpleCollision(objList[i], objList[v], context.scene.coll_mode)    
                        
            #Solve the intersection problem in different ways                
            if context.scene.coll_solve == 'DELETE':
                i = 0
                for ob in objList[:]:
                    if collPoints[i] > context.scene.max_coll-1:
                        #dont delete first / join object
                        if context.scene.singObj:
                            if joinActiveOb != ob:
                                sce.objects.unlink(ob)
                                objList.remove(ob)
                        else:
                            sce.objects.unlink(ob)
                            objList.remove(ob)
                    i += 1
                        
            if context.scene.coll_solve == 'MOVE':     
                 offVec = Vector((context.scene.fixedPosX, context.scene.fixedPosY, context.scene.fixedPosZ))       
                 for i in range(0, len(objList)):
                    if collPoints[i] > context.scene.max_coll-1:
                        objList[i].location += offVec
                        
            if context.scene.coll_solve == 'SCALE':
                if context.scene.kshape:
                    newScale = Vector((context.scene.minSclZ, context.scene.minSclZ, context.scene.minSclZ))    
                else:
                    newScale = Vector((context.scene.minSclX, context.scene.minSclY, context.scene.minSclZ))
                for i in range(0, len(objList)):
                    if collPoints[i] > context.scene.max_coll-1:
                        objList[i].scale = newScale
                        
            if context.scene.coll_solve == 'SELECT' and not context.scene.singObj:
                originalDeselect = True
                for i in range(0, len(objList)):
                    if collPoints[i] > context.scene.max_coll-1:
                        objList[i].select = True
            sce.update()
                        
        """Join Objects"""
        if not context.scene.realtime and context.scene.singObj and (originalObj.type == 'MESH' or originalObj.type == 'CURVE'):
            context.scene.objects.active = joinActiveOb
            masterObj.select = False
            for ob in srcList:
                ob.select = False
            bpy.ops.object.join()
            masterObj.select = True
            context.scene.objects.active = originalObj

        """Enable modifier viewport visibility for the original object(s)"""
        if useGroup:
            for ob in bpy.data.groups[context.scene.objGroup].objects:
                modCounter = 0
                for mod in ob.modifiers:
                    obID = ob["sourceID"]
                    ob.modifiers[mod.name].show_viewport = grpModList[obID][modCounter]                      
                    modCounter += 1
        else:
            modCounter = 0
            for mod in masterObj.modifiers:
                masterObj.modifiers[mod.name].show_viewport = modList[modCounter]
                modCounter += 1
        
        if context.scene.singObj and not context.scene.realtime:    
            masterObj.select = False
            for ob in srcList:
                ob.select = False
            joinActiveOb.select = True
            context.scene.objects.active = joinActiveOb

            if context.scene.global_mode == 'LOCAL':
                joinActiveOb.parent = masterObj
                
            if not context.scene.pobjects:
                bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')          

            """Enable modifier viewport visibility for the clone object"""
            if not useGroup:
                modCounter = 0
                for mod in context.object.modifiers:
                    context.object.modifiers[mod.name].show_viewport = modList[modCounter]
                    modCounter += 1
            else:
                """Remove possible leftovers"""
                for mod in context.object.modifiers:
                    context.object.modifiers.remove(mod)

        else:
            originalObj.select = False
            index = 0
            for ob in objList:
                context.scene.objects.active = ob
                obSelectState = ob.select
                ob.select = True
                #ob.draw_type = originalDraw
                if context.scene.realtime:
                    ob.name = originalName + ".roaRt." + str(index)
                    index += 1
                if ((not context.scene.pobjects) or context.scene.singObj) and not context.scene.realtime:
                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
  
                modCounter = 0
                if not context.scene.realtime:
                    if useGroup:
                        modCounter = 0
                        for mod in ob.modifiers:
                            obID = ob["sourceID"]
                            ob.modifiers[mod.name].show_viewport = grpModList[obID][modCounter]                      
                            modCounter += 1
                    else:
                        for mod in ob.modifiers:
                            ob.modifiers[mod.name].show_viewport = modList[modCounter]
                            modCounter += 1
                ob.select = obSelectState
          
        originalObj = masterObj
        if not originalDeselect:
            masterObj.select = True  
            if originalObj != masterObj:
                originalObj.select = False 
            context.scene.objects.active = None
        else:
            masterObj.select = False
            originalDeselect = True
            context.scene.objects.active = None 
        return {'FINISHED'}
 
 

class CustomPanel(bpy.types.Panel):
    """Random Object Array"""
    bl_label = "Random Object Array"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'ROA'
    bl_context = 'objectmode'

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        split = box.split()
        col = split.column()
        col.prop(context.scene, "realtime")
        col = split.column()
        col.prop(context.scene, "kchildren")
        split = box.split()
        col = split.column(align=True)
        col.operator(ROA_Reset.bl_idname, text = "Reset all values") 
        col.operator(ROA_Set.bl_idname, text = "Make Realtime object") 

        col = split.column(align=True)
        col.operator(ROA_Store.bl_idname, text = "Save to object")         
        col.operator(ROA_Read.bl_idname, text = "Load from object") 
        
                
        split = box.split()
        col = split.column()
        
        col.prop(context.scene, "useSeed")
        if context.scene.useSeed:
            col = split.column()
            col.prop(context.scene, "randSeed")
            
        split = box.split()
        col = split.column(align=True) 
        if context.scene.dmode:
            col.prop(context.scene, "gridSizeX")
            col.prop(context.scene, "gridSizeY")
            col.prop(context.scene, "gridSizeZ")
        else:
            col.prop(context.scene, "numOfObjects")

            
        split = box.split()
        col = split.column(align=True)

        col.prop(context.scene, "copyType")
                
        col.label(text="Fixed Offset")
        col.prop(context.scene, "fixedPosX")
        col.prop(context.scene, "fixedPosY")
        col.prop(context.scene, "fixedPosZ")
        col.prop(context.scene, "relOffset")   
                       
        if context.scene.relOffset:  
            col.prop(context.scene, "rel_axis")    
        
        col = split.column(align=True)
        
        col.prop(context.scene, "dmode")  
        col.label(text="Random Offset")
        col.prop(context.scene, "randomPosX")
        col.prop(context.scene, "randomPosY")
        col.prop(context.scene, "randomPosZ")  
        col.prop(context.scene, "rPosRange")      
 
        split = box.split()
        col = split.column(align=True)    
            
        col.label(text="Fixed Rotation")
        col.prop(context.scene, "fixedRotX")
        col.prop(context.scene, "fixedRotY")
        col.prop(context.scene, "fixedRotZ")
        col.prop(context.scene, "cangles")
        col.prop(context.scene, "fangles")
         
        col = split.column(align=True)
        
        col.label(text="Random Rotation")
        col.prop(context.scene, "randRotX")
        col.prop(context.scene, "randRotY")
        col.prop(context.scene, "randRotZ")
        col.prop(context.scene, "rRotRange")

        split = box.split()
        col = split.column(align=True)

        col.label(text="Random Scale Min.")
        if not context.scene.kshape:
            col.prop(context.scene, "minSclX")
            col.prop(context.scene, "minSclY")
            col.prop(context.scene, "minSclZ")
        else:
            col.prop(context.scene, "minSclZ", text="Min:")

            
        col.prop(context.scene, "kshape")
        col.prop(context.scene, "cScale")   

        col = split.column(align=True) 
        
        col.label(text="Random Scale Max.")
        if not context.scene.kshape:
            col.prop(context.scene, "maxSclX")
            col.prop(context.scene, "maxSclY")
            col.prop(context.scene, "maxSclZ")
        else:
            col.prop(context.scene, "maxSclZ", text="Max:")
           
        col.prop(context.scene, "pobjects") 
        col.prop(context.scene, "pickGrp")
        
        if not context.scene.kshape:
            if context.scene.cScale:
                split = box.split()
                col = split.column(align=True)
                col.prop(context.scene, "fScaleX")
                col.prop(context.scene, "fScaleY")
                col.prop(context.scene, "fScaleZ")    
        else:
            if context.scene.cScale:
                split = box.split()
                col = split.column()
                col.prop(context.scene, "fScaleZ", text="Cumulate scale")  
 
        if context.scene.pickGrp:
            split = box.split()
            col = split.column() 
            col.label(text="Group:")
            col.prop_search(context.scene, "objGroup", bpy.data, "groups", text="")
            #col.prop(context.scene, "gRate")
            
            #if context.scene.gRate:

                #row.template_list(...)

                #col.prop(context.scene, "grpCount")
    
        
        """Warning labels""" 
        if context.object is not None:  
            if context.object.type == 'MESH':
                mesh = bpy.context.active_object.data
                triCount = len(mesh.polygons) 
                objCount = context.scene.gridSizeX * context.scene.gridSizeY * context.scene.gridSizeZ 
                totalTris = objCount * triCount
                totalTrisFormated =  '{:,}'.format(totalTris)
                if (objCount > 8000) or (totalTris > 5000000) :
                    box.label(text="Warning! You try to create")
                    box.label(text=" %d objects with" % objCount)
                    box.label(text=" %s polygons." % totalTrisFormated)
                    box.label(text="This may freeze Blender.")
        if context.scene.rintersect: 
            objCount = context.scene.gridSizeX * context.scene.gridSizeY * context.scene.gridSizeZ if context.scene.dmode else context.scene.numOfObjects
            if objCount > 1000 and context.scene.coll_mode == 'AABB':
                    box.label(text="Warning! Finding collisions for")
                    box.label(text="%d objects can take a very" % objCount)
                    box.label(text="long time and may freeze Blender!")
                    box.label(text="Maximum recommend number for this mode: 1000.")

            if objCount > 4000 and context.scene.coll_mode == 'ORDI':
                    box.label(text="Warning! Finding collisions for")
                    box.label(text="%d objects can take a very" % objCount)
                    box.label(text="long time and may freeze Blender!")
                    box.label(text="Maximum recommend number for this mode: 4000.")

        """Clone on mesh, not in grid mode"""
        if not context.scene.dmode:
            split = box.split()
            col = split.column(align=True)     
            col.label(text="Target Mesh:")
            col.prop_search(context.scene, "targetObject", context.scene, "objects", text="")
            col = split.column(align=True)     
            col.label(text="Clone to")
            col.prop(context.scene, "target_mode")    
            if context.scene.targetObject != "":
                split = box.split()
                col = split.column() 
                col.prop(context.scene, "nangles")  
                col = split.column() 
                col.prop(context.scene, "fillMode")  
                if context.scene.target_mode == "POINTS":
                    col.prop(context.scene, "cyclic")  

        split = box.split()
        col = split.column()     
        col.prop(context.scene, "shapeK")
        col = split.column()
        col.prop(context.scene, "rintersect")
                
        if context.scene.rintersect: 
            col.prop(context.scene, "max_coll")
            split = box.split()
            col = split.column(align=True) 
            col.prop(context.scene, "coll_mode")  
            col.prop(context.scene, "coll_solve")
            if context.scene.coll_mode == "ORDI" or context.scene.coll_mode == "SIMP":
                col.prop(context.scene, "orgDist")
            else:
                col.prop(context.scene, "aabbSize")
                
        if context.object is not None:
            box.operator(ROA_Apply.bl_idname, text = "Apply").isRT = False 
            split = box.split()
            col = split.column()
            col.prop(context.scene, "animMode") 
 

def register():
    bpy.utils.register_class(ROA_Apply)
    bpy.utils.register_class(ROA_Reset)
    bpy.utils.register_class(ROA_Store)
    bpy.utils.register_class(ROA_Read)
    bpy.utils.register_class(ROA_Set)
    bpy.utils.register_class(CustomPanel)
    bpy.types.Scene.targetObject = bpy.props.StringProperty()
    bpy.types.Scene.objGroup = bpy.props.StringProperty()
    bpy.app.handlers.scene_update_post.append(scene_update)
    bpy.app.handlers.frame_change_pre.append(roa_anim_mode)
    
def unregister():
    bpy.utils.unregister_class(ROA_Apply)
    bpy.utils.unregister_class(ROA_Reset)
    bpy.utils.unregister_class(ROA_Store)
    bpy.utils.unregister_class(ROA_Set)
    bpy.utils.unregister_class(ROA_Read)
    bpy.utils.unregister_class(CustomPanel)
    del bpy.types.Scene.targetObject
    bpy.app.handlers.scene_update_post.remove(scene_update)
    bpy.app.handlers.frame_change_pre.remove(roa_anim_mode)

if __name__ == "__main__":
    register()



