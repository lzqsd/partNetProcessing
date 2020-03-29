import glob
import os.path as osp


def fixMesh(name ):
    with open(name, 'r') as objIn:
        lines = objIn.readlines()

    newLines = []
    isModified = False
    for line in lines:
        if line[0] == 'v' or line[0] == 'f':
            newLines.append(line )
        elif line[0] == 'u':
            lineParts = line.split('f')
            if len(lineParts ) > 1:
                isModified = True
                mat_group = lineParts[0].split('g')
                newLines.append(mat_group[0] + '\n')
                newLines.append('g' + mat_group[1] + '\n')
                newLines.append('f' + lineParts[1] )
            else:
                newLines.append(line )

    if isModified == True:
        print('%s will be modified' % name )
        with open(name, 'w') as objOut:
            for line in newLines:
                objOut.write(line )

if __name__ == '__main__':
    root = '02747177'
    dirs = glob.glob(osp.join(root, '*') )
    for d in dirs:
        objName = osp.join(d, 'merged.obj')
        if osp.isfile(objName ):
            fixMesh(objName )
