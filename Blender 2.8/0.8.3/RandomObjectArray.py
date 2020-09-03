# -*- coding: utf-8 -*-
'''
    package: Random Object Array -- blender addon 
    --
    file: RandomObjectArray.py 
    --
    Copyright (C) <2018> -- Manuel Geissinger <manuel@artunchained.de> 
    --
    --
    This program is FREE SOFTWARE: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3 of the License.
    -
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    --
    --
    HISTORY:
    2019-06-15 Juno update for Blender 2.80 by Emanuel Rumpf (em-rumpf@gmx.de) 
    --
'''



bl_info = \
	{
		"name" : "RandomObjectArray",
		"author" : "Manuel Geissinger <manuel@artunchained.de>",
		"version" : (0, 8, 3),
		"blender": (2, 80, 0),
		"location" : "View 3D > Object > Random Object Array",
		"description" : "Script similar to the array modifier with random values",
		"warning" : "",
		"wiki_url" : "",
		"tracker_url" : "",
		"category" : "Object",
	}

import bpy
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import Operator, Panel, UIList
from bpy.app.handlers import persistent
import random
import time
import math
import mathutils
from mathutils import*


"""Debug"""
#import faulthandler
#faulthandler.enable()



def get_active_object():
	OBS = bpy.context.view_layer.objects
	return OBS.active 
	
def set_active_object(obj):
	OBS = bpy.context.view_layer.objects
	OBS.active = obj

def object_to_collection(obj):
	''' link object to active collection ''' 
	OBS = bpy.context.collection.objects
	if obj.name in OBS:
		pass
		# print('WARNING: RandomObjectArray addon: collection.objects.link() -- object is linked already ! ' )
	else:
		OBS.link( obj )
	#



class RandomObjectArraySettings(bpy.types.PropertyGroup):
	numOfObjects : IntProperty(name="Count", default=1, description="Number of Copies to create", min=0, max=10000)
	
	fixedPosX : FloatProperty(name="X", default=0, description="Static offset", step=1, precision=4)
	fixedPosY : FloatProperty(name="Y", default=0, description="Static offset", step=1, precision=4)
	fixedPosZ : FloatProperty(name="Z", default=0, description="Static offset", step=1, precision=4)
	
	randomPosX : FloatProperty(name="X", default=0, description="Random offset", step=1, precision=4)
	randomPosY : FloatProperty(name="Y", default=0, description="Random offset", step=1, precision=4)
	randomPosZ : FloatProperty(name="Z", default=0, description="Random offset", step=1, precision=4)
	
	fixedRotX : FloatProperty(name="X", default=0, description="Static rotation", min=-360, max=360, step=1, precision=4)
	fixedRotY : FloatProperty(name="Y", default=0, description="Static rotation", min=-360, max=360, step=1, precision=4)
	fixedRotZ : FloatProperty(name="Z", default=0, description="Static rotation", min=-360, max=360, step=1, precision=4)
	
	randRotX : FloatProperty(name="X", default=0, description="Random rotation", min=-360, max=360, step=1, precision=4)
	randRotY : FloatProperty(name="Y", default=0, description="Random rotation", min=-360, max=360, step=1, precision=4)
	randRotZ : FloatProperty(name="Z", default=0, description="Random rotation", min=-360, max=360, step=1, precision=4)
	
	minSclX : FloatProperty(name="X", default=1, description="Random scale minimum", step=1, precision=4)
	minSclY : FloatProperty(name="Y", default=1, description="Random scale minimum", step=1, precision=4)
	minSclZ : FloatProperty(name="Z", default=1, description="Random scale minimum", step=1, precision=4)
	
	maxSclX : FloatProperty(name="X", default=1, description="Random scale maximum", step=1, precision=4)
	maxSclY : FloatProperty(name="Y", default=1, description="Random scale maximum", step=1, precision=4)
	maxSclZ : FloatProperty(name="Z", default=1, description="Random scale maximum", step=1, precision=4)
	
	cangles : BoolProperty(name='Cumulate Rotation', description='Cumulate Rotation: Fixed rotation will cumulate for every new object', default=False)
	fangles : BoolProperty(name='Full Angles', description='Full Angles: If set, random or static rotation angle n° will be either 0° or n° but nothing in between', default=False)
	fanglesX : BoolProperty(name='X', description='Axis for full angle rotation', default=True)
	fanglesY : BoolProperty(name='Y', description='Axis for full angle rotation', default=True)
	fanglesZ : BoolProperty(name='Z', description='Axis for full angle rotation', default=True)
	
	coffset : BoolProperty(name='Cumulate Offset', description='Cumulate Offset: RFixed offset will cumulate for every new object', default=True)
	dmode : BoolProperty(name='Grid Mode', description='Spread objects on a 2D / 3D grid instead, random values will be added / substracted from the grid point coords', default=False)
	
	gridSizeX : IntProperty(name="X", description="Grid Size X Axis", default=1, min=1)
	gridSizeY : IntProperty(name="Y", description="Grid Size Y Axis", default=1, min=1)
	gridSizeZ : IntProperty(name="Z", description="Grid Size Z Axis", default=1, min=1)
	
	kshape : BoolProperty(name='Keep Shape', description='Keep Shape: If set, object will keep its realtive scale', default=True)
	  
	singObj : BoolProperty(name='Single Object', description='Joins created duplicates into one object. Be aware that execution may take a long time for a high number or high poly objects.', default=False)
	
	rPosRange : BoolProperty(name='Range +/-', description='If activated, random numbers will be calculated from -n to n instead of 0 to n ', default=True)
	 
	rRotRange : BoolProperty(name='Range +/-', description='If activated, random numbers will be calculated from -n to n instead of 0 to n ', default=True)
	
	nangles : BoolProperty(name='From normal', description='If activated rotation will be calculated from face normals, otherwise they will be global', default=True)
	  
	rintersect : BoolProperty(name='Avoid intersections', description='Collision detection that checks the array for intersecting objects', default=False)
	 
	coll_mode : EnumProperty(items = [('AABB', 'AABB', 'Axis aligned bounding box collision'), ('ORDI', 'Origin distance', 'Distance between origins in blender units'), ('SIMP', 'Simplified', 'Fastest yet slightly unprecise mode')  ], name = "Collision mode", default = 'AABB') 
	orgDist : FloatProperty(name="Distance", default=1, description="Detect objects within this radius", step=1, precision=4)
	
	coll_solve : EnumProperty(items = [('DELETE', 'Delete', 'Delete colliding objects'), ('MOVE', 'Move', 'Move colliding objects by the constant offset values again (may not solve intersections). Works best on 3-dimensional arrays'), ('SCALE', 'Scale', 'Scale colliding objects smaller to the minScale value (may not solve all intersections)'), ('SELECT', 'Select', 'Select all colliding objects for the user decide what to do')], name = "Solving method", default = 'DELETE') 
	max_coll : IntProperty(name="Max. collisions", description="Objects intersecting with at least this number of objects will be removed.", default=1, min=1, max=100)
	
	realtime : BoolProperty(name='Realtime', description='Show preview of the process in realtime', default=False)
	
	corners : BoolProperty(name='Corners', description='Add corners to the array', default=False)
	numOfCorners : IntProperty(name="Corner count", description="Number of corners", default=1, min=1, max=10)
	
	
	aabbSize : IntProperty(name="Bounding box size %", description="Increase or decrease the size of the axis aligned bounding box by a percentage", default=100, min=1, max=500)
	
	global_mode : EnumProperty(items = [('GLOBAL', 'Global', 'Offset and rotation are global. For target mesh use GLOBAL!'), ('LOCAL', 'Local', 'Offset and rotation are local. For target mesh use GLOBAL!') ], name = "Global / Local", default = 'LOCAL') 
	
	relOffset : BoolProperty(name='Relative offset', description='Offset will be relative, depending on the objects dimensions. If unchecked the offset will be absolute.', default=False)
	rel_axis : EnumProperty(items = [('X', 'X', 'Axis to use for relative offset and row offset (has to be the same axis for both)'), ('Y', 'Y', 'Axis to use for relative offset'), ('Z', 'Z', 'Axis to use for relative offset')  ], name = "", default = 'X') 
	fillMode : BoolProperty(name='Fill mode', description='Fills the mesh instead of choosing target faces randomly', default=True)
	
	
	kchildren : BoolProperty(name='Keep children', description='Keep the children parented to the orginal object. Otherwise they get deleted.', default=False)
	keepP : BoolProperty(name='From parent', description='Keep parent transformation', default=False)
	pickGrp : BoolProperty(name='Pick from Group', description='Pick objects from group randomly', default=False)
	gRate : BoolProperty(name='Use rate', description='Duplicate some objects of the group more than others', default=False)
	grpCount : IntProperty(name="Object rate", description="Make it that number of times more likely to duplicate this object than others.", default=0, min=0, max=100)
	
	copyType : EnumProperty(items = [('SINGLE', 'Single object', 'All copies are joined into one object.'), ('INST', 'Instances', 'Copies are created as instances, also known as linked duplicates.'), ('REAL', 'Real copies', 'Objects are created as real objects')], name = "", default = 'INST') 
	shapeKey : BoolProperty(name='Shape key', description='Changes the second shape key of the objec(s) randomly', default=False)
	
	useSeed : BoolProperty(name='Use random seed', description='Use fixed seed for random values to get a more reproducable result. Otherwise system time is used.', default=True)
	randSeed : IntProperty(name='Seed', description='Random seed value', default=1, min=1, max=1000)
	  
	animMode : BoolProperty(name='Anim mode', description='Apply full stack on frame change. Warning, use only for rendering and make sure your roa-object is selected!', default=False)
	shapeK : BoolProperty(name='Shape key', description='Randomizes the first shape key (not the base!) of each duplicate between 0 and 1. Only works with real copies right now.', default=False)
	applyK : BoolProperty(name='Apply Shape key', description='Applies the shape key (removes it) so objects can be joined later', default=False)
	
	cScale : BoolProperty(name='Cumulate scale', description='Fixed scale will cumulate for every new object', default=False)
	fScaleX : FloatProperty(name="X", default=1, description="Cumulate scale X", step=1, precision=4)
	fScaleY : FloatProperty(name="Y", default=1, description="Cumulate scale Y", step=1, precision=4)
	fScaleZ : FloatProperty(name="Z", default=1, description="Cumulate scale Z", step=1, precision=4)
	
	target_mode : EnumProperty(items = [('FACES', 'Faces', 'Clone to the faces of the target mesh'), ('POINTS', 'Points', 'Clone to the points of the target mesh')], name = "", default = 'FACES') 
	cyclic : BoolProperty(name='Cyclic', description='Target is a closed circle', default=False)
	
	invert_vertex_group_density : BoolProperty(name='invert density', description='invert vertex group density', default=False)
	invert_vertex_group_scale : BoolProperty(name='invert scale', description='invert vertex group scale', default=False)
	
	pobjects : BoolProperty(name='Parent objects', description='Parent duplicates to the original object', default=True)
	regenerate : BoolProperty(name='Regenerate objectes', description='Always regenerate objects', default=False)
	
	objList : StringProperty()
	maxCount : IntProperty(name="Max. count", default=200, description="Maximum number of copies to create in realtime", min=1, max=1000)
	
	autosave : BoolProperty(name='Autosave', description='All settings will be automatically saved to and loaded from ROA objects.', default=True)
	autoread : BoolProperty(name='Autoread', description='Trigger for autoreading only once at a time', default=True)
	autoLastActive : StringProperty()
	
	groupCountIndex : IntProperty(default=0)
	groupCountIndexLast : IntProperty(default=-1)
	groupActiveCount: IntProperty(min=0, default=1)
	groupNoRepeat : BoolProperty(name='Avoid repetition', description='If active ROA will try to avoid direct repetition of group objects, so \"Object A\" will never be next to \"Object A\".', default=False)
	
	rowoffset : BoolProperty(name='Row offset', description='Add another set of x/y/z parameters to offset every row', default=False)
	
	rowOffsetX : FloatProperty(name="X", default=0, description="Static offset", step=1, precision=4)
	rowOffsetY : FloatProperty(name="Y", default=0, description="Static offset", step=1, precision=4)
	rowOffsetZ : FloatProperty(name="Z", default=0, description="Static offset", step=1, precision=4)

	rowOffsetRX : FloatProperty(name="X", default=0, description="Static offset", step=1, precision=4)
	rowOffsetRY : FloatProperty(name="Y", default=0, description="Static offset", step=1, precision=4)
	rowOffsetRZ : FloatProperty(name="Z", default=0, description="Static offset", step=1, precision=4)
 
	stepRotation : BoolProperty(name='Step rotation', description='Add another set of min and max x/y/z angles and a step angle to make a repeating stepwise rotation', default=False)
	
	stepRotMinX : FloatProperty(name="X", default=0, description="Step Rotation minimum degrees X", step=1, precision=4)
	stepRotMinY : FloatProperty(name="Y", default=0, description="Step Rotation minimum degrees Y", step=1, precision=4)
	stepRotMinZ : FloatProperty(name="Z", default=0, description="Step Rotation minimum degrees Z", step=1, precision=4)
	
	stepRotMaxX : FloatProperty(name="X", default=0, description="Step Rotation maximum degrees X", step=1, precision=4)
	stepRotMaxY : FloatProperty(name="Y", default=0, description="Step Rotation maximum degrees Y", step=1, precision=4)
	stepRotMaxZ : FloatProperty(name="Z", default=0, description="Step Rotation maximum degrees Z", step=1, precision=4)

	stepRotStepX : FloatProperty(name="X", default=0, description="Step Rotation step degrees X", step=1, precision=4)
	stepRotStepY : FloatProperty(name="Y", default=0, description="Step Rotation step degrees Y", step=1, precision=4)
	stepRotStepZ : FloatProperty(name="Z", default=0, description="Step Rotation step degrees Z", step=1, precision=4)
	  
	mirror : BoolProperty(name='Mirror', description='Mirror objects randomly on one or more axis', default=False)
	mirrorX : BoolProperty(name='X', description='Axis for mirroring', default=True)
	mirrorY : BoolProperty(name='Y', description='Axis for mirroring', default=True)
	mirrorZ : BoolProperty(name='Z', description='Axis for mirroring', default=True)
	
	mirrorProbX : FloatProperty(name="X", default=0.1, description="X-axis mirroring. Probability of mirroring to occur. E.g. 0.25 equals 25%, 1 equals 100%.. Calculated seperately for each axis", step=1, precision=2, min=0, max=1)	
	mirrorProbY : FloatProperty(name="Y", default=0.1, description="Y-axis mirroring. Probability of mirroring to occur. E.g. 0.25 equals 25%, 1 equals 100%.. Calculated seperately for each axis", step=1, precision=2, min=0, max=1)	
	mirrorProbZ : FloatProperty(name="Z", default=0.1, description="Z-axis mirroring. Probability of mirroring to occur. E.g. 0.25 equals 25%, 1 equals 100%.. Calculated seperately for each axis", step=1, precision=2, min=0, max=1)	
	
