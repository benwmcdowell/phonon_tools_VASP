from numpy import zeros,array

def parse_modes_VASP(outcar):
    with open(outcar, 'r') as outcar:
        modes=[]
        mode_types=[]
        while True:
            line=outcar.readline()
            if not line:
                break
            if 'NIONS' in line:
                atomnum=int(line.split()[11])
            elif 'THz' in line:
                if '/i' in line:
                    mode_types.append('imaginary')
                else:
                    mode_types.append('real')
                modes.append(zeros((atomnum,3)))
                line=outcar.readline()
                for i in range(atomnum):
                    line=outcar.readline().split()
                    modes[-1][i]+=array([float(line[j]) for j in range(3,6)])
    
    return modes, mode_types
