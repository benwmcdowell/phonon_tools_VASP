from numpy import array,dot
from numpy.linalg import inv
from getopt import getopt
import sys
from parse_modes_VASP import parse_modes_VASP

def displace_along_modes(poscar,outcar,scale,**args):
    modes,mode_types=parse_modes_VASP(outcar)
    if 'mode_nums' in args:
        modes_to_use=args['mode_nums']
    else:
        modes_to_use=[i for i in range(len(mode_types))]
        
    try:
        lv,coord,atomtypes,atomnums,seldyn=parse_poscar(poscar)
    except ValueError:
        lv,coord,atomtypes,atomnums=parse_poscar(poscar)
        seldyn=0
        
    for i in range(len(modes)):
        if mode_types[i]=='imaginary' and i in modes_to_use:
            coord+=modes[i]*scale
    if seldyn==0:
        write_poscar('./POSCAR_disp',lv,coord,atomtypes,atomnums)
    else:
        write_poscar('./POSCAR_disp',lv,coord,atomtypes,atomnums,seldyn=seldyn)
    
def parse_poscar(ifile):
    with open(ifile, 'r') as file:
        lines=file.readlines()
        sf=float(lines[1])
        latticevectors=[float(lines[i].split()[j])*sf for i in range(2,5) for j in range(3)]
        latticevectors=array(latticevectors).reshape(3,3)
        atomtypes=lines[5].split()
        atomnums=[int(i) for i in lines[6].split()]
        if 'Direct' in lines[7] or 'Cartesian' in lines[7]:
            start=8
            mode=lines[7].split()[0]
        else:
            mode=lines[8].split()[0]
            start=9
            seldyn=[''.join(lines[i].split()[-3:]) for i in range(start,sum(atomnums)+start)]
        coord=array([[float(lines[i].split()[j]) for j in range(3)] for i in range(start,sum(atomnums)+start)])
        if mode!='Cartesian':
            for i in range(sum(atomnums)):
                for j in range(3):
                    while coord[i][j]>1.0 or coord[i][j]<0.0:
                        if coord[i][j]>1.0:
                            coord[i][j]-=1.0
                        elif coord[i][j]<0.0:
                            coord[i][j]+=1.0
                coord[i]=dot(coord[i],latticevectors)
            
    #latticevectors formatted as a 3x3 array
    #coord holds the atomic coordinates with shape ()
    try:
        return latticevectors, coord, atomtypes, atomnums, seldyn
    except NameError:
        return latticevectors, coord, atomtypes, atomnums

def write_poscar(ofile, lv, coord, atomtypes, atomnums, **args):
    with open(ofile,'w') as file:
        if 'title' in args:
            file.write(str(args['title']))
        file.write('\n1.0\n')
        for i in range(3):
            for j in range(3):
                file.write(str('{:<018f}'.format(lv[i][j])))
                if j<2:
                    file.write('  ')
            file.write('\n')
        for i in atomtypes:
            file.write('  '+str(i))
        file.write('\n')
        for i in atomnums:
            file.write('  '+str(i))
        file.write('\n')
        if 'seldyn' in args:
            file.write('Selective Dynamics\n')
        file.write('Direct\n')
        for i in range(len(coord)):
            coord[i]=dot(coord[i],inv(lv))
        for i in range(len(coord)):
            for j in range(3):
                file.write(str('{:<018f}'.format(coord[i][j])))
                if j<2:
                    file.write('  ')
            if 'seldyn' in args:
                for j in range(3):
                    file.write('  ')
                    file.write(args['seldyn'][i][j])
            file.write('\n')
    
if __name__ == '__main__':
    short_opts='h'
    long_opts=['help']
    try:
        modes=sys.argv[1]
        scale=float(sys.argv[2])
    except IndexError:
        print('missing required arguments. exiting...')
        sys.exit()
    try:
        opts,args=getopt(sys.argv[3:],short_opts,long_opts)
    except IndexError:
        print('error specifying optional arguments')
        sys.exit()
    for i,j in opts:
        if i in ['-h','--help']:
            print('''
help options:
    -h, --help                    the first argument is the POSCAR file that should be displaced along imaginary modes
                                  the second argument is the scale by which the structure should be displaced
                                  for example, using ./POSCAR 2.0 will displace ./POSCAR by 2x the normalized eigenvectors contained in the OUTCAR file of the current directory
''')
            sys.exit()
    try:
        displace_along_modes(ifile,scale)
    except NameError:
        print('incorrect specification of files. exiting...')
        sys.exit()