class ROA_GroupCountData(bpy.types.PropertyGroup):
	name : bpy.props.StringProperty()
	count : bpy.props.IntProperty(default=1)
	#id : IntProperty()

def stateChange(propName, theProp): 
	if stateDict[propName] != theProp:
		stateDict[propName] = theProp
		return True
	return False

def checkAll():
	check = False
	
	"""Regenerate always on entering realtime"""
	check = stateChange("realtime", bpy.context.scene.roa_settings.realtime)
	if check:
		bpy.context.scene.roa_settings.regenerate = True
		
	check = check or stateChange("numOfObjects", bpy.context.scene.roa_settings.numOfObjects)
	check = check or stateChange("randomPosX", bpy.context.scene.roa_settings.randomPosX) or  stateChange("randomPosY", bpy.context.scene.roa_settings.randomPosY) or  stateChange("randomPosZ", bpy.context.scene.roa_settings.randomPosZ) 
	check = check or stateChange("gridSizeX", bpy.context.scene.roa_settings.gridSizeX) or stateChange("gridSizeY", bpy.context.scene.roa_settings.gridSizeY) or stateChange("gridSizeZ", bpy.context.scene.roa_settings.gridSizeZ)
	check = check or stateChange("fixedPosX", bpy.context.scene.roa_settings.fixedPosX) or stateChange("fixedPosY", bpy.context.scene.roa_settings.fixedPosY) or stateChange("fixedPosZ", bpy.context.scene.roa_settings.fixedPosZ)
	check = check or stateChange("fixedRotX", bpy.context.scene.roa_settings.fixedRotX) or stateChange("fixedRotY", bpy.context.scene.roa_settings.fixedRotY) or stateChange("fixedRotZ", bpy.context.scene.roa_settings.fixedRotZ)
	check = check or stateChange("randRotX", bpy.context.scene.roa_settings.randRotX) or  stateChange("randRotY", bpy.context.scene.roa_settings.randRotY) or  stateChange("randRotZ", bpy.context.scene.roa_settings.randRotZ) 
	check = check or stateChange("minSclX", bpy.context.scene.roa_settings.minSclX) or  stateChange("minSclY", bpy.context.scene.roa_settings.minSclY) or  stateChange("minSclZ", bpy.context.scene.roa_settings.minSclZ) 
	check = check or stateChange("maxSclX", bpy.context.scene.roa_settings.maxSclX) or  stateChange("maxSclY", bpy.context.scene.roa_settings.maxSclY) or  stateChange("maxSclZ", bpy.context.scene.roa_settings.maxSclZ) 
	check = check or stateChange("dmode", bpy.context.scene.roa_settings.dmode) or stateChange("coffset", bpy.context.scene.roa_settings.coffset) or stateChange("rPosRange", bpy.context.scene.roa_settings.rPosRange)
	check = check or stateChange("rRotRange", bpy.context.scene.roa_settings.rRotRange) or stateChange("cangles", bpy.context.scene.roa_settings.cangles) or stateChange("fangles", bpy.context.scene.roa_settings.fangles)
	check = check or stateChange("fanglesX", bpy.context.scene.roa_settings.fanglesX) or stateChange("fanglesY", bpy.context.scene.roa_settings.fanglesY) or stateChange("fanglesZ", bpy.context.scene.roa_settings.fanglesZ)
	check = check or stateChange("kshape", bpy.context.scene.roa_settings.kshape) or stateChange("nangles", bpy.context.scene.roa_settings.nangles)
	check = check or stateChange("targetObject", bpy.context.scene.targetObject) or stateChange("objGroup", bpy.context.scene.objGroup) or stateChange("pickGrp", bpy.context.scene.roa_settings.pickGrp)
	check = check or stateChange("relOffset", bpy.context.scene.roa_settings.relOffset) or stateChange("rel_axis", bpy.context.scene.roa_settings.rel_axis) or stateChange("fillMode", bpy.context.scene.roa_settings.fillMode)
	check = check or stateChange("useSeed", bpy.context.scene.roa_settings.useSeed) or stateChange("randSeed", bpy.context.scene.roa_settings.randSeed) or stateChange("shapeK", bpy.context.scene.roa_settings.shapeK)
	check = check or stateChange("cScale", bpy.context.scene.roa_settings.cScale) or stateChange("fScaleX", bpy.context.scene.roa_settings.fScaleX) or stateChange("fScaleY", bpy.context.scene.roa_settings.fScaleY) or stateChange("fScaleZ", bpy.context.scene.roa_settings.fScaleZ)
	check = check or stateChange("target_mode", bpy.context.scene.roa_settings.target_mode) or stateChange("cyclic", bpy.context.scene.roa_settings.cyclic) 
	check = check or stateChange("vertex_group_density", bpy.context.scene.vertex_group_density) or stateChange("invert_vertex_group_density", bpy.context.scene.roa_settings.invert_vertex_group_density) 
	check = check or stateChange("groupActiveCount", bpy.context.scene.roa_settings.groupActiveCount) or stateChange("groupNoRepeat", bpy.context.scene.roa_settings.groupNoRepeat)
	check = check or stateChange("rowoffset", bpy.context.scene.roa_settings.rowoffset)
	check = check or stateChange("rowOffsetX", bpy.context.scene.roa_settings.rowOffsetX) or stateChange("rowOffsetY", bpy.context.scene.roa_settings.rowOffsetY) or stateChange("rowOffsetZ", bpy.context.scene.roa_settings.rowOffsetZ)
	check = check or stateChange("rowOffsetRX", bpy.context.scene.roa_settings.rowOffsetRX) or stateChange("rowOffsetRY", bpy.context.scene.roa_settings.rowOffsetRY) or stateChange("rowOffsetRZ", bpy.context.scene.roa_settings.rowOffsetRZ)
	check = check or stateChange("stepRotation", bpy.context.scene.roa_settings.stepRotation) or stateChange("stepRotMinX", bpy.context.scene.roa_settings.stepRotMinX) or stateChange("stepRotMinY", bpy.context.scene.roa_settings.stepRotMinY) or stateChange("stepRotMinZ", bpy.context.scene.roa_settings.stepRotMinZ)  
	check = check or stateChange("stepRotMaxX", bpy.context.scene.roa_settings.stepRotMaxX) or stateChange("stepRotMaxY", bpy.context.scene.roa_settings.stepRotMaxY) or stateChange("stepRotMaxZ", bpy.context.scene.roa_settings.stepRotMaxZ)
	check = check or stateChange("stepRotStepX", bpy.context.scene.roa_settings.stepRotStepX) or stateChange("stepRotStepY", bpy.context.scene.roa_settings.stepRotStepY) or stateChange("stepRotStepZ", bpy.context.scene.roa_settings.stepRotStepZ)
	check = check or stateChange("mirror", bpy.context.scene.roa_settings.mirror) or stateChange("mirrorX", bpy.context.scene.roa_settings.mirrorX) or stateChange("mirrorY", bpy.context.scene.roa_settings.mirrorY) or stateChange("mirrorZ", bpy.context.scene.roa_settings.mirrorZ)
	check = check or stateChange("mirrorProbX", bpy.context.scene.roa_settings.mirrorProbX) or stateChange("mirrorProbY", bpy.context.scene.roa_settings.mirrorProbY) or stateChange("mirrorProbZ", bpy.context.scene.roa_settings.mirrorProbZ)
	return check

def prepareRT():
	OBS = bpy.context.view_layer.objects
	
	"""Exceptions for the new realtime mode (recycle)"""
	if bpy.context.scene.roa_settings.pickGrp or bpy.context.scene.roa_settings.relOffset or bpy.context.scene.roa_settings.kchildren:
		bpy.context.scene.roa_settings.regenerate = True
	
	if bpy.context.scene.roa_settings.regenerate:
		obj = get_active_object() 
		obj.select_set( True )
		bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
		if bpy.context.scene.roa_settings.kchildren:
			for ob in bpy.context.selected_objects:
				if not ".roaRt." in ob.name:
					if not "ROA_RT_BOX_TEMPORARY_OBJECT" in ob.name:
						ob.select_set( False )
		bpy.ops.object.delete()  
		set_active_object( obj )
		obj.select_set( True )
		bpy.context.scene.roa_settings.regenerate = False

		return obj
	else:
		obj = get_active_object() 
		return obj

def cleanupRT(obj):	
	set_active_object( obj )
	obj.select_set( True )
	
def isROA():
	try:
		if get_active_object() is not None:
			originalObject = get_active_object()
			is_set = originalObject["isROA"]
			return is_set
		#
		return False
		#
	except:
		return False
	#

stateDict = {"realtime": False,
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
			 "fanglesX": False,
			 "fanglesY": False,
			 "fanglesZ": False,
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
			 "cyclic": False,
			 "vertex_group_density": "",
			 "invert_vertex_group_density": False,
			 "autosave": True,
			 "groupActiveCount": -1,
			 "groupNoRepeat": False,
			 "rowoffset": False,
			 "rowOffsetX": 0,
			 "rowOffsetY": 0,
			 "rowOffsetZ": 0,
			 "rowOffsetRX": 0,
			 "rowOffsetRY": 0,
			 "rowOffsetRZ": 0,
			 "stepRotation": False,
			 "stepRotMinX": 0,
			 "stepRotMinY": 0,
			 "stepRotMinZ": 0,
			 "stepRotMaxX": 0,
			 "stepRotMaxY": 0,
			 "stepRotMaxZ": 0,
			 "stepRotStepX": 0,
			 "stepRotStepY": 0,
			 "stepRotStepZ": 0, 
			 "mirror": False,
			 "mirrorX": True,
			 "mirrorY": True,
			 "mirrorZ": True,
			 "mirrorProbX": 0.1,
			 "mirrorProbY": 0.1,
			 "mirrorProbZ": 0.1}
			 
stateDefault = stateDict.copy()

def active_obj_changed():
	#if hasattr(bpy.context, "active_object"):
	try:
		if get_active_object() is not None:
			ob = get_active_object()
			if bpy.context.scene.roa_settings.autoLastActive != ob.name:
				bpy.context.scene.roa_settings.autoLastActive = ob.name
				return True
			else:
				return False
	except:
		pass		
	return False
	



def _update_grouplist_():
	if len(bpy.context.scene.groupCountData) > 0:
		#clear list
		bpy.context.scene.groupCountData.clear()
		#also clear index
		bpy.context.scene.roa_settings.groupCountIndex = 0
		bpy.context.scene.roa_settings.groupCountIndexLast = -1
	#
		
	#if (isROA() or self.buttonPress) and bpy.data.groups: # FIXME: buttonPress removed
	if isROA() and bpy.data.collections:
		#
		if bpy.context.scene.objGroup != "":
			"""Add the master object first"""
			item = bpy.context.scene.groupCountData.add()
			item.name = get_active_object().name+" (Master)" 
			for ob in bpy.data.collections[bpy.context.scene.objGroup].objects:
				item = bpy.context.scene.groupCountData.add()
				item.name = ob.name
			#for
		#if objGroup
	#if isROA

	
class OT_ROA_update_grouplist(bpy.types.Operator):
	bl_idname = "object.roa_updategrouplist"
	bl_label = "Update"
	#bl_options = {'UNDO'}
	
	buttonPress : bpy.props.BoolProperty(default=False)
	
	def execute(self, context):
		_update_grouplist_()
		return {'FINISHED'}			 


@persistent
def handler_depsgraph_update_pre(paramx):  # note: was scene_update() in blender 2.79
	scn = bpy.context.scene 
	#
	if active_obj_changed():
		"""Workaround - Grouplist gets filled here as it can't be done while drawing"""
		#
		# disabled: infinite recursion -- FIXME ? 
		#bpy.ops.object.roa_updategrouplist()
		_update_grouplist_()
		
		if scn.roa_settings.autosave and isROA():
			bpy.ops.object.roa_read()
			
	if scn.roa_settings.realtime:
		#
		
		#if scn.is_updated: # FIXME: scene.is_updated() does not exist 
		if True:
			#
			if isROA(): 
				if checkAll():					
					"""Update the group list count"""
					if len(scn.groupCountData) > 0 and scn.objGroup != "":
						scn.groupCountData[ scn.roa_settings.groupCountIndex ].count = scn.roa_settings.groupActiveCount

					rtOb = prepareRT()
					if rtOb is not None and rtOb.select_get() == True:
						bpy.ops.object.roa_apply(isRT=True)
						cleanupRT(rtOb)
					#
					
				#end checkAll
			#end isROA
			
			
			#else:
			#	scn.roa_settings.realtime = False 
			#	stateChange("realtime", scn.roa_settings.realtime)
				
