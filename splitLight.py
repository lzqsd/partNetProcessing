import glob
import os
import os.path as osp
import trimesh

dirs = glob.glob('*')
dirs = [d for d in dirs if osp.isdir(d) ]
dirs = sorted(dirs )
cnt = 0
catId = '03636649'
for d in dirs:
    cnt += 1
    objName = osp.join(d, 'alignedNew.obj')
    if not osp.isfile(objName ):
        continue
    print('%d/%d: %s' % (cnt, len(dirs), objName ) )

    # load annotation
    annFile = osp.join(d, 'ann.txt' )
    with open(annFile, 'r') as fIn:
        anns = fIn.readlines()

    matNumFile = osp.join(d, 'matNum.txt')
    with open(matNumFile, 'r') as fIn:
        matNum = fIn.readline()
    matNum = int(matNum.strip() )

    anns = [x.strip() for x in anns if len(x.strip() ) > 0]
    anns = [x for x in anns if x[0] != '#']

    partIds = []
    for x in anns:
        patMat = x.split(' ')[1:]
        patMat = [int(x) for x in patMat ]
        if 9 in patMat:
            partIds.append(matNum - 1 - int(x.split(' ')[0] ) )

    # Output mesh
    meshes = trimesh.load_mesh(objName )
    if hasattr(meshes, 'geometry'):
        vArr, fArr, mArr = [], [], []
        vArr_l, fArr_l, mArr_l  = [], [], []
        vNum = 0
        vNum_l = 0

        gcnt = 0
        for key, mesh in meshes.geometry.items():
            print(mesh.faces.shape[0] )
            if gcnt in partIds:
                vArr_l.append(mesh.vertices )
                fArr_l.append(mesh.faces + vNum_l )
                vNum_l +=mesh.vertices.shape[0]
            else:
                vArr.append(mesh.vertices )
                fArr.append(mesh.faces + vNum )
                vNum = vNum + mesh.vertices.shape[0]
                mArr.append('%s_%s_part%d' % (catId, d, matNum - 1 - gcnt ) )
            gcnt += 1

        # Output mesh
        with open(osp.join(d, 'aligned_light.obj'), 'w') as fOut:
            for v in vArr_l:
                for n in range(0, v.shape[0] ):
                    fOut.write('v %.4f %.4f %.4f\n' % (v[n, 0], v[n, 1], v[n, 2]) )
            for n in range(0, len(fArr_l ) ):
                f = fArr_l[n ]
                for n in range(0, f.shape[0] ):
                    fOut.write('f %d %d %d\n' % (f[n,0] + 1, f[n, 1] + 1, f[n, 2] + 1) )


        with open(osp.join(d, 'aligned_shape.obj'), 'w') as fOut:
            for v in vArr:
                for n in range(0, v.shape[0] ):
                    fOut.write('v %.4f %.4f %.4f\n' % (v[n, 0], v[n, 1], v[n, 2]) )
            for n in range(0, len(fArr ) ):
                fOut.write('usemtl %s\n' % mArr[n] )
                f = fArr[n ]
                for n in range(0, f.shape[0] ):
                    fOut.write('f %d %d %d\n' % (f[n,0] + 1, f[n, 1] + 1, f[n, 2] + 1) )
        os.system('python generateUVmapped.py --src_path %s' % d )
    else:
        assert(len(anns) == 1)
        assert(partId == 0 )
