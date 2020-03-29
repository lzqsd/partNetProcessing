import glob
import os.path as osp
import os

dirs = glob.glob('*')
dirs = [x for x in dirs if x != 'textures' and osp.isdir(x )]
dirs = sorted(dirs )

with open('partQaulity.txt', 'w') as fOut:
    for catName in dirs:
        lowQuals = []
        noLabels = []

        modelNames = glob.glob(osp.join(catName, '*') )
        modelNames = [x for x in modelNames if osp.isdir(x) ]

        for modelName in modelNames:
            if osp.isfile(osp.join(modelName, 'ann.txt') ):
                with open(osp.join(modelName, 'ann.txt'), 'r') as annIn:
                    title = annIn.readline()
                    if title[0] == '!':
                        lowQuals.append(modelName.split('/')[-1] )
            else:
                noLabels.append(modelName.split('/')[-1] )

        if len(lowQuals ) + len(noLabels ) >= 1:
            fOut.write('CatID %s: Total number of models %d\n' %
                    (catName, len(modelNames ) ) )
            if len(lowQuals ) >= 1:
                fOut.write('Low Quality Models: Total number of models %d\n' % len(lowQuals ) )
                for modelId in lowQuals:
                    fOut.write('%s ' % modelId )
                fOut.write('\n')
            if len(noLabels ) >= 1:
                fOut.write('No Label Models: Total number of models %d\n' % len(noLabels ) )
                for modelId in noLabels:
                    fOut.write('%s ' % modelId )
                fOut.write('\n')
            fOut.write('\n')