@persistent
def roa_anim_mode(scene):
	if bpy.context.scene.roa_settings.animMode:
		bpy.context.scene.roa_settings.realtime = False 
		stateChange("realtime", bpy.context.scene.roa_settings.realtime)
		rtOb = prepareRT()
		if rtOb is not None and rtOb.select_get() == True:
			bpy.ops.object.roa_apply(isRT=False)
			cleanupRT(rtOb)	
	 
class OT_ROA_Update(bpy.types.Operator):
	"""Update the realtime preview"""
	bl_idname = "object.roa_update"
	bl_label = "Reset"
		
	def execute(self, context):  
		bpy.context.scene.roa_settings.regenerate = True 
		rtOb = prepareRT()
		if rtOb is not None and rtOb.select_get() == True:
			bpy.ops.object.roa_apply(isRT=True)
			cleanupRT(rtOb)
		return {'FINISHED'}

# User Request
class OT_ROA_Reset(bpy.types.Operator):
	"""Reset all values. This won't delete any objects or update realtime preview, also saved values aren't overwritten, except when using autosave"""
	bl_idname = "object.roa_reset"
	bl_label = "Reset"
	#bl_options = {'UNDO'}

	def execute(self, context):
		context.scene.roa_settings.numOfObjects = stateDefault["numOfObjects"]
		context.scene.roa_settings.fixedPosX = stateDefault["fixedPosX"]
		context.scene.roa_settings.fixedPosY = stateDefault["fixedPosY"]
		context.scene.roa_settings.fixedPosZ = stateDefault["fixedPosZ"]
		context.scene.roa_settings.randomPosX = stateDefault["randomPosX"]
		context.scene.roa_settings.randomPosY = stateDefault["randomPosY"]
		context.scene.roa_settings.randomPosZ = stateDefault["randomPosZ"]
		context.scene.roa_settings.fixedRotX = stateDefault["fixedRotX"]
		context.scene.roa_settings.fixedRotY = stateDefault["fixedRotY"]
		context.scene.roa_settings.fixedRotZ = stateDefault["fixedRotZ"]
		context.scene.roa_settings.randRotX = stateDefault["randRotX"]
		context.scene.roa_settings.randRotY = stateDefault["randRotY"]
		context.scene.roa_settings.randRotZ = stateDefault["randRotZ"]
		context.scene.roa_settings.minSclX = stateDefault["minSclX"]
		context.scene.roa_settings.minSclY = stateDefault["minSclY"]
		context.scene.roa_settings.minSclZ = stateDefault["minSclZ"]
		context.scene.roa_settings.maxSclX = stateDefault["maxSclX"]
		context.scene.roa_settings.maxSclY = stateDefault["maxSclY"]
		context.scene.roa_settings.maxSclZ = stateDefault["maxSclZ"]
		context.scene.roa_settings.cangles = stateDefault["cangles"]
		context.scene.roa_settings.fangles = stateDefault["fangles"]
		context.scene.roa_settings.fanglesX = stateDefault["fanglesX"]		
		context.scene.roa_settings.fanglesY = stateDefault["fanglesY"]
		context.scene.roa_settings.fanglesZ = stateDefault["fanglesZ"]
		context.scene.roa_settings.coffset = stateDefault["coffset"]
		context.scene.roa_settings.dmode = stateDefault["dmode"]
		context.scene.roa_settings.gridSizeX = stateDefault["gridSizeX"]
		context.scene.roa_settings.gridSizeY = stateDefault["gridSizeY"]
		context.scene.roa_settings.gridSizeZ = stateDefault["gridSizeZ"]
		context.scene.roa_settings.kshape = stateDefault["kshape"]
		context.scene.roa_settings.singObj = stateDefault["singObj"]
		context.scene.roa_settings.rPosRange = stateDefault["rPosRange"]
		context.scene.roa_settings.rRotRange = stateDefault["rRotRange"]
		context.scene.roa_settings.nangles = stateDefault["nangles"]
		context.scene.roa_settings.pobjects = stateDefault["pobjects"]
		context.scene.targetObject = stateDefault["targetObject"]
		context.scene.objGroup = stateDefault["objGroup"] 
		context.scene.roa_settings.pickGrp = stateDefault["pickGrp"]	
		context.scene.roa_settings.kchildren = stateDefault["kchildren"]
		context.scene.roa_settings.relOffset = stateDefault["relOffset"]
		context.scene.roa_settings.rintersect = stateDefault["rintersect"]
		context.scene.roa_settings.max_coll = stateDefault["max_coll"] 
		context.scene.roa_settings.coll_mode = stateDefault["coll_mode"]
		context.scene.roa_settings.coll_solve = stateDefault["coll_solve"]
		context.scene.roa_settings.rel_axis = stateDefault["rel_axis"]
		context.scene.roa_settings.fillMode = stateDefault["fillMode"]
		context.scene.roa_settings.copyType = stateDefault["copyType"]
		context.scene.roa_settings.useSeed = stateDefault["useSeed"]
		context.scene.roa_settings.randSeed = stateDefault["randSeed"]
		context.scene.roa_settings.shapeK = stateDefault["shapeK"]
		context.scene.roa_settings.cScale = stateDefault["cScale"]
		context.scene.roa_settings.fScaleX = stateDefault["fScaleX"]
		context.scene.roa_settings.fScaleY = stateDefault["fScaleY"]
		context.scene.roa_settings.fScaleZ = stateDefault["fScaleZ"]  
		context.scene.roa_settings.target_mode = stateDefault["target_mode"]	  
		context.scene.roa_settings.cyclic = stateDefault["cyclic"]	
		context.scene.vertex_group_density = stateDefault["vertex_group_density"]	
		context.scene.roa_settings.invert_vertex_group_density = stateDefault["invert_vertex_group_density"]	
		context.scene.roa_settings.autosave = stateDefault["autosave"]	
		context.scene.roa_settings.groupNoRepeat = stateDefault["groupNoRepeat"]  
		context.scene.roa_settings.rowoffset = stateDefault["rowoffset"]  
		context.scene.roa_settings.rowOffsetX = stateDefault["rowOffsetX"]
		context.scene.roa_settings.rowOffsetY = stateDefault["rowOffsetY"]
		context.scene.roa_settings.rowOffsetZ = stateDefault["rowOffsetZ"]	 
		context.scene.roa_settings.rowOffsetRX = stateDefault["rowOffsetRX"]
		context.scene.roa_settings.rowOffsetRY = stateDefault["rowOffsetRY"]
		context.scene.roa_settings.rowOffsetRZ = stateDefault["rowOffsetRZ"]
		context.scene.roa_settings.stepRotation = stateDefault["stepRotation"]
		context.scene.roa_settings.stepRotMinX = stateDefault["stepRotMinX"]
		context.scene.roa_settings.stepRotMinY = stateDefault["stepRotMinY"]
		context.scene.roa_settings.stepRotMinZ = stateDefault["stepRotMinZ"]	
		context.scene.roa_settings.stepRotMaxX = stateDefault["stepRotMaxX"]
		context.scene.roa_settings.stepRotMaxY = stateDefault["stepRotMaxY"]
		context.scene.roa_settings.stepRotMaxZ = stateDefault["stepRotMaxZ"]				  
		context.scene.roa_settings.stepRotStepX = stateDefault["stepRotStepX"]
		context.scene.roa_settings.stepRotStepY = stateDefault["stepRotStepY"]
		context.scene.roa_settings.stepRotStepZ = stateDefault["stepRotStepZ"]
		context.scene.roa_settings.mirror = stateDefault["mirror"]  
		context.scene.roa_settings.mirrorX = stateDefault["mirrorX"]
		context.scene.roa_settings.mirrorY = stateDefault["mirrorY"]
		context.scene.roa_settings.mirrorZ = stateDefault["mirrorZ"]  
		context.scene.roa_settings.mirrorProbX = stateDefault["mirrorProbX"]
		context.scene.roa_settings.mirrorProbY = stateDefault["mirrorProbY"]
		context.scene.roa_settings.mirrorProbZ = stateDefault["mirrorProbZ"] 
		return {'FINISHED'}

#Store all values in the original object for interactivity	
class OT_ROA_Set(bpy.types.Operator):
	"""Assign ROA to the object to enable realtime, loading / saving and more"""
	bl_idname = "object.roa_set"
	bl_label = "Make ROA"
	#bl_options = {'UNDO'}
	
	def execute(self, context): 
		if get_active_object() is None:
			self.report({'ERROR'}, "ROA needs an active object to work on. (right click it again maybe) ")
			return {'FINISHED'}
		originalObject = get_active_object()
		originalObject["isROA"] = True
		return {'FINISHED'}
	
class OT_ROA_Store(bpy.types.Operator):
	"""Save all values to the object"""
	bl_idname = "object.roa_store"
	bl_label = "Save"
	#bl_options = {'UNDO'}
	def execute(self, context): 
		if get_active_object() is None:
			self.report({'ERROR'}, "ROA needs an active object to work on. (right click it again maybe) ")
			return {'FINISHED'}
		originalObject = get_active_object()
		#for backwards compatibility
		originalObject["ROAversion"] = '85'
		
		originalObject["numOfObjects"] = context.scene.roa_settings.numOfObjects
		originalObject["fixedPosX"] = context.scene.roa_settings.fixedPosX
		originalObject["fixedPosY"] = context.scene.roa_settings.fixedPosY
		originalObject["fixedPosZ"] = context.scene.roa_settings.fixedPosZ
		originalObject["randomPosX"] = context.scene.roa_settings.randomPosX
		originalObject["randomPosY"] = context.scene.roa_settings.randomPosY
		originalObject["randomPosZ"] = context.scene.roa_settings.randomPosZ		
		originalObject["fixedRotX"] = context.scene.roa_settings.fixedRotX
		originalObject["fixedRotY"] = context.scene.roa_settings.fixedRotY
		originalObject["fixedRotZ"] = context.scene.roa_settings.fixedRotZ					 
		originalObject["randRotX"] = context.scene.roa_settings.randRotX
		originalObject["randRotY"] = context.scene.roa_settings.randRotY
		originalObject["randRotZ"] = context.scene.roa_settings.randRotZ 
		originalObject["minSclX"] = context.scene.roa_settings.minSclX
		originalObject["minSclY"] = context.scene.roa_settings.minSclY
		originalObject["minSclZ"] = context.scene.roa_settings.minSclZ
		originalObject["maxSclX"] = context.scene.roa_settings.maxSclX
		originalObject["maxSclY"] = context.scene.roa_settings.maxSclY
		originalObject["maxSclZ"] = context.scene.roa_settings.maxSclZ
		originalObject["cangles"] = context.scene.roa_settings.cangles
		originalObject["fangles"] = context.scene.roa_settings.fangles
		originalObject["coffset"] = context.scene.roa_settings.coffset
		originalObject["dmode"] = context.scene.roa_settings.dmode
		originalObject["gridSizeX"] = context.scene.roa_settings.gridSizeX
		originalObject["gridSizeY"] = context.scene.roa_settings.gridSizeY
		originalObject["gridSizeZ"] = context.scene.roa_settings.gridSizeZ
		originalObject["kshape"] = context.scene.roa_settings.kshape
		originalObject["singObj"] =  context.scene.roa_settings.singObj  
		originalObject["rPosRange"] = context.scene.roa_settings.rPosRange
		originalObject["rRotRange"] = context.scene.roa_settings.rRotRange
		originalObject["nangles"] = context.scene.roa_settings.nangles
		originalObject["pobjects"] = context.scene.roa_settings.pobjects
		originalObject["targetObject"] = context.scene.targetObject	  
		#72
		originalObject["objGroup"] = context.scene.objGroup
		originalObject["pickGrp"] = context.scene.roa_settings.pickGrp	
		originalObject["kchildren"] = context.scene.roa_settings.kchildren
		originalObject["relOffset"] = context.scene.roa_settings.relOffset
		originalObject["rintersect"] = context.scene.roa_settings.rintersect
		originalObject["max_coll"] = context.scene.roa_settings.max_coll
		originalObject["coll_mode"] = context.scene.roa_settings.coll_mode
		originalObject["coll_solve"] = context.scene.roa_settings.coll_solve
		originalObject["rel_axis"] = context.scene.roa_settings.rel_axis
		#73
		originalObject["fillMode"] = context.scene.roa_settings.fillMode
		#74
		originalObject["copyType"] = context.scene.roa_settings.copyType
		#75
		originalObject["useSeed"] = context.scene.roa_settings.useSeed
		originalObject["randSeed"] = context.scene.roa_settings.randSeed
		#76
		originalObject["shapeK"] = context.scene.roa_settings.shapeK
		#77
		originalObject["cScale"] = context.scene.roa_settings.cScale
		originalObject["fScaleX"] = context.scene.roa_settings.fScaleX
		originalObject["fScaleY"] = context.scene.roa_settings.fScaleY
		originalObject["fScaleZ"] = context.scene.roa_settings.fScaleZ
		#78			 
		originalObject["target_mode"] = context.scene.roa_settings.target_mode
		originalObject["cyclic"] = context.scene.roa_settings.cyclic
		#79
		originalObject["vertex_group_density"] = context.scene.vertex_group_density
		originalObject["invert_vertex_group_density"] = context.scene.roa_settings.invert_vertex_group_density
		#80
		originalObject["autosave"] = context.scene.roa_settings.autosave
		#81
		"""Compile group counts into one string"""
		counts = ""
		if len(bpy.context.scene.groupCountData) > 0:
			for item in bpy.context.scene.groupCountData:
				counts += item.name + ",,," + str(item.count) + ",,,"
		originalObject["groupCounts"] = counts
		#82
		originalObject["groupNoRepeat"] = context.scene.roa_settings.groupNoRepeat
		#83
		originalObject["rowoffset"] = context.scene.roa_settings.rowoffset
		originalObject["rowOffsetX"] = context.scene.roa_settings.rowOffsetX
		originalObject["rowOffsetY"] = context.scene.roa_settings.rowOffsetY
		originalObject["rowOffsetZ"] = context.scene.roa_settings.rowOffsetZ		
		originalObject["rowOffsetRX"] = context.scene.roa_settings.rowOffsetRX
		originalObject["rowOffsetRY"] = context.scene.roa_settings.rowOffsetRY
		originalObject["rowOffsetRZ"] = context.scene.roa_settings.rowOffsetRZ
		#84
		originalObject["fanglesX"] = context.scene.roa_settings.fanglesX
		originalObject["fanglesY"] = context.scene.roa_settings.fanglesY
		originalObject["fanglesZ"] = context.scene.roa_settings.fanglesZ		
		originalObject["stepRotation"] = context.scene.roa_settings.stepRotation
		originalObject["stepRotMinX"] = context.scene.roa_settings.stepRotMinX
		originalObject["stepRotMinY"] = context.scene.roa_settings.stepRotMinY
		originalObject["stepRotMinZ"] = context.scene.roa_settings.stepRotMinZ		
		originalObject["stepRotMaxX"] = context.scene.roa_settings.stepRotMaxX
		originalObject["stepRotMaxY"] = context.scene.roa_settings.stepRotMaxY
		originalObject["stepRotMaxZ"] = context.scene.roa_settings.stepRotMaxZ  
		originalObject["stepRotStepX"] = context.scene.roa_settings.stepRotStepX
		originalObject["stepRotStepY"] = context.scene.roa_settings.stepRotStepY
		originalObject["stepRotStepZ"] = context.scene.roa_settings.stepRotStepZ  
		#85
		originalObject["mirror"] = context.scene.roa_settings.mirror
		originalObject["mirrorX"] = context.scene.roa_settings.mirrorX
		originalObject["mirrorY"] = context.scene.roa_settings.mirrorY
		originalObject["mirrorZ"] = context.scene.roa_settings.mirrorZ
		originalObject["mirrorProbX"] = context.scene.roa_settings.mirrorProbX
		originalObject["mirrorProbY"] = context.scene.roa_settings.mirrorProbY
		originalObject["mirrorProbZ"] = context.scene.roa_settings.mirrorProbZ		 
		return {'FINISHED'}

