import os
from mathutils import *
import os.path as osp
import glob
import xml.etree.ElementTree as et
from xml.dom import minidom
import numpy as np
import argparse


def addShape(root, name,
        materialNum = None,
        textures = None,
        checkerIm = None,
        isChecker = True ):

    shape = et.SubElement(root, 'shape' )
    shape.set('id', '{0}_object'.format(name) )
    shape.set('type', 'obj' )
    stringF = et.SubElement(shape, 'string' )
    stringF.set('name', 'filename' )
    stringF.set('value', name )

    if isChecker:
        for n in range(0, materialNum ):
            bsdf = et.SubElement(shape, 'bsdf' )
            bsdf.set('id', 'part%d' % n )
            bsdf.set('type', 'diffuse' )
            texture = et.SubElement(bsdf, 'texture' )
            texture.set('name', 'reflectance' )
            texture.set('type', 'bitmap' )
            filename = et.SubElement(texture, 'string' )
            filename.set('name', 'filename' )
            filename.set('value', checkerIm )
    else:
        for n in range(0, len(textures ) ):
            bsdf = et.SubElement(shape, 'bsdf' )
            bsdf.set('id', 'part%d' % n )
            bsdf.set('type', 'microfacet' )

            textureDir = textures[n]

            # Add diffuse albedo
            albedo = et.SubElement(bsdf, 'texture' )
            albedo.set('name', 'albedo' )
            albedo.set('type', 'bitmap' )
            albedofile = et.SubElement(albedo, 'string' )
            albedofile.set('name', 'filename' )
            albedofile.set('value', osp.join(textureDir, 'diffuse_tiled.png') )

            # Add new normal
            normal = et.SubElement(bsdf, 'texture' )
            normal.set('name', 'normal')
            normal.set('type', 'bitmap')
            normalfile = et.SubElement(normal, 'string')
            normalfile.set('name', 'filename')
            normalfile.set('value', osp.join(textureDir, 'normal_tiled.png') )

            # Add new normal
            roughness = et.SubElement(bsdf, 'texture' )
            roughness.set('name', 'roughness')
            roughness.set('type', 'bitmap')
            roughnessfile = et.SubElement(roughness, 'string')
            roughnessfile.set('name', 'filename')
            roughnessfile.set('value', osp.join(textureDir, 'rough_tiled.png') )

    return root

def addSensor(root, fovValue, imWidth, imHeight, sampleCount):
    camera = et.SubElement(root, 'sensor')
    camera.set('type', 'perspective')
    fov = et.SubElement(camera, 'float')
    fov.set('name', 'fov')
    fov.set('value', '%.4f' % (fovValue) )
    fovAxis = et.SubElement(camera, 'string')
    fovAxis.set('name', 'fovAxis')
    fovAxis.set('value', 'x')
    film = et.SubElement(camera, 'film')
    film.set('type', 'ldrfilm')
    width = et.SubElement(film, 'integer')
    width.set('name', 'width')
    width.set('value', '%d' % (imWidth) )
    height = et.SubElement(film, 'integer')
    height.set('name', 'height')
    height.set('value', '%d' % (imHeight) )
    sampler = et.SubElement(camera, 'sampler')
    sampler.set('type', 'adaptive')
    sampleNum = et.SubElement(sampler, 'integer')
    sampleNum.set('name', 'sampleCount')
    sampleNum.set('value', '%d' % (sampleCount) )
    return root

def transformToXml(root ):
    rstring = et.tostring(root, 'utf-8')
    pstring = minidom.parseString(rstring)
    xmlString = pstring.toprettyxml(indent="    ")
    xmlString= xmlString.split('\n')
    xmlString = [x for x in xmlString if len(x.strip()) != 0 ]
    xmlString = '\n'.join(xmlString )
    return xmlString


def addEnv(root, envmapName, scaleFloat):
    emitter = et.SubElement(root, 'emitter')
    emitter.set('type', 'envmap')
    filename = et.SubElement(emitter, 'string')
    filename.set('name', 'filename')
    filename.set('value', envmapName )
    scale = et.SubElement(emitter, 'float')
    scale.set('name', 'scale')
    scale.set('value', '%.4f' % (scaleFloat) )
    return root


parser = argparse.ArgumentParser()
parser.add_argument('--src_path', help='path to the shape root')
parser.add_argument('--modelId', default = 0, type=int, help='the starting point' )
opt = parser.parse_args()

materialNames = ['wood', 'plastic', 'rough_stone', 'specular_stone', 'paint', 'leather', 'metal', 'fabric', 'rubber', 'area_light']
checkerIm = '/newfoundland/zhl/generateUV/textures/checkerboard.jpg'
textureRoot = '/newfoundland/zhl/generateUV/textures/'
envmapName = '/newfoundland/zhl/generateUV/textures/env.hdr'
imWidth = 320
imHeight = 240
fovValue = 63.4
sampleCount = 128
program = '/home/zhl/OptixRenderer/src/bin/optixRenderer'


