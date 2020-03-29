import glob
import os.path as osp
import os


catDirs = glob.glob('*')
catDirs = [x for x in catDirs if osp.isdir(x) ]
matList = ['wood', 'plastic', \
        'rough_stone', 'specular_stone', \
        'paint', 'leather', \
        'metal', 'fabric', \
        'rubber']

for catDir in catDirs:
    if osp.isfile(osp.join(catDir, 'annoMatParts.txt') ):
        modelDirs = glob.glob(osp.join(catDir, '*') )
        modelDirs = [x for x in modelDirs if osp.isdir(x) ]

        # Count the number of models that contain annotation
        count = 0
        for modelDir in modelDirs:
            if osp.isdir(osp.join(modelDir, 'parts') ):
                count += 1

        print('%s: %d' % (catDir, count ) )

        with open(osp.join(catDir, 'annoMatParts.txt'), 'r') as fIn:
            lines = fIn.readlines()
            lines = lines[1:]
            for line in lines:
                matSubList = line.split(':')[1].strip()
                matSubList = [x.strip() for x in matSubList.split(',') ]
                for mat in matSubList:
                    if not mat in matList:
                        print('%s : %s: %s' % (catDir, line.split(':')[0].strip(), mat) )