class OT_ROA_Read(bpy.types.Operator):
	"""Load all values from the object"""
	bl_idname = "object.roa_read"
	bl_label = "Load"
	#bl_options = {'UNDO'}
	
	def execute(self, context): 
		if get_active_object() is None:
			self.report({'ERROR'}, "ROA needs an active object to work on. (right click it again maybe) ")
			return {'FINISHED'}
		dataList = {}
		originalObject = get_active_object()
		ver = 0
		
		try:
			ver = int(originalObject["ROAversion"])
		except:
			self.report({'ERROR'}, "Sorry, object doesn't seem to have ROA data")
			return {'FINISHED'}
		
		#for backwards compatibility
		if ver > 70:
			try:
				context.scene.roa_settings.numOfObjects = originalObject["numOfObjects"]
				context.scene.roa_settings.fixedPosX = originalObject["fixedPosX"]
				context.scene.roa_settings.fixedPosY = originalObject["fixedPosY"]
				context.scene.roa_settings.fixedPosZ = originalObject["fixedPosZ"]
				context.scene.roa_settings.randomPosX = originalObject["randomPosX"]
				context.scene.roa_settings.randomPosY = originalObject["randomPosY"]
				context.scene.roa_settings.randomPosZ = originalObject["randomPosZ"]
				context.scene.roa_settings.fixedRotX = originalObject["fixedRotX"]
				context.scene.roa_settings.fixedRotY = originalObject["fixedRotY"]
				context.scene.roa_settings.fixedRotZ = originalObject["fixedRotZ"]
				context.scene.roa_settings.randRotX = originalObject["randRotX"]
				context.scene.roa_settings.randRotY = originalObject["randRotY"]
				context.scene.roa_settings.randRotZ = originalObject["randRotZ"]
				context.scene.roa_settings.minSclX = originalObject["minSclX"]
				context.scene.roa_settings.minSclY = originalObject["minSclY"]
				context.scene.roa_settings.minSclZ = originalObject["minSclZ"]
				context.scene.roa_settings.maxSclX = originalObject["maxSclX"]
				context.scene.roa_settings.maxSclY = originalObject["maxSclY"]
				context.scene.roa_settings.maxSclZ = originalObject["maxSclZ"]
				context.scene.roa_settings.cangles = originalObject["cangles"]
				context.scene.roa_settings.fangles = originalObject["fangles"]
				context.scene.roa_settings.coffset = originalObject["coffset"]
				context.scene.roa_settings.dmode = originalObject["dmode"]
				context.scene.roa_settings.gridSizeX = originalObject["gridSizeX"]
				context.scene.roa_settings.gridSizeY = originalObject["gridSizeY"]
				context.scene.roa_settings.gridSizeZ = originalObject["gridSizeZ"]
				context.scene.roa_settings.kshape = originalObject["kshape"]
				context.scene.roa_settings.singObj = originalObject["singObj"]
				context.scene.roa_settings.rPosRange = originalObject["rPosRange"]
				context.scene.roa_settings.rRotRange = originalObject["rRotRange"]
				context.scene.roa_settings.nangles = originalObject["nangles"]
				context.scene.roa_settings.pobjects = originalObject["pobjects"]
				context.scene.targetObject = originalObject["targetObject"]

			except:
				self.report({'ERROR'}, "Sorry, object doesn't seem to have ROA data")

		if ver > 71:  
			try:
				context.scene.objGroup = originalObject["objGroup"] 
				context.scene.roa_settings.pickGrp = originalObject["pickGrp"]	
				context.scene.roa_settings.kchildren = originalObject["kchildren"]
				context.scene.roa_settings.relOffset = originalObject["relOffset"]
				context.scene.roa_settings.rintersect = originalObject["rintersect"]
				context.scene.roa_settings.max_coll = originalObject["max_coll"] 
				context.scene.roa_settings.coll_mode = originalObject["coll_mode"]
				context.scene.roa_settings.coll_solve = originalObject["coll_solve"]
				context.scene.roa_settings.rel_axis = originalObject["rel_axis"]
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")
		if ver > 72:  
			try:
				context.scene.roa_settings.fillMode = originalObject["fillMode"] 
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")
				
		if ver > 73:  
			try:
				context.scene.roa_settings.copyType = originalObject["copyType"] 
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")

		if ver > 74:  
			try:
				context.scene.roa_settings.useSeed = originalObject["useSeed"] 
				context.scene.roa_settings.randSeed = originalObject["randSeed"] 
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")	
		if ver > 75:  
			try:
				context.scene.roa_settings.shapeK = originalObject["shapeK"] 
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")	
		if ver > 76:  
			try:
				context.scene.roa_settings.cScale = originalObject["cScale"] 
				context.scene.roa_settings.fScaleX = originalObject["fScaleX"]
				context.scene.roa_settings.fScaleY = originalObject["fScaleY"]
				context.scene.roa_settings.fScaleZ = originalObject["fScaleZ"]
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")
		if ver > 77:  
			try:
				context.scene.roa_settings.target_mode = originalObject["target_mode"] 
				context.scene.roa_settings.cyclic = originalObject["cyclic"] 
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")	 
		if ver > 78:  
			try:
				context.scene.vertex_group_density = originalObject["vertex_group_density"] 
				context.scene.roa_settings.invert_vertex_group_density = originalObject["invert_vertex_group_density"] 
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")			 
		if ver > 79:  
			try:
				context.scene.roa_settings.autosave = originalObject["autosave"] 
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")
				
		if ver > 80:  
			
			try:
				counts = originalObject["groupCounts"] 
				if counts != "":
					countList = counts.split(",,,")
							
					if len(bpy.context.scene.groupCountData) > 0 and len(countList) > 0:
						for item in bpy.context.scene.groupCountData:
							for count in countList:
								if count == item.name:
									index = countList.index(count)
									item.count = int(countList[index+1])
							
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug."+str(ver))
				
		if ver > 81:  
			try:
				context.scene.roa_settings.groupNoRepeat = originalObject["groupNoRepeat"] 
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")	
				
		if ver > 82:  
			try:
				context.scene.roa_settings.rowoffset = originalObject["rowoffset"] 
				context.scene.roa_settings.rowOffsetX = originalObject["rowOffsetX"]
				context.scene.roa_settings.rowOffsetY = originalObject["rowOffsetY"]
				context.scene.roa_settings.rowOffsetZ = originalObject["rowOffsetZ"]			
				context.scene.roa_settings.rowOffsetRX = originalObject["rowOffsetRX"]
				context.scene.roa_settings.rowOffsetRY = originalObject["rowOffsetRY"]
				context.scene.roa_settings.rowOffsetRZ = originalObject["rowOffsetRZ"]
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")	
				 
		if ver > 83:  
			try:
				context.scene.roa_settings.fanglesX = originalObject["fanglesX"]  
				context.scene.roa_settings.fanglesY = originalObject["fanglesY"]
				context.scene.roa_settings.fanglesZ = originalObject["fanglesZ"]								
				
				context.scene.roa_settings.stepRotation = originalObject["stepRotation"] 
				context.scene.roa_settings.stepRotMinX = originalObject["stepRotMinX"]
				context.scene.roa_settings.stepRotMinY = originalObject["stepRotMinY"]
				context.scene.roa_settings.stepRotMinZ = originalObject["stepRotMinZ"]
				
				context.scene.roa_settings.stepRotMaxX = originalObject["stepRotMaxX"]
				context.scene.roa_settings.stepRotMaxY = originalObject["stepRotMaxY"]
				context.scene.roa_settings.stepRotMaxZ = originalObject["stepRotMaxZ"]
				
				context.scene.roa_settings.stepRotStepX = originalObject["stepRotStepX"]
				context.scene.roa_settings.stepRotStepY = originalObject["stepRotStepY"]
				context.scene.roa_settings.stepRotStepZ = originalObject["stepRotStepZ"]
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")	 
				
		if ver > 84:  
			try:
				context.scene.roa_settings.mirror = originalObject["mirror"] 
				context.scene.roa_settings.mirrorX = originalObject["mirrorX"]
				context.scene.roa_settings.mirrorY = originalObject["mirrorY"]
				context.scene.roa_settings.mirrorZ = originalObject["mirrorZ"]			
				context.scene.roa_settings.mirrorProbX = originalObject["mirrorProbX"]
				context.scene.roa_settings.mirrorProbY = originalObject["mirrorProbY"]
				context.scene.roa_settings.mirrorProbZ = originalObject["mirrorProbZ"]
			except:
				self.report({'ERROR'}, "Sorry, something went wrong. Please report this bug.")						
		return {'FINISHED'}

#Simple collision detection
def simpleCollision(object1, object2, method):
	if method == 'SIMP':
		#Simplified distance mode
		if abs(object1.location[0]-object2.location[0]) <= bpy.context.scene.roa_settings.orgDist and abs(object1.location[1]-object2.location[1]) <= bpy.context.scene.roa_settings.orgDist and abs(object1.location[2]-object2.location[2]) <= bpy.context.scene.roa_settings.orgDist:
			return 1
		return 0
	
	if method == 'ORDI':
		#Origin distance mode
		if math.sqrt((object1.location[0]-object2.location[0])**2 + (object1.location[1]-object2.location[1])**2 + (object1.location[2]-object2.location[2])**2) <= bpy.context.scene.roa_settings.orgDist:
			return 1
		return 0

	if method == 'AABB':
		#Get Bounding Box vectors
		box1 = [object1.matrix_world @ Vector(c) for c in object1.bound_box]
		box2 = [object2.matrix_world @ Vector(c) for c in object2.bound_box]
	
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

		if bpy.context.scene.roa_settings.aabbSize != 100:
			scaleFac = 1 - (bpy.context.scene.roa_settings.aabbSize / 100)
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
	activeObj = get_active_object()
	
	bpy.ops.mesh.primitive_cube_add() 
	bound_box = get_active_object() 
	bound_box.name = "ROA_RT_BOX_TEMPORARY_OBJECT"
	bound_box.draw_type = 'BOUNDS'

	if bpy.context.scene.roa_settings.dmode:
		dimX = activeObj.dimensions[0] * bpy.context.scene.roa_settings.gridSizeX * (bpy.context.scene.roa_settings.fixedPosX) / 2
		dimY = activeObj.dimensions[1] * bpy.context.scene.roa_settings.gridSizeY * (bpy.context.scene.roa_settings.fixedPosY) / 2
		dimZ = activeObj.dimensions[2] * bpy.context.scene.roa_settings.gridSizeZ * (bpy.context.scene.roa_settings.fixedPosZ) / 2
	else:
		dimX = activeObj.dimensions[0] + activeObj.dimensions[0] * bpy.context.scene.roa_settings.numOfObjects * (bpy.context.scene.roa_settings.fixedPosX) / 2
		dimY = activeObj.dimensions[1] + activeObj.dimensions[1] * bpy.context.scene.roa_settings.numOfObjects * (bpy.context.scene.roa_settings.fixedPosY) / 2
		dimZ = activeObj.dimensions[2] + activeObj.dimensions[2] * bpy.context.scene.roa_settings.numOfObjects * (bpy.context.scene.roa_settings.fixedPosZ) / 2

	bound_box.parent = activeObj
	bound_box.dimensions = (dimX, dimY, dimZ)	 
	bound_box.location = Vector((dimX / 2, dimY / 2, dimZ / 2)) - Vector((activeObj.dimensions[0] / 2, activeObj.dimensions[1] / 2,activeObj.dimensions[2] / 2)) 
	bound_box.select_set( False )
	
	set_active_object( activeObj )
	
