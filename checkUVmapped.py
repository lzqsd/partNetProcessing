import glob
import os.path as osp
import os

dirs = glob.glob('*')
dirs = [x for x in dirs if x != 'textures' and osp.isdir(x )]
dirs = sorted(dirs )

with open('uvQuality.txt', 'w') as fOut:
    for catName in dirs:
        noUV = []

        modelNames = glob.glob(osp.join(catName, '*') )
        modelNames = [x for x in modelNames if osp.isdir(x) ]
        modelNames = sorted(modelNames )

        for modelName in modelNames:
            if osp.isfile(osp.join(modelName, 'ann.txt') ):
                with open(osp.join(modelName, 'ann.txt'), 'r') as annIn:
                    title = annIn.readline()
                    if not title[0] == '!':
                        alignedObj = osp.join(modelName, 'aligned.obj')
                        if not osp.isfile(alignedObj ):
                            noUV.append(modelName )

        if len(noUV ) >= 1:
            fOut.write('CatID %s: Total number of models %d\n' %
                    (catName, len(modelNames ) ) )
            fOut.write('No UV Models: Total number of models %d\n' % len(noUV ) )
            for modelId in noUV:
                fOut.write('%s ' % modelId.split('/')[-1] )
            fOut.write('\n\n')
