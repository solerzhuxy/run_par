"""
Run parallel
"""
from os import sep
def worker(dst='/tmp',stderr_fn='stderr.out',
             stdout_fn='stdout.out',exe_fn='evpsc'):
    """
    Arguments
    =========    
    dst       = '/tmp'
    stderr_fn = 'stderr.out'
    stdout_fn = 'stdout.out'
    exe_fn    = 'evpsc'

    Given the arguments, carry out below
    --
    Run *exe_fn* under *dst*
    and save stderr and stdout into *stderr_fn* and stdout_fn*
    under *dst* folder

    Once the subprocess starts, return *process*, stdout, stderr
    Note that stdout and stderr are *file* objects using *open*
    """
    import subprocess
    path0=os.getcwd()

    os.chdir(dst)
    stdo=open(stdout_fn,'w'); stde=open(stderr_fn,'w')
    process=subprocess.Popen(['.%s%s'%(sep,exe_fn)],
                             stderr=stde,stdout=stdo)
    os.chdir(path0)
    return process,stdo,stde
