"""
Make tars that contains 'EVPSC' executable and other files
corresponding to the process that the end-user wants
"""
from os import sep, getcwd, chdir,system
from glob import glob
from tempfile import mktemp

## import multiprocessing
import subprocess

def worker(cmd,stdout=None,stderr=None,i=-1,head=None,
           wd=None,ishell=True):
    import shlex
    if head==None: head=''
    print '%s Worker #%i started'%(head,i)
    if stdout==None: stdout=open('/dev/null','w')

    if wd!=None:
        path0 = getcwd()
        chdir(wd)

    if ishell:
        cmd = shlex.split(cmd)
    else:
        cmd = [cmd]

    p = subprocess.Popen(cmd,
                         stderr=stderr,
                         stdout=stdout)

    if wd!=None: chdir(path0)

    return p

def ivgvar20in_workers(path='.', max_np=3):
    """ """
    common_fns, par_fns, par_loading_paths, par_ids_loading_paths = ivgvar20in(path=path)
    cmds    = []; fn_tars = []
    stdouts = []; stderrs = []
    for i in range(len(par_fns)):
        cmd,fn_tar,stdout,stderr = tar_cmd(
            i,common_fns,par_fns[i],'evpsc','EVPSC.IN')
        cmds.append(cmd); fn_tars.append(fn_tar)
        stdouts.append(stdout); stderrs.append(stderr)
    workers = []
    for i in range(len(cmds)):
        p = worker(cmd=cmds[i],
                   head='- Make tar -',
                   stdout=stdouts[i],
                   stderr=stderrs[i],
                   i=i,
                   ishell=True)

        workers.append(p)
        n = n_active(workers)

        ## limit the number of active calculations
        if n<max_np: pass
        else:
        ## Wait until a work is finished.
            while not(n<max_np):
                n=n_active(workers)

    ## Wait until all processes are finished.
    fin=False
    while not(fin):
        n=n_active(workers)
        if n==0: fin=True

    ## --
    for i in range(len(cmds)):
        stdouts[i].close();stderrs[i].close()
    return fn_tars, par_loading_paths, par_ids_loading_paths

def ivgvar20in(path='.'):
    """ Make a collection of tar(s) for ivgvar.eq.20 """
    fn_line_number_container=[9,11,15,39]
    common_fns_container = []

    ## -- Read lines from 'EVPSC.IN'
    f=open('%s%s%s'%(path,sep,'EVPSC.IN'),'r')
    l=f.readlines();f.close();lines=[]

    for i in range(len(l)):
        lines.append(l[i].split('\n')[0])
    ## --

    ## -- Add common file names
    for i in range(len(fn_line_number_container)):
        ix = fn_line_number_container[i]-1
        common_fns_container.append(lines[ix])

    ## add snapshots files to distribute to each parallel kernel
    paths = [] ## Check if snapshots are from various paths?
    par_fns_container = [ ]
    npar = int(lines[40-1])
    for i in range(npar):
        l = lines[40+i]
        _path_ = l.split(sep)[-2]
        if not(_path_ in paths): paths.append(_path_)
        par_fns_container.append(l)


    ## Allocate snapshots to individual paths
    par_fns_container_paths = []
    par_ids_container_paths = []
    for i in range(len(paths)):
        par_fns_container_paths.append([])
        par_ids_container_paths.append([])
        _path_ = paths[i]
        for j in range(len(par_fns_container)):
            _snap_fn_ = par_fns_container[j]
            if _snap_fn_.split(sep)[-2]==_path_:
                par_fns_container_paths[i].append(
                    _snap_fn_)
                par_ids_container_paths[i].append(
                    j)

    return common_fns_container, par_fns_container,\
        par_fns_container_paths,par_ids_container_paths

def ivgvar20out(path='.',fn=None,stdout_fn='stdout_tar',
                stderr_fn='stdin_tar',wait=False):
    """
    Make a tar file under the given directory for ivgvar.eq.20
    """
    import subprocess
    path0=getcwd()
    # --
    stdo = open(stdout_fn,'w'); stde = open(stderr_fn,'w');
    fns=glob('*.out','*.OUT')

    ## Determine the 'tar' command
    if fn==None:
        fn = mktemp(dir=path,suffix='.tar',
                    prefix='EVPSC_ivg20_rst_')
    cmd ='tar -cf %s'%fn
    for i in range(len(fns)):
        cmd = '%s %s'%(cmd,fns[i])
    p = subprocess.Popen([cmd],stderr=stde,stdout=stdo)
    if wait: p.wait()
    # --
    chdir(path0)
    return p, stdo, stde

def tar_cmd(i,common_fns,*args):
    fn_tar='ivg20in_%i.tar'%i
    stdo=mktemp(dir=getcwd(),
                prefix='stdout_ivg20in_')
    stde=mktemp(dir=getcwd(),
                prefix='stderr_ivg20in_')
    stdout=open(stdo,'w');stderr=open(stde,'w')
    cmd = 'tar -cvf %s'%fn_tar
    for i in range(len(common_fns)):
        cmd = '%s %s'%(cmd,common_fns[i])
    for arg in args: cmd = '%s %s'%(cmd,arg)
    return cmd, fn_tar, stdout, stderr

def n_active(workers):
    n = 0
    for i in range(len(workers)):
        if workers[i].poll()==None:
            n=n+1
    return n
