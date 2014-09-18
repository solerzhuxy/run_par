"""
Collection of applications of RP
"""
from os import getcwd, sep, chdir, system
from make_tar import n_active,ivgvar20in_workers,worker
import time

def diff(orig_path=None,max_np=3,noti=False):
    """
    NIST-Diffraction for SF/IG/EPS(hkl) measurements
    on 'deformed' polycrystals under various plastic deformation
    The parallel calculation is carried out on various plastic
    levels

    1. prepare a tar (make_tar.py)
    2. make temp directory and distribute the prepared tars.
    3. Obtain paths of 'mktemp'ed directories
    4. Run parallel
    5. Gather calculation results from the paths
    6. Reassemble data file
       - expected to be themost tedious process
    """
    if orig_path==None: orig_path = getcwd()
    t0 = time.time()

    # 1. prepare a tar (make_tar.py)
    fn_tars, strain_paths, ids_paths = ivgvar20in_workers(path=orig_path,max_np=max_np)
    npaths = len(strain_paths)
    print '%i kinds of strain paths are given'%npaths

    n_works = len(fn_tars)
    print '-- Tar file preparation completed\n'

    # 2. make temp directories and distribute the prepared tars.
    paths2workers = []
    for i in range(n_works):
        # 2-1. Make temp dir and distribute/extract tars
        temp_dir = mkd_mv_extract(
            dir='/tmp',prefix='EVPSC_diff_ivg20_',
            src=fn_tars[i])
        # 2-2. Obtain paths of 'mktemp'ed directories
        paths2workers.append(temp_dir)
        # 2-3. Modify the 'EVPSC.IN' file
        EVPSCIN_mod_ivg20(wd=temp_dir,nth=i)
    print '-- Tar distribution completed\n'

    # 3. Gather workers / and run parallel
    workers=[]; cmds=[]
    for i in range(n_works):
        # 3-1 determine commands
        cmd = './evpsc'
        cmds.append(cmd)
        # 3-2. Run parallel using a limited number of cores
        try:
            p = worker(cmd,stdout=None,i=i,head='- Diff EVPSC - ',
                       wd=paths2workers[i],ishell=False)
        except:
            chdir(orig_path)
            raise IOError, 'Error in worker for EVPSC'
        workers.append(p)
        n = n_active(workers)
        if n<max_np: pass
        else:
            ## Wait until a work is finished if n>max_np
            while not(n<max_np):
                time.sleep(5)
                n = n_active(workers)

    # 4. Wait until all processes are finished.

    n=1000
    while (n!=0):
        time.sleep(5)
        n = n_active(workers)
    print 'Parallel calculations are finished'

    ## post calculation activity
    from assemble_dat import cat_ivgvar20, tar_ivgvar20
    """
    List of important files:
    ['ig_mod_ph1.out','igstrain_bix_ph1.out','igstrain_fbulk_ph1.out',
    'igstrain_load_ph1.out','igstrain_unload_ph1.out','int_els_ph1.out',
    'int_eps_ph1.out','pepshkl.out','sf_ph1.out',sf_fac_ph1.out','STR_STR.OUT']
    """

    # 5. Gather calculation results from the paths
    #    if various kinds of paths were considered
    if npaths>1:
        tar_fns = tar_ivgvar20(orig=orig_path,worker_paths=paths2workers,
                               strain_paths=strain_paths,
                               ids=ids_paths)
    # 6. Reassemble data file if a single path was considered
    #    - expected to be themost tedious process
    elif npaths==1:
        cat_ivgvar20(orig=orig_path,worker_paths=paths2workers)

    print 'Parallel Job for EVPSC diff (ivgvar.eq.20) is finished at %s'%orig_path
    t1 = time.time(); elapsed = t1 - t0
    print 'Elapsed time (hh:mm:ss)  %s'%time.strftime('%H:%M:%S',time.gmtime(elapsed))

    if noti:
        import noti
        noti.mail_me(subj='Parallel run for EVPSC diff is completed',
                     contents='Job finished under %s'%orig_path,
                     addr='youngung.jeong@gmail.com')


"""
In Below are hints for mkmv
"""
from tempfile import mkdtemp
from shutil import move
def mkd(dir='/tmp',prefix='EVPSC_diff_ivg20_'):
    """
    Make a temporary directories (mktemp) and return
    the path
    """
    return mkdtemp(dir=dir,prefix=prefix)
def mv(src,dst): move(src,dst)
def mkd_mv_extract(dir='/tmp',prefix='EVPSC_diff_ivg20_',src=None):
    """
    Mv tar source to the random folder.
    and untar
    """
    if src==None: raise IOError, 'src argument is missing'
    temp_dir = mkd(dir=dir,prefix=prefix)
    mv(src,temp_dir)

    ## extract
    path0 = getcwd()

    try:
        chdir(temp_dir)
        cmd = 'tar -xf %s'%src
        iflag = system(cmd)
    except:
        chdir(path0)
        raise IOError, 'Error during tar extraction 1'

    chdir(path0)
    if iflag!=0: raise IOError, 'Error during tar extraction 2'
    ##
    return temp_dir

def EVPSCIN_mod_ivg20(wd,nth):
    """
    Modify the EVPSC.IN file in *wd* directory, to run
    only for *nth* snapshot (nth starts from 0)
    """
    path0=getcwd()
    chdir(wd)
    try:
        f=open('EVPSC.IN','r');
        l0=f.readlines();f.close()

        f=open('EVPSC.IN','w')
        for i in range(40-1):
            if i==35:f.write('1\n')
            else:f.write(l0[i])

        f.write('1\n')     # only one snapshot
        f.write(l0[40+nth])  # only *40+i* snapshot file in the list
        f.close()
    except:
        chdir(path0)
        raise IOError, 'Failed during modification of EVPSC.IN'
        pass
    chdir(path0)

if __name__=='__main__':
    import getopt, sys

    ## defaults
    max_np = 3
    orig_path = getcwd()

    diff(orig_path=orig_path, max_np=max_np)
