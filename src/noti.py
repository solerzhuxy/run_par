## notification template
import os
def mail_me(mail_path='/usr/bin/mail', 
            subj='Parallel Job Finished',
            contents='Job Finished',
            addr ='youngung.jeong@gmail.com',
            attch = None):
    cmd="echo '%s' | %s -s '%s' %s"%(
        contents, mail_path, subj, addr)
    print cmd
    iflag = os.system(cmd)
    if iflag!=0: print 'Error in sending the notification'
    