dirs = glob.glob(osp.join(opt.src_path, '*') )
dirs = [x for x in dirs if osp.isdir(x) ]
dirs = sorted(dirs )

d = dirs[opt.modelId ]
file_loc = osp.join(d, 'merged.obj')
save_loc = osp.join(d, 'uv_mapped.obj')

if not osp.isfile(file_loc ):
    print('Warning: no merged.obj for model %s' % d)
    exit()

if osp.isfile(save_loc):
    print('Warning: uv_mapped.obj for model %s has been generated' % d )
    exit()

import bpy
bpy.ops.object.delete()
bpy.ops.import_scene.obj( filepath=file_loc, use_split_groups=False )
obj_object = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj_object
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.uv.cube_project(cube_size=2.2)

bpy.ops.export_scene.obj(filepath=save_loc, check_existing=False, use_selection=True,
                     group_by_material=True, use_smooth_groups=False )
bpy.ops.object.delete()

annFile = osp.join(d, 'ann.txt')
if not osp.isfile(annFile ):
    print('Warning: no ann.txt for model %s' % d)
    exit()

with open(annFile, 'r') as annIn:
    anns = annIn.readlines()

if anns[0][0] == '!':
    print('Marked as low quality model')
    exit()
else:
    materials = []
    matNum = int(anns[0].strip().split(' ')[1] )
    materials = [None for n in range(0, matNum) ]
    for ann in anns:
        if ann[0] == '#':
            continue
        else:
            annList = ann.strip().split(' ')
            matId = int(annList[0] )
            matCat = [int(x) for x in annList[1:] ]
            materials[matId ] = matCat

print(materials )

# create camera file
yAxis = np.array([0, 0.3, 0], dtype=np.float32 )
xAxis = np.array([1, 0, 0], dtype=np.float32 )
zAxis = np.array([0, 0, 1], dtype=np.float32 )
angles = np.array([0, 90, 180, 270], dtype=np.float32 ) * np.pi / 180.0
dist = 2.5

camFile = osp.join(d, 'cam.txt' )
with open(camFile, 'w') as camOut:
    camOut.write('%d\n' % len(angles ) )
    for angle in angles:
        origin = dist * (xAxis * np.cos(angle) + yAxis * np.sin(angle) + zAxis )
        camZAxis = origin / np.sqrt(np.sum(origin * origin ) )
        lookat = np.array([0, 0, 0] )
        up = yAxis - np.sum(yAxis * camZAxis ) * camZAxis
        up = up / np.sqrt(np.sum(up * up ) )

        camOut.write('%.3f %.3f %.3f\n' % (origin[0], origin[1], origin[2] ) )
        camOut.write('%.3f %.3f %.3f\n' % (lookat[0], lookat[1], lookat[2] ) )
        camOut.write('%.3f %.3f %.3f\n' % (up[0], up[1], up[2] ) )

# create xml file to render checkerboard
root = et.Element('scene')
root.set('version', '0.5.0')
integrator = et.SubElement(root, 'integrator')
integrator.set('type', 'path')
root = addShape(root, 'uv_mapped.obj', materialNum = matNum, checkerIm = checkerIm )
root = addSensor(root, fovValue, imWidth, imHeight, sampleCount )
xmlString = transformToXml(root )

xmlFile = osp.join(d, 'checkerboard.xml')
with open(xmlFile, 'w') as xmlOut:
    xmlOut.write(xmlString )

# render texture and normal
cmd1 = '%s -f %s -c %s -o %s -m 1 --forceOutput' % \
        (program, xmlFile, 'cam.txt', 'test.jpg')
os.system(cmd1 )
cmd2 = '%s -f %s -c %s -o %s -m 2 --forceOutput' % \
        (program, xmlFile, 'cam.txt', 'test.jpg')
os.system(cmd2 )

# create xml file to render material samples
root = et.Element('scene')
root.set('version', '0.5.0')
integrator = et.SubElement(root, 'integrator')
integrator.set('type', 'path')

textures = []
for material in materials:
    matId = np.random.randint(len(material ) )
    matCatType = materialNames[material[matId] ]
    textures.append(osp.join(textureRoot, matCatType ) )

root = addShape(root, 'uv_mapped.obj', materialNum = matNum, textures = textures, isChecker = False )
root = addSensor(root, fovValue, imWidth, imHeight, sampleCount )
root = addEnv(root, envmapName, scaleFloat = 3)
xmlString = transformToXml(root )

xmlFile = osp.join(d, 'material.xml')
with open(xmlFile, 'w') as xmlOut:
    xmlOut.write(xmlString )

# render images with materials
cmd1 = '%s -f %s -c %s -o %s -m 0 --forceOutput' % \
        (program, xmlFile, 'cam.txt', 'material.png')
os.system(cmd1 )

