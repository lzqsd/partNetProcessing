import glob
import os.path as osp
import json
import os

dirs = glob.glob('*')
dirs = [x for x in dirs if osp.isdir(x) ]
modelIds = {}
for d in dirs:
    mIds = glob.glob(osp.join(d, '*') )
    mIds = [x.split('/')[-1] for x in mIds if osp.isdir(x) ]

    for mId in mIds:
        modelIds[mId ] = d.split('/')[-1]

partRoot = '../partnet/data_v0/'
partDirs = glob.glob(osp.join(partRoot, '*') )
partMIds = {}
for partDir in partDirs:
    if osp.isdir(partDir ):
        meta = osp.join(partDir, 'meta.json')
        with open(meta, 'r') as metaIn:
            data = json.load(metaIn )
        partMIds[data['model_id'] ] = partDir

missingIds = []
missingCats = []
for mId, cId in modelIds.items():
    if not mId in partMIds:
        missingIds.append(mId )
        if not cId in missingCats:
            missingCats.append(cId )
    else:
        print('CatId %s MatId %s' % (cId, mId ) )
        partDir = partMIds[mId ]
        os.system('mkdir %s' % osp.join(cId, mId, 'parts') )
        os.system('cp %s %s' % (osp.join(partDir, '*.json'), osp.join(cId, mId, 'parts') ) )
        os.system('cp -r %s %s' % (osp.join(partDir, 'objs'), osp.join(cId, mId, 'parts') ) )

print('Missing Models: %d' % len(missingIds ) )
print('Missing Categories: %d' % len(missingCats ) )