def removeRTBox():
	if bpy.data.objects.get("ROA_RT_BOX_TEMPORARY_OBJECT") is not None:
		activeObj = get_active_object()
		try:
			bpy.context.scene.objects.unlink(bpy.data.objects["ROA_RT_BOX_TEMPORARY_OBJECT"])
		
		except:
			pass
		set_active_object( activeObj )
		
class OT_ROA_SelectParent(bpy.types.Operator):
	"""Select the parent object of the currently selected object, to be able to edit the array."""
	bl_idname = "object.roa_selectparent"
	bl_label = "Select Parent"
	
	def execute(self, context): 
		if get_active_object() is not None and len(bpy.context.selected_objects) > 0:
			isROA = False
			try:
				isROA = get_active_object().parent["isROA"]
			except:
				pass
		
			if isROA and get_active_object().parent is not None:
				current = get_active_object()
				set_active_object( current.parent )
				current.parent.select_set( True )				
				current.select_set( False )
				
		return {'FINISHED'}  
		
class OT_ROA_EDIT(bpy.types.Operator):
	"""Switch Realtime Edit Mode on and off. Only works if ROA is assigned to an object"""
	bl_idname = "object.roa_edit"
	bl_label = "EDIT in Realtime"
	
	def execute(self, context): 
		if get_active_object() is not None and len(bpy.context.selected_objects) > 0:
			isROA = False
			try:
				isROA = get_active_object()["isROA"]
			except:
				pass
			
			if isROA:
				if bpy.context.scene.roa_settings.realtime:
					bpy.context.scene.roa_settings.realtime = False
				else:
					bpy.context.scene.roa_settings.realtime = True
				stateChange("realtime", bpy.context.scene.roa_settings.realtime)
			else:
				self.report({'ERROR'}, "Only ROA objects can be processed in Realtime EDIT Mode! Assign ROA first or make an Apply directly.")

		return {'FINISHED'}
	
class OT_ROA_Apply(bpy.types.Operator):
	"""Apply the full stack of operations. Note: some operations like "Avoid intersections" aren't executed in realtime mode, only when hitting Apply."""
	bl_idname = "object.roa_apply"
	bl_label = "Apply"
	#bl_options = {'UNDO'}
	
	isRT : bpy.props.BoolProperty(default=True)

	@classmethod
	def poll(self, context):
		if get_active_object() is not None:
			if get_active_object().select_get() == False: 
				return
		return get_active_object() is not None
	
	def execute(self, context):							 
		"""Save all Data"""
		sce = bpy.context.scene		
		originalObj = get_active_object()
		masterObj = originalObj	
			
		"""Autosave"""
		if context.scene.roa_settings.autosave:
			hasSave = False
			try:
				hasSave = masterObj["isROA"]
			except:
				pass
			if hasSave:
				bpy.ops.object.roa_store()	  
			  
		"""Leftover from the past, to be changed"""
		if context.scene.roa_settings.copyType == 'SINGLE':
			context.scene.roa_settings.singObj = True
		else:
			context.scene.roa_settings.singObj = False
			
		"""Check for incompatibilities"""
		if not self.isRT and context.scene.roa_settings.singObj:
			for area in bpy.context.screen.areas:
				if area.type == 'VIEW_3D':
					if area.spaces.active.local_view is not None:
						self.report({'ERROR'}, "Single object mode can't be used in the local User Perspective.\n Please press numpad / to leave the local User Perspective before applying.")
						return {'FINISHED'}
					
			if not (get_active_object().type == 'MESH' or get_active_object().type == 'CURVE'):
				self.report({'ERROR'}, "Single object mode (joining objects) can be used on mesh type or curve type objects only.")
				return {'FINISHED'}
		if context.scene.roa_settings.copyType == 'REAL' or context.scene.roa_settings.copyType == 'SINGLE': 
			if get_active_object().type == 'EMPTY':
				self.report({'ERROR'}, "None type objects (e.g. Group instances) can only be copied as instances")
				return {'FINISHED'}

		
		"""Remove Realtime leftovers"""
		if not self.isRT:
			bpy.context.scene.roa_settings.regenerate = True
			rtOb = prepareRT()
			context.scene.roa_settings.realtime = False
			stateChange("realtime", bpy.context.scene.roa_settings.realtime)
		  
		"""Random seed"""
		if context.scene.roa_settings.useSeed:
			random.seed(context.scene.roa_settings.randSeed)	  
		
		"""Cause of the group mode we need to make this in two steps now"""
		modList = []
		for mod in masterObj.modifiers:
			modList.append(masterObj.modifiers[mod.name].show_viewport)

		"""Pick grom group preparation"""
		useGroup = False
		srcList = []
		grpModList = []
		if context.scene.roa_settings.pickGrp and bpy.data.collections:
			if context.scene.objGroup != "":
				obID = 0
				"""Append Master object first because we're using group count now"""
				srcList.append(masterObj)
				for ob in bpy.data.collections[context.scene.objGroup].objects:
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
		originalLocation = originalObj.location
