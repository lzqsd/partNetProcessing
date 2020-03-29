import glob
import os
import os.path as osp

srcRoot = '../shapenet/ShapeNetCore.v2/'
dirs = glob.glob('*')
dirs = [x for x in dirs if x[0] == '0']
with open('missing.txt', 'w') as fileOut:
    for d in dirs:
        models = glob.glob(osp.join(d, '*') )
        models = [x for x in models if osp.isdir(x) ]
        for model in models:
            catId, modelId = model.split('/')[-2:]
            src = osp.join(srcRoot, catId, modelId )
            if not osp.isdir(src ):
                fileOut.write(model + '\n')
                print(model )
            else:
                os.system('cp %s %s' %
                        (osp.join(src, 'models', 'model_normalized.obj'),
                            osp.join(model, 'origin.obj') ) )
