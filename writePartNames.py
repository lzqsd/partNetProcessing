import json
import os.path as osp
import glob

catDirs = glob.glob('*')
#catDirs = [x for x in catDirs if osp.isdir(x) ]
catDirs = ['door']

def readJson(jsonFile, partNames ):

    def findParts(data, partNames ):
        for d in data:
            if 'objs' in d:
                if not d['name'] in partNames:
                    partNames.append(d['name'] )
            else:
                if 'children' in d:
                    partNames = findParts(d['children'], partNames )
        return partNames

    with open(jsonFile, 'r') as fIn:
        data = json.load(fIn )
    partNames = findParts(data, partNames )

    return partNames

for catDir in catDirs:
    objDirs = glob.glob(osp.join(catDir, '*') )
    objDirs = [x for x in objDirs if osp.isdir(x) ]
    partNames = []

    metaInfo = None
    for objDir in objDirs:
        if metaInfo is None:
            metaFile = osp.join(objDir, 'parts', 'meta.json')
            if osp.isfile(metaFile ):
                with open(metaFile, 'r') as metaIn:
                    metaInfo = json.load(metaIn )['model_cat']

        jsonFile = osp.join(objDir, 'parts', 'result.json')
        if osp.isfile(jsonFile ):
            partNames = readJson(jsonFile, partNames )

    if not metaInfo is None:
        with open(osp.join(catDir, 'annoMatParts.txt'), 'w') as fOut:
            fOut.write('%s\n' % metaInfo )
            for part in partNames:
                fOut.write('%s:\n' % part )