#		originalLayers = originalObj.layers			# FIXME ??? : layers removed in 2.80
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
		targetPolyList = []
		if (context.scene.targetObject != "") and (context.scene.roa_settings.dmode != True):
			#Global / Local to be removed
			context.scene.roa_settings.global_mode = 'GLOBAL'
			targetObj = context.scene.objects[context.scene.targetObject]
			if targetObj.type == 'MESH':
				targetObjMatrix = targetObj.matrix_world
				if context.scene.roa_settings.target_mode == "FACES":										
					#Weight maps
					if context.scene.vertex_group_density != "":
						targetGrp = targetObj.vertex_groups[context.scene.vertex_group_density].index
						for poly in targetObj.data.polygons:
							polyWeight = 0				
							for vert in poly.vertices:
								try:
									polyWeight += targetObj.data.vertices[vert].groups[targetGrp].weight
								except:
									pass

							polyWeight /= len(poly.vertices)
							
							#propability of being added depending of weight value
							if context.scene.roa_settings.invert_vertex_group_density:
								if polyWeight < 0.001:
									targetPolyList.append(poly)
								else:
									if random.random() + polyWeight < 0.7:
										targetPolyList.append(poly) 
							else:
								if polyWeight > 0.999:
									targetPolyList.append(poly)
								else:
									if random.random() + polyWeight > 1.3:
										targetPolyList.append(poly)
						targetObjPolyCount = len(targetObj.data.polygons) 
					else:
						targetPolyList = targetObj.data.polygons
						targetObjPolyCount = len(targetObj.data.polygons) 
						
					distFactor = context.scene.roa_settings.numOfObjects / targetObjPolyCount
					targetPolyIndex = 0

				if context.scene.roa_settings.target_mode == "POINTS":
					targetPointIndex = 0
					#Weight maps
					if context.scene.vertex_group_density != "":
						targetGrp = targetObj.vertex_groups[context.scene.vertex_group_density].index
						for vertex in targetObj.data.vertices:  
							vertWeight = 0
							try:
								vertWeight += vertex.groups[targetGrp].weight
							except:
								pass
							
							#propability of being added depending of weight value
							if context.scene.roa_settings.invert_vertex_group_density:
								if vertWeight < 0.001:
									targetPointList.append(targetObj.matrix_world * vertex.co)
								else:
									if random.random() + vertWeight < 0.7:
										targetPointList.append(targetObj.matrix_world * vertex.co) 
							else:
								if vertWeight > 0.999:
									targetPointList.append(targetObj.matrix_world * vertex.co)
								else:
									if random.random() + vertWeight > 1.3:
										targetPointList.append(targetObj.matrix_world * vertex.co)
							
					else:						
						for vertex in targetObj.data.vertices:  
							targetPointList.append(targetObj.matrix_world * vertex.co) 
								
				cloneToMesh = True	 
						
		else:
			context.scene.roa_settings.global_mode = 'LOCAL'
			
		"""Create Grid for grid mode"""
		realCount = 0
		if context.scene.roa_settings.dmode:
			offsetGrid = []
			oGridX = context.scene.roa_settings.gridSizeX
			oGridY = context.scene.roa_settings.gridSizeY
			oGridZ = context.scene.roa_settings.gridSizeZ
			
			realCount = objCount = oGridX * oGridY * oGridZ
			"""Limit maximum count in realtime preview"""
			if context.scene.roa_settings.realtime:
				if objCount > context.scene.roa_settings.maxCount:
					maxRow = int(context.scene.roa_settings.maxCount ** (1/3.)) 
					if maxRow < 2:
						maxRow = 2
					oGridX = oGridX if oGridX < maxRow else maxRow
					oGridY = oGridY if oGridY < maxRow else maxRow
					oGridZ = oGridZ if oGridZ < maxRow else maxRow
					objCount = oGridX * oGridY * oGridZ
					
			"""Depending on the relative axis we have to create the grid in a different way"""
			if not (context.scene.roa_settings.relOffset or context.scene.roa_settings.rowoffset) or context.scene.roa_settings.rel_axis == 'Z':		
				for x in range(0, oGridX, 1):
					for y in range(0, oGridY, 1):
						for z in range(0, oGridZ, 1):	
							offsetGrid.append((x*context.scene.roa_settings.fixedPosX,y*context.scene.roa_settings.fixedPosY,z*context.scene.roa_settings.fixedPosZ))
			elif context.scene.roa_settings.rel_axis == 'Y':
				for x in range(0, oGridX, 1):
					for z in range(0, oGridZ, 1):
						for y in range(0, oGridY, 1):	
							offsetGrid.append((x*context.scene.roa_settings.fixedPosX,y*context.scene.roa_settings.fixedPosY,z*context.scene.roa_settings.fixedPosZ))				  
			elif context.scene.roa_settings.rel_axis == 'X':  
				for z in range(0, oGridZ, 1):
					for y in range(0, oGridY, 1):
						for x in range(0, oGridX, 1):	
							offsetGrid.append((x*context.scene.roa_settings.fixedPosX,y*context.scene.roa_settings.fixedPosY,z*context.scene.roa_settings.fixedPosZ))				  
		else:
			realCount = objCount = context.scene.roa_settings.numOfObjects			
			"""Limit maximum count in realtime preview"""
			if context.scene.roa_settings.realtime:
				if objCount > context.scene.roa_settings.maxCount:
					objCount = context.scene.roa_settings.maxCount
			
		"""Load exisiting children into list"""
		objList = []
		listMaster = ""
		try: 
			listMaster = masterObj["name"]
		except:
			pass
		
		if not context.scene.roa_settings.regenerate and masterObj.name == listMaster and not context.scene.roa_settings.kchildren:
			index = 1
			try:
				objNameList = masterObj["Children"].split("<.>")
				for name in objNameList:
					"""Handle a decreasing number right away"""
					if index <= objCount and not "ROA_RT_BOX_TEMPORARY_OBJECT" in name and bpy.data.objects[name].parent == masterObj:
						objList.append(bpy.data.objects[name])
						#ob.select_set( False )
						index += 1
					else:
						bpy.data.objects[name].select_set( True )
			except: #If anything goes wrong, revert to the old method
				masterObj.select_set( True )
				bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
				for ob in bpy.context.selected_objects: #sorted(bpy.context.selected_objects, key=lambda ob: ob.name):
					"""Handle a decreasing number right away"""
					if index < objCount-1 and not "ROA_RT_BOX_TEMPORARY_OBJECT" in ob.name:
						objList.append(ob)
						ob.select_set( False )
						index += 1
			try:
				bpy.data.objects["ROA_RT_BOX_TEMPORARY_OBJECT"].select_set( True )
			except:
				pass
			
			masterObj.select_set( False )
			bpy.ops.object.delete(use_global=False)
			set_active_object( masterObj )
			masterObj.select_set( True )

		
		"""Calculate preview bounding box"""
		"""Never was very usefull, will be reactived on user request
		if context.scene.roa_settings.realtime and realCount > context.scene.roa_settings.maxCount:
			createRTBox()
		else:
			removeRTBox()"""
		
		"""Show progress"""  
		if not self.isRT:
			wm = bpy.context.window_manager	
			if (objCount+1 >= 100):
				progressPercent = round((objCount+1) / 100)
			else:
				progressPercent = 1
			progressIndex = 1	  
			wm.progress_begin(1, 100)
		
		"""Step rotation counter"""
		stepRotStepcounterX = stepRotStepcounterY = stepRotStepcounterZ = 1
		  
		for index in range(1, objCount+1):			
			"""Pick from group"""
			if useGroup:
				"""Work with copies of the lists for more freedom"""
				tmpSrcList = srcList.copy()
				tmpGroupCountData = []
				for element in bpy.context.scene.groupCountData:
					tmpGroupCountData.append(element.count)
				  
				"""Avoid repetition, temporarily remove the last clone source from the lists"""
				if context.scene.roa_settings.groupNoRepeat and 'prevGrpCopy' in locals():				
					#remove all instances of the object and it's data from both lists
					indices = []
					i = 0
					for ob in tmpSrcList:
						if ob == prevGrpCopy:
							indices.append(i)
						i += 1
						
					for i in sorted(indices, reverse=True):
						del tmpGroupCountData[i]
						del tmpSrcList[i]
					#print("Next run: -------------------------")
					#print("modified", tmpGroupCountData, tmpSrcList) 
				"""Use group count"""
				if len(tmpGroupCountData) > 0:
					total = subtotal = 0
					for item in tmpGroupCountData:
						total += item
					pick = round(random.random() * total)
				
					iIndex = 0
					for item in tmpGroupCountData:
						#print("Pick", pick, "Currentmax:", subtotal + tmpGroupCountData[iIndex])
						if iIndex > 0:
							subtotal += tmpGroupCountData[iIndex-1]
						#print("Pick", pick, "Currentmax:", subtotal + tmpGroupCountData[iIndex])
						#print("Index", iIndex)
						if iIndex < len(tmpGroupCountData):
							if subtotal <= pick <= subtotal + tmpGroupCountData[iIndex]:
								#print("Pick index", iIndex)
								originalObj = tmpSrcList[iIndex]
								#print("Picked", originalObj)
						iIndex += 1
										
				else:
					originalObj = tmpSrcList[round(random.random() * len(tmpSrcList)) - 1]

				prevGrpCopy = originalObj
		 
				originalDim = originalObj.dimensions
			
			
			"""Offset Range +/-"""
			if context.scene.roa_settings.rPosRange:
				rndPosX = random.random() * context.scene.roa_settings.randomPosX * 2 - context.scene.roa_settings.randomPosX
				rndPosY = random.random() * context.scene.roa_settings.randomPosY * 2 - context.scene.roa_settings.randomPosY
				rndPosZ = random.random() * context.scene.roa_settings.randomPosZ * 2 - context.scene.roa_settings.randomPosZ
			else:
				rndPosX = random.random() * context.scene.roa_settings.randomPosX
				rndPosY = random.random() * context.scene.roa_settings.randomPosY
				rndPosZ = random.random() * context.scene.roa_settings.randomPosZ
			rndPos = (rndPosX, rndPosY, rndPosZ)
			
			
			"""Step Rotation"""
			stepRotX = stepRotY = stepRotZ = 0
			if context.scene.roa_settings.stepRotation:
				if context.scene.roa_settings.stepRotMinX + context.scene.roa_settings.stepRotStepX * stepRotStepcounterX > context.scene.roa_settings.stepRotMaxX:
					stepRotStepcounterX = 0 
				
				if context.scene.roa_settings.stepRotMinY + context.scene.roa_settings.stepRotStepY * stepRotStepcounterY > context.scene.roa_settings.stepRotMaxY:
					stepRotStepcounterY = 0 
				
				if context.scene.roa_settings.stepRotMinZ + context.scene.roa_settings.stepRotStepZ * stepRotStepcounterZ > context.scene.roa_settings.stepRotMaxZ:
					stepRotStepcounterZ = 0 
					
				stepRotX = context.scene.roa_settings.stepRotMinX + context.scene.roa_settings.stepRotStepX * stepRotStepcounterX
				stepRotY = context.scene.roa_settings.stepRotMinY + context.scene.roa_settings.stepRotStepY * stepRotStepcounterY
				stepRotZ = context.scene.roa_settings.stepRotMinZ + context.scene.roa_settings.stepRotStepZ * stepRotStepcounterZ
				
				stepRotStepcounterX +=1  
				stepRotStepcounterY +=1  
				stepRotStepcounterZ +=1  
				
			
			"""Random Rotation & Full Angles"""
			if context.scene.roa_settings.fangles and context.scene.roa_settings.fanglesX:
				rangePM = 1
				if context.scene.roa_settings.rRotRange:
					if (random.random() < 0.5):
						rangePM = -1
				
				if (random.random() < 0.5):
					rndRotX = context.scene.roa_settings.randRotX * rangePM
				else:
					rndRotX = 0
			else:
				if context.scene.roa_settings.rRotRange:
					rndRotX = random.random() * context.scene.roa_settings.randRotX * 2 - context.scene.roa_settings.randRotX
				else:
					rndRotX = random.random() * context.scene.roa_settings.randRotX 
			
			if context.scene.roa_settings.fangles and context.scene.roa_settings.fanglesY:
				rangePM = 1
				if context.scene.roa_settings.rRotRange:
					if (random.random() < 0.5):
						rangePM = -1
				
				if (random.random() < 0.5):
					rndRotY = context.scene.roa_settings.randRotY * rangePM
				else:
					rndRotY = 0
			else:
				if context.scene.roa_settings.rRotRange:
					rndRotY = random.random() * context.scene.roa_settings.randRotY * 2 - context.scene.roa_settings.randRotY
				else:
					rndRotY = random.random() * context.scene.roa_settings.randRotY				 
			
			if context.scene.roa_settings.fangles and context.scene.roa_settings.fanglesZ:
				rangePM = 1
				if context.scene.roa_settings.rRotRange:
					if (random.random() < 0.5):
						rangePM = -1
				
				if (random.random() < 0.5):
					rndRotZ = context.scene.roa_settings.randRotZ * rangePM
				else:
					rndRotZ = 0
			else:
				if context.scene.roa_settings.rRotRange:
					rndRotZ = random.random() * context.scene.roa_settings.randRotZ * 2 - context.scene.roa_settings.randRotZ
				else:
					rndRotZ = random.random() * context.scene.roa_settings.randRotZ		
			
			"""Random Scale / Keep Shape"""
			if context.scene.roa_settings.kshape:
				rndSclZ = random.random() * (context.scene.roa_settings.maxSclZ - context.scene.roa_settings.minSclZ) + context.scene.roa_settings.minSclZ
				rndScl = (rndSclZ, rndSclZ, rndSclZ)
				"""Cumulate scale"""
				if context.scene.roa_settings.cScale:
					rndSclZ *= context.scene.roa_settings.fScaleZ**index
					rndScl = (rndSclZ, rndSclZ, rndSclZ)

			else:
				rndSclX = random.random() * (context.scene.roa_settings.maxSclX - context.scene.roa_settings.minSclX) + context.scene.roa_settings.minSclX
				rndSclY = random.random() * (context.scene.roa_settings.maxSclY - context.scene.roa_settings.minSclY) + context.scene.roa_settings.minSclY
				rndSclZ = random.random() * (context.scene.roa_settings.maxSclZ - context.scene.roa_settings.minSclZ) + context.scene.roa_settings.minSclZ
				rndScl = (rndSclX, rndSclY, rndSclZ)
				"""Cumulate scale"""
				if context.scene.roa_settings.cScale:
					rndSclX *= context.scene.roa_settings.fScaleX**index
					rndSclY *= context.scene.roa_settings.fScaleY**index
					rndSclZ *= context.scene.roa_settings.fScaleZ**index
					rndScl = (rndSclX, rndSclY, rndSclZ)
					
							
			"""Mirroring"""
			if context.scene.roa_settings.mirror:
				if context.scene.roa_settings.mirrorX and random.random() >= 1 - context.scene.roa_settings.mirrorProbX:
					rndScl = (rndScl[0]*-1, rndScl[1], rndScl[2])	
				if context.scene.roa_settings.mirrorY and random.random() >= 1 - context.scene.roa_settings.mirrorProbY:
					rndScl = (rndScl[0], rndScl[1]*-1, rndScl[2])
				if context.scene.roa_settings.mirrorZ and random.random() >= 1 - context.scene.roa_settings.mirrorProbZ:
					rndScl = (rndScl[0], rndScl[1], rndScl[2]*-1)
				 
							 
			"""Cumulate Offset is always true, except for target mesh"""
			if cloneToMesh:
				cuIndex = 1	  
			else:
				cuIndex = index
			
			if context.scene.roa_settings.dmode:
				#After a code update of the indexing (so there can be 0 copies), the offset index for grid mode needs to skip the first object
				if index == 1:
					continue
				offsetPos = offsetGrid[index-1]
			else:
				offsetPos = (context.scene.roa_settings.fixedPosX*cuIndex, context.scene.roa_settings.fixedPosY*cuIndex, context.scene.roa_settings.fixedPosZ*cuIndex)

			"""Cumulate Rotation"""
			if context.scene.roa_settings.cangles:
				cuRotX = context.scene.roa_settings.fixedRotX * index
				cuRotY = context.scene.roa_settings.fixedRotY * index
				cuRotZ = context.scene.roa_settings.fixedRotZ * index
			else:
				cuRotX = context.scene.roa_settings.fixedRotX
				cuRotY = context.scene.roa_settings.fixedRotY
				cuRotZ = context.scene.roa_settings.fixedRotZ
			
			"""Rotation"""
			rotX = (rndRotX+cuRotX+stepRotX)*0.0174533
			rotY = (rndRotY+cuRotY+stepRotY)*0.0174533
			rotZ = (rndRotZ+cuRotZ+stepRotZ)*0.0174533
			rotVal = (rotX, rotY, rotZ)
				
	
			"""Create duplicates""" 
			if len(objList) < index:  
				duplicate = originalObj.copy()	
				
				object_to_collection( duplicate )  # add to active collection (=> add to view layer)
                # TODO: Add to ROA-Collection cause otherwise conflicts
                # with Pick-From-Group where objects are added to the Pick-Collection causing recursion
				
				currentObj = duplicate	
				if context.scene.roa_settings.copyType == 'REAL' or context.scene.roa_settings.copyType == 'SINGLE':
					duplicate.data = originalObj.data.copy()  
					currentObj.data = duplicate.data
					
				currentObj["isROA"] = False
				objList.append(currentObj)	
			else:
				duplicate = objList[index-1]

				object_to_collection( duplicate )   # add to active collection (=> add to view layer)
				
				currentObj = duplicate  
				if context.scene.roa_settings.copyType == 'REAL' or context.scene.roa_settings.copyType == 'SINGLE':
					duplicate.data = objList[index-1].data
					currentObj.data = duplicate.data

				currentObj["isROA"] = False
 
			"""Shape key"""
			if context.scene.roa_settings.shapeK:
				shapeKey = bpy.data.objects[duplicate.name].data.shape_keys
				if shapeKey is not None and len(shapeKey.key_blocks) >= 2:
					shapeKey.key_blocks[1].value = random.random()
					if not context.scene.roa_settings.realtime and context.scene.roa_settings.applyK:
						currentObj.shape_key_add(from_mix=True)
						#After adding the mix it should be 3 keys..bit vague though
						try:
							for i in range(0, 3):
								currentObj.active_shape_key_index = 0
								sKey = currentObj.active_shape_key
								currentObj.shape_key_remove(sKey)
						except:
							pass
			
			if useGroup:
				duplicate.location = currentObj.location = masterObj.location 
										
			""" Set Parent """
			duplicate.parent = masterObj 
			
			"""Clone on Mesh, not in grid mode""" 
			if cloneToMesh:
				if context.scene.roa_settings.target_mode == "FACES":								 
					currentPoly = targetPolyList[targetPolyIndex]
					#if currentPoly.select_get() == False:
					#	continue
					quat = currentPoly.normal.to_track_quat('Z', 'X')
					loc = Matrix.Translation(currentPoly.center)
					mat = targetObjMatrix * loc * quat.to_matrix().to_4x4()
						
					duplicate.matrix_world = mat
					if context.scene.roa_settings.nangles: 
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
		
					if context.scene.roa_settings.fillMode:
						targetPolyIndex += 1
						if targetPolyIndex >= len(targetPolyList):
							targetPolyIndex = 0
					else:
						targetPolyIndex = round(random.random() * len(targetPolyList))
						if targetPolyIndex >= len(targetPolyList):
							targetPolyIndex = 0
							
				if context.scene.roa_settings.target_mode == "POINTS": 
					#parenting still messes with some things 
					duplicate.matrix_parent_inverse = masterObj.matrix_world.inverted()
					if context.scene.roa_settings.nangles:
						#if cyclic or not
						if targetPointIndex+1 < len(targetPointList):
							edgeTangent = Vector(targetPointList[targetPointIndex+1]) - Vector(targetPointList[targetPointIndex])
						else:
							if context.scene.roa_settings.cyclic:
								edgeTangent = Vector(targetPointList[0]) - Vector(targetPointList[targetPointIndex])
							else:
								edgeTangent = Vector(targetPointList[targetPointIndex]) - Vector(targetPointList[targetPointIndex-1])

						
					if context.scene.roa_settings.nangles:  
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
						
					if context.scene.roa_settings.fillMode:
						targetPointIndex += 1
						if targetPointIndex >= len(targetPointList):
							targetPointIndex = 0
					else:
						targetPointIndex  = round(random.random() * len(targetPointList))
						if targetPointIndex >= len(targetPointList):
							targetPointIndex = 0
							
				"""Vertex Group Scale"""
				if context.scene.vertex_group_scale != "":
					targetGrp = targetObj.vertex_groups[context.scene.vertex_group_scale].index

					polyWeight = 0	
					#if context.scene.roa_settings.target_mode == "FACES":			  
					for vert in currentPoly.vertices:
						try:
							polyWeight += targetObj.data.vertices[vert].groups[targetGrp].weight
						except:
							pass

					polyWeight /= len(currentPoly.vertices)
					
					if context.scene.roa_settings.invert_vertex_group_scale:	
						polyWeight = 1 - polyWeight
					
					if polyWeight == 0:
						polyWeight += 0.1
						
					duplicate.scale *= polyWeight							  
							  
			else:  
				duplicate.rotation_euler = Vector(rotVal)
				duplicate.scale = Vector(rndScl) 
				if context.scene.roa_settings.global_mode == 'LOCAL':
					duplicate.location = Vector(offsetPos) + Vector(rndPos)
				else:
					duplicate.location = Vector(originalLocation) + Vector(offsetPos) + Vector(rndPos)
			
			"""Relative offset"""
			if context.scene.roa_settings.relOffset and targetObj == None:
				"""For the sakes of the different modes and simplicity we just override the previously added offset here"""
				if lastObj == masterObj:
					if context.scene.roa_settings.rel_axis == 'X':
						duplicate.location[0] = lastObj.scale[0]*lastObj.dimensions[0]/2 + duplicate.scale[0]*duplicate.dimensions[0]/2 + context.scene.roa_settings.fixedPosX					
						
					if context.scene.roa_settings.rel_axis == 'Y':
						duplicate.location[1] = lastObj.scale[1]*lastObj.dimensions[1]/2 + duplicate.scale[1]*duplicate.dimensions[1]/2 + context.scene.roa_settings.fixedPosY		
	
					if context.scene.roa_settings.rel_axis == 'Z':
						duplicate.location[2] = lastObj.scale[2]*lastObj.dimensions[2]/2 + duplicate.scale[2]*duplicate.dimensions[2]/2 + context.scene.roa_settings.fixedPosZ

				else:
					if context.scene.roa_settings.rel_axis == 'X':
						if not context.scene.roa_settings.dmode or (cuIndex-1) % oGridX != 0:
							duplicate.location[0] = lastObj.location[0] + lastObj.scale[0]*lastObj.dimensions[0]/2 + duplicate.scale[0]*duplicate.dimensions[0]/2 + context.scene.roa_settings.fixedPosX

					if context.scene.roa_settings.rel_axis == 'Y':
						if not context.scene.roa_settings.dmode or (cuIndex-1) % oGridY != 0:
							duplicate.location[1] = lastObj.location[1] + lastObj.scale[1]*lastObj.dimensions[1]/2 + duplicate.scale[1]*duplicate.dimensions[1]/2 + context.scene.roa_settings.fixedPosY
							
					if context.scene.roa_settings.rel_axis == 'Z':
						if not context.scene.roa_settings.dmode or (cuIndex-1) % oGridZ != 0:
							duplicate.location[2] = lastObj.location[2] + lastObj.scale[2]*lastObj.dimensions[2]/2 + duplicate.scale[2]*duplicate.dimensions[2]/2 + context.scene.roa_settings.fixedPosZ
				duplicate.location += Vector(rndPos)
				lastObj = duplicate  
				
			"""Alpha feature: additional row offset"""
			"""May interfeire with some other important features"""
			"""May be changed or removed in the future"""			
			if context.scene.roa_settings.rowoffset and context.scene.roa_settings.dmode:
				rndOffX = random.random() * context.scene.roa_settings.rowOffsetRX * 2 - context.scene.roa_settings.rowOffsetRX
				rndOffY = random.random() * context.scene.roa_settings.rowOffsetRY * 2 - context.scene.roa_settings.rowOffsetRY
				rndOffZ = random.random() * context.scene.roa_settings.rowOffsetRZ * 2 - context.scene.roa_settings.rowOffsetRZ
				if context.scene.roa_settings.rel_axis == 'X':
					if cuIndex > oGridX:
						duplicate.location += (cuIndex-1) // oGridX * Vector([context.scene.roa_settings.rowOffsetX, context.scene.roa_settings.rowOffsetY, context.scene.roa_settings.rowOffsetZ]) + Vector([rndOffX, rndOffY, rndOffZ])
			
				if context.scene.roa_settings.rel_axis == 'Y':
					if cuIndex > oGridY:
						duplicate.location += (cuIndex-1) // oGridY * Vector([context.scene.roa_settings.rowOffsetX, context.scene.roa_settings.rowOffsetY, context.scene.roa_settings.rowOffsetZ]) + Vector([rndOffX, rndOffY, rndOffZ])
		 
				if context.scene.roa_settings.rel_axis == 'Z':
					if cuIndex > oGridZ:
						duplicate.location += (cuIndex-1) // oGridZ * Vector([context.scene.roa_settings.rowOffsetX, context.scene.roa_settings.rowOffsetY, context.scene.roa_settings.rowOffsetZ]) + Vector([rndOffX, rndOffY, rndOffZ])

			duplicate.select_set( False ) # obj not part of view layer  --- FIXME ?? (add to collection ?)
			currentObj.select_set( False ) # obj not part of view layer  --- FIXME ??

			"""Show progress"""
			if not self.isRT:
				if index % progressPercent == 0:
					progressIndex += 1 
				wm.progress_update(progressIndex)
			
		"""End show progress"""
		if not self.isRT:
			wm.progress_end()
		
		"""Update Scene and write object names to string"""
		joinActiveOb = None
		if not self.isRT and context.scene.roa_settings.singObj:
			firstOb = True
			masterObj.select_set( False )
			for ob in objList:
				"""The recycled objects are already linked, so trying is the easiest and fastest solution"""
				try:
					sce.objects.link(ob) 
					#ob.layers = originalLayers # FIXME ??? : layers removed in 2.80
					ob.select_set( True )
				except:
					pass
				if firstOb:
					bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=True)
					bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
					firstOb = False
					joinActiveOb = ob
		else:  
			#save the name of the master object, cause if it gets duplicated by the user, roa would access the wrong list
			masterObj["name"] = masterObj.name
			spacer = masterObj["Children"] = ""
			firstOb = True
			index = 0
			for ob in objList:
				if self.isRT:
					ob.name = originalName + ".roaRt." + str(index)
				
				index += 1
				masterObj["Children"] += spacer + ob.name
				if firstOb:
					spacer = "<.>"
					firstOb = False
				"""The recycled objects are already linked, so trying is the easiest and fastest solution"""
				try:
					sce.objects.link(ob)			
					# ob.layers = originalLayers  # FIXME ??? : layers removed in 2.80 
				except:
					pass
				#
			#
		#
		
		#
		#sce.update()   # FIXME ? -- use bpy.context.view_layer.update() ?
		bpy.context.view_layer.update()
		
		
		"""check for intersections, not in realtime mode"""
		if context.scene.roa_settings.rintersect and not self.isRT:
			collPoints = [0] * len(objList)
			maxPoints = 0
			for i in range(0, len(objList)):
				for v in range(i + 1, len(objList)):
					collPoints[i] += simpleCollision(objList[i], objList[v], context.scene.roa_settings.coll_mode)	
						
			#Solve the intersection problem in different ways				
			if context.scene.roa_settings.coll_solve == 'DELETE':
				i = 0
				for ob in objList[:]:
					if collPoints[i] > context.scene.roa_settings.max_coll-1:
						#dont delete first / join object
						if context.scene.roa_settings.singObj:
							if joinActiveOb != ob:
								bpy.context.collection.objects.unlink(ob)
								objList.remove(ob)
						else:
							bpy.context.collection.objects.unlink(ob)
							objList.remove(ob)
					i += 1
						
			if context.scene.roa_settings.coll_solve == 'MOVE':	 
				offVec = Vector((context.scene.roa_settings.fixedPosX, context.scene.roa_settings.fixedPosY, context.scene.roa_settings.fixedPosZ))	
				for i in range(0, len(objList)):
					if collPoints[i] > context.scene.roa_settings.max_coll-1:
						objList[i].location += offVec
						
			if context.scene.roa_settings.coll_solve == 'SCALE':
				if context.scene.roa_settings.kshape:
					newScale = Vector((context.scene.roa_settings.minSclZ, context.scene.roa_settings.minSclZ, context.scene.roa_settings.minSclZ))	
				else:
					newScale = Vector((context.scene.roa_settings.minSclX, context.scene.roa_settings.minSclY, context.scene.roa_settings.minSclZ))
				for i in range(0, len(objList)):
					if collPoints[i] > context.scene.roa_settings.max_coll-1:
						objList[i].scale = newScale
						
			if context.scene.roa_settings.coll_solve == 'SELECT' and not context.scene.roa_settings.singObj:
				originalDeselect = True
				for i in range(0, len(objList)):
					if collPoints[i] > context.scene.roa_settings.max_coll-1:
						objList[i].select_set( True )
					#
				#
			#
			
			#sce.update() # FIXME ? -- use bpy.context.view_layer.update() ?
			bpy.context.view_layer.update()
						
		"""Join Objects"""
		if not self.isRT and context.scene.roa_settings.singObj and (originalObj.type == 'MESH' or originalObj.type == 'CURVE'):
			set_active_object( joinActiveOb )
			masterObj.select_set( False )
			for ob in srcList:
				ob.select_set( False )
			bpy.ops.object.join()
			masterObj.select_set( True )
			set_active_object( originalObj )

		"""Enable modifier viewport visibility for the original object(s)"""
		if useGroup:
			for ob in bpy.data.collections[context.scene.objGroup].objects:
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
		
		if context.scene.roa_settings.singObj and not self.isRT:	
			masterObj.select_set( False )
			for ob in srcList:
				ob.select_set( False )
			joinActiveOb.select_set( True )
			set_active_object( joinActiveOb )

			if context.scene.roa_settings.global_mode == 'LOCAL':
				joinActiveOb.parent = masterObj
				
			if not context.scene.roa_settings.pobjects:
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
			originalObj.select_set( False )
			index = 0
			for ob in objList:				  
				set_active_object( ob )
				
				obSelectState = ob.select_get()  ## FIXME:  Error: Object (input object) not in View Layer 'View Layer'! (add to collection ??)
				
				ob.select_set( True )

				if ((not context.scene.roa_settings.pobjects) or context.scene.roa_settings.singObj) and not self.isRT:
					bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
  
				modCounter = 0
				if not self.isRT:
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
				ob.select_set( obSelectState )
				
		originalObj = masterObj
		if not originalDeselect:
			masterObj.select_set( True )
			if originalObj != masterObj:
				originalObj.select_set( False )
			set_active_object( None )
		else:
			masterObj.select_set( False )
			originalDeselect = True
			set_active_object( None )
					
		return {'FINISHED'}
	
