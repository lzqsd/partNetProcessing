import glob
import cv2
import os
import os.path as osp
import numpy as np

def load_mesh(meshName ):
    with open(meshName, 'r') as objIn:
        lines = objIn.readlines()
    lines = [l.strip() for l in lines ]

    # Read obj and change material names
    vertices = []
    normals = []
    textures = []
    faces = []
    f = []
    materials = []
    for l in lines:
        if len(l) > 2:
            if l[0:2] == 'v ':
                v = l.split(' ')[1:4]
                v = [float(x) for x in v ]
                vertices.append(np.array(v).reshape(1, 3) )
            elif l[0:2] == 'vn':
                vn = l.split(' ')[1:4]
                vn = [float(x) for x in vn]
                normals.append(np.array(vn).reshape(1, 3) )
            elif l[0:2] == 'vt':
                textures.append(l )
            elif l[0:2] == 'f ':
                f.append(l)
            elif l[0:2] == 'us':
                matName = l.split(' ')[1]
                matName = '%s_%s_%s' % (catId, modelId, matName )
                materials.append('usemtl %s' % matName )
                if not len(f) == 0:
                    faces.append(f )
                f = []
    faces.append(f )

    vertices = np.concatenate(vertices, axis=0 )
    normals = np.concatenate(normals, axis=0 )

    return vertices, normals, textures, faces, materials


def computeDiagLength(vertices ):
    minX, maxX = vertices[:, 0].min(), vertices[:, 0].max()
    minY, maxY = vertices[:, 1].min(), vertices[:, 1].max()
    minZ, maxZ = vertices[:, 2].min(), vertices[:, 2].max()
    diagLength = (maxX - minX) * (maxX - minX ) + \
            (maxY - minY ) * (maxY - minY ) + \
            (maxZ - minZ ) * (maxZ - minZ )
    diagLength = np.sqrt(diagLength )
    return diagLength

rotMats = {}

cats = glob.glob('*')
cats = [x for x in cats if osp.isdir(x) and x != 'textures']
cats = sorted(cats )
for cat in cats:
    models = glob.glob(osp.join(cat, '*') )
    models = [x for x in models if osp.isdir(x ) ]
    models = sorted(models )
    for model in models:
        objInFile = osp.join(model, 'uv_mapped.obj')
        outputFile = osp.join(model, 'aligned.obj')
        if osp.isfile(objInFile):
            print(model )
            catId, modelId = model.split('/')[-2:]
            vertices, normals, textures, faces, materials = load_mesh(objInFile )
            diagLength = computeDiagLength(vertices )

            # Align with old models
            originFile = osp.join(model, 'origin.obj')
            if osp.isfile(originFile ):
                vertOrig, normOrig, _, _, _ = load_mesh(originFile )

                # Scale the shape
                diagLength_o = computeDiagLength(vertOrig )
                scale = diagLength_o / diagLength
                vertices = vertices * scale

                # Rotate the shape
                vertices[:, 0] = -vertices[:, 0]
                vertices[:, 2] = -vertices[:, 2]
                normals[:, 0] = -normals[:, 0]
                normals[:, 2] = -normals[:, 2]

                # Translate the shape
                for dim in range(0, 3):
                    minD, maxD = vertices[:, dim].min(), vertices[:, dim].max()
                    minD_o, maxD_o = vertOrig[:, dim].min(), vertOrig[:, dim].max()
                    translate = 0.5 * (maxD_o - maxD + minD_o - minD )
                    vertices[:, dim] = vertices[:, dim] + translate

                # Check the quality
                isAligned = True
                for dim in range(0, 3):
                    minD, maxD = vertices[:, dim].min(), vertices[:, dim].max()
                    minD_o, maxD_o = vertOrig[:, dim].min(), vertOrig[:, dim].max()
                    gap = max(np.abs(maxD_o - maxD), np.abs(minD_o - minD ) )
                    if gap > 0.05 * diagLength:
                        with open('alignmentFailure.txt', 'a') as fileOut:
                            fileOut.write(model + '\n')
                            print('Alignment failure: %s' % model )
                            if osp.isfile(outputFile ):
                                os.system('rm %s' % outputFile )
                        isAligned = False
                        break

                if isAligned == False:
                    continue

            # Output the rotated mesh
            with open(outputFile, 'w') as objOut:
                for n in range(0, vertices.shape[0] ):
                    objOut.write('v %.4f %.4f %.4f\n' % \
                            (vertices[n, 0], vertices[n, 1], vertices[n, 2] ) )
                for n in range(0, normals.shape[0] ):
                    objOut.write('vn %.4f %.4f %.4f\n' % \
                            (normals[n, 0], normals[n, 1], normals[n, 2] ) )
                for n in range(0, len(textures) ):
                    objOut.write(textures[n] + '\n')

                for n in range(0, len(materials ) ):
                    objOut.write(materials[n] + '\n')
                    f = faces[n]
                    for m in range(0, len(f) ):
                        objOut.write(f[m] + '\n')

            with open(osp.join(model, 'matNum.txt'), 'w') as matOut:
                matOut.write('%d' % len(materials) )

