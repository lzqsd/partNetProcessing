import glob
import os.path as osp

dirs = glob.glob('*')
dirs = [x for x in dirs if osp.isdir(x)]
dirs = sorted(dirs )

with open('models.txt', 'w') as modOut:
    cnt = 0
    for d in dirs:
        mods = glob.glob(osp.join(d, '*') )
        mods = [x.split('/')[-1] for x in mods if osp.isdir(x) ]
        mods = sorted(mods )
        for m in mods:
            modOut.write('%s %s %d\n' % (d, m, cnt ) )
            cnt += 1