class ROA_UL_Group_Count(UIList):	 
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		split = layout.split()
		split.label(text=str(item.name))
		split = layout.split()
		split.label(text=str(item.count))
		#split.prop(item, "name", text="", emboss=False, translate=False, icon='BORDER_RECT')

class ROA_PT_Panel(bpy.types.Panel):
	"""Random Object Array"""
	bl_label = "Random Object Array"
	bl_space_type = 'VIEW_3D'
	bl_context = 'objectmode'
	#
	bl_region_type = "UI"
	bl_category = "RO-Array"
	
	
	def draw(self, context):
		layout = self.layout
		
		box = layout.box()	
		split = box.split()
		col = split.column(align=True)
		
		
		row = col.row(align=True)
		if get_active_object() is None  or len(bpy.context.selected_objects) == 0:
			row.enabled=False
			
		if bpy.context.scene.roa_settings.realtime:
			rtButtonText = "EDIT Mode is active"
			row.alert = True
		else:
			rtButtonText = "EDIT in Realtime"
			
		row.operator(OT_ROA_EDIT.bl_idname, text = rtButtonText)
		row = col.row(align=True)
		row.operator(OT_ROA_Apply.bl_idname, text = "Apply").isRT = False 
		
		if get_active_object() is not None and len(bpy.context.selected_objects) > 0:
			isROA = False
			try: 
				isROA = get_active_object().parent["isROA"]
			except:
				pass
			if isROA:
				row = col.row(align=True)
				row.operator(OT_ROA_SelectParent.bl_idname, text = "Select Parent ROA Object")
			
		split = box.split()
		col = split.column(align=True)
		col.operator(OT_ROA_Reset.bl_idname, text = "Reset all values") 
		col.operator(OT_ROA_Set.bl_idname, text = "Assign ROA") 

		col = split.column(align=True)
		col.operator(OT_ROA_Store.bl_idname, text = "Save to object")		 
		col.operator(OT_ROA_Read.bl_idname, text = "Load from object") 
				 
		split = box.split()
		col = split.column(align=True) 
		if context.scene.roa_settings.dmode:
			col.prop(context.scene.roa_settings, "gridSizeX")
			col.prop(context.scene.roa_settings, "gridSizeY")
			col.prop(context.scene.roa_settings, "gridSizeZ")
		else:
			row = col.row(align=True)
			row.prop(context.scene.roa_settings, "numOfObjects")
			
		row = col.row(align=True)
		split=row.split(factor=0.65, align=True)
  
		split.operator(OT_ROA_Update.bl_idname, text="Update Relatime Preview")

		split.prop(context.scene.roa_settings, "maxCount", text="Max count")
		
		split = box.split()
		col = split.column(align=True)

		col.prop(context.scene.roa_settings, "copyType")
				
		col.label(text="Fixed Offset")
		col.prop(context.scene.roa_settings, "fixedPosX")
		col.prop(context.scene.roa_settings, "fixedPosY")
		col.prop(context.scene.roa_settings, "fixedPosZ")
		col.prop(context.scene.roa_settings, "relOffset")  
		col.prop(context.scene.roa_settings, "mirror") 
		
		if context.scene.roa_settings.mirror:  
			#sadly doesn't fit in one column
			row = box.row(align=True)
			row.prop(context.scene.roa_settings, "mirrorX")
			row.prop(context.scene.roa_settings, "mirrorY")
			row.prop(context.scene.roa_settings, "mirrorZ")	
			row = box.row(align=True)
			row.label("Mirror probability:")
			row = box.row(align=True)
			row.prop(context.scene.roa_settings, "mirrorProbX")	
			row.prop(context.scene.roa_settings, "mirrorProbY")
			row.prop(context.scene.roa_settings, "mirrorProbZ")
								
		if context.scene.roa_settings.dmode: 
			col.prop(context.scene.roa_settings, "rowoffset")			 
			
		if context.scene.roa_settings.relOffset or context.scene.roa_settings.rowoffset:  
			col = box.column(align=True)
			col.label(text="Axis for relative offset / row offset")
			col.prop(context.scene.roa_settings, "rel_axis")
		
		
		col = split.column(align=True)
		
		col.prop(context.scene.roa_settings, "dmode")  
		col.label(text="Random Offset")
		col.prop(context.scene.roa_settings, "randomPosX")
		col.prop(context.scene.roa_settings, "randomPosY")
		col.prop(context.scene.roa_settings, "randomPosZ")  
		col.prop(context.scene.roa_settings, "rPosRange")	  
		
		if context.scene.roa_settings.rowoffset and context.scene.roa_settings.dmode:
				split = box.split()
				col = split.column(align=True)
				col.label(text="Row Offset X | Y | Z") 
				row = col.row(align=True)
				row.prop(context.scene.roa_settings, "rowOffsetX")
				row.prop(context.scene.roa_settings, "rowOffsetY")
				row.prop(context.scene.roa_settings, "rowOffsetZ")

		if context.scene.roa_settings.stepRotation:		  
			split = box.split()
			col = split.column(align=True)
			col.label(text="Step Rotation Min")
			col.prop(context.scene.roa_settings, "stepRotMinX")
			col.prop(context.scene.roa_settings, "stepRotMinY")
			col.prop(context.scene.roa_settings, "stepRotMinZ")
			
			col = split.column(align=True)
			col.label(text="Step Rotation Max")
			col.prop(context.scene.roa_settings, "stepRotMaxX")
			col.prop(context.scene.roa_settings, "stepRotMaxY")
			col.prop(context.scene.roa_settings, "stepRotMaxZ")
			
			split = box.split()
			col = split.column(align=True)
			col.label(text="Step Rotation step size")
			row = col.row(align=True)
			row.prop(context.scene.roa_settings, "stepRotStepX")
			row.prop(context.scene.roa_settings, "stepRotStepY")
			row.prop(context.scene.roa_settings, "stepRotStepZ")

		split = box.split()
		col = split.column(align=True)	
			
		col.label(text="Fixed Rotation")
		col.prop(context.scene.roa_settings, "fixedRotX")
		col.prop(context.scene.roa_settings, "fixedRotY")
		col.prop(context.scene.roa_settings, "fixedRotZ")
		col.prop(context.scene.roa_settings, "cangles")
		col.prop(context.scene.roa_settings, "fangles")
		
		if context.scene.roa_settings.fangles:  
			#sadly doesn't fit in one column
			row = box.row(align=True)
			row.prop(context.scene.roa_settings, "fanglesX")
			row.prop(context.scene.roa_settings, "fanglesY")
			row.prop(context.scene.roa_settings, "fanglesZ")	
		
		col = split.column(align=True)
		
		col.label(text="Random Rotation")
		col.prop(context.scene.roa_settings, "randRotX")
		col.prop(context.scene.roa_settings, "randRotY")
		col.prop(context.scene.roa_settings, "randRotZ")
		col.prop(context.scene.roa_settings, "rRotRange")
		col.prop(context.scene.roa_settings, "stepRotation")		

		split = box.split()
		col = split.column(align=True)

		col.label(text="Random Scale Min.")
		if not context.scene.roa_settings.kshape:
			col.prop(context.scene.roa_settings, "minSclX")
			col.prop(context.scene.roa_settings, "minSclY")
			col.prop(context.scene.roa_settings, "minSclZ")
		else:
			col.prop(context.scene.roa_settings, "minSclZ", text="Min:")

			
		col.prop(context.scene.roa_settings, "kshape")
		col.prop(context.scene.roa_settings, "cScale")

		col = split.column(align=True) 
		
		col.label(text="Random Scale Max.")
		if not context.scene.roa_settings.kshape:
			col.prop(context.scene.roa_settings, "maxSclX")
			col.prop(context.scene.roa_settings, "maxSclY")
			col.prop(context.scene.roa_settings, "maxSclZ")
		else:
			col.prop(context.scene.roa_settings, "maxSclZ", text="Max:")
		
		col.prop(context.scene.roa_settings, "pobjects") 
		col.prop(context.scene.roa_settings, "pickGrp")
		
		if not context.scene.roa_settings.kshape:
			if context.scene.roa_settings.cScale:
				split = box.split()
				col = split.column(align=True)
				col.prop(context.scene.roa_settings, "fScaleX")
				col.prop(context.scene.roa_settings, "fScaleY")
				col.prop(context.scene.roa_settings, "fScaleZ")	
		else:
			if context.scene.roa_settings.cScale:
				split = box.split()
				col = split.column()
				col.prop(context.scene.roa_settings, "fScaleZ", text="Cumulate scale")  
 
		if context.scene.roa_settings.pickGrp:
			split = box.split()
			col = split.column() 
			col.label(text="Group:")
			col.prop_search(context.scene, "objGroup", bpy.data, "collections", text="")						 
			col.template_list("ROA_UL_Group_Count", "", context.scene, "groupCountData", context.scene.roa_settings, "groupCountIndex")
			split = box.split()
			col = split.column()			 
			"""monitor for index change to update count correctly"""
			if context.scene.objGroup != "":
				if len(context.scene.groupCountData) > 0:
					if context.scene.roa_settings.groupCountIndexLast != context.scene.roa_settings.groupCountIndex:
						context.scene.roa_settings.groupActiveCount = context.scene.groupCountData[context.scene.roa_settings.groupCountIndex].count
						context.scene.roa_settings.groupCountIndexLast = context.scene.roa_settings.groupCountIndex 
				col.operator(OT_ROA_update_grouplist.bl_idname, text="Update group list").buttonPress = True
				col = split.column()  
				col.prop(context.scene.roa_settings, "groupActiveCount", text="Count") 
				if not context.scene.roa_settings.dmode:
					split = box.split()
					col = split.column()  
					col.prop(context.scene.roa_settings, "groupNoRepeat", text="Avoid Repetition") 
		 
		
		"""Warning labels""" 
		"""Disabled permanently as it's causing freezes"""
		"""
		if context.object is not None:  
			if context.object.type == 'MESH':
				mesh = get_active_object().data
				triCount = len(mesh.polygons) 
				objCount = context.scene.roa_settings.gridSizeX * context.scene.roa_settings.gridSizeY * context.scene.roa_settings.gridSizeZ 
				totalTris = objCount * triCount
				totalTrisFormated =  '{:,}'.format(totalTris)
				if (objCount > 8000) or (totalTris > 5000000) :
					box.label(text="Warning! You try to create")
					box.label(text=" %d objects with" % objCount)
					box.label(text=" %s polygons." % totalTrisFormated)
					box.label(text="This may freeze Blender.")
		if context.scene.roa_settings.rintersect: 
			objCount = context.scene.roa_settings.gridSizeX * context.scene.roa_settings.gridSizeY * context.scene.roa_settings.gridSizeZ if context.scene.roa_settings.dmode else context.scene.roa_settings.numOfObjects
			if objCount > 1000 and context.scene.roa_settings.coll_mode == 'AABB':
					box.label(text="Warning! Finding collisions for")
					box.label(text="%d objects can take a very" % objCount)
					box.label(text="long time and may freeze Blender!")
					box.label(text="Maximum recommend number for this mode: 1000.")

			if objCount > 4000 and context.scene.roa_settings.coll_mode == 'ORDI':
					box.label(text="Warning! Finding collisions for")
					box.label(text="%d objects can take a very" % objCount)
					box.label(text="long time and may freeze Blender!")
					box.label(text="Maximum recommend number for this mode: 4000.")"""

		"""Clone on mesh, not in grid mode"""
		if not context.scene.roa_settings.dmode:
			split = box.split()
			col = split.column(align=True)	 
			col.label(text="Target Mesh:")
			col.prop_search(context.scene, "targetObject", context.scene, "objects", text="")
			col = split.column(align=True)	 
			col.label(text="Clone to")
			col.prop(context.scene.roa_settings, "target_mode")	
			if context.scene.targetObject != "":
				try:
					row = box.row()
					row.label(text="Target polygon count: "+str(len(bpy.data.objects[context.scene.targetObject].data.polygons)))
				except:
					pass
				split = box.split()
				col = split.column() 
				col.prop(context.scene.roa_settings, "nangles")  
				col = split.column() 
				col.prop(context.scene.roa_settings, "fillMode")  
				if context.scene.roa_settings.target_mode == "POINTS":
					col.prop(context.scene.roa_settings, "cyclic")  
				
				"""Weight maps"""	
				ob = context.scene.objects[context.scene.targetObject]
				split = box.split()
				col = split.column(align=True)	 
				row = col.row(align=True)
				row.prop_search(context.scene, "vertex_group_density", ob, "vertex_groups", text="Density")
				row.prop(context.scene.roa_settings,"invert_vertex_group_density", text="", toggle=True, icon='ARROW_LEFTRIGHT')
				
				"""Scale influence"""
				row = col.row(align=True)
				row.prop_search(context.scene, "vertex_group_scale", ob, "vertex_groups", text="Scale")
				row.prop(context.scene.roa_settings,"invert_vertex_group_scale", text="", toggle=True, icon='ARROW_LEFTRIGHT')


		split = box.split()
		col = split.column()	 
		col.prop(context.scene.roa_settings, "shapeK")
		if context.scene.roa_settings.shapeK:
			col = split.column()
			col.prop(context.scene.roa_settings, "applyK")	
		col = split.column()
		col.prop(context.scene.roa_settings, "rintersect")
				
		if context.scene.roa_settings.rintersect: 
			col.prop(context.scene.roa_settings, "max_coll")
			split = box.split()
			col = split.column(align=True) 
			col.prop(context.scene.roa_settings, "coll_mode")  
			col.prop(context.scene.roa_settings, "coll_solve")
			if context.scene.roa_settings.coll_mode == "ORDI" or context.scene.roa_settings.coll_mode == "SIMP":
				col.prop(context.scene.roa_settings, "orgDist")
			else:
				col.prop(context.scene.roa_settings, "aabbSize")			
			
			"""Anim mode is broken"""
			#split = box.split()
			#col = split.column()
			#col.prop(context.scene.roa_settings, "animMode") 
				 
		split = box.split()
		col = split.column()
		
		col.prop(context.scene.roa_settings, "useSeed")
		if context.scene.roa_settings.useSeed:
			col = split.column()
			col.prop(context.scene.roa_settings, "randSeed")
				
		split = box.split()
		col = split.column()			
		col.prop(context.scene.roa_settings, "autosave", text="Autosave & Autoload")
		col = split.column()
		col.prop(context.scene.roa_settings, "kchildren")
					
 



