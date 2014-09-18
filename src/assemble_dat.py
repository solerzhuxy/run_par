"""
Reassemble data file distributed in various paths
are very tedious...


      1. int_els_ph*iph*.out
      2. igstrain_fbulk_ph1.out
      3. STR_STR.OUT
      4. igstrain_bix_ph1.out (sff_converter uses this file)


"""
from os import getcwd, chdir, sep, popen, system
from MP.mat.mech import find_nhead

def tar_ivgvar20(orig,worker_paths=[],strain_paths=[],ids=[],
                 tar_members=['int_els_ph1.out','igstrain_fbulk_ph1.out',
                              'STR_STR.OUT','igstrain_bix_ph1.out']):
    """
    It is advised to save important files separately
    before concatenate the results into a single set of files.
    This is particularly important when snapshots under various
    paths are simultaneously diffracted to change the condition
    in 'dif' file - e.g., for diffrent hkls for all paths.

    Run cat_ivgvar20 independently for paths
    """
    import tempfile
    npaths = len(strain_paths)
    tar_fns = []
    for i in range(npaths):
        ## one path at a time
        _worker_paths_ = []
        for j in range(ids[i]):
            _worker_paths_.append(worker_paths[ids[i][j]])
        cat_ivgvar20(orig,worker_paths=_worker_paths_)

        ## tar.gz for relevant paths
        tar_fn = 'EVPSC_diff_%s_%s.tar.gz'%(
            strain_path[i],
            tempfile.mktemp(dir=orig).sep[-1])
        tar_fns.append(tar_fn)
        cmd = 'tar -cvzf %s '%tar_fn
        for j in range(len(tar_members)):
            member = tar_members[j]
            cmd = '%s %s'%(cmd, member)
        os.system(cmd)
        ##
        for j in range(len(tar_members)):
            os.remove(tar_members[j])

    print 'Following tar.gz files generated:'
    for i in range(npaths):
        print tar_fns[i]
    return tar_fns

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
      4. igstrain_bix_ph1.out (sff_converter uses this file)
      5. Need more to add??

    =========
    Arguments
    orig
    worker_paths = []
    """
    ## in case istep is important, preserve the isteps
    ## based on the order in the worker_paths.
    path0 = getcwd() # valid in case orig differs from cwd

    fns = ['STR_STR.OUT','int_els_ph*.out','igstrain_fbulk_ph*.out','igstrain_bix_ph1.out']

    ## 'STR_STR.OUT' file
    str_lines = []
    fn = 'STR_STR.OUT'
    for i in range(len(worker_paths)):
        chdir(worker_paths[i])
        #        try:
        n = find_nhead(fn) # number of head lines
        p = popen('cat %s'%fn)
        lines = p.readlines()
        if i==0:  str_lines.append(lines[0])
        valid_lines=lines[n:]
        for j in range(len(valid_lines)):
            str_lines.append(valid_lines[j])
        #        except:
        # chdir(path0)
        # raise IOError,'Failed during cat %s'%fn
        chdir(path0)
    fstr = open(fn,'w')
    for i in range(len(str_lines)):
        fstr.write(str_lines[i])
    fstr.close()


    ## 'igstrain_fbulk_ph*.out'
    ## -- Assume single phase
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


    ## 'igstrain_bix_ph1.out'
    ## -- Assume single phase

    igstrainbix_lines = []
    fn = 'igstrain_bix_ph1.out'
    for i in range(len(worker_paths)):
        chdir(worker_paths[i])
        try:
            ## n = find_nhead(fn)
            n = 1 ## hardwired
            p = popen('cat %s'%fn)
            lines = p.readlines()
            if i==0:
                for j in range(n):
                    igstrainbix_lines.append(lines[j])
            valid_lines = lines[n:]
            for j in range(len(valid_lines)):
                igstrainbix_lines.append(valid_lines[j])
        except:
            chdir(path0)
            raise IOError, 'Failed during cat %s'%fn
        chdir(path0)

    f_igstrainbix = open(fn,'w')
    for i in range(len(igstrainbix_lines)):
        f_igstrainbix.write(igstrainbix_lines[i])
    f_igstrainbix.close()

    ## 'int_els_ph*.out'
    ## -- Assume single phase
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
                ## fix the step line
                l = valid_lines[j]
                stp_col = '6i'%(i+1)
                l[:6] = stp_col
                ##
                intels_lines.append(l)
        except:
            chdir(path0)
            raise IOError, 'Failed during cat %s'%fn
        chdir(path0)

    f_intels = open(fn,'w')
    for i in range(len(intels_lines)):
        f_intels.write(intels_lines[i])
    f_intels.close()
