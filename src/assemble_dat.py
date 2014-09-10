"""
Reassemble data file distributed in various paths
are very tedious...
"""
from os import getcwd, chdir, sep, popen
from MP.mat.mech import find_nhead

def cat_ivgvar20(orig,worker_paths=[],*args):
    """
    Reassemble data by gaithering files distributed in worker_paths
    Then, move the assembled data file to *orig* path

    List of important files:
    ['ig_mod_ph1.out','igstrain_bix_ph1.out','igstrain_fbulk_ph1.out',
    'igstrain_load_ph1.out','igstrain_unload_ph1.out','int_els_ph1.out',
    'int_eps_ph1.out','pepshkl.out','sf_ph1.out',sf_fac_ph1.out','STR_STR.OUT']

    ## 2014 SEP 10
     * Determine the important files by assuming that
       the only post-run application is to carry out
       the rs_ex.ex_consistency analysis.

      1. int_els_ph*iph*.out
      2. igstrain_fbulk_ph1.out
      3. STR_STR.OUT
      4. Need more to add??

    =========
    Arguments
    orig
    worker_paths = []
    """
    ## in case istep is important, preserve the isteps
    ## based on the order in the worker_paths.
    path0 = getcwd() # valid in case orig differs from cwd

    fns = ['STR_STR.OUT','int_els_ph*.out','igstrain_fbulk_ph*.out']

    ## 'STR_STR.OUT' file
    str_lines = []
    fn = 'STR_STR.OUT'
    for i in range(len(worker_paths)):
        chdir(worker_paths[i])
        try:
            n = find_nhead(fn) # number of head lines
            p = popen('cat %s'%fn)
            lines = p.readlines()
            if i==0:  str_lines.append(lines[0])
            valid_lines=lines[n:]
            for j in range(len(valid_lines)):
                str_lines.append(valid_lines[j])
        except:
            chdir(path0)
            raise IOError,'Failed during cat %s'%fn
        chdir(path0)
    fstr = open(fn,'w')
    for i in range(len(str_lines)):
        fstr.write(str_lines[i])
    fstr.close()




    ## 'igstrain_fbulk_ph*.out'
    ## -- 'assumed a single phase'

    igstrainfbulk_lines = []
    fn = 'igstrain_fbulk_ph1.out'
    for i in range(len(worker_paths)):
        chdir(worker_paths[i])
        try:
            ## n = find_nhead(fn)
            n = 1 ## hardwired
            p = popen('cat %s'%fn)
            lines = p.readlines()
            if i==0: 
                for j in range(n):
                    igstrainfbulk_lines.append(lines[j])
            valid_lines = lines[n:]
            for j in range(len(valid_lines)):
                igstrainfbulk_lines.append(valid_lines[j])
        except:
            chdir(path0)
            raise IOError, 'Failed during cat %s'%fn
        chdir(path0)

    f_igstrainfbulk = open(fn,'w')
    for i in range(len(igstrainfbulk_lines)):
        f_igstrainfbulk.write(igstrainfbulk_lines[i])
    f_igstrainfbulk.close()

    ## 'int_els_ph*.out'
    ## -- 'assumed a single phase'

    intels_lines = []
    fn = 'int_els_ph1.out'
    for i in range(len(worker_paths)):
        chdir(worker_paths[i])
        try:
            n = find_nhead(fn)
            p = popen('cat %s'%fn)
            lines = p.readlines()
            if i==0: 
                for j in range(n):
                    intels_lines.append(lines[j])
            valid_lines = lines[n:]
            for j in range(len(valid_lines)):
                intels_lines.append(valid_lines[j])
        except:
            chdir(path0)
            raise IOError, 'Failed during cat %s'%fn
        chdir(path0)

    f_intels = open(fn,'w')
    for i in range(len(intels_lines)):
        f_intels.write(intels_lines[i])
    f_intels.close()