# ------------------------------------------------------------------------
#	Registration
# ------------------------------------------------------------------------

classes = (
#	MyProperties,
 #WM_OT_HelloWorld,
  #  OBJECT_MT_CustomMenu,
# OBJECT_PT_CustomPanel
	
	RandomObjectArraySettings,
	#
	OT_ROA_Update,
	OT_ROA_Reset,
	OT_ROA_Store,
	OT_ROA_Set ,
	OT_ROA_Read ,
	OT_ROA_SelectParent,
	OT_ROA_EDIT,
	OT_ROA_Apply,
	OT_ROA_update_grouplist,
	#
	ROA_UL_Group_Count, # UIList
	ROA_GroupCountData,  # PropertyGroup
	#
	ROA_PT_Panel, # Panel 
)

def register():
	from bpy.utils import register_class
	#
	for cls in classes:
		register_class(cls)
	#
	
	bpy.types.Scene.roa_settings = bpy.props.PointerProperty(type=RandomObjectArraySettings)
	bpy.types.Scene.targetObject = bpy.props.StringProperty()
	bpy.types.Scene.vertex_group_density = bpy.props.StringProperty()
	bpy.types.Scene.vertex_group_scale = bpy.props.StringProperty()
	bpy.types.Scene.objGroup = bpy.props.StringProperty()
	bpy.types.Scene.groupCountData = bpy.props.CollectionProperty(type=ROA_GroupCountData)
	#
	#bpy.app.handlers.scene_update_post.append(scene_update)
	bpy.app.handlers.depsgraph_update_pre.append(handler_depsgraph_update_pre)


def unregister():
	from bpy.utils import unregister_class
	#
	for cls in reversed(classes):
		unregister_class(cls)
	#
	
	del bpy.types.Scene.roa_settings
	del bpy.types.Scene.targetObject
	del bpy.types.Scene.vertex_group_density 
	del bpy.types.Scene.vertex_group_scale
	del bpy.types.Scene.objGroup 
	del bpy.types.Scene.groupCountData
	#
	bpy.app.handlers.depsgraph_update_pre.remove( handler_depsgraph_update_pre)


if __name__ == "__main__":
	register()





