import glob
import cv2
import os
import os.path as osp
import numpy as np
import trimesh
import torch
from torch.autograd import Variable
import trimesh as trm
from trimesh.base import Trimesh
from chamfer_distance import ChamferDistance

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
                v = l.split(' ')
                v = [x.strip() for x in v if len(x.strip() ) > 0 ]
                v = v[1:4]
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


def computeDiagLength(vertices, faceVert ):

    faceVert = faceVert.flatten()
    faceVert = np.unique(faceVert )

    vertices = vertices[faceVert, :]

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

chamferDist = ChamferDistance()

os.system('rm alignmentFailure.txt' )
catCount = 0

for cat in cats:
    catCount += 1
    models = glob.glob(osp.join(cat, '*') )
    models = [x for x in models if osp.isdir(x ) ]
    models = sorted(models )

    cnt = 0
    for model in models:
        print(catCount, cnt +1, model )
        objInFile = osp.join(model, 'uv_mapped.obj')
        outputFile = osp.join(model, 'alignedNew.obj')
        if osp.isfile(outputFile ):
            continue

        if osp.isfile(objInFile ):

            catId, modelId = model.split('/')[-2:]
            vertices, normals, textures, faces, materials = load_mesh(objInFile )

            # sample the srcPoint
            faceVert = []
            for f in faces:
                for l in f:
                    l = l.strip().split(' ')[1:]
                    l = [int(x.split('/')[0] ) for x in l ]
                    l = np.array(l ).astype(np.int32 )[np.newaxis, :]
                    faceVert.append(l )
            faceVert = np.concatenate(faceVert )
            faceVert -= 1

            faceVert_u = np.unique(faceVert.flatten() )

            mesh = Trimesh(vertices = vertices, faces = faceVert )
            srcPoint, _= trm.sample.sample_surface_even(mesh, 2000 )

            diagLength = computeDiagLength(vertices, faceVert )

            # Align with old models
            originFile = osp.join(model, 'origin.obj')
            if osp.isfile(originFile ):
                vertOrig, normOrig, _, faceOrig, _ = load_mesh(originFile )

                faceVertOrig = []
                for f in faceOrig:
                    for l in f:
                        l = l.strip().split(' ')[1:]
                        l = [x.strip() for x in l if len(x.strip()) > 0 ]
                        l = [int(x.split('/')[0] ) for x in l ]
                        l = np.array(l ).astype(np.int32 )[np.newaxis, :]
                        faceVertOrig.append(l )
                faceVertOrig = np.concatenate(faceVertOrig )
                faceVertOrig -= 1

                faceVertOrig_u = np.unique(faceVertOrig.flatten() )
                vertOrig_s = vertOrig[faceVertOrig_u, :]

                # sample the targetPoint
                mesh = Trimesh(vertices = vertOrig, faces = faceVertOrig )
                targetPoint, _ = trm.sample.sample_surface_even(mesh, 2000 )

                # Scale the shape
                diagLength_o = computeDiagLength(vertOrig, faceVertOrig )

                scale = diagLength_o / diagLength
                vertices = vertices * scale
                srcPoint = srcPoint * scale

                # Rotate the shape
                minDist = 2e10
                bestVertices = None
                bestNormals = None
                bestPoints = None

                for angle in range(0, 360, 90 ):
                    rotMat = np.eye(3)
                    rotMat[0, 0] = np.cos(angle / 180.0 * np.pi )
                    rotMat[0, 2] = np.sin(angle / 180.0 * np.pi )
                    rotMat[2, 0] = -np.sin(angle / 180.0 * np.pi )
                    rotMat[2, 2] = np.cos(angle / 180.0 * np.pi )

                    vertices_t = np.matmul(rotMat, vertices.transpose() ).transpose()
                    normals_t = np.matmul(rotMat, normals.transpose() ).transpose()
                    srcPoint_t = np.matmul(rotMat, srcPoint.transpose() ).transpose()

                    # Translate the shape
                    for dim in range(0, 3):
                        minD, maxD = vertices_t[:, dim].min(), vertices_t[:, dim].max()
                        minD_o, maxD_o = vertOrig_s[:, dim].min(), vertOrig_s[:, dim].max()
                        translate = 0.5 * (maxD_o - maxD + minD_o - minD )
                        vertices_t[:, dim] = vertices_t[:, dim] + translate
                        srcPoint_t[:, dim] = srcPoint_t[:, dim] + translate

                    # compute chamfer_distance
                    srcPoint_t_v = Variable(torch.from_numpy(
                        srcPoint_t.astype(np.float32 ) ) ).cuda()
                    targetPoint_v = Variable(torch.from_numpy(
                        targetPoint.astype(np.float32) ) ).cuda()

                    dist1, _, dist2, _ = chamferDist(srcPoint_t_v.unsqueeze(0), \
                            targetPoint_v.unsqueeze(0) )
                    dist = torch.sum(dist1 ) + torch.sum(dist2 )
                    dist = dist.data.item()

                    print('Angle, Dist: %d %.3f' % (angle, dist ) )

                    if dist < minDist:
                        minDist = dist
                        bestVertices = vertices_t
                        bestNormals = normals_t
                        bestPoints = srcPoint_t

                if minDist > 10:
                    print('Warning: the min dist is too large, two models cannot be aligned')
                    with open('alignmentFailure.txt', 'a') as fOut:
                        fOut.write(model + '\n')
                    continue

                vertices = bestVertices
                normals = bestNormals
                srcPoint = bestPoints

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

        cnt += 1
