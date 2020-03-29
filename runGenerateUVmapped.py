import os
import glob
import os.path as osp

src_paths = glob.glob('*')
src_paths = [x for x in src_paths if osp.isdir(x) and x != 'textures']
src_paths = sorted(src_paths )

for src_path in src_paths:
    dirs = glob.glob(osp.join(src_path, '*') )
    dirs = [x for x in dirs if osp.isdir(x) ]
    dirs = sorted(dirs )
    for n in range(0, len(dirs ) ):
        print('%d/%d: %s' % (n, len(dirs), dirs[n]) )
        cmd = 'CUDA_VISIBLE_DEVICES=4 python generateUVmapped.py --src_path %s --modelId %s' % \
                (src_path, n )
        os.system(cmd )
